#!/bin/bash

set -e

script_path=$(
  cd "$(dirname $0)"
  pwd
)

pushd ${script_path}

source ../venv/bin/activate

mkdir -p ../auto/surge

python3 python/surge_gfwlist.py \
  --output-file="../auto/surge/gfwlist.list" \
  --abp-rule-base64="https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt" \
  --type="list"

python3 python/surge_gfwlist.py \
  --output-file="../auto/surge/gfwlist.set" \
  --abp-rule-base64="https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt" \
  --type="set"

deactivate

popd
