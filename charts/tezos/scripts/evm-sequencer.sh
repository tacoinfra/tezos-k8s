set -e

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
ROLLUP_DATA_DIR="$TEZ_VAR/rollup"
EVM_DATA_DIR="$TEZ_VAR/evm"

set -x

if [ ! -e "${EVM_DATA_DIR}/store/store.dict" ]; then
  $TEZ_BIN/octez-evm-node init from rollup node ${ROLLUP_DATA_DIR} --data-dir ${EVM_DATA_DIR}
fi


CMD="$TEZ_BIN/octez-evm-node run sequencer \
  with endpoint http://127.0.0.1:8932 \
  signing with edsk3rw6fcwjPe5xkGWAbSquLDQALKP8XyMhy4c6PQGr7qQKTYa8rX \
  --data-dir ${EVM_DATA_DIR} \
  --time-between-blocks 6 \
  --rpc-addr 0.0.0.0"

exec $CMD
