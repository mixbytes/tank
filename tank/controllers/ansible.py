#!/usr/bin/env python

from __future__ import print_function

import os
import sys
from collections import namedtuple

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

loader = DataLoader()

inventory = InventoryManager(loader=loader, sources='digital_ocean.py')
variable_manager = VariableManager(loader=loader, inventory=inventory)
playbook_path = 'play.yml'

if not os.path.exists(playbook_path):
    print('[INFO] The playbook does not exist')
    sys.exit()

Options = namedtuple('Options',
                     ['listtags', 'listtasks', 'listhosts', 'syntax',
                      'connection', 'module_path', 'forks', 'remote_user',
                      'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                      'sftp_extra_args', 'scp_extra_args', 'become',
                      'become_method', 'become_user', 'verbosity', 'check',
                      'diff', 'skip_tags'])
options = Options(
    listtags=False, listtasks=False, listhosts=False, syntax=False,
    connection='ssh', module_path=None, forks=100, remote_user='root',
    private_key_file=None, ssh_common_args=None, ssh_extra_args=None,
    sftp_extra_args=None, scp_extra_args=None, become=True,
    become_method='sudo', become_user='root', verbosity=None, check=False,
    diff=False, skip_tags=['debug'])

# This can accomodate various other command line arguments.`
# variable_manager.extra_vars = {'hosts': 'mywebserver'}

passwords = {}

pbex = PlaybookExecutor(
    playbooks=[playbook_path], inventory=inventory,
    variable_manager=variable_manager, loader=loader, options=options,
    passwords=passwords)

results = pbex.run()
