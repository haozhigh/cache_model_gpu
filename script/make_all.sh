#!/bin/bash

if [ $1 == "clean" ]; then
    echo "##Removing everything in ../build"
    rm -f ../build/*_profiler
    rm -f ../build/*_sim
    rm -f ../build/*_trace_base
    rm -f ../build/cachemodel_*
    exit 0
fi

cd ../src/benchmarks
suites=`ls`
for suite in $suites; do
    if [ $suite != common ]; then
        cd $suite
        benches=`ls`
        for bench in $benches; do
            echo "####Start bench: $suite/$bench"
            cd $bench
            make
            cd ..
            echo
        done
        cd ..
    fi
done
cd ../../script

cd ../src/model_base
echo "####Start making model_base"
make
echo
cd ../../script

cd ../src/model_modify
echo "####Start making model_modify"
make
echo
cd ../../script
