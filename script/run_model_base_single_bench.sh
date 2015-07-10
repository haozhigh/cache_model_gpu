#!/bin/bash

bench=$1
if [ -z $bench ]; then
    echo "Need an argument to specify benchmark name"
    exit -1
fi

build_absolute_dir=`pwd`/../build
executable=cachemodel_base

cd ../src/benchmarks
suites=`ls`
for suite in $suites; do
    if [ $suite == common ]; then
        continue
    fi

    cd $suite
    if [ -d $bench ]; then
        echo "####Start bench: $suite/$bench"
        cd $bench

        cd $build_absolute_dir
        output_dir=../output/model_base/$suite/$bench
        if [ ! -e $output_dir ]; then
            mkdir -p $output_dir
        fi
        ./$executable $bench $suite
        cd -

        echo
        cd ..
    fi
    cd ..
done
