#!/bin/bash
build_absolute_dir=`pwd`/../build

bench=$1
if [ -z $bench ]; then
    echo "Not enough command-line arguments!"
    exit -1
fi

cd ../src/benchmarks
suites=`ls`
for suite in $suites; do
    if [ $suite == common ]; then
        continue
    fi

    cd $suite
    if [ -d $bench ]; then
        echo "####Generate base traces for: $suite/$bench"
        cd $bench

        args=''
        if [ -e args ]; then
            args=`cat ./args`
        fi

        cd $build_absolute_dir
        output_dir=../output/trace_base/$suite/$bench
        output_file=$output_dir/run.log
        if [ ! -d $output_dir ]; then
            mkdir -p $output_dir
        fi
        if [ "`ls $output_dir`" != "" ]; then
            rm $output_dir/*
        fi
        executable=${bench}_trace_base
        ./$executable $suite $bench $args | tee $output_file
        cd -

        echo
        cd ..
    fi
    cd ..
done
