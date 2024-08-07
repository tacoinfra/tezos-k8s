import argparse
import os
import string
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

L1_NODE_NAME = "node"
BAKER_NAME = "baker"
DAL_NODE_NAME = "dal-node"
SIGNER_NAME = "signer"

cli_args = {
    "nodes": {
        "help": "number of peers in the cluster",
        "default": 1,
        "type": int,
    },
    "bakers": {
        "help": "number of bakers in the cluster",
        "default": 1,
        "type": int,
    },
    "signers": {
        "help": "number of remote signers in the cluster",
        "default": 1,
        "type": int,
    },
    "dal_nodes": {
        "help": "number of DAL nodes in the cluster",
        "default": 0,
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
        "default": "tezos/tezos:octez-v20.2",
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
    if args.nodes < 1:
        print(f"Invalid argument --nodes ({args.nodes}) " f"must be non-zero")
        exit(1)

    if args.bakers < 1:
        print(f"Invalid argument --bakers ({args.bakers}) " f"must be non-zero")
        exit(1)


def node_config(n):
    ret = {
        "is_bootstrap_node": False,
        "config": {
            "shell": {"history_mode": "rolling"},
            "metrics_addr": [":9932"],
        },
    }
    if n < 2:
        ret["is_bootstrap_node"] = True
        ret["config"]["shell"]["history_mode"] = "archive"
    return ret


def assign_node_rpc_url(entities, num_nodes, node_name_prefix):
    for i, key in enumerate(entities):
        node_index = i % num_nodes
        entities[key][
            "node_rpc_url"
        ] = f"http://{node_name_prefix}-{node_index}.{node_name_prefix}:8732"


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
                "command": "PsParisC",
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

        current_bakers = len(old_values["bakers"])
        if current_bakers != args.bakers:
            print("ERROR: the number of bakers must not change on a pre-existing chain")
            print(f"Current number of bakers: {current_bakers}")
            print(f"Attempted change to {args.bakers} bakers")
            exit(1)

    if old_values.get("node_config_network", {}).get("genesis"):
        print("Using existing genesis parameters")
        base_constants["node_config_network"] = old_values["node_config_network"]
    else:
        # create new chain genesis params if brand new chain
        base_constants["node_config_network"]["genesis"] = {
            "protocol": "Ps9mPmXaRzmzk35gbAYNCAw6UXdE2qoABTHbN2oEEc1qM7CwT9P",
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        }
        if args.dal_nodes:
            base_constants["node_config_network"]["dal_config"] = {
                "activated": True,
                "use_mock_srs_for_testing": {
                    "redundancy_factor": 16,
                    "page_size": 4096,
                    "slot_size": 65536,
                    "number_of_shards": 2048,
                },
                "bootstrap_peers": ["dal-bootstrap:11732"],
            }

    accounts = {"secret": {}, "public": {}}
    if old_values.get("accounts"):
        print("Using existing secret keys")
        accounts["secret"] = old_values["accounts"]
    else:
        baking_accounts = {
            f"{BAKER_NAME}-{char}": {} for char in string.ascii_lowercase[: args.bakers]
        }
        for account in baking_accounts:
            print(f"Generating keys for account {account}")
            keys = gen_key(args.octez_docker_image)
            for key_type in keys:
                accounts[key_type][account] = {
                    "key": keys[key_type],
                    "is_bootstrap_baker_account": True,
                    "bootstrap_balance": "4000000000000",
                }
        if args.signers:
            print(f"Generating keys for account authorized-key-0")
            keys = gen_key(args.octez_docker_image)
            for key_type in keys:
                accounts[key_type]["authorized-key-0"] = {
                    "key": keys[key_type],
                    "is_bootstrap_baker_account": False,
                    "bootstrap_balance": "1000000",
                }

    # First 2 nodes are acting as bootstrap nodes for the others, and run in
    # archive mode. Any other bakers will be in rolling mode.
    nodes = {
        L1_NODE_NAME: {
            "runs": ["octez_node"],
            "storage_size": "15Gi",
            "instances": [node_config(n) for n in range(args.nodes)],
        },
        "rolling-node": None,
    }

    # Initialize DAL nodes data
    dalNodes = {}
    for n in range(args.dal_nodes):
        dalNodes[f"{DAL_NODE_NAME}-{n}"] = {
            "attest_using_accounts": [],
        }
    if args.dal_nodes:
        # add bootstrap dal node
        dalNodes["dal-bootstrap"] = {
            "bootstrapProfile": True,
        }

    # Assign node_rpc_url for DAL nodes
    assign_node_rpc_url(dalNodes, args.nodes, L1_NODE_NAME)

    # Initialize bakers data and assign to DAL nodes in round-robin fashion
    bakers = {}
    for i, char in enumerate(string.ascii_lowercase[: args.bakers]):
        baker_name = f"{BAKER_NAME}-{char}"
        bakers[char] = {
            "bake_using_accounts": [baker_name],
        }
        if args.signers:
            bakers[char]["authorized_keys"] = ["authorized-key-0"]
        if args.dal_nodes:
            dal_node_index = i % args.dal_nodes
            bakers[char][
                "dal_node_rpc_url"
            ] = f"http://{DAL_NODE_NAME}-{dal_node_index}:10732"
            # Add the baker to the DAL node's attest_for_accounts list
            dalNodes[f"{DAL_NODE_NAME}-{dal_node_index}"][
                "attest_using_accounts"
            ].append(baker_name)

    # Assign node_rpc_url for bakers
    assign_node_rpc_url(bakers, args.nodes, L1_NODE_NAME)

    octezSigners = {}
    if args.signers:
        for i in range(args.bakers):
            signer_index = i % args.signers

            if not f"{SIGNER_NAME}-{signer_index}" in octezSigners:
                octezSigners[f"{SIGNER_NAME}-{signer_index}"] = {
                    "accounts": [],
                    "authorized_keys": ["authorized-key-0"],
                }
            octezSigners[f"{SIGNER_NAME}-{signer_index}"]["accounts"].append(
                f"baker-{string.ascii_lowercase[i]}"
            )

    base_constants["node_config_network"]["activation_account_name"] = f"{BAKER_NAME}-a"
    if args.signers:
        base_constants["node_config_network"][
            "activation_account_authorized_key"
        ] = "authorized-key-0"

    with open(
        f"{os.path.dirname(os.path.realpath(__file__))}/parameters.yaml", "r"
    ) as yaml_file:
        parametersYaml = yaml.safe_load(yaml_file)
        activation = {
            "activation": {
                "protocol_hash": "PsParisCZo7KAh1Z1smVd9ZMZ1HHn5gkzbM94V3PLCpknFWhUAi",
                "protocol_parameters": parametersYaml,
            },
        }

    bootstrap_peers = args.bootstrap_peers if args.bootstrap_peers else []

    protocol_constants = {
        "expected_proof_of_work": args.expected_proof_of_work,
        **base_constants,
        "bootstrap_peers": bootstrap_peers,
        "accounts": accounts["secret"],
        "octezSigners": octezSigners,
        "dalNodes": dalNodes,
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
