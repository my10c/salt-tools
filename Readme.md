# AWS TOOLS

These are tool and grains for saltstack 

```
** NOTE: my salt base directory is /data/salt/prod/ **
```

### Installation Instructions : ec2_info.py & ec2_tag.py

The grains are base that the configuration files is locate
under the directory ** /etc/bs/ **

Create the file /etc/bs/aws , owned by root wtih
permission 0400 with the content show in the example
bellow

```
[default]
output = json
region = {your-region}
aws_access_key_id = {your-access-key}
aws_secret_access_key = {your-secret-key}
```

put the grains under {salt-grain_dir} (default to /srv/_grains)
and then push the grains to the minions with:

```
salt '*' saltutil.sync_grains
```

check the grains

```
salt '*' grains.get ec2
salt '*' grains.get ec2_tags
```

### Installation Instructions : bs_sysinfo.py & bs_tags.py

The grain bs_sysinfo.py grain does not require ant configuration.

The grain bs_tags.py is look for the file ** /etc/bs/tags **
and set tke key-value pair in that file as grains. It can be use for
whatever you like, example below:

```
ec2_tags prod-momo1
dc us-east-1a
env prod
saltmaster true
ntp server
smtp client
apps salt
```

So now you could use something like this

```
{% if salt['grains.get']('env') == 'prod %}
do-something
{% endif %}
```

How to generate the file is totally up to you, so many
possiblilty; I have a script that generate the file 
one I fire up a new aws instance...


### Installation Instructions : dosalt
Before usage adjust the values of the below variable:

```
_grain_exp
_grain_name
```

example

```
_grain_exp="ec2_tags:Name:"     <-- base onthe ec2_tags Name : the default AWS tag name-value pair
_grain_name="bs_tags:env:prod"  <-- base on the bs_tags.py
```

The one thing dosalt does it to sync the local repo with github
so its always updated... check around line 383 for update_from_repo
you will need to create this files: /data/salt/prod/files/certs/github/git_hithub_salt_id_rsa
with something like:

```
#/bin/bash
ssh -i /data/salt/prod/files/certs/github/git_hithub_salt_id_rsa -l git "$@
```

and create the ssh key with and add that your github repo to be allowed to pull only!

```
sh-keygen -t rsa -C "Salt RO" -b 2048 -n "salt@saltmaster" -P '' -f /data/salt/prod/files
```



Enjoy
d@ momo
