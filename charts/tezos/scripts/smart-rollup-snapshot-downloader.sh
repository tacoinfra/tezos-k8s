#!/bin/sh

set -e

data_dir="/var/tezos"
rollup_dir="$data_dir/rollup"
snapshot_file=$rollup_dir/rollup.snapshot

if [ ! -d "$data_dir" ]; then
  echo "ERROR: /var/tezos doesn't exist. There should be a volume mounted."
  exit 1
fi

if [ -e "$rollup_dir/context/store.dict" ]; then
  echo "Smart rollup snapshot has already been imported. Exiting."
  exit 0
fi

echo "Did not find a pre-existing smart rollup snapshot."

mkdir -p "$rollup_dir"
curl -LfsS ${SNAPSHOT_URL} | tee >(sha256sum > ${snapshot_file}.sha256sum) > "$snapshot_file"
