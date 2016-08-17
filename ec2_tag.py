#!/usr/bin/env python
""" python """
#
# Copyright (c) Emil Stenqvist <emsten@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#	* Redistributions of source code must retain the above copyright
#	notice, this list of conditions and the following disclaimer.
#	* Redistributions in binary form must reproduce the above copyright
#	notice, this list of conditions and the following disclaimer in the
#	documentation and/or other materials provided with the distribution.
#	* Neither the name of the <organization> nor the
#	names of its contributors may be used to endorse or promote products
#	derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSEcw
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#*
#* File         :       ec2_tag.py
#*
#* Description  :   Saltstack grain to get an instance tags
#*
#* Author       :   Emil Stenqvist <emsten@gmail.com>
#*                  Luc Suryo <luc@badassops.com>
#*
#* Version      :   0.3
#*
#* Date         :   Jan 14, 2016
#*
#* History      :
#*    Date:    Author:			Info:
#*   unknown   Emil Stenqvist	First Release
#*  Licensed under Apache License:
#*  (https://raw.github.com/saltstack/salt/develop/LICENSE)
#*  (Inspired by https://github.com/dginther/ec2-tags-salt-grain)
#*
#*   Jan 14, 2016  Luc Suryo
#*    Adjusted so it uses only a file for the AWS credentials
#*    and change to BSD License
#*
#*   Jan 29, 2026  LIS
#*    Adjusted to os python re to obtain the values
# Info:
# Create a file as define as the variable DEFAULT_AWS_FILE below
# add 2 lines with the access_key = and the secret_key values
# example:
#   access_key=momo
#   secret_key=momo
# to test:
#     $ salt '*' saltutil.sync_grains
#     $ salt '*' grains.get ec2_tags


import os
import logging
from distutils.version import StrictVersion

import re
import boto.ec2
import boto.utils
import salt.log

LOG = logging.getLogger(__name__)
logging.basicConfig()

# Global variables
DEFAULT_AWS_FILE = '/etc/bs/aws'

def _get_aws_credentials():
    _spliter = re.compile(r'\s+=\s+')
    _removal = re.compile(r'(\'|"|\n)')
    if os.path.exists(DEFAULT_AWS_FILE):
        try:
            credentials_file = open(DEFAULT_AWS_FILE, 'r')
        except:
            return None
        for line in iter(credentials_file):
            # make sure to skip empty lines
            if line:
                # make sure to skip any line that starts with #
                if not line.startswith("#"):
                    data = re.split(_spliter, line)
                    # Get the access_key and secret_key value, skip all other
                    if line.startswith("access_key"):
                        # get value and remove any spaces, ' and " and strip carriage return from string
                        access_key = _removal.sub("", data[1])
                    if line.startswith("secret_key"):
                        # get value and remove any spaces,' and " and strip carriage return from string
                        secret_key = _removal.sub("", data[1])

        credentials_file.close()
        if access_key and secret_key:
            return dict(access_key=access_key, secret_key=secret_key)
        else:
            LOG.error("Credentials file issue %s, either no access_key and/or secret_key", DEFAULT_AWS_FILE)
            return None
    else:
        LOG.error("No Credentials file %s", DEFAULT_AWS_FILE)
        return None

def _get_instance_info():
    identity = boto.utils.get_instance_identity()['document']
    return identity['instanceId'], identity['region']

def _on_ec2():
    m = boto.utils.get_instance_metadata(timeout=0.1, num_retries=1)
    return bool(m)

def get_ec2_tags():
    boto_version = StrictVersion(boto.__version__)
    required_boto_version = StrictVersion('2.8.0')
    if boto_version < required_boto_version:
        LOG.error("Installed boto version %s < %s, can't find ec2_tags",
                  boto_version, required_boto_version)
        return None
    if not _on_ec2():
        LOG.info("Not an EC2 instance, skipping")
        return None
    instance_id, region = _get_instance_info()
    credentials = _get_aws_credentials()
    if credentials is None:
        return None
    # Connect to EC2 and parse the Roles tags for this instance
    try:
        conn = boto.ec2.connect_to_region(
            region,
            aws_access_key_id=credentials['access_key'],
            aws_secret_access_key=credentials['secret_key'],
        )
    except Exception as err:
        LOG.error("Could not get AWS connection: %s", err)
        return None
    ec2_tags = {}
    try:
        tags = conn.get_all_tags(filters={'resource-type': 'instance',
                                          'resource-id': instance_id})
        for tag in tags:
            ec2_tags[tag.name] = tag.value
    except Exception as err:
        LOG.error("Couldn't retrieve instance tags: %s", err)
        return None
    ret = dict(ec2_tags=ec2_tags)
    # Provide ec2_tags_roles functionality
    if 'Roles' in ec2_tags:
        ret['ec2_roles'] = ec2_tags['Roles'].split(',')
    return ret

if __name__ == '__main__':
    print('{}'.format(get_ec2_tags()))
