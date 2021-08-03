#!/bin/bash

### use script from https://github.com/felixonmars/dnsmasq-china-list

set -e

script_path=$(cd `dirname $0`; pwd)
pushd ${script_path}/..

DIR="$(mktemp -d)"
git clone --depth=1 https://github.com/felixonmars/dnsmasq-china-list.git ${DIR}
pushd ${DIR}
make SERVER=114.114.114.114 dnsmasq
popd
mkdir -p auto/dnsmasq
grep -Pv "[^\x00-\x7F]" ${DIR}/accelerated-domains.china.dnsmasq.conf > auto/dnsmasq/china-domains.conf
#cp ${DIR}/accelerated-domains.china.dnsmasq.conf auto/dnsmasq/china-domains.conf

popd
