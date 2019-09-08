#!/bin/bash

set -e

script_path=$(cd "`dirname $0`"; pwd)

pushd ${script_path}/..

rm -rf venv
python3 -m venv venv

source venv/bin/activate

pip3 install --upgrade pip
pip3 install -r script/python/requirements.txt

deactivate

popd

