#!/usr/bin/python3

import os
import re
from common import *

def main():
    csv_lines = list()
    csv_lines.append('cate,suite,bench,duration\n')

    output_root_dir = os.path.join(os.getcwd(), '../output')
    output_duration_dir = os.path.join(output_root_dir, 'duration')

    cates = os.listdir(output_duration_dir)
    for cate in cates:
        cate_dir = os.path.join(output_duration_dir, cate)
        suites = os.listdir(cate_dir)
        for suite in suites:
            suite_dir = os.path.join(cate_dir, suite)
            benches = os.listdir(suite_dir)
            for bench in benches:
                output_file = os.path.join(suite_dir, bench)
                duration = parse_duration_output(output_file)
                csv_line = cate + ',' + suite + ','
                csv_line = csv_line + bench.split('.')[0] + ','
                csv_line = csv_line + str(duration) + '\n'
                csv_lines.append(csv_line)

    csv_dir = os.path.join(output_root_dir, 'csv')
    f = open(os.path.join(csv_dir, 'duration.csv'), 'w')
    f.writelines(csv_lines)
    f.close()

if __name__ == '__main__':
    main()
