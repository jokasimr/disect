#!/bin/bash


##### TEST 1 BAD DEPENDENCY
rm -f tests/minimal-requirements.txt
./disect.py tests/working-requirements.txt tests/minimal-requirements.txt start > /dev/null

for i in `seq 16`
do
    
    if grep -q 'ipykernel==' tests/minimal-requirements.txt
    then
        ./disect.py tests/working-requirements.txt tests/minimal-requirements.txt good > /dev/null
    else
        ./disect.py tests/working-requirements.txt tests/minimal-requirements.txt bad > /dev/null
    fi
done

diff tests/minimal-requirements.txt.expected tests/minimal-requirements.txt
if [ $? == 1 ]
then
    echo 'One bad dep test failed.'
fi


##### TEST 2 BAD DEPENDENCIES
rm -f tests/minimal-requirements.txt
./disect.py tests/working-requirements.txt tests/minimal-requirements.txt start > /dev/null

for i in `seq 26`
do
    if grep -q 'ipykernel==' tests/minimal-requirements.txt \
    && grep -q 'Jinja2==' tests/minimal-requirements.txt
    then
        ./disect.py tests/working-requirements.txt tests/minimal-requirements.txt good > /dev/null
    else
        ./disect.py tests/working-requirements.txt tests/minimal-requirements.txt bad > /dev/null
    fi
done

diff tests/minimal-requirements.txt.two_bad.expected tests/minimal-requirements.txt
if [ $? == 1 ]
then
    echo 'Two bad deps test failed.'
fi
