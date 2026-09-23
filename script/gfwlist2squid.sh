#!/bin/bash

set -e

script_path=$(
  cd "$(dirname $0)"
  pwd
)

pushd ${script_path}

source ../venv/bin/activate

mkdir -p ../auto/squid

python3 python/gfwlist2squid.py \
  --gfwlist-url="https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt" \
  --proxy-domain-file="../auto/squid/gfwlist_domains.txt" \
  --proxy-regex-file="../auto/squid/gfwlist_regex.txt" \
  --direct-domain-file="../auto/squid/gfwlist_direct_domains.txt" \
  --direct-regex-file="../auto/squid/gfwlist_direct_regex.txt" \
  --unsupported-file="../auto/squid/gfwlist_unsupported.txt"

deactivate

popd
