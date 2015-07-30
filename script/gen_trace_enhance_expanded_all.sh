#!/bin/bash
build_absolute_dir=`pwd`/../build

source common.sh

cd ../src/benchmarks
suites=`ls`
for suite in $suites; do
    if [ $suite == common ]; then
        continue
    fi

    cd $suite
    benches=`ls`
    for bench in $benches; do
        echo "####Generate enhance_expanded traces for: $suite/$bench"
        cd $bench

        args=''
        if [ -e args ]; then
            args=`cat ./args`
        fi

        cd $build_absolute_dir
        output_dir=../output/trace_enhance_expanded/$suite/$bench
        output_file=$output_dir/run.log
        if [ ! -d $output_dir ]; then
            mkdir -p $output_dir
        fi
        if [ "`ls $output_dir`" != "" ]; then
            rm $output_dir/*
        fi
        duration_output_dir=../output/duration/trace_enhance_expanded/$suite
        duration_output_file=$duration_output_dir/${bench}.out
        if [ ! -d $duration_output_dir ]; then
            mkdir -p $duration_output_dir
        fi
        time_start=`get_time_ms`
        executable=${bench}_trace_enhance_expanded
        ./$executable $suite $bench $args | tee $output_file
        time_end=`get_time_ms`
        duration=$((time_end - time_start))
        echo $duration > $duration_output_file
        cd -

        echo
        cd ..
    done
    cd ..
done
