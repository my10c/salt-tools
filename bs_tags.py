#!/usr/bin/env python
"""A python Saltstack grain """
#
# Copyright (c) 2012 - 2016, BadAssOps inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#    * Neither the name of the <organization> nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
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
#* File        :  bs_tags.py
#*
#* Description :  a saltsack grain that displays tags name and value based on
#*                the content of the defined tag file
#*
#* Author    :    Luc Suryo <luc@badassops.com>
#*
#* Version    :    0.4
#*
#* Date       :    Jun 22, 2016
#*
#* History    :
#*   Date:           Author  Info:
#*   March 1, 2012   LIS     First Release
#*   Jan 5, 2016     LIS     Adjusted for bs
#*                           so grain is also named bs_tags
#*   Jan 28, 2016   LIS      make sure we always return lowercase
#*   Jun 22, 2016   LIS      adjusted for multiple apps and tag options
#*
# read the file /etc/bs/tags and create a list of tag where the first
# word on the line is the tag name and the rest of the line are/is the tag's value(s).
# to test:
#     $ salt '*' saltutil.sync_grains
#     $ salt '*' grains.get bs_tag
#
# (Inspired by https://github.com/dginther/ec2-tags-salt-grain)

import os
import sys
import time
import re
import logging
import salt.log

LOG = logging.getLogger(__name__)
logging.basicConfig()

# Defaults
DEFAULT_TAG_FILE = '/etc/bs/tags'

def get_bs_tags():
    """  no parameters
    """
    _removal = re.compile(r'([|])')
    bs_tags = {}
    bs_sub_tags = {}
    if os.path.exists(DEFAULT_TAG_FILE):
        try:
            tag_file = open(DEFAULT_TAG_FILE, 'r')
        except Exception as err:
            LOG.error('Unable to read the tags fille %s, %s:', DEFAULT_TAG_FILE, err)
            return None

        for line in iter(tag_file):
        # make sure to skip empty lines and to skip any line that starts with #
            if line and not line.startswith("#"):
                # remove any []
                line = _removal.sub("", line)
                values = line.split()
                words = len(values)
                # make sure to skip empty lines
                if len != 0:
                    # tag name is always first word
                    tag_name = values[0].lower()
                    if words == 1:
                        # the line has only 1 word/value then we always assign 'none'
                        bs_tags[tag_name] = "none"
                    else:
                        # the line has more then 1 word/value
                        bs_tags[tag_name] = values[1].lower()
                        # there are more then 2 words, assign these to the .options tag
                        if values[2:]:
                            extras_list = []
                            if values[0].lower() == 'apps':
                                extras_list.append(str(values[1]).lower())
                            for value in values[2:]:
                                extras_list.append(str(value).strip('[],').lower())
                            bs_sub_tags[tag_name.lower() + "_options"] = extras_list
                            bs_tags.update(bs_sub_tags)
        tag_file.close()
        if not bs_tags:
            return None
        else:
            return dict(bs_tags=bs_tags)
    else:
        LOG.info('There is no tags fille %s', DEFAULT_TAG_FILE)
        return None

if __name__ == '__main__':
    print('{}'.format(get_bs_tags()))
    sys.exit(0)
