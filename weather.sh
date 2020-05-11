#!/bin/bash

weather() {
    curl -s "wttr.in/$1?m1"
}
