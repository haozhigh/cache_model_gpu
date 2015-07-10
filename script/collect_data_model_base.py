#!/usr/bin/python3

import os
import re
from common import *

def main():
    csv_lines = list()
    csv_lines.append('suite,bench,kernel,compulsory_miss,other_miss\n')

    output_dir = os.path.join(os.getcwd(), '../output')
    trace_dir = os.path.join(output_dir, 'model_base')

    suites = os.listdir(trace_dir)
    for suite in suites:
        suite_dir = os.path.join(trace_dir, suite)
        benches = os.listdir(suite_dir)
        for bench in benches:
            bench_dir = os.path.join(suite_dir, bench)
            out_files = get_output_files(bench_dir, 'out')
            for out_file in out_files:
                model_stat = parse_model_output_base(os.path.join(bench_dir, out_file))
                miss_com = model_stat.l1_misses_com / model_stat.l1_accesses
                miss_cap = model_stat.l1_misses_cap / model_stat.l1_accesses
                miss_ass = model_stat.l1_misses_ass / model_stat.l1_accesses
                miss_other = miss_ass + miss_cap
                csv_line = suite + ","
                csv_line = csv_line + bench + ","
                csv_line = csv_line + model_stat.kernel + ","
                csv_line = csv_line + str(miss_com) + ','
                csv_line = csv_line + str(miss_other) + '\n'
                csv_lines.append(csv_line)

    f = open(os.path.join(output_dir, 'miss_rate_model_base.csv'), 'w')
    f.writelines(csv_lines)
    f.close()

if __name__ == '__main__':
    main()
