#!/bin/sh

set -e

data_dir="/var/tezos"
rollup_data_dir="$data_dir/rollup"
snapshot_file="$rollup_data_dir/rollup.snapshot"

if [ ! -d "$data_dir" ]; then
  echo "ERROR: /var/tezos doesn't exist. There should be a volume mounted."
  exit 1
fi

if [ -e "$rollup_data_dir/storage/l2_blocks/data" ]; then
  echo "Smart rollup snapshot has already been imported. Exiting."
  exit 0
fi

# if [ -e "${snapshot_file}" ]; then
#   echo "Temporary - snapshot file already dl'd, not doing it again"
#   exit 0
# fi

echo "Did not find a pre-existing smart rollup snapshot."

echo "Downloading ${SNAPSHOT_URL}"
mkdir -p "$rollup_data_dir"
curl -LfsS ${SNAPSHOT_URL} | tee >(sha256sum > ${snapshot_file}.sha256sum) > "$snapshot_file"

chown -R 1000:1000 "$data_dir"