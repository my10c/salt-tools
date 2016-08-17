# AWS TOOLS

These are tool and grains for saltstack 


### Installation Instructions

The grains are base that the configuration files is locate
under ** /etc/bs/ **

Create teh file /etc/bs/aws , owned by root wtih
permission 0400. Example

```
[default]
output = json
region = {your-region}
aws_access_key_id = {your-access-key}
aws_secret_access_key = {your-secret-key}

```

put the grains under {salt-grain_dir} (default to /srv/_grains)
and then push the grains to the minions with: salt '*' saltutil.sync_grains




Enjoy
d@ momo
