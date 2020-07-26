#!/bin/bash

set -e

script_path=$(
  cd "$(dirname $0)"
  pwd
)

pushd ${script_path}

source ../venv/bin/activate

mkdir -p ../auto/privoxy
python3 python/privoxy_gfwlist.py \
  --output-file="../auto/privoxy/gfwlist.action" \
  --forward="socks5" \
  --proxy="ss-local:1080" \
  --abp-rule-base64="https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"

deactivate

popd
