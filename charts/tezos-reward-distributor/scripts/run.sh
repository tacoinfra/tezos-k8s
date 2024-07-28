#!/bin/sh
# remove lock if present
if [ -f /trd/cfg/lock ]; then
  rm /trd/cfg/lock
fi

if [ "${DRY_RUN}" == "false" ]; then
  dry_run_arg=""
else
  dry_run_arg="--dry_run"
fi
python src/main.py \
  -M 2 \
  --reward_data_provider ${REWARD_DATA_PROVIDER} \
  --node_addr_public ${TEZOS_NODE_ADDR} \
  --node_endpoint ${TEZOS_NODE_ADDR} \
  --base_directory /trd \
  --signer_endpoint ${SIGNER_ADDR} \
  --initial_cycle ${INITIAL_CYCLE} \
  -N ${NETWORK} \
  ${EXTRA_TRD_ARGS} \
  ${dry_run_arg}

# if TRD fails, send a slack alert
if [ $? -ne 0 ]; then
  # check if webhook is set
  if [ -z "${SLACK_WEBHOOK}" ]; then
    echo "TRD failed, but SLACK_WEBHOOK is not set, failing job"
    exit 1
  fi
  curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"Payout failed for $BAKER_ALIAS\"}" ${SLACK_WEBHOOK}
fi
