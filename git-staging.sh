#!/usr/bin/env bash

git checkout staging
git merge development
git push origin staging
git checkout development