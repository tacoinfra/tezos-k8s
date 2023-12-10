import argparse
import os
import sys
from datetime import datetime, timezone

import yaml


# https://stackoverflow.com/a/52424865/207209
class MyDumper(yaml.Dumper):  # your force-indent dumper
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


class QuotedString(str):  # just subclass the built-in str
    pass


def quoted_scalar(dumper, data):  # a representer to force quotations on scalars
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


# add the QuotedString custom type with a forced quotation representer to your dumper
MyDumper.add_representer(QuotedString, quoted_scalar)
# end https://stackoverflow.com/a/52424865/207209

from tqchain.keys import gen_key, set_use_docker

from ._version import get_versions

sys.path.insert(0, "tqchain")

__version__ = get_versions()["version"]

ARCHIVE_BAKER_NODE_NAME = "archive-node"
ROLLING_REGULAR_NODE_NAME = "rolling-node"


cli_args = {
    "should_generate_unsafe_deterministic_data": {
        "help": (
            "Should tezos-k8s generate deterministic account keys and genesis"
            " block hash instead of mkchain using octez-client to generate"
            " random ones. This option is helpful for testing purposes."
        ),
        "action": "store_true",
        "default": False,
    },
    "number_of_nodes": {
        "help": "number of peers in the cluster",
        "default": 0,
        "type": int,
    },
    "number_of_bakers": {
        "help": "number of bakers in the cluster",
        "default": 1,
        "type": int,
    },
    "expected_proof_of_work": {
        "help": "Node identity generation difficulty",
        "default": 0,
        "type": int,
    },
    "bootstrap_peers": {
        "help": "Bootstrap addresses to connect to. Can specify multiple.",
        "action": "extend",
        "nargs": "+",
    },
    "octez_docker_image": {
        "help": "Version of the Octez docker image",
        "default": "tezos/tezos:v17.3",
    },
    "use_docker": {
        "action": "store_true",
        "default": None,
    },
    "no_use_docker": {
        "dest": "use_docker",
        "action": "store_false",
    },
}


# python versions < 3.8 doesn't have "extend" action
class ExtendAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)


def get_args():
    parser = argparse.ArgumentParser(
        description="Generate helm values for use with the tezos-chain helm chart"
    )

    parser.register("action", "extend", ExtendAction)
    parser.add_argument("chain_name", action="store", help="Name of your chain")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    for k, v in cli_args.items():
        parser.add_argument(*["--" + k.replace("_", "-")], **v)

    return parser.parse_args()


def validate_args(args):
    if args.number_of_nodes < 0:
        print(
            f"Invalid argument --number-of-nodes ({args.number_of_nodes}) "
            f"must be non-negative"
        )
        exit(1)

    if args.number_of_bakers < 0:
        print(
            f"Invalid argument --number-of-bakers ({args.number_of_bakers}) "
            f"must be non-negative"
        )
        exit(1)

    if args.number_of_nodes + args.number_of_bakers < 1:
        print(
            f"Invalid arguments: either "
            f"--number-of-nodes ({args.number_of_nodes}) or "
            f"--number-of-bakers ({args.number_of_bakers}) must be non-zero"
        )
        exit(1)


def node_config(name, n, is_baker):
    ret = {
        "is_bootstrap_node": False,
        "config": {
            "shell": {"history_mode": "rolling"},
            "metrics_addr": [":9932"],
        },
        "authorized_keys": ["authorized-key-0"],
    }
    return ret

def baker_config(name, n):
    ret = {"bake_using_accounts": [f"{name}-{n}"],
        "node_rpc_url": "http://archive-node-0.archive.node:8732"}
    return ret


