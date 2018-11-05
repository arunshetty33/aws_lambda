#!/usr/bin/env python2
 
# Author: Jonathan Raffre <jonathan.raffre.xebia@axa.com> <jraffre@xebia.fr>
# Purpose : list all instances in the current stack and generate the
#           shinken configuration
# Dependencies : boto (2.30+), jinja2
# TODO: implement region detection
 
from __future__ import print_function
import boto.utils
import boto.ec2
import jinja2
import json
import os
import subprocess
import re
 
instanceStoragePath = "/var/tmp/aws-inventory-instance-list.json"
shinkenConfigPath = "/etc/shinken"
hostgroupConfigPath = "%s/hostgroups" % shinkenConfigPath
hostsConfigPath = "%s/hosts" % shinkenConfigPath
 
hostgroupFileTemplate = jinja2.Template(\
"""\
define hostgroup {
    hostgroup_name     {{ hostgroup }}
    {% if members %}
    members            {{ members }}
    {% else %}
    hostgroup_members  {{ hostgroup_members }}
    {% endif %}
}
""")
 
hostFileTemplate = jinja2.Template(\
"""\
define host {
    use            generic-host
    contact_groups admins
    host_name      {{ name }}
    address        {{ local_ip }}
}
""")
 
# Retrieve the current stack name
instanceMetadata = boto.utils.get_instance_metadata()
availabilityZone = instanceMetadata['placement']['availability-zone']
instanceID = instanceMetadata['instance-id']
 
connEC2 = boto.ec2.connect_to_region('eu-west-2')
myself = connEC2.get_all_instances(instance_ids=[instanceID])
 
if len(myself) != 0:
    tags = myself[0].instances[0].tags
else:
    print("Could not get the current instance from AWS.")
    exit(1)
 
if 'aws:cloudformation:stack-name' in tags:
    stackName = tags['aws:cloudformation:stack-name']
else:
    print("This instance is not in a cloudformation stack, bailing out.")
    exit(1)
 
# Listing all the instances in this stack and group by role
instances = connEC2.get_all_instances(filters={'tag:aws:cloudformation:stack-name': stackName})
instancesHash = { 'all': [], 'datafront': [], 'scoring': [], 'worker': [], 'admin': [], 'analytics' : [], 'elasticsearch': []}
 
for i in instances:
    if i.instances[0].state == 'running':
        instance = {}
        instance['local_ip'] = i.instances[0].private_ip_address
        instance['name'] = i.instances[0].tags['Name']
        role = i.instances[0].tags['role']
        # Add to all list
        instancesHash['all'].append(instance)
        for r in instancesHash.keys():
            if re.search(r, role):
                instancesHash[r].append(instance)
 
# Compare with previous' instance list
if os.path.isfile(instanceStoragePath):
  with open(instanceStoragePath, 'r') as f:
      previousInstanceHash = json.load(f)
  if not cmp(instancesHash, previousInstanceHash): # no changes
      exit(0)
 
# Storing instance list for future comparison
with open(instanceStoragePath, "w") as instanceStorage:
    instanceStorage.write(json.dumps(instancesHash))
 
# Generating all hosts
for host in instancesHash['all']:
    with open("%s/%s.cfg" % (hostsConfigPath, host['name']), 'w') as hostfile:
     hostfile.write(hostFileTemplate.render(name=host['name'], local_ip=host['local_ip']))
 
# Generating hostgroups
instancesHash.pop('all')
 
for r, h in instancesHash.items():
    # List hosts for the current hostgroup
    hostlist = [host['name'] for host in h]
    # Generate hostgroup
    with open("%s/%s.cfg" % (hostgroupConfigPath, r), 'w') as hostgroupfile:
        hostgroupfile.write(hostgroupFileTemplate.render(hostgroup=r, members=','.join(hostlist)))
 
# Generate global hostgroup
with open("%s/all.cfg" % hostgroupConfigPath, 'w') as hostgroupfile:
    hostgroupfile.write(hostgroupFileTemplate.render(hostgroup='all', hostgroup_members=','.join(instancesHash.keys())))
 
try:
    subprocess.check_output("service shinken restart arbiter", shell=True)
except subprocess.CalledProcessError:
    exit(1)
 
exit(0)