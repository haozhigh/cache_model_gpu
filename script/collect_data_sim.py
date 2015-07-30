#!/usr/bin/python3

import os
from common import *

def main():
    csv_lines = list()
    csv_lines.append('suite,bench,kernel,compulsory_miss,other_miss,access\n')

    out_dir = '../output/sim'
    suites = os.listdir(out_dir)
    for suite in suites:
        suite_out_dir = os.path.join(out_dir, suite)
        benches = get_benches(suite_out_dir)
        for bench in benches:
            print(bench)
            bench_out_dir = os.path.join(suite_out_dir, bench)
            reg_sim_stats = parse_sim_output(os.path.join(bench_out_dir, 'regular.trc'))
            inf_sim_stats = parse_sim_output(os.path.join(bench_out_dir, 'infinite.trc'))
            for i in range(0, len(inf_sim_stats)):
                kernel = reg_sim_stats[i].kernel
                miss_com = inf_sim_stats[i].l1_miss_rate
                miss_other = reg_sim_stats[i].l1_miss_rate - inf_sim_stats[i].l1_miss_rate
                access = reg_sim_stats[i].l1_accesses
                csv_line = suite + ','
                csv_line = csv_line + bench + ','
                csv_line = csv_line + kernel + ','
                csv_line = csv_line + str(miss_com) + ','
                csv_line = csv_line + str(miss_other) + ','
                csv_line = csv_line + str(access) + '\n'
                csv_lines.append(csv_line)

    f = open(os.path.join(out_dir, '../missrate_sim.csv'), 'w')
    f.writelines(csv_lines)
    f.close()

if __name__ == '__main__':
    main()