def main():
    args = get_args()

    validate_args(args)
    set_use_docker(args.use_docker)

    base_constants = {
        "images": {
            "octez": args.octez_docker_image,
        },
        "node_config_network": {"chain_name": args.chain_name},
        # Custom chains should not pull snapshots or tarballs
        "snapshot_source": None,
        "node_globals": {
            # Needs a quotedstring otherwise helm interprets "Y" as true and it does not work
            "env": {
                "all": {"TEZOS_CLIENT_UNSAFE_DISABLE_DISCLAIMER": QuotedString("Y")}
            }
        },
        "protocols": [
            {
                "command": "PtNairob",
                "vote": {"liquidity_baking_toggle_vote": "pass"},
            }
        ],
    }

    # preserve pre-existing values, if any (in case of scale-up)
    old_values = {}
    files_path = f"{os.getcwd()}/{args.chain_name}"
    if os.path.isfile(f"{files_path}_values.yaml"):
        print(
            "Found old values file. Some pre-existing values might remain\n"
            "the same, e.g. public/private keys, and genesis block. Please\n"
            "delete the values file to generate all new values.\n"
        )
        with open(f"{files_path}_values.yaml", "r") as yaml_file:
            old_values = yaml.safe_load(yaml_file)

        current_number_of_bakers = len(
            old_values["nodes"][ARCHIVE_BAKER_NODE_NAME]["instances"]
        )
        if current_number_of_bakers != args.number_of_bakers:
            print("ERROR: the number of bakers must not change on a pre-existing chain")
            print(f"Current number of bakers: {current_number_of_bakers}")
            print(f"Attempted change to {args.number_of_bakers} bakers")
            exit(1)

    if old_values.get("node_config_network", {}).get("genesis"):
        print("Using existing genesis parameters")
        base_constants["node_config_network"]["genesis"] = old_values[
            "node_config_network"
        ]["genesis"]
    else:
        # create new chain genesis params if brand new chain
        base_constants["node_config_network"]["genesis"] = {
            "protocol": "Ps9mPmXaRzmzk35gbAYNCAw6UXdE2qoABTHbN2oEEc1qM7CwT9P",
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        }

    accounts = {"secret": {}, "public": {}}
    if old_values.get("accounts"):
        print("Using existing secret keys")
        accounts["secret"] = old_values["accounts"]
    elif not args.should_generate_unsafe_deterministic_data:
        baking_accounts = {
            f"{ARCHIVE_BAKER_NODE_NAME}-{n}": {} for n in range(args.number_of_bakers)
        }
        for account in [*baking_accounts, "authorized-key-0"]:
            print(f"Generating keys for account {account}")
            keys = gen_key(args.octez_docker_image)
            for key_type in keys:
                accounts[key_type][account] = {
                    "key": keys[key_type],
                    "is_bootstrap_baker_account": False
                    if account == "authorized-key-0"
                    else True,
                    "bootstrap_balance": "4000000000000",
                }

    # First 2 bakers are acting as bootstrap nodes for the others, and run in
    # archive mode. Any other bakers will be in rolling mode.
    nodes = {
        ARCHIVE_BAKER_NODE_NAME: {
            "runs": ["octez_node"],
            "storage_size": "15Gi",
            "instances": [
                {
                   "is_bootstrap_node": False,
                   "config": {
                       "shell": {"history_mode": "rolling"},
                       "metrics_addr": [":9932"],
                   },
               } for _ in range(args.number_of_bakers)
            ],
        },
        ROLLING_REGULAR_NODE_NAME: None,
    }
    if args.number_of_nodes:
        nodes[ROLLING_REGULAR_NODE_NAME] = {
            "storage_size": "15Gi",
            "instances": [
                node_config(ROLLING_REGULAR_NODE_NAME, n, is_baker=False)
                for n in range(args.number_of_nodes)
            ],
        }

    bakers = {f"baker-{i}": {"bake_using_accounts": [f"{ARCHIVE_BAKER_NODE_NAME}-{i}"],
        "node_rpc_url": "http://archive-node-0.archive-node:8732"} 
           for i in range(args.number_of_bakers)}

    octezSigners = {
        "tezos-signer-0": {
            "accounts": [
                f"{ARCHIVE_BAKER_NODE_NAME}-{n}" for n in range(args.number_of_bakers)
            ],
            "authorized_keys": ["authorized-key-0"],
        }
    }

    activation_account_name = f"{ARCHIVE_BAKER_NODE_NAME}-0"
    base_constants["node_config_network"][
        "activation_account_name"
    ] = activation_account_name

    with open(
        f"{os.path.dirname(os.path.realpath(__file__))}/parameters.yaml", "r"
    ) as yaml_file:
        parametersYaml = yaml.safe_load(yaml_file)
        activation = {
            "activation": {
                "protocol_hash": "PtNairobiyssHuh87hEhfVBGCVrK3WnS8Z2FT4ymB5tAa4r1nQf",
                "protocol_parameters": parametersYaml,
            },
        }

    bootstrap_peers = args.bootstrap_peers if args.bootstrap_peers else []

    protocol_constants = {
        "should_generate_unsafe_deterministic_data": args.should_generate_unsafe_deterministic_data,
        "expected_proof_of_work": args.expected_proof_of_work,
        **base_constants,
        "bootstrap_peers": bootstrap_peers,
        "accounts": accounts["secret"],
        "octezSigners": octezSigners,
        "bakers": bakers,
        "nodes": nodes,
        **activation,
    }

    with open(f"{files_path}_values.yaml", "w") as yaml_file:
        yaml.dump(
            protocol_constants,
            yaml_file,
            Dumper=MyDumper,
            default_flow_style=False,
            sort_keys=False,
        )
        print(f"Wrote chain constants to {files_path}_values.yaml")


if __name__ == "__main__":
    main()
