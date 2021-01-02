#!/bin/bash

set -e

script_path=$(cd "$(dirname "$0")"; pwd)
pushd ${script_path}/..

mkdir -p auto/surge
curl 'https://core.telegram.org/resources/cidr.txt' | awk '{ gsub(/[ \t]+$/, "", $0); p = "IP-CIDR"; if ($0 ~ ":") p = "IP-CIDR6"; printf("%s,%s,no-resolve\n", p, $0) }' >auto/surge/telegram-cidr.list

popd
