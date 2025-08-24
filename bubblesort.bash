#!/bin/bash

# Bubble sort in bash
arr=(64 34 25 12 22 11 90)  # array to be sorted
n=${#arr[@]}                # length of array

echo "Original array: ${arr[@]}"

for ((i = 0; i < n-1; i++)); do
    for ((j = 0; j < n-i-1; j++)); do
        if (( arr[j] > arr[j+1] )); then
            # swap
            temp=${arr[j]}
            arr[j]=${arr[j+1]}
            arr[j+1]=$temp
        fi
    done
done

echo "Sorted array:   ${arr[@]}"
