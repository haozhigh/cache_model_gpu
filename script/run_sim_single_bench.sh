#!/bin/bash

bench=$1
if [ -z $bench ]; then
    echo "Need an argument to specify benchmark name"
    exit -1
fi

run_type=$2
if [ "$run_type" == "regular" -o "$run_type" == "infinite" ]; then
    echo "##Argument check passed"
else
    echo Need a argument to specify run type
    exit -1
fi

build_absolute_dir=`pwd`/../build

cd ../src/benchmarks
suites=`ls`
for suite in $suites; do
    if [ $suite == common ]; then
        continue
    fi

    cd $suite
    if [ -d $bench ]; then
        cd $bench
        echo "####Start bench: $suite/$bench"

        args=''
        if [ -e args ]; then
            args=`cat ./args`
        fi

        cd $build_absolute_dir
        output_dir=../output/sim/$suite/$bench
        output_file=$output_dir/${run_type}.trc
        if [ ! -d $output_dir ]; then
            mkdir $output_dir -p
        fi
        executable=${bench}_sim
        ./$executable $args | tee $output_file
        cd -

        echo
        cd ..
    fi
    cd ..
done
