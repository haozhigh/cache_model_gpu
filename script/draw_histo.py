#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import os
from common import *

def draw_histo(suite, bench, out_file):
    kernel_names = parse_ocelot_log(out_file)
    base_name = os.path.basename(out_file)
    base_name = base_name.split('.')[0]
    base_name = base_name.split('_')[1]
    kernel = kernel_names[int(base_name)] 
    ddict = parse_histo_output(out_file)

    pcs = ddict.get_row_ids()
    num_pcs = len(pcs)
    pc_id = 1
    for pc in pcs:
        ax = plt.subplot(num_pcs, 1, pc_id)
        pc_id = pc_id + 1
        distance_occurance = ddict.get_row(pc)
        distances = ddict.get_col_ids(pc)
        index = np.arange(len(distances))
        rect = ax.bar(index + 0.3, distance_occurance, 0.4, color = 'green', alpha = 0.5)
        for i in range(0, len(rect)):
            height = rect[i].get_height()
            ax.text(rect[i].get_x() + rect[i].get_width() / 2, height * 1.01, '%d'%(int(distance_occurance[i])), ha = 'center', va = 'baseline')
        ax.set_xlim(0, len(distances))
        ax.set_xticks(index + 0.5)
        ax.set_xticklabels(distances, rotation = 'vertical')
        ax.set_xlabel("Distance")
        ax.set_ylabel("Occurance")
        ax.set_title("PC: " + str(pc))

    chart_out_dir = "../output/charts/" + suite + "/" + bench + "/"
    chart_out_file = os.path.join(chart_out_dir, "histo_" + kernel + ".png")
    ensure_dir_exists(chart_out_dir)
    fig = plt.gcf()
    fig.set_size_inches(14, 6 * num_pcs)
    fig.set_dpi(72)
    fig.set_tight_layout(True)
    fig.savefig(chart_out_file)
    fig.clf()

def main():
    model_version = get_model_version_from_argv()
    if model_version == -1:
        return -1

    model_out_dir = "../output/model_" + model_version + "_histo"
    suites = os.listdir(model_out_dir)
    for suite in suites:
        suite_out_dir = os.path.join(model_out_dir, suite)
        benches = os.listdir(suite_out_dir)
        for bench in benches:
            print("####Starting Processing " + bench)
            print('')
            bench_out_dir = os.path.join(suite_out_dir, bench)
            out_files = get_output_files(bench_out_dir, 'out')
            for out_file in out_files:
                draw_histo(suite, bench, os.path.join(bench_out_dir, out_file))

if __name__ == '__main__':
    main()
