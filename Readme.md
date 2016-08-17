# AWS TOOLS

These are tool and grains for saltstack 


### Installation Instructions

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


Enjoy
d@ momo
