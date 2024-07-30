#! /usr/bin/env python
from flask import Flask
from web3 import Web3
import requests
import time
import logging

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

application = Flask(__name__)
web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

AGE_LIMIT_IN_SECS = 600
# https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
# Default readiness probe timeoutSeconds is 1s, timeout sync request before that and return a
# connect timeout error if necessary

@application.route("/health")
def health():
    if not web3.is_connected():
        err = ("Error: Failed to connect evm node. ", 500)
        application.logger.error(err)
        return err

    latest_block = web3.eth.get_block('latest')

    latest_block_timestamp = latest_block['timestamp']
    current_timestamp = int(time.time())
    time_diff = current_timestamp - latest_block_timestamp
    if time_diff > AGE_LIMIT_IN_SECS:
        err = (
            "Error: Chain head is %s secs old, older than %s"
            % (time_diff, AGE_LIMIT_IN_SECS),
            500,
        )
        application.logger.error(err)
        return err
    return "evm rpc is healthy"


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=32767, debug=False)