set -ex

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
ROLLUP_DATA_DIR="${TEZ_VAR}/rollup"

$TEZ_BIN/octez-smart-rollup-node init observer \
  config for "${ROLLUP_ADDRESS}" \
  with operators \
  --history-mode archive \
  --data-dir "${ROLLUP_DATA_DIR}" \
  --rpc-addr 0.0.0.0 \
  --pre-images-endpoint "${ROLLUP_PREIMAGES_ENDPOINT}" \
  --force

CMD="$TEZ_BIN/octez-smart-rollup-node \
  --endpoint ${NODE_RPC_URL} \
    run \
    --data-dir ${ROLLUP_DATA_DIR} \
    --acl-override allow-all \
    --log-kernel-debug"

exec $CMD
