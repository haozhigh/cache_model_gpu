#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from common import *

def main():
    mod_records, mod_fields = get_records_from_csv('../output/miss_rate_model_modify.csv')
    sim_records, sim_fields = get_records_from_csv('../output/miss_rate_sim.csv')
    prof_records, prof_fields = get_records_from_csv('../output/miss_rate_profiler.csv')

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

        draw_model_2c_compare(mod_r, mod_f, prof_r, prof_f, sim_r, sim_f, 'model_modify_' + suite + '.png')

if __name__ == "__main__":
    main()
