#!/bin/bash

up() {
    times=$1
    while [ "$times" -gt "0" ]; do
        cd ..
        times=$(($times - 1))
    done
}
