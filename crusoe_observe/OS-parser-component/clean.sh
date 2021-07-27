#!/usr/bin/env bash

ROOT=$(dirname "$0")

rm -rf ${ROOT}/*.egg-info ${ROOT}/.tox ${ROOT}/.coverage ${ROOT}/.benchmarks ${ROOT}/build ${ROOT}/dist ${ROOT}/htmlcov ${ROOT}/.pytest_cache
