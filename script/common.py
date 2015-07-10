#!/usr/bin/python3

import os
import re
import csv
import numpy as np
import matplotlib.pyplot as plt

class ProfilerStat:
    def __init__(self):
        self.kernel = None
        self.l1_miss_rate = 0
        self.l2_miss_rate = 0

class ModelStat:
    def __init__(self):
        self.kernel = None
        self.l1_accesses = 0
        self.l1_misses_com = 0
        self.l1_misses_cap = 0
        self.l1_misses_ass = 0
        self.l1_misses_lat = 0
        self.l1_hits = 0
        self.l1_miss_rate = 0

class SimStat:
    def __init__(self):
        self.kernel = None
        self.l1_hit = 0
        self.l1_hit_reserved = 0
        self.l1_reservation_fail = 0
        self.l1_accesses = 0
        self.l1_misses = 0
        self.l1_miss_rate = 0

##  Parse the output of nvprof profiler, grab statistics needed
##  input:
##      out_file: full path of the file containing model output
##  output:
##      prof_stat: a list of ProfilerStat objects
def parse_profiler_output(out_file):
    f = open(out_file, 'r')
    s = f.read()
    f.close()

    prof_stats = list()

    pattern = re.compile(r'Kernel: (\S+)\(.*\)\s*\d+\s+l1_cache_global_hit_rate\s+L1 Global Hit Rate\s+\S+%\s+\S+%\s+(\S+)%\s*\d+\s+l2_l1_read_hit_rate\s+L2 Hit Rate \(L1 Reads\)\s+\S+%\s+\S+%\s+(\S+)%')
    match = pattern.search(s)
    while match != None:
        prof_stat = ProfilerStat()
        prof_stat.kernel = match.group(1)
        prof_stat.l1_miss_rate = 1 - float(match.group(2)) / 100
        prof_stat.l2_miss_rate = 1 - float(match.group(3)) / 100

        prof_stats.append(prof_stat)
        match = pattern.search(s, pos = match.end())
    return prof_stats

##  Parse the output log of ocelot, get kernel names of the bench
##  input:
##      out_file: full path of the file containing model output
##  output:
##      a list of demangled kernel names
def parse_ocelot_log(out_file):
    dir_name = os.path.dirname(out_file)
    if dir_name.find('model_base') >= 0:
        log_dir = dir_name.replace('model_base', 'trace_base')
    elif dir_name.find('model_modify') >= 0:
        log_dir = dir_name.replace('model_modify', 'trace_base')
    run_log = os.path.join(log_dir, 'run.log')

    f = open(run_log, 'r')
    s = f.read()
    f.close()

    kernel_names = list()

    p = re.compile(r'^\s*Starting with (\S*)\s*$', re.MULTILINE)
    m = p.search(s)
    while m != None:
        name = m.group(1)
        kernel_names.append(demangle_cpp_fun_name(name))
        m = p.search(s, pos = m.end())
    return kernel_names


