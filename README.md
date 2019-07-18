# MixBytes Tank

MixBytes Tank is a console tool which can set up a blockchain cluster in minutes in a cloud and bench it using various transaction loads.
It'll highlight problems of the blockchain and give insights into performance and stability of the technology.

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
- Terraform 0.11.13
- Terraform-Inventory v0.8

## Installation

### Terraform & Terraform-Inventory

Can be done with [tank/install-terraform.sh](tank/install-terraform.sh) on Debian-like Linux systems (will require `sudo`).

Alternatively, the mentioned terraform* requirements can be manually downloaded and unpacked to the `/usr/local/bin` directory.

In the next release this process will be automated.

### Tank
```shell
pip3 install mixbytes-tank
```


## Usage

### 1. Configure the user config

Configure `~/.tank.yml`. The example can be found at [docs/config.yml.example](docs/config.yml.example).

Please configure at least one cloud provider. The essential steps are:
* providing (and possibly creating) a key pair;
* registering the public key with your cloud provider if needed;
* specifying a cloud provider access token or credentials.

### 2. Create or get a tank testcase

The example can be found at [docs/testcase_example.yml](docs/testcase_example.yml).

### 3. Start a tank run

```shell
tank cluster deploy <testcase file>
```

As a result, the listing of the instances of the cluster will be printed along with the run id.

### 4. Login into the monitoring

Locate the IP address of the newly created instance which name ends with `-monitoring`.
Open in a browser `http://{monitoring ip}:3000/dashboards`, username and password are `tank`.
Metrics from the cluster can be seen in the predefined dashboards.

### 5. List current active runs

There can be multiple tank runs at the same time. The runs list and the brief information about each run can be seen via: 

```shell
tank cluster list
```

### 6. Create synthetic load

```shell
tank cluster bench <run id> <load profile js> [--tps N] [--total-tx N]
```

`<run id>` - id of the run

`<load profile js>` - js file with the load profile: custom logic which creates transactions to be sent to the cluster

`--tps` - global transactions per second generation rate,

`--total-tx` - how many transactions to send (total).

### 7. Shutdown and remove the cluster

```shell
tank cluster destroy <run id>
```
