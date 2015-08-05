#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import os
from common import *

def main():
    model_version = get_model_version_from_argv()
    if model_version == -1:
        return -1

    model_out_dir = "../output/" + model_version
    suites = os.listdir(model_out_dir)
    for suite in suites:
        model_suite_out_dir = os.path.join(model_out_dir, suite)
        benches = os.listdir(model_suite_out_dir)
        for bench in benches:
            model_bench_out_dir = os.path.join(model_suite_out_dir, bench)


if __name__ == '__main__':
    main()
