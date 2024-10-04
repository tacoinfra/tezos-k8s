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
# Some exit codes are excluded. List of exit codes:
# https://github.com/tezos-reward-distributor-organization/tezos-reward-distributor/blob/cdf7d3884bdf880c5e13267c6d6ad3af470b2e4e/src/util/exit_program.py#L6
exit_code=$?
if [ $exit_code -ne 0 ]; then
  # check if bot token and channel are set
  if [ -z "${SLACK_BOT_TOKEN}" ] || [ -z "${SLACK_CHANNEL}" ]; then
    echo "TRD failed, but SLACK_BOT_TOKEN or SLACK_CHANNEL is not set, failing job"
    exit 1
  fi
  echo "TRD exited in error, exit code is ${exit_code}, maybe send slack alert"
  EXIT_CODE=${exit_code} python -c "
import os
import sys
import requests
import json

slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
slack_channel = os.getenv('SLACK_CHANNEL')
baker_alias = os.getenv('BAKER_ALIAS')
exit_code = os.getenv('EXIT_CODE')

if exit_code == '9':
    print(f'TRD returned exit code 9 (PROVIDER_BUSY) for Tezos baker {baker_alias}. Not alerting.')
    sys.exit(0)
else:
    message = f'TRD Payout failed for Tezos baker {baker_alias}, exit code {exit_code}.'

response = requests.post(
    'https://slack.com/api/chat.postMessage',
    headers={
        'Authorization': f'Bearer {slack_bot_token}',
        'Content-Type': 'application/json; charset=utf-8'
    },
    data=json.dumps({
        'channel': slack_channel,
        'text': message
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
