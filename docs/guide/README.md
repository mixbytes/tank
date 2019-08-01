# Guide

## Requirements

- Python3
- Terraform 0.11.13
- Terraform-Inventory v0.8


## Installation

### Terraform & Terraform-Inventory

To install, run [tank/install-terraform.sh](../../tank/install-terraform.sh) on Debian-like Linux systems (`sudo` is required).

Alternatively, the mentioned terraform* requirements can be manually downloaded and unpacked to the `/usr/local/bin` directory.

In the next release this process will be automated.

### Optional: create virtualenv

Optionally, create and activate virtualenv (assuming `venv` is a directory of a newly-created virtualenv)

Linux:
```shell
sudo apt-get install -y python3-virtualenv
python3 -m virtualenv -p python3 venv
```

MacOS:
```shell
pip3 install virtualenv
python3 -m virtualenv -p python3 venv
```

After creating virtualenv and opening a terminal, activate virtualenv first to be able to work with Tank:

```shell
. venv/bin/activate
```

Alternatively, each time call the Tank executable directly: `venv/bin/tank`.

### Tank
```shell
pip3 install mixbytes-tank
```


## Configuration

### User config

The user config is stored in `~/.tank.yml`. It keeps settings which are the same for the current user regardless of the blockchain or the testcase used at the moment
(e.g., it tells which cloud provider to use no matter which blockchain you are testing).

The example can be found at [docs/config.yml.example](../config.yml.example).

The user config contains cloud provider configurations, pointer to the current cloud provider, and some auxiliary values.

#### Cloud provider configuration

Please configure at least one cloud provider. The essential steps are:
* providing (and possibly creating) a key pair;
* registering a public key with your cloud provider (if needed);
* specifying a cloud provider access token or credentials.

We recommend creating a distinct key pair for benchmarking purposes.
The key must not be protected with a passphrase.
The simplest way is:

```shell
ssh-keygen -t rsa -b 2048 -f bench_key
```

The command will create a private key file (`bench_key`) and a public key file (`bench_key.pub`).
The private key will be used to gain access to the cloud instances created during a run.
It must be provided to each cloud provider using the `pvt_key` option.

The public key goes to cloud provider settings in accordance with the cloud provider requirements (e.g. GCE takes a file and DO - only a fingerprint).

A cloud provider is configured as a designated section in the user config.
The Digital Ocean section is called `digitalocean`, the Google Compute Engine section - `gce`.

The purpose of having multiple cloud provider sections at the time is to be able to quickly switch cloud providers using the `provider` pointer in the `tank` section.

##### Ansible variables forwarding

There is a way to globally specify some Ansible variables for a particular cloud provider.
It can be done in the `ansible` section of the cloud provider configuration.
Obviously, the values specified should be used in some blockchain bindings (see below).
The fact that the same variables will be passed to any blockchain binding makes this feature rarely used and low-level.
Each variable will be prefixed with `bc_` before being passed to Ansible.

#### Other options

#### Logging

Note: these options affect only Tank logging. Terraform and Ansible won't be affected.

`log.logging`: `level`: sets the log level. Acceptable values are `ERROR`, `WARNING` (by default), `INFO`, `DEBUG`.

`log.logging`: `file`: sets the log file name (console logging is set by default).

### Testcase

A Tank testcase describes a benchmark scenario.

The simple example can be found at [docs/testcase_example.yml](../testcase_example.yml).

Principal testcase contents are a current blockchain binding name and configuration of instances.

#### Blockchain binding

