#!/bin/bash

set -e

script_path=$(cd "`dirname $0`"; pwd)

pushd ${script_path}

source ../venv/bin/activate

mkdir -p ../auto/surge
python3 python/surge_ad.py \
  --output-file=../auto/surge/ad.list \
  --abp-rule=https://easylist-downloads.adblockplus.org/easylistchina.txt \
  --abp-rule=https://easylist-downloads.adblockplus.org/easylistchina+easylist.txt \
  --abp-rule=https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/ABP-FX.txt

deactivate

popd
