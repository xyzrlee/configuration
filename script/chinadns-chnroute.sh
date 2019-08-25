#!/bin/bash

script_path=$(cd `dirname $0`; pwd)
pushd ${script_path}/..

mkdir -p auto/chinadns
curl 'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest' | grep ipv4 | grep CN | awk -F\| '{ printf("%s/%d\n", $4, 32-log($5)/log(2)) }' >auto/chinadns/chnroute.txt

popd