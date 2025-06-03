#!/bin/bash

set -e

# build
git checkout --orphan gh-pages
git rm -rf --cached ../
npm run build

cd dist/spa

git --work-tree dist/spa add -f -A
git --work-tree dist/spa commit -m 'deploy'
# git push git@github.com:Mosquito-Alert/anomaly_detection HEAD:gh-pages --force
git push origin HEAD:gh-pages --force
rm -r dist/spa
git checkout -f main
git branch -D gh-pages

