#!/bin/bash

for i in `seq 1 8`; 
do
    echo $i;
    python3 makeSchedule.py $i >> report.$i.txt &
done
