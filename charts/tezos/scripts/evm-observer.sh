set -ex

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
ROLLUP_DATA_DIR="${TEZ_VAR}/rollup"
EVM_DATA_DIR="${TEZ_VAR}/evm"
EVM_CONFIG_FILE="${EVM_DATA_DIR}/config.json"

# Wait till rollup node to be fully synchronized to run init from rollup command
WAIT_LIMIT=30
COUNTER=1
while [ "$(curl -s http://localhost:8932/local/synchronized)" != "synchronized" ] && [ $COUNTER -lt $WAIT_LIMIT ]; do
  echo "polling ${COUNTER}/${WAIT_LIMIT}: rollup node not synchronized yet"
  sleep 60
done

if [ "$(curl -s http://localhost:8932/local/synchronized)" != "synchronized" ]; then
  echo "ERROR: rollup node not synchronized within wait limit, exiting...."
  exit 1
fi

if [ ! -e "${EVM_DATA_DIR}/store.sqlite" ]; then
  $TEZ_BIN/octez-evm-node init from rollup node ${ROLLUP_DATA_DIR} --data-dir ${EVM_DATA_DIR}
fi

cat > "${EVM_CONFIG_FILE}" << EOF
{ "rpc-addr": "0.0.0.0", "cors_origins": [ "*" ],
  "cors_headers": [ "*" ],
  "observer":
  { "preimages_endpoint":
  "https://snapshots.eu.tzinit.org/etherlink-ghostnet/wasm_2_0_0",
    "evm_node_endpoint":
    "https://node.ghostnet.etherlink.com",
    "time_between_blocks": 6
  },
  "rollup_node_endpoint": "http://127.0.0.1:8932", "verbose": "notice",
  "tx-pool-tx-per-addr-limit": "200",
  "experimental_features": { "sqlite_journal_mode": "wal" },
  "log_filter": { "max_nb_blocks": 1000, "max_nb_logs": 100000 },
  "max_active_connections": 8000 }
EOF

CMD="$TEZ_BIN/octez-evm-node run observer \
     --evm-node-endpoint ${EVM_NODE_ENDPOINT} \
     --rollup-node-endpoint http://127.0.0.1:8932 \
     --cors-origins '*' --cors-headers '*' \
     --data-dir ${EVM_DATA_DIR} \
     --preimages-endpoint ${ROLLUP_PREIMAGES_ENDPOINT} \
     --rpc-addr 0.0.0.0 --rpc-port 8545"

exec $CMD