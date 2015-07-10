#!/bin/bash

build_absolute_dir=`pwd`/../build
executable=cachemodel_modify

cd ../src/benchmarks
suites=`ls`
for suite in $suites; do
    if [ $suite == common ]; then
        continue
    fi

    cd $suite
    benches=`ls`
    for bench in $benches; do
        echo "####Start bench: $suite/$bench"
        cd $bench

        cd $build_absolute_dir
        output_dir=../output/model_modify/$suite/$bench
        if [ ! -e $output_dir ]; then
            mkdir -p $output_dir
        fi
        ./$executable $bench $suite
        cd -

        cd ..
        echo
    done
    cd ..
done
