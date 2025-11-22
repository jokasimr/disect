#!/bin/bash


inname=tests/working-requirements.txt
tmpname=tests/minimal-requirements.txt

##### TEST 1 BAD DEPENDENCY
for package in ipykernel scipy anyio zipp webcolors
do
    rm -f $tmpname
    ./disect.py $inname $tmpname start > /dev/null

    for i in `seq 16`
    do
        if grep -q "$package==" $tmpname
        then
            ./disect.py $inname $tmpname good > /dev/null
        else
            ./disect.py $inname $tmpname bad > /dev/null
        fi
    done

    if ! grep -q "$package==" $tmpname \
     || grep -qv "$package" $tmpname | grep "=="
    then
        echo "Test failed: One bad dep ($package)"
    fi
done


##### TEST 2 BAD DEPENDENCIES
for package1 in ipykernel scipy
do
for package2 in anyio zipp webcolors
do
    rm -f $tmpname
    ./disect.py $inname $tmpname start > /dev/null

    for i in `seq 21`
    do
        if grep -q "$package1==" $tmpname \
        && grep -q "$package2==" $tmpname
        then
            ./disect.py $inname $tmpname good > /dev/null
        else
            ./disect.py $inname $tmpname bad > /dev/null
        fi
    done

    if ! grep -q "$package1==" $tmpname \
     || ! grep -q "$package2==" $tmpname \
     || grep -v -e "$package1" -e "$package2" $tmpname | grep -q "=="
    then
        echo "Test failed: Two bad dep ($package1, $package2)"
    fi
done
done
