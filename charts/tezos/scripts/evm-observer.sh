set -e

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
ROLLUP_DATA_DIR="${TEZ_VAR}/rollup"
EVM_DATA_DIR="${TEZ_VAR}/evm"

set -x

if [ ! -e "${EVM_DATA_DIR}/store/store.1.mapping" ]; then
  $TEZ_BIN/octez-evm-node init from rollup node ${ROLLUP_DATA_DIR} --data-dir ${EVM_DATA_DIR}
fi

CMD="$TEZ_BIN/octez-evm-node run observer \
     --evm-node-endpoint ${EVM_NODE_ENDPOINT} \
     --rollup-node-endpoint http://127.0.0.1:8932 \
     --data-dir ${EVM_DATA_DIR} \
     --preimages-endpoint ${EVM_WASM_ENDPOINT} \
     --rpc-addr 0.0.0.0 \
     --rpc-port 8545 \
     --cors-origins '*' \
     --cors-headers '*'

exec $CMD