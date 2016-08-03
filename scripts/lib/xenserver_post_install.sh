#!/bin/bash
server=$( grep DHCPACK /var/log/messages | tail -1 | awk '{ print $NF }' ) system=$( hostname )
# Disable pxe (disable netboot)
wget -O /dev/null "http://$server/cblr/svc/op/nopxe/system/$system"
