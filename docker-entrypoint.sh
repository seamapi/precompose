#!/usr/bin/env bash

set -euo pipefail

if [ -n "${GPG_PRIVATE_KEY:-}" ] && [ -n "${GPG_PASSPHRASE:-}" ]; then
  echo "Importing GPG key"

  TMP_KEY=$(mktemp)
  TMP_PASSPHRASE="${HOME}/.passphrase"

  cleanup() {
    rm -f "$TMP_KEY" "$TMP_PASSPHRASE"
  }

  trap cleanup EXIT

  cat <<< "$GPG_PRIVATE_KEY" > "$TMP_KEY"
  cat <<< "$GPG_PASSPHRASE" > "$TMP_PASSPHRASE"

  gpgconf --launch dirmngr
  gpgconf --launch gpg-agent

  gpg --batch --passphrase-file "$TMP_PASSPHRASE" --import "$TMP_KEY"

  for keygrip in $(gpg --with-colons --with-keygrip --list-secret-keys | grep ^grp: | cut -d: -f10) ; do
    /usr/lib/gnupg2/gpg-preset-passphrase --preset "$keygrip" < "$TMP_PASSPHRASE"
  done
else
  echo "No GPG key"
fi

# If we have a command, run that, otherwise run an interactive shell
if [ "$#" -gt 0 ]; then
  exec -- "$@"
else
  exec bash -i
fi
