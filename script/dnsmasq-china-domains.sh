#!/bin/bash

### use script from https://github.com/felixonmars/dnsmasq-china-list

set -e

script_path=$(cd `dirname $0`; pwd)
pushd ${script_path}/..

DIR="$(mktemp -d)"
git clone --depth=1 https://github.com/felixonmars/dnsmasq-china-list.git ${DIR}
pushd ${DIR}
make SERVER=119.29.29.29 dnsmasq
popd
mkdir -p auto/dnsmasq
cp ${DIR}/accelerated-domains.china.dnsmasq.conf auto/dnsmasq/china-domains.conf

popd
