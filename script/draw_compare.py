#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from common import *

def main():
    model_version = get_model_version_from_argv()
    if model_version == -1:
        return -1

    csv_dir = "../output/csv"
    mod_out_file = os.path.join(csv_dir, 'missrate_model_' + model_version + '.csv')
    sim_out_file = os.path.join(csv_dir, 'missrate_sim.csv')
    prof_out_file = os.path.join(csv_dir, 'missrate_profiler.csv')
    mod_records, mod_fields = get_records_from_csv(mod_out_file)
    sim_records, sim_fields = get_records_from_csv(sim_out_file)
    prof_records, prof_fields = get_records_from_csv(prof_out_file)

    suites = ['polybench_gpu', 'parboil']
    for suite in suites:
        mod_r, mod_f = filter_records_by_suite(mod_records, suite)
        mod_f[3] = str2float(mod_f[3])
        mod_f[4] = str2float(mod_f[4])
        sim_r, sim_f = filter_records_by_suite(sim_records, suite)
        sim_f[3] = str2float(sim_f[3])
        sim_f[4] = str2float(sim_f[4])
        sim_f[5] = str2float(sim_f[5])
        prof_r, prof_f = filter_records_by_suite(prof_records, suite)
        prof_f[3] = str2float(prof_f[3])

        chart_out_dir = "../output/charts"
        out_file = os.path.join(chart_out_dir, 'compare_' + model_version + '_' + suite + '.png')
        draw_compare(mod_r, mod_f, prof_r, prof_f, sim_r, sim_f, out_file)

if __name__ == "__main__":
    main()
