#!/bin/bash

set -e

script_path=$(cd `dirname $0`; pwd)
pushd ${script_path}/..

rm -rf ./venv
python3 -m venv ./venv
source ./venv/bin/activate
which python3
which pip3

pip3 install gfwlist2privoxy
DIR="$(mktemp -d)"
wget https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt -O ${DIR}/gfwlist.txt
gfwlist2privoxy -i ${DIR}/gfwlist.txt -f ${DIR}/gfwlist.action -p 127.0.0.1:1080 -t socks5
sed -i '1d' ${DIR}/gfwlist.action

deactivate

mkdir -p auto/privoxy
cp -v ${DIR}/gfwlist.action auto/privoxy/

popd