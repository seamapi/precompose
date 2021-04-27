#!/usr/bin/env bash

set -euo pipefail

groupadd -g "$BUILDER_GID" builder
useradd -u "$BUILDER_UID" -g "$BUILDER_GID" builder

if [ "$#" -lt 1 ]; then
  exec su builder
else
  exec su builder -c "$*"
fi
