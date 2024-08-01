#! /usr/bin/env python
from flask import Flask
import requests
import time
import logging

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

application = Flask(__name__)

AGE_LIMIT_IN_SECS = 600
# https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
# Default readiness probe timeoutSeconds is 1s, timeout sync request before that and return a
# connect timeout error if necessary
NODE_CONNECT_TIMEOUT = 0.9

@application.route("/health")
def health():
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": ["latest", False],
            "id": 1
        }
        resp = requests.post("http://127.0.0.1:8545", json=payload, timeout=NODE_CONNECT_TIMEOUT)
        resp = resp.json()
    except ConnectTimeout as e:
        err = "Timeout connect to node, %s" % repr(e), 500
        application.logger.error(err)
        return err
    except ReadTimeout as e:
        err = "Timeout read from node, %s" % repr(e), 500
        application.logger.error(err)
        return err
    except RequestException as e:
        err = "Could not connect to node, %s" % repr(e), 500
        application.logger.error(err)
        return err

    latest_block = resp['timestamp']
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