#!/usr/bin/env bash

set -euo pipefail

/opt/python/cp36-cp36m/bin/pip3 wheel --no-cache-dir -w dist dist/*.tar.gz
