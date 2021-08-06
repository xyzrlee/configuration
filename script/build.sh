#!/usr/bin/env bash

set -e

script_path=$(cd `dirname $0`; pwd)
pushd ${script_path}/..

chmod +x *.sh

venv.sh
gitignore.sh
surge-ad.sh
surge-gfwlist.sh
dnscrypt-proxy-forwarding.sh
privoxy-gfwlist.sh
chinadns-chnroute.sh
dnsmasq-china-domains.sh
telegram-cidr.sh

popd
