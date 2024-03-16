set -e

bin_dir="/usr/local/bin"
data_dir="/var/tezos"
rollup_dir="$data_dir/rollup"
smart_rollup_node="$bin_dir/octez-smart-rollup-node"
snapshot_file=${rollup_dir}/rollup.snapshot

if [ ! -f ${snapshot_file} ]; then
    echo "No snapshot to import."
    exit 0
fi

${smart_rollup_node} snapshot import ${snapshot_file} --data-dir ${rollup_data_dir} --no-check
find ${node_dir}

rm -rvf ${snapshot_file}
