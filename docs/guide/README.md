# Guide

## Requirements

- Python3
- Terraform 0.11.13
- Terraform-Inventory v0.8


## Installation

### Terraform & Terraform-Inventory

Can be done with [tank/install-terraform.sh](../../tank/install-terraform.sh) on Debian-like Linux systems.

Alternatively, the mentioned terraform* requirements can be manually downloaded and unpacked to the `/usr/local/bin` directory.

In the next release this process will be automated.

### Optional: create virtualenv

Optionally, create and activate virtualenv (assuming `venv` is a directory of newly created virtualenv)

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

After virtualenv creation and each time after opening a terminal, activate virtualenv to work with Tank:

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

The user config is stored in `~/.tank.yml`. It keeps settings which are the same for the current user regardless of the blockchain or the testcase used at the moment.
E.g., it tells which cloud provider to use no matter which blockchain you are testing.

The example can be found at [docs/config.yml.example](../config.yml.example).

The user config contains cloud provider configurations, pointer to the cloud provider selected at the moment, and some auxiliary values.

#### Cloud provider configuration

Please configure at least one cloud provider. The essential steps are:
* providing (and possibly creating) a key pair;
* registering the public key with your cloud provider if needed;
* specifying a cloud provider access token or credentials.

We recommend creating a distinct key pair for benchmarking purposes.
The key must not be protected with a passphrase.
The simplest way is:

```shell
ssh-keygen -t rsa -b 2048 -f bench_key
```

The command will create the private key file `bench_key` and the public key file `bench_key.pub`.
The private key will be used to gain access to the cloud instances created during a run.
It has to be provided using the `pvt_key` option to each cloud provider.

The public key is passed to a cloud provider settings according to particular cloud provider requirements (e.g. GCE takes the file and DO only a fingerprint).

A cloud provider is configured as a designated section in the user config.
The Digital Ocean section is named `digitalocean`.
The Google Compute Engine section is named `gce`.

The purpose of having multiple cloud provider sections at the time is to be able to quickly switch the cloud provider using the `provider` pointer in the `tank` section.

##### Ansible variables forwarding

There is a way to globally specify some Ansible variables for a particular cloud provider.
It can be done in the `ansible` section of the cloud provider configuration.
Obviously, the values specified should be used in some of blockchain bindings (see below).
The fact that the same variables will be passed to any blockchain binding makes this feature rarely used and low-level.
Each variable will be prefixed with `bc_` before being passed to Ansible.

#### Other options

#### Logging

Note: this options affect only logging of Tank itself. Terraform and Ansible won't be affected.

`log.logging`: `level`: sets the log level. Acceptable values are `ERROR`, `WARNING` (default), `INFO`, `DEBUG`.

`log.logging`: `file`: sets the log file name (default is console logging).

### Testcase

A Tank testcase describes scenario of one benchmark.

The example can be found at [docs/testcase_example.yml](../testcase_example.yml).

Principal contents of a testcase are a name of a blockchain binding used and a configuration of instances.

#### Blockchain binding

Tank supports many blockchains by using a concept of binding.
A binding provides an ansible role to deploy the blockchain and javascript code to create load on the cluster.
Similarly, typically a database uses bindings to provide APIs to programming languages.

You shouldn't worry about writing or understanding a binding unless you want to add support of some blockchain to Tank.
A binding consists of an Ansible part (some examples [here](https://github.com/mixbytes?utf8=✓&q=tank.ansible&type=&language=)) 
and a js part [examples here](https://github.com/mixbytes?utf8=✓&q=tank.bench&type=&language=).

A binding is specified in a straightforward way, by its name, e.g.: `binding: polkadot`.

A blockchain cluster consists of a number of different instance roles, e.g. fullnodes and miners/validators.
Available roles depend on the binding used.
For each instance role you can specify a number of instances (default is 0) and an instance type, which is cloud-agnostic machine size.

##### Ansible variables forwarding

There is a way to pass some Ansible variables from a testcase to a cluster.
This low-level feature can be used to tailor the blockchain to a particular test case.
Variables can be specified in the `ansible` section of a testcase.
Each variable will be prefixed with `bc_` before being passed to Ansible.


## Usage

### Start a Tank run

Deploy a new cluster via
```shell
tank cluster deploy <testcase file>
```

This command will create a cluster dedicated to the specified test case.
Such clusters are named runs in the Tank's terminology.
There can be multiple coexisting runs on a developer's machine.
Any changes to the testcase made after the `deploy` command start won't affect the run.

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

Locate an IP corresponding to a hostname ending with `-monitoring` - thats where all the metrics are (see below).

The cluster is up and running at this moment.
You can see its' state in dashboards or query the cluster information via `info` and `inspect` commands (see below).

### Login into the monitoring

Open in a browser `http://{the monitoring ip from the previous step}:3000/dashboards`, username and password are `tank`.

Metrics from the cluster can be seen in the predefined dashboards or queried at `http://{the monitoring ip}:3000/explore`.

### Current active runs

There can be multiple tank runs at the same time. The runs list and the brief information about each run can be seen via: 

```shell
tank cluster list
```

### Information about a run

To list hosts of a cluster type

```shell
tank cluster info hosts {run id here}
```

To get detailed cluster info type

```shell
tank cluster inspect {run id here}
```

### Synthetic load

Tank can run a load profile coded in javascript on the cluster. 

```shell
tank cluster bench <run id> <load profile js> [--tps N] [--total-tx N]
```

`<run id>` - id of the run,

`<load profile js>` - js file with the load profile: custom logic which creates transactions to be sent to the cluster,

`--tps` - global transactions per second generation rate,

`--total-tx` - how many transactions to send (total).

In the simplest case a developer writes logic to create and send transaction and 
Tank takes care of distributing and running the code, providing the requested tps.

You can bench the same cluster with different load profiles by providing different arguments to the bench subcommand.
The documentation on profile development can be found at [https://github.com/mixbytes/tank.bench-common](https://github.com/mixbytes/tank.bench-common#what-is-profile). 

Binding parts responsible for benching can be found [here](https://github.com/mixbytes?utf8=✓&q=tank.bench&type=&language=).
Examples of load profiles can be found in `profileExamples` subfolders, e.g. [https://github.com/mixbytes/tank.bench-polkadot/tree/master/profileExamples](https://github.com/mixbytes/tank.bench-polkadot/tree/master/profileExamples).

### Shutdown and remove a cluster

Entire Tank data of a particular run (both in the cloud and on the developer's machine) will be irreversibly deleted:

```shell
tank cluster destroy <run id>
```
