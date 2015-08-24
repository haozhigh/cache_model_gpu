#!/usr/bin/python3

print("-i ../../../../datasets/parboil/tpacf/small/input/Datapnts.1,", end = "")
for i in range(100):
    print("../../../../datasets/parboil/tpacf/small/input/" + "Randompnts." + str(i + 1) + ",", end = "")
print(" -o ../../../../output/bench_output/parboil/tpacf_small.out")
