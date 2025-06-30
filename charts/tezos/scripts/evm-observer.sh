set -ex

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
ROLLUP_DATA_DIR="${TEZ_VAR}/rollup"
EVM_DATA_DIR="${TEZ_VAR}/evm"
EVM_CONFIG_FILE="${EVM_DATA_DIR}/config.json"

EVM_CONFIGMAP_DIR="${TEZ_VAR}/evm-config"
EVM_CONFIGMAP_CONFIG_FILE="${EVM_CONFIGMAP_DIR}/config.json"

# Wait till rollup node to be fully synchronized to run init from rollup command
WAIT_LIMIT=30
COUNTER=1
while [ "$(curl -s http://localhost:8932/local/synchronized | sed 's/^"//;s/"$//')" != "synchronized" ] && [ $COUNTER -lt $WAIT_LIMIT ]; do
  COUNTER=$((COUNTER + 1))
  echo "polling ${COUNTER}/${WAIT_LIMIT}: rollup node not synchronized yet"
  sleep 60
done

if [ "$(curl -s http://localhost:8932/local/synchronized | sed 's/^"//;s/"$//')" != "synchronized" ]; then
  echo "ERROR: rollup node not synchronized within wait limit, exiting...."
  exit 1
fi

if [ ! -e "${EVM_DATA_DIR}/store.sqlite" ]; then
  $TEZ_BIN/octez-evm-node init from rollup node ${ROLLUP_DATA_DIR} --data-dir ${EVM_DATA_DIR}
fi

# Provide basic config if there is no config specified in values.yaml
if [ ! -e "${EVM_CONFIGMAP_CONFIG_FILE}" ]; then
  cat > "${EVM_CONFIG_FILE}" << EOF
  { "rpc-addr": "0.0.0.0", "cors_origins": [ "*" ],
    "cors_headers": [ "*" ],
    "rollup_node_endpoint": "http://127.0.0.1:8932", "verbose": "notice",
    "max_active_connections": 8000 }
EOF
else
  cp -vf ${EVM_CONFIGMAP_CONFIG_FILE} ${EVM_CONFIG_FILE}
fi

CMD="$TEZ_BIN/octez-evm-node run observer \
     --evm-node-endpoint ${EVM_NODE_ENDPOINT} \
     --rollup-node-endpoint http://127.0.0.1:8932 \
     --data-dir ${EVM_DATA_DIR} \
     --preimages-endpoint ${ROLLUP_PREIMAGES_ENDPOINT} \
     --rpc-addr 0.0.0.0 --rpc-port 8545"

exec $CMD