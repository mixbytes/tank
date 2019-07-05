# MixBytes Tank

## Requirements

- Python3
- Terraform 0.11.13
- Terraform-Inventory v0.8

## Installation

### Terraform & Terraform-Inventory

Can be done with [tank/install-terraform.sh](tank/install-terraform.sh).

### Optional: create virtualenv

Optionally, create and activate virtualenv

```shell
sudo apt-get install -y python3-virtualenv
python3 -m virtualenv -p python3 venv
```

After virtualenv creation and each time after opening a terminal, activate virtualenv to work with the tank:

```shell
. venv/bin/activate
```

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

### 4. Login into the monitoring

Locate the newly created instance which name ends with `-monitoring` in your cloud, find the instance ip.
Open in browser `http://{monitoring ip}:3000/dashboards`, username and password are `tank`.

The dashboards can always be found at `http://{monitoring ip}:3000/dashboards`

### 5. List current active runs

There can be multiple tank runs at the same time. List and brief information can be seen via: 

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


## Hacking

### Alternative binding version

Bindings can be configured at `~/.tank/bindings.yml` (by default the predefined binding config is copied and used).
