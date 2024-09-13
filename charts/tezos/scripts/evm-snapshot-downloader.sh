set -e

TEZ_VAR=/var/tezos
EVM_DATA_DIR="${TEZ_VAR}/evm"
SNAPSHOT_FILE="${EVM_DATA_DIR}/snapshot.gz"

if [ ! -d "${TEZ_VAR}" ]; then
  echo "ERROR: /var/tezos doesn't exist. There should be a volume mounted."
  exit 1
fi

if [ -e "${EVM_DATA_DIR}/store.sqlite" ]; then
  echo "EVM node data is already populated"
  exit 0
fi

echo "Couldn't find a pre-existing evm snapshot."

echo "Downloading ${EVM_SNAPSHOT_URL}"
mkdir -p "${EVM_DATA_DIR}"
curl -LfsS ${EVM_SNAPSHOT_URL} | tee >(sha256sum > ${SNAPSHOT_FILE}.sha256sum) > "${SNAPSHOT_FILE}"

chown -R 1000:1000 "${EVM_SNAPSHOT_URL}"
