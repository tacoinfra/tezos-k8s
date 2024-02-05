# Tezos Baker

## Running a Tezos Testnet baker

Running a Tezos Baker on testnet is easy.

In a Tezos Testnet, it is acceptable to use an in-memory signer. In this example, we run a bakery called "Acme Bakery". The private baking key is passed as helm parameter in `values.yaml` and stored in a Kubernetes secret.

The below `values.yaml` will start a ghostnet baker:

```
images:
  octez: tezos/tezos:v19.0 # replace with most recent version
node_config_network:
  chain_name: ghostnet
node_globals:
  env:
    all:
      TEZOS_CLIENT_UNSAFE_DISABLE_DISCLAIMER: "Y"
protocols:
  - command: Proxford # replace with the most recent protocol
    vote:
      liquidity_baking_toggle_vote: pass
accounts:
  acme-bakery:
    key: edsk3ESSEABwYbxAnUAKfbZ7s4XpBDiNFaS3xKkzWJcWtCp57Ty1mN
bakers:
  acme-bakery:
    bake_using_accounts:
      - acme-bakery
    node_rpc_url: http://node-0.node:8732
nodes:
  acme:
    runs:
      - octez_node
    storage_size: 50Gi
    instances:
      - config:
          shell:
            history_mode: rolling
  rolling-node: null
```

This will launch:

* an `octez-node` pod
* a `baker` pod

Then, you need to register as a baker. See [Octez documentation](https://tezos.gitlab.io/introduction/howtorun.html#register-and-check-your-rights).

## Running a Mainnet Baker

On mainnet, running an in-memory signer is **strongly discouraged**. Indeed, improper disclosure of the baker's secret key may lead to theft of funds or equivocation.

Instead, the recommended method is to use a Key Management System (KMS) or Hardware Security Module (HSM).

### Running with a remote signer

A Tezos-k8s baker can be configured to run with a remote signer external to the cluster.

You must know:
* the URL to the remote signing endpoint. It must be accessible to the cluster, with a VPC or on the public Internet,
* the public key of the baker's address (not the hash starting with `tz`)

Configure a mainnet signer as follows:

```
images:
  octez: tezos/tezos:v19.0 # replace with most recent version
protocols:
  - command: Proxford # replace with the most recent protocol
    vote:
      liquidity_baking_toggle_vote: pass
accounts:
  acme-bakery:
    key: edpkxxxx # the public key
    signer_url: https://my-signer-url/tz1xxxxx
bakers:
  acme-bakery:
    bake_using_accounts:
      - acme-bakery
    node_rpc_url: http://node-0.acme:8732
nodes:
  acme:
    runs:
      - octez_node
    storage_size: 50Gi
    instances:
      - config:
          shell:
            history_mode: rolling
  rolling-node: null
```

#### Note on the remote signer

For mainnet, it is recommended to use a remote signer that enforces high watermark protection, in order to prevent equivocation.

Examples of such signers are:

* signer backed by:
  * [Signatory](https://signatory.io)
  * a Ledger hardware device running the Tezos Signer app
* [Tezos Consensus KMS Signer](https://serverlessrepo.aws.amazon.com/applications/us-east-2/030073751340/tezos-consensus-kms-signer) on AWS Serverless Application Repository
