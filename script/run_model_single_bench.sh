#!/bin/bash

source common.sh

model_version=$1
if [ -z $model_version ]; then
    echo "Need an argument to specify model version"
    echo "Available versions: base modify modify_expanded enhance enhance_expanded enhance_histo"
    exit -1
fi

if [ "$model_version" != "base" -a "$model_version" != "modify" -a "$model_version" != "modify_expanded" -a "$model_version" != "enhance" -a "$model_version" != "enhance_expanded" -a "$model_version" != "enhance_histo" ]; then
    echo "Model version $model_modify doesn't match"
    echo "Available versions: base modify modify_expanded enhance enhance_expanded enhance_histo"
    exit -1
fi
echo "#### Starting run cachemodel $model_version"

bench=$2
if [ -z $bench ]; then
    echo "Need an argument to specify bench to run"
    exit -1
fi

build_absolute_dir=`pwd`/../build
executable=cachemodel_$model_version

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
        output_dir=../output/model_$model_version/$suite/$bench
        if [ ! -e $output_dir ]; then
            mkdir -p $output_dir
        fi
        duration_output_dir=../output/duration/model_$model_version/$suite
        duration_output_file=$duration_output_dir/${bench}.out
        if [ ! -d $duration_output_dir ]; then
            mkdir -p $duration_output_dir
        fi
        time_start=`get_time_ms`
        ./$executable $bench $suite
        time_end=`get_time_ms`
        duration=$((time_end - time_start))
        echo $duration > $duration_output_file
        cd -

        cd ..
        echo
    fi
    cd ..
done
