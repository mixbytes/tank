# MixBytes Tank [![master](https://travis-ci.org/mixbytes/tank.svg?branch=master)](https://travis-ci.org/mixbytes/tank)

MixBytes Tank is a console tool which can set up a blockchain cluster in minutes in a cloud and bench it using various transaction loads.
It'll highlight blockchain problems and give insights into performance and stability of the technology.

At the moment, supported blockchains are [Haya](https://github.com/mixbytes/haya) and [Polkadot](https://polkadot.network).

Setup - bench - dispose workflow is very similar to a test case, that is why configuration of such run is described in a declarative YAML file called "testcase".

More info can be found at:

* [Guide](docs/guide/README.md)
* [Cookbook](docs/cookbook/README.md)
* Quick guide below

Contributions are welcomed!

Discuss in our chat: [https://t.me/MixBytes](https://t.me/MixBytes).


# Quick guide

## Requirements

- Python3

## Installation

```shell
pip3 install mixbytes-tank
```

Use the `--pre` option to get the latest release candidate:

```shell
pip3 install mixbytes-tank --pre
```


## Usage

### 1. Configure the user config

Configure `~/.tank.yml`. The example can be found at [docs/config.yml.example](docs/config.yml.example).

Please configure at least one cloud provider. The essential steps are:
* providing (and possibly creating) a key pair
* registering a public key with your cloud provider (if needed)
* specifying a cloud provider access token or credentials

### 2. Create or get a tank testcase

The example can be found at [docs/testcase_example.yml](docs/testcase_example.yml).

### 3. Start a tank run

```shell
tank cluster deploy <testcase file>
```

As a result, the cluster instance listing will be printed along with the run id and the monitoring link.

### 4. Log in to the monitoring

Open the monitoring link in your browser, type in 'tank' in the username and password fields.
You will see cluster metrics in the predefined dashboards.

### 5. List current active runs

There can be multiple tank runs at the same time. The runs list and brief information about each run can be seen via: 

```shell
tank cluster list
```

### 6. Create synthetic load

```shell
tank cluster bench <run id> <load profile js> [--tps N] [--total-tx N]
```

`<run id>` - run ID

`<load profile js>` - a js file with a load profile: custom logic which creates transactions to be sent to the cluster

`--tps` - total number of generated transactions per second,

`--total-tx` - total number of transactions to be sent.

### 7. Shutdown and remove the cluster

```shell
tank cluster destroy <run id>
```


# Development

## Branching

features -> `develop` -> `master`.

`master` is production-ready code.

`develop` is expected-to-be production-ready code which is merged into master after thorough testing
(so, no faulty code in `develop` pls).

`develop` and `master` branches are permanent.
