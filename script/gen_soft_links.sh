#!/bin/bash
cd ../src/benchmarks
suites=`ls`

for suite in $suites; do
    if [ "$suite" == "common" ]; then
        continue
    fi

    cd $suite
    benches=`ls`
    for bench in $benches; do
        cd $bench
        echo "##Generating links for $suite/$bench"

        if [ ! -e gpgpusim.config ]; then
            ln -s ../../common/gpgpusim.config .
        fi

        if [ ! -e config_fermi_islip.icnt ]; then
            ln -s ../../common/config_fermi_islip.icnt .
        fi

        cd ..
    done
    cd ..
done
