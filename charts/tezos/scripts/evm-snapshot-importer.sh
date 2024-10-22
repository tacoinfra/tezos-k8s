set -ex

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
EVM_DATA_DIR="${TEZ_VAR}/evm"
SNAPSHOT_FILE="${EVM_DATA_DIR}/snapshot.gz"

if [ ! -f ${SNAPSHOT_FILE} ]; then
    echo "No snapshot to import."
    exit 0
fi

if [ -e "${EVM_DATA_DIR}/store.sqlite" ]; then
  echo "EVM node data is already populated"
  exit 0
fi

"${TEZ_BIN}/octez-evm-node" snapshot import ${SNAPSHOT_FILE} --data-dir ${EVM_DATA_DIR}

echo "List populated data dir of evm "
find ${EVM_DATA_DIR}

rm -rvf ${SNAPSHOT_FILE}
