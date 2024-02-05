# Creating a Private Blockchain

## mkchain

mkchain is a python script that generates Helm values, which Helm then uses to create your Tezos chain on k8s.

Follow _just_ the Install mkchain step in `./mkchain/README.md`. See there for more info on how you can customize your chain.

Set as an environment variable the name you would like to give to your chain:

```shell
export CHAIN_NAME=my-chain
```

## Start your private chain

Run `mkchain` to create your Helm values

```shell
mkchain $CHAIN_NAME
```

This will create the file `./${CHAIN_NAME}_values.yaml`

Create a Helm release that will start your chain:

```shell
helm install $CHAIN_NAME tacoinfra/tezos-chain \
--values ./${CHAIN_NAME}_values.yaml \
--namespace tacoinfra --create-namespace
```

Your kubernetes cluster will now be running a series of jobs to
perform the following tasks:

- generate a node identity
- create a baker account
- generate a genesis block for your chain
- start the bootstrap-node baker to bake/validate the chain
- activate the protocol
- bake the first block

You can find your node in the tacoinfra namespace with some status information using kubectl.

```shell
kubectl -n tacoinfra get pods -l appType=octez-node
```

You can view (and follow using the `-f` flag) logs for your node using the following command:

```shell
kubectl -n tacoinfra logs -l appType=octez-node -c octez-node -f --prefix
```

Congratulations! You now have an operational Tezos based permissioned
chain running one node.

## Adding nodes within the cluster

You can spin up a number of regular peer nodes that don't bake in your cluster by passing `--nodes N` to `mkchain`. You can use this to both scale up and down.

Or if you previously spun up the chain using `mkchain`, you may adjust
your setup to an arbitrary number of nodes by updating the "nodes"
section in the values yaml file.

nodes is a dictionary where each key value pair defines a statefulset
and a number of instances thereof.  The name (key) defines the name of
the statefulset and will be the base of the pod names.  The name must be
DNS compliant or you will get odd errors.  The instances are defined as a
list because their names are simply `-N` appended to the statefulsetname.
Said names are traditionally kebab case.

At the statefulset level, the following parameters are allowed:

   - storage_size: the size of the PV
   - runs: a list of containers to run, e.g. "baker", "accuser"
   - instances: a list of nodes to fire up, each is a dictionary
     defining:
     - `bake_using_accounts`: The name of the accounts that should be used
                              for baking.
     - `is_bootstrap_node`: Is this node a bootstrap peer.
     - config: The `config` property should mimic the structure
               of a node's config.json.
               Run `tezos-node config --help` for more info.

defaults are filled in for most values.

E.g.:

```
nodes:
  baking-node:
    storage_size: 15Gi
    runs:
      - baker
      - logger
    instances:
      - bake_using_accounts: [baker0]
        is_bootstrap_node: true
        config:
          shell:
            history_mode: rolling
  full-node:
    instances:
      - {}
      - {}
```

This will run the following nodes:
   - `baking-node-0`
   - `full-node-0`
   - `full-node-1`

`baking-node-0` will run baker and logger containers
and will be the only bootstrap node.  `full-node-*` are just nodes
with no extras. 

To upgrade your Helm release run:

```shell
helm upgrade $CHAIN_NAME tacoinfra/tezos-chain \
--values ./${CHAIN_NAME}_values.yaml \
--namespace tacoinfra
```

The nodes will start up and establish peer-to-peer connections in a full mesh topology.

List all of your running nodes: `kubectl -n tacoinfra get pods -l appType=octez-node`
