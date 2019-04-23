# MixBytes Tank

### Requirements

- Docker

### Install

```shell
docker run --rm registry.gitlab.com/cyberos/infrastructure/tank:develop install | bash
```

### Use

#### 1. Create cluster and provision with default blockchain

Execute the command and answer the questions asked.

```shell
tank config-create
tank deploy
```

#### 2. Run bench

```shell
tank test_run
```