#!/usr/bin/env python
"""A python Saltstack grain """
#
# Copyright (c) 2012 - 2016, BadAssOps inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#   * Neither the name of the <organization> nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
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
#* File     :       bs_sysinfo.py
#*
#* Description  :   a saltsack grain that displays the used partions, install memory
#*                  and the core counts
#*
#* Author   :   Luc Suryo <luc@badassops.com>
#*
#* Version  :   0.2
#*
#* Date     :   Jan 19, 2016
#*
#* History  :
#*         Date:            Info:                                  Author:
#*         March 5, 2012    First Release                              LIS
#*         Jan 19, 2016     Adjusted for bs                         LIS
#*                          so grain is also named bs_sysinfo
#*
# to test:
#     $ salt '*' saltutil.sync_grains
#     $ salt '*' grains.get bs_sysinfo
#

import os
import sys
import re
import logging
import salt.log
import multiprocessing

LOG = logging.getLogger(__name__)
logging.basicConfig()


def get_partitions_size():
    size_info = {}

    try:
        size_proc = open('/proc/partitions', 'r')
    except Exception as err:
        LOG.error('Unable to read the /proc/partitions file: error %s' % str(err))
        return None

    values = [p.split() for p in size_proc.readlines()[2:]]
    for value in values:
        if value[0] != 'major':
            size_info['/dev/'+value[3]] = value[2]
    size_proc.close()
    return size_info

def get_total_memory():
    mem_info = {}
    mem_regex = re.compile(ur'^MemTotal')

    try:
        mem_proc = open('/proc/meminfo', 'r')
    except Exception as err:
        LOG.error('Unable to read the /proc/meminfo file: error %s' % str(err))
        return None

    for line in iter(mem_proc):
        if mem_regex.search(line):
            values = line.split()
            mem_info['memtotal'] = values[1]
    mem_proc.close()
    return dict(memory=mem_info)

def get_partitions_info():
    par_info = {}
    partitions_size = {}

    partitions_size = get_partitions_size()
    if partitions_size == None:
        return None

    par_regex = re.compile(ur'^(\/dev\/)(xvd|sd|disk|mapper)')
    sym_regex = re.compile(ur'^(\/dev\/)(disk|mapper)')

    try:
        par_proc = open('/proc/mounts', 'r')
    except Exception as err:
        LOG.error('Unable to read the /proc/mounts file: error %s' % str(err))
        return None

    for line in iter(par_proc):
        if par_regex.search(line):
            values = line.split()
            # get name of the device
            if sym_regex.search(line):
                disk_info_par = os.path.realpath(values[0])
            else:
                disk_info_par = values[0]

            # get partitiion size
            disk_size_par = partitions_size[disk_info_par]
            if disk_size_par == 'None':
                return None

            # get partitiion mount point
            if values[1] == '/' :
                disk_mount_par = 'root'
            else:
                 disk_mount_par= values[1]

            work_dict = {}
            work_dict['device'] = disk_info_par
            work_dict['size'] = disk_size_par
            par_info[disk_mount_par] = dict(work_dict)
    par_proc.close()
    return dict(partitions=par_info)

def get_core_count():
    core_info = {}
    try:
        cores_count = multiprocessing.cpu_count()
    except:
        LOG.error('Unable to get cpu count')
        return None

    core_info['count'] = cores_count
    return dict(cpu_cores=core_info)

def get_bs_sysinfo():
    bs_sysinfo = {}
    # All these must be sucessfull otherwise we return None
    try:
        bs_sysinfo.update(get_total_memory())
        bs_sysinfo.update(get_partitions_info())
        bs_sysinfo.update(get_core_count())
    except:
        LOG.error('Something when wrong')
        return None

    return dict(bs_sysinfo=bs_sysinfo)

if __name__=='__main__':
    print('{}'.format(get_bs_sysinfo()))
    sys.exit(0)
