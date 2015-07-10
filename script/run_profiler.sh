#!/bin/bash
nvprof_flags="--metrics l1_cache_global_hit_rate,l2_l1_read_hit_rate"
build_absolute_dir=`pwd`/../build

cd ../src/benchmarks
suites=`ls`
for suite in $suites; do
    if [ $suite == common ]; then
        continue
    fi

    cd $suite
    benches=`ls`
    for bench in $benches; do
        cd $bench
        echo "####Start bench: $suite/$bench"

        args=''
        if [ -e args ]; then
            args=`cat ./args`
        fi

        cd $build_absolute_dir
        output_dir=../output/profiler/$suite
        output_file=$output_dir/${bench}.txt
        if [ ! -d $output_dir ]; then
            mkdir $output_dir -p
        fi
        executable=${bench}_profiler
        nvprof $nvprof_flags ./$executable $args 2> $output_file
        nvprof ./$executable $args 2>> $output_file
        cd -

        echo
        cd ..
    done
    cd ..
done
