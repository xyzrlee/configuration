#!/bin/bash

set -e

script_path=$(cd `dirname $0`; pwd)

pushd ${script_path}
rm -rf ../venv
python3 -m venv ../venv
../venv/bin/pip3 install wheel
../venv/bin/pip3 install -r python/adblockplus2surge/requirements.txt
mkdir -p ../auto/surge
../venv/bin/python3 python/run_adblockplus2surge.py \
  --output-file=../auto/surge/ad.list \
  --abp-rule=https://easylist-downloads.adblockplus.org/easylistchina.txt \
  --abp-rule=https://easylist-downloads.adblockplus.org/easylistchina+easylist.txt \
  --abp-rule=https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/ABP-FX.txt
popd
