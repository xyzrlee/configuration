#!/bin/bash

script_path=$(cd `dirname $0`; pwd)
pushd ${script_path}/..

rm .gitignore
mv gh-pages.gitignore .gitignore

popd