#!/bin/bash

function usage {
echo "usage: create_network_interface.sh <interface> <mac> <ip> <netmask> <gateway>"
}

if [  $# -ne  5 ]; 
then
   echo "missing arguments no of args $#"
   usage
   exit 1
fi

UUID=$(uuidgen)

config_string=$"DEVICE=$1\nBOOTPROTO=static\nHWADDR=$2\nIPV6INIT=\"no\"\nMTU=\"1500\"\nNM_CONTROLLED=\"no\"\nONBOOT=\"yes\"\nTYPE=\"Ethernet\"\nUUID=\"$UUID\"\nIPADDR=$3\nNETMASK=$4\nGATEWAY=$5" 
path=/etc/sysconfig/network-scripts/ifcfg-"$1"
echo -e "$config_string" > "$path"
service network restart
result=$?
if [ "$result" -ne 0 ]; 
then
   echo "failed to configure network interface return val=$result"
   exit 1
fi
exit 0
