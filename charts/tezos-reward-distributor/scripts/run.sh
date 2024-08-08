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
  # check if bot token and channel are set
  if [ -z "${SLACK_BOT_TOKEN}" ] || [ -z "${SLACK_CHANNEL}" ]; then
    echo "TRD failed, but SLACK_BOT_TOKEN or SLACK_CHANNEL is not set, failing job"
    exit 1
  fi
  python -c "
import os
import requests
import json

slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
slack_channel = os.getenv('SLACK_CHANNEL')
baker_alias = os.getenv('BAKER_ALIAS')

response = requests.post(
    'https://slack.com/api/chat.postMessage',
    headers={
        'Authorization': f'Bearer {slack_bot_token}',
        'Content-Type': 'application/json; charset=utf-8'
    },
    data=json.dumps({
        'channel': slack_channel,
        'text': f'TRD Payout failed for Tezos baker {baker_alias}'
    })
)

if not response.json().get('ok'):
    print('Failed to send Slack alert')
    print(response.json())
    exit(1)
"
  if [ $? -ne 0 ]; then
    echo "Failed to send Slack alert"
    exit 1
  fi
fi