Tank supports many blockchains by using a concept of binding.
A binding provides an ansible role to deploy the blockchain (some examples [here](https://github.com/mixbytes?utf8=✓&q=tank.ansible&type=&language=))
and javascript code - to create load in the cluster ([examples here](https://github.com/mixbytes?utf8=✓&q=tank.bench&type=&language=)).
Similarly, databases use bindings to provide APIs to programming languages.

A binding is specified by its name, e.g.:
```yaml
binding: polkadot
```

You shouldn't worry about writing or understanding a binding unless you want to add support of some blockchain to Tank.

#### Blockchain instances

A blockchain cluster consists of a number of different *instance roles*, e.g. fullnodes and miners/validators.
Available roles depend on the binding used.

A *blockchain instances configuration* is a set of *role configurations*.
E.g., in the simplest case:

```yaml
instances:
  boot: 1
  producer: 3
```

##### role configuration

A *role configuration* is a number in the simplest case. The number specifies how many servers to set up with this role installed.

```yaml
instances:
  producer: 3
```

Alternatively, a role configuration can be written as an object with various options - generally applicable and role configuration-specific.

```yaml
instances:
  boot:
    count: 1
```

* An option `count` specifies how many servers to set up with this role installed.

* An option `regions` sets a *region configuration* for the role configuration.

##### region configuration

A region configuration provides *region options* per a region name.

In the simplest case, a region configuration says how many role instances to set up per region:

```yaml
instances:
  producer:
    regions:
      Europe: 4
      Asia: 3
      NorthAmerica: 3
```

A region name is one of the following: `Europe`, `Asia`, `NorthAmerica`, `random`, `default`.

`Europe`, `Asia`, `NorthAmerica` region names are self-explanatory.

`default` region is a synonym for default region used by Tank.

`random` region says that instances must be distributed evenly across available regions.

Region names are cloud provider-agnostic and can be configured in `~/.tank/regions.yml` (by default the predefined region config is copied and used at the moment of the first run creation).

In the common case a *region options* can be written as a set of various options - generally applicable and region-specific.

* `count` region option specifies how many servers to set up into the region.

##### Generally applicable options

Generally applicable options can be specified in the number of contexts: *instances*, *role configuration*, *region configuration*.

More local contexts has higher precedence over wrapping contextes,
e.g. an option specified in a role configuration takes precedence over the same option specified on the `instances` level:

```yaml
instances:
  type: standard

  boot:
    count: 1
    type: large

  producer:
    regions:
      random: 10
```

The options are:

* `type` - an instance type, which is a cloud-agnostic machine size.
Available types: micro (~1 GB mem), small (~2 GB mem), standard (4GB), large (8GB), xlarge (16GB), xxlarge (32GB), huge (64GB)
* `packetloss` - simulates bad network operation - percent of packets lost

##### Instance configuration examples

The simple geographically distributed test case - [docs/testcase_geo_example.yml](../testcase_geo_example.yml).

An example utilizing generally applicable options and a region configuration - [docs/testcase_geo_advanced_example.yml](../testcase_geo_advanced_example.yml).

#### Ansible variables forwarding

There is a way to pass some Ansible variables from a testcase to a cluster.
This low-level feature can be used to tailor the blockchain for a particular test case.
Variables can be specified in the `ansible` section of a testcase.
Each variable will be prefixed with `bc_` before being passed to Ansible.


## Usage

### Run the tank

Deploy a new cluster via
```shell
tank cluster deploy <testcase file>
```

This command will create a cluster dedicated to the specified test case.
Such clusters are named *runs* in Tank terminology.
There can be multiple coexisting runs on a developer's machine.
Any changes to the testcase made after the `deploy` command won't affect the run.

After the command is finished, you will see a listing of cluster machines and a run id, e.g.:

```shell
IP             HOSTNAME
-------------  -------------------------------------
167.71.36.223  tank-polkadot-db2d81e031a1-boot-0
167.71.36.231  tank-polkadot-db2d81e031a1-monitoring
167.71.36.222  tank-polkadot-db2d81e031a1-producer-0
165.22.74.160  tank-polkadot-db2d81e031a1-producer-1

Tank run id: festive_lalande
```

Locate an IP corresponding to a hostname ending with `-monitoring` - that's where all the metrics are (see below).

The cluster is up and running at this moment.
You can see its state on the dashboards or query cluster information via `info` and `inspect` commands (see below).

### Log in to the monitoring

Open `http://{monitoring ip}:3000/dashboards` in your browser, type `monitoring` options from your `/.tank.yml` configuration file in username and password fields.
If you didn't define these options in your configuration file, type 'tank' in username and password fields.
You will see cluster metrics in the predefined dashboards.
You can query the metrics at `http://{the monitoring ip}:3000/explore`.

### Current active runs

There can be multiple tank runs at the same time. The runs list and brief information about each run can be seen via: 

```shell
tank cluster list
```

### Information about a run

To list hosts of a cluster call

```shell
tank cluster info hosts {run id here}
```

To get a detailed cluster info call

```shell
tank cluster inspect {run id here}
```

### Synthetic load

Tank can run a javascript load profile on the cluster.

```shell
tank cluster bench <run id> <load profile js> [--tps N] [--total-tx N]
```

`<run id>` - run ID

`<load profile js>` - a js file with a load profile: custom logic which creates transactions to be sent to the cluster

`--tps` - total number of generated transactions per second,

`--total-tx` - total number of transactions to be sent.

In the simplest case, a developer writes logic to create and send transaction, and 
Tank takes care of distributing and running the code, providing the requested tps.

You can bench the same cluster with different load profiles by providing different arguments to the bench subcommand.
The documentation on profile development can be found at [https://github.com/mixbytes/tank.bench-common](https://github.com/mixbytes/tank.bench-common#what-is-profile). 

Binding parts responsible for benching can be found [here](https://github.com/mixbytes?utf8=✓&q=tank.bench&type=&language=).
Examples of load profiles can be found in `profileExamples` subfolders, e.g. [https://github.com/mixbytes/tank.bench-polkadot/tree/master/profileExamples](https://github.com/mixbytes/tank.bench-polkadot/tree/master/profileExamples).

### Shut down and remove a cluster

Entire Tank data of a particular run (both in the cloud and on the developer's machine) will be irreversibly deleted:

```shell
tank cluster destroy <run id>
```
