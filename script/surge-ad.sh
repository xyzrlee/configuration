#!/bin/bash

### use script from https://github.com/h2y/Shadowrocket-ADBlock-Rules

script_path=$(cd `dirname $0`; pwd)

pushd ${script_path}
mkdir -p ..auto/surge
python3 ad.py ../auto/surge/ad.list
popd
