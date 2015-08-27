#!/bin/sh

expiry_list=('20151016')

dash1='======================================='
dash2='~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

for ticker in $@
do
    echo ""
    echo ""
    echo "$dash1 $ticker $dash1"
    echo ""
    for expiry in "${expiry_list[@]}"
    do
        echo ""
        echo "$dash2 $ticker $expiry $dash2"
        ./long_vertical_spread.py $ticker $expiry
        echo ""
    done
done

