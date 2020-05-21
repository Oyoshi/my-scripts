#!/bin/bash

rmf() {
    find -type d -iname "*$1*" -a -prune -exec rm -rf {} \;
}
