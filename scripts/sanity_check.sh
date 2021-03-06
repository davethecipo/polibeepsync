#!/usr/bin/env bash
root=$(git rev-parse --show-toplevel)

flake8 "$root/polibeepsync"
py.test --cov polibeepsync "$root/tests"

exit $?
