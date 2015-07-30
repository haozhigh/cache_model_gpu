#!/usr/bin/python3

import os
import re
from common import *

def main():
    csv_lines = list()
    csv_lines.append("suite,bench,kernel,l1_miss_rate,l2_miss_rate\n")

    output_dir = os.path.join(os.getcwd(), '../output/profiler')
    suites = os.listdir(output_dir)

    for suite in suites:
        suite_output_dir = os.path.join(output_dir, suite)
        output_files = get_output_files(suite_output_dir, 'txt')

        for output_file in output_files:
            bench = output_file.split('.')[0]
            output_path = os.path.join(suite_output_dir, output_file)
            prof_stats = parse_profiler_output(output_path)
            for prof_stat in prof_stats:
                csv_line = suite + ','
                csv_line = csv_line + bench + ','
                csv_line = csv_line + prof_stat.kernel + ','
                csv_line = csv_line + str(prof_stat.l1_miss_rate) + ','
                csv_line = csv_line + str(prof_stat.l2_miss_rate) + '\n'
                csv_lines.append(csv_line)

    f = open(os.path.join(output_dir, '../missrate_profiler.csv'), 'w')
    f.writelines(csv_lines)
    f.close()

if __name__ == '__main__':
    main()
