#!/bin/bash

### use script from https://github.com/felixonmars/dnsmasq-china-list

DNS_PLACEHOLDER="===DNS==="
DNS_SERVERS="223.5.5.5 223.6.6.6 119.29.29.29"

set -e

script_path=$(cd "$(dirname "$0")"; pwd)
pushd ${script_path}/..

DIR="$(mktemp -d)"
git clone --depth=1 https://github.com/felixonmars/dnsmasq-china-list.git ${DIR}
pushd ${DIR}
make SERVER="${DNS_PLACEHOLDER}" dnscrypt-proxy
popd
mkdir -p auto/dnscrypt-proxy
cp ${DIR}/dnscrypt-proxy-forwarding-rules.txt auto/dnscrypt-proxy/forwarding-rules.txt
sed -i -e "s/${DNS_PLACEHOLDER}/ ${DNS_SERVERS}/g" auto/dnscrypt-proxy/forwarding-rules.txt

popd