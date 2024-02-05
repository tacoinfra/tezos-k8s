# Public network node
Connecting to a public net is easy!

(See [here](https://tezos.gitlab.io/user/history_modes.html) for info on snapshots and node history modes)

Simply run the following to spin up a rolling history node:

```shell
helm install tezos-mainnet tacoinfra/tezos-chain \
--namespace tacoinfra --create-namespace
```

Running this results in:

- Creating a Helm [release](https://helm.sh/docs/intro/using_helm/#three-big-concepts) named tezos-mainnet for your k8s cluster.
- k8s will spin up one regular (i.e. non-baking node) which will download and import a mainnet snapshot. This will take a few minutes.
- Once the snapshot step is done, your node will be bootstrapped and syncing with mainnet!

You can find your node in the tacoinfra namespace with some status information using `kubectl`.

```shell
kubectl -n tacoinfra get pods -l appType=octez-node
```

You can monitor (and follow using the `-f` flag) the logs of the snapshot downloader/import container:

```shell
kubectl logs -n tacoinfra statefulset/rolling-node -c snapshot-downloader -f
```

You can view logs for your node using the following command:

```shell
kubectl -n tacoinfra logs -l appType=octez-node -c octez-node -f --prefix
```
