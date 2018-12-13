#!/bin/bash

while read address
do
    read RSSI
    echo "$address,$RSSI"
done
