function get_time_ms {
    t1=`date +%s`
    t1=$(((t1 % 100000) * 1000))
    t2=10#`date +%N`
    t2=$((t2 / 1000000))
    t=$((t1 + t2))
    echo $t
}
