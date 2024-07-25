set -e

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
ROLLUP_DATA_DIR="$TEZ_VAR/rollup"

CMD="$TEZ_BIN/octez-smart-rollup-node \
  --endpoint http://tezos-node-rpc:8732 \
    run \
    --data-dir ${ROLLUP_DATA_DIR}" \
    --acl-override allow-all \
    --log-kernel-debug"

exec $CMD
