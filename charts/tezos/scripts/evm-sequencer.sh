set -e

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
CLIENT_DIR="$TEZ_VAR/client"
ROLLUP_DATA_DIR="$TEZ_VAR/rollup"
SEQUENCER_DATA_DIR="$TEZ_VAR/sequencer"

set -x

octez-evm-node init from rollup node ${ROLLUP_DATA_DIR} \
--data-dir ${SEQUENCER_DATA_DIR}


CMD="$TEZ_BIN/octez-evm-node run sequencer \
  with endpoint http://rollup-${MY_POD_NAME}:8932 \
  signing with edsk3rw6fcwjPe5xkGWAbSquLDQALKP8XyMhy4c6PQGr7qQKTYa8rX \
  --data-dir ${SEQUENCER_DATA_DIR} \
  --time-between-blocks 6 \
  --rpc-addr 0.0.0.0"

exec $CMD
