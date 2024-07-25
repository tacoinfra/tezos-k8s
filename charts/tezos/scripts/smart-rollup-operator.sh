set -e

TEZ_VAR=/var/tezos
TEZ_BIN=/usr/local/bin
CLIENT_DIR="$TEZ_VAR/client"
ROLLUP_DATA_DIR="$TEZ_VAR/rollup"
ROLLUP_DATA_DIR_PREIMAGES="$ROLLUP_DATA_DIR/wasm_2_0_0"

xxd -p -c 0 /usr/local/share/tezos/evm_kernel/evm_installer.wasm | tr -d '\n' > /var/tezos/smart-rollup-boot-sector
mkdir -p "$ROLLUP_DATA_DIR_PREIMAGES"
cp /usr/local/share/tezos/evm_kernel/* "$ROLLUP_DATA_DIR_PREIMAGES"

set -x
$TEZ_BIN/octez-smart-rollup-node \
  --endpoint http://tezos-node-rpc:8732 \
  -d $CLIENT_DIR \
  init operator config for ${ROLLUP_ADDRESS} with operators ${OPERATORS_PARAMS} \
  --data-dir ${ROLLUP_DATA_DIR} \
  --boot-sector-file /var/tezos/smart-rollup-boot-sector \
  --rpc-addr 0.0.0.0 \
  --force

CMD="$TEZ_BIN/octez-smart-rollup-node \
  --endpoint http://tezos-node-rpc:8732 \
  -d $CLIENT_DIR \
  run \
  --data-dir ${ROLLUP_DATA_DIR}"
exec $CMD
