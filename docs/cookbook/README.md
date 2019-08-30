# Cookbook

### Changing a blockchain node image

Sometimes (e.g. during development) it's useful to test a blockchain node image rather than the one specified in the binding.

To do so, redefine a corresponding Ansible variable in a testcase.
E.g. for Polkadot case, you can write the following testcase:

```yaml
binding: polkadot

instances:
  boot: 1
  producer: 3

ansible:
  polkadot_image: your-dockerhub-account/polkadot:docker-tag
```

### Alternative binding version

Sometimes it is not enough to tweak a couple of Ansible variables as described above, and you may want to make changes to the binding.

Bindings can be configured in `~/.tank/bindings.yml` (by default the predefined binding config is copied during the first run creation).

You can create your own binding with any name and supply a git link to the binding Ansible role.
The link can be accompanied with a branch / tag name to use.

Fork an existing binding into a new repository. Alternatively, you can create a branch in the existing binding repository.
Make the desired changes in the repository.

Configure a new binding in `~/.tank/bindings.yml`:

```yaml
my_binding:
    ansible:
        src: https://github.com/me/my-binding-repo
```

use it in a testcase:

```yaml
binding: my_binding

instances:
  boot: 1
  producer: 3
```