##  Parse the output of gpu l1 cache model, grab statistics needed
##  input:
##      out_file: full path of the file containing model output
##      run_log: full path of the file containing run log of ocelot
##  output:
##      model_stat: a ModelStat object
def parse_model_output_base(out_file):
    kernel_names = parse_ocelot_log(out_file)

    f = open(out_file, 'r')
    s = f.read()
    f.close()

    model_stat = ModelStat()
    base_name = os.path.basename(out_file)
    base_name = base_name.split('.')[0]
    base_name = base_name.split('_')[1]
    model_stat.kernel = kernel_names[int(base_name)] 
    
    p = re.compile(r'^modelled_accesses: (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_accesses = 0
    else:
        model_stat.l1_accesses = int(m.group(1))

    p = re.compile(r'^modelled_misses\(compulsory\): (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_misses_com = 0
    else:
        model_stat.l1_misses_com = int(m.group(1))

    p = re.compile(r'^modelled_misses\(capacity\): (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_misses_cap = 0
    else:
        model_stat.l1_misses_cap = int(m.group(1))

    p = re.compile(r'^modelled_misses\(associativity\): (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_misses_ass = 0
    else:
        model_stat.l1_misses_ass = int(m.group(1))

    p = re.compile(r'^modelled_misses\(latency\): (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_misses_lat = 0
    else:
        model_stat.l1_misses_lat = int(m.group(1))

    p = re.compile(r'^modelled_hits: (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_hits = 0
    else:
        model_stat.l1_hits = int(m.group(1))

    model_stat.l1_miss_rate = 1 - model_stat.l1_hits / model_stat.l1_accesses
    return model_stat

##  Parse the output of gpu l1 cache model, for traditional 3C model
##  input:
##      out_file: full path of the file containing model output
##      run_log: full path of the file containing run log of ocelot
##  output:
##      model_stat: a ModelStat object
def parse_model_output_new(out_file):
    kernel_names = parse_ocelot_log(out_file)

    f = open(out_file, 'r')
    s = f.read()
    f.close()

    model_stat = ModelStat()
    base_name = os.path.basename(out_file)
    base_name = base_name.split('.')[0]
    base_name = base_name.split('_')[1]
    model_stat.kernel = kernel_names[int(base_name)] 
    
    p = re.compile(r'^CASE: 0 miss_compulsory: (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_misses_com = 0
    else:
        model_stat.l1_misses_com = int(m.group(1))

    p = re.compile(r'^CASE: 0 miss_capacity: (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_misses_cap = 0
    else:
        model_stat.l1_misses_cap= int(m.group(1))

    p = re.compile(r'^modelled_hits: (\d*)\s*$', re.MULTILINE)
    m = p.search(s)
    if m == None:
        model_stat.l1_hits = 0
    else:
        model_stat.l1_hits = int(m.group(1))

    model_stat.l1_misses_ass = 0
    model_stat.l1_accesses = model_stat.l1_misses_com + model_stat.l1_misses_cap + model_stat.l1_misses_ass + model_stat.l1_hits
    model_stat.l1_miss_rate = 1 - model_stat.l1_hits / model_stat.l1_accesses
    return model_stat

def parse_sim_output(out_file):
    f = open(out_file, 'r')
    s = f.read()
    f.close()

    sim_stats = list()
    sum_hit = 0
    sum_hit_reserved = 0
    sum_miss = 0
    sum_reservation_fail = 0

    p1 = re.compile(r'^kernel_name = (\S*)\s*$', re.MULTILINE)
    p2 = re.compile(r'^\s*Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[HIT\] = (\d*)\s*$', re.MULTILINE)
    p3 = re.compile(r'^\s*Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[HIT_RESERVED\] = (\d*)\s*$', re.MULTILINE)
    p4 = re.compile(r'^\s*Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[MISS\] = (\d*)\s*$', re.MULTILINE)
    p5 = re.compile(r'^\s*Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[RESERVATION_FAIL\] = (\d*)\s*$', re.MULTILINE)
    m1 = p1.search(s)
    while m1 != None:
        sim_stat = SimStat()
        sim_stat.kernel = demangle_cpp_fun_name(m1.group(1))

        m2 = p2.search(s, pos = m1.end())
        if m2 == None:
            sim_stat.l1_hit = sum_hit
        else:
            sim_stat.l1_hit = int(m2.group(1))
        sim_stat.l1_hit = sim_stat.l1_hit - sum_hit
        sum_hit = sum_hit + sim_stat.l1_hit

        m3 = p3.search(s, pos = m1.end())
        if m3 == None:
            sim_stat.l1_hit_reserved = sum_hit_reserved
        else:
            sim_stat.l1_hit_reserved = int(m3.group(1))
        sim_stat.l1_hit_reserved = sim_stat.l1_hit_reserved - sum_hit_reserved
        sum_hit_reserved = sum_hit_reserved + sim_stat.l1_hit_reserved
        
        m4 = p4.search(s, pos = m1.end())
        if m4 == None:
            sim_stat.l1_misses = sum_miss
        else:
            sim_stat.l1_misses = int(m4.group(1))
        sim_stat.l1_misses = sim_stat.l1_misses - sum_miss
        sum_miss = sum_miss + sim_stat.l1_misses

        m5 = p5.search(s, pos = m1.end())
        if m5 == None:
            sim_stat.l1_reservation_fail = sum_reservation_fail
        else:
            sim_stat.l1_reservation_fail = int(m5.group(1))
        sim_stat.l1_reservation_fail = sim_stat.l1_reservation_fail - sum_reservation_fail
        sum_reservation_fail = sum_reservation_fail + sim_stat.l1_reservation_fail

        sim_stat.l1_accesses = sim_stat.l1_hit + sim_stat.l1_hit_reserved + sim_stat.l1_misses
        sim_stat.l1_miss_rate = sim_stat.l1_misses / sim_stat.l1_accesses
        sim_stats.append(sim_stat)
        m1 = p1.search(s, pos = m1.end())
    return sim_stats

def demangle_cpp_fun_name(name):
    cmd = "c++filt " + name
    pipe = os.popen(cmd)
    data = pipe.read()
    pipe.close()
    return data.split('(')[0]

##  Sort records by the first element of each reocrd
##  input:
##      records: records to be sorted
##  output:
##      none: change done in the input records
def sort_records(records):
    for i in range(0, len(records) - 1):
        for j in range(i + 1, len(records)):
            compare1 = records[i][0] + records[i][1] + records[i][2]
            compare2 = records[j][0] + records[j][1] + records[j][2]
            if compare1 > compare2:
                tmp = records[i]
                records[i] = records[j]
                records[j] = tmp

##  Read a csv file content to python lists
##  input:
##      file_name: full-path file name of the csv file
##  output:
##      (records, fields)
def get_records_from_csv(file_name):
    file = open(file_name, 'r')
    csv_reader = csv.reader(file)
    records = list()
    is_header_line = True

    for line in csv_reader:
        if is_header_line:
            is_header_line = False
            continue
        records.append(line)
    file.close()
    sort_records(records)
    return records, convert_records_to_fields(records)

##  Convert 2-dimension data of records to fields
##  input:
##      records: records to be converted
##  output:
##      fields: converted fields
def convert_records_to_fields(records):
    fields = list()
    num_fields = len(records[0])

    for i in range(0, num_fields):
        fields.append(list())
    for record in records:
        i = 0
        for item in record:
            fields[i].append(item)
            i = i + 1
    return fields

##  Filter records by each record's suite
##  input:
##      records: original records
##      suite: suite name
##  output:
##      (records, fields): filtered records and fields
def filter_records_by_suite(records, suite):
    filtered_records = list()
    for record in records:
        if record[0] == suite:
            filtered_records.append(record)
    sort_records(filtered_records)
    return filtered_records, convert_records_to_fields(filtered_records)

##  convert a list of strings to a list of integers
##  input:
##      str
##  output:
##      a list of integers
def str2int(str):
    return [int(x) for x in str]

##  convert a list of strings to a list of floats
##  input:
##      str
##  output:
##      a list of floats
def str2float(str):
    return [float(x) for x in str]

##  Get output file name of a given bench
##  input:
##      output_dir: directory of output files
##      suffix: suffix of the output files
##  output:
##      output_files: list of output file names
def get_output_files(output_dir, suffix):
    output_files = os.listdir(output_dir)
    i = 0
    pattern = r'^.*' + suffix + r'$'
    while i < len(output_files):
        output_file = output_files[i]
        if (not re.match(pattern, output_file)):
            output_files.remove(output_file)
            continue
        i = i + 1
    return output_files

##  Get a list of benchmarks, assuming that each benchmark occupies a seperate dir
##  input:
##      bench_dir: directory of the benchmarks
##  output:
##      benches: a list of benchmarks
def get_benches(bench_dir):
    benches = os.listdir(bench_dir)
    i = 0
    while i < len(benches):
        bench = benches[i]
        if not os.path.isdir(os.path.join(bench_dir, bench)):
            benches.remove(bench)
            continue
        i = i + 1
    return benches

##  Check if a file is newer than another
##  input:
##      file1: first file
##      file2: second file
##  output:
##      True or False
def file_newer_than(file1, file2):
    if not os.path.exists(file1):
        return False
    if not os.path.exists(file2):
        return False
    if os.path.getmtime(file1) > os.path.getmtime(file2):
        return True
    else:
        return False

##  Add two vectors
##  intpu:
##      x: vector one
##      y: vector two
##  output:
##      z: add result vector
def add_vector(x, y):
    if len(x) != len(y):
        return list()
    z = list()
    for i in range(0, len(x)):
        z.append(x[i] + y[i])
    return z

def draw_model_2c_compare(mod_records, mod_fields, prof_reocrds, prof_fields, sim_records, sim_fields, output_file):
    kernel_names = mod_fields[2]
    index = np.arange(len(kernel_names))

    rect1 = plt.bar(index + 0.05, mod_fields[3], 0.3, label = 'model(compulsory)', color = 'w', hatch = '---')
    mod_accumulate_miss = mod_fields[3]
    rect2 = plt.bar(index + 0.05, mod_fields[4], 0.3, bottom = mod_accumulate_miss, label = 'model(other)', color = 'w', hatch = '///')
    mod_accumulate_miss = add_vector(mod_accumulate_miss, mod_fields[4])

    for i in range(0, len(rect1)):
        height = rect1[i].get_height() + rect2[i].get_height()
        plt.text(rect2[i].get_x() + rect2[i].get_width() / 2, height * 1.01, '%d'%(int(mod_accumulate_miss[i] * 100)), ha = 'center', va = 'baseline')

    rect4 = plt.bar(index + 0.35, sim_fields[3], 0.3, label = 'sim(compulsory)', color = 'w', hatch = 'x')
    sim_accumulate_miss = sim_fields[3]
    rect5 = plt.bar(index + 0.35, sim_fields[4], 0.3, bottom = sim_accumulate_miss, label = 'sim(other)', color = 'w', hatch = '*')
    sim_accumulate_miss = add_vector(sim_accumulate_miss, sim_fields[4])

    for i in range(0, len(rect4)):
        height = rect4[i].get_height() + rect5[i].get_height()
        plt.text(rect5[i].get_x() + rect5[i].get_width() / 2, height * 1.01, '%d'%(int(sim_accumulate_miss[i] * 100)), ha = 'center', va = 'baseline')

    rect7 = plt.bar(index + 0.65, prof_fields[3], 0.3, label = 'profiler', color = 'w')
    for rect in rect7:
        plt.text(rect.get_x() + rect.get_width() / 2, rect.get_height() * 1.01, '%d'%(int(rect.get_height() * 100)), ha = 'center', va = 'baseline')

    plt.xlim(0, len(kernel_names))
    plt.xticks(index + 0.5, kernel_names, rotation = 'vertical')
    ##plt.title('l1 missrate of profiler and model')
    plt.title('llllll ')
    plt.xlabel('kernel name')
    plt.ylabel('miss rate')
    plt.legend(loc = 'lower left', fontsize = 'small', ncol = 5, bbox_to_anchor = (0, 1))

    fig = plt.gcf()
    fig.set_size_inches(14, 8)
    fig.set_dpi(72)
    fig.set_tight_layout(True)
    fig.savefig("../output/" + output_file)
    fig.clf()


def main():
    print(demangle_cpp_fun_name("_Z17fdtd_step1_kernelPfS_S_S_i"))

if __name__ == '__main__':
    main()