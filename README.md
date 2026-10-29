# flclash-public-auto

Public-node configs, auto-built every 30 minutes by GitHub Actions from
`Hidashimora/free-vpn-anti-rkn` 29.txt (the pool that worked on the user's phone;
1.1 did not).

FlClash / Mihomo full config:

```
https://cdn.jsdelivr.net/gh/geniusppl/flclash-public-auto@main/flclash.yaml
```

Import that URL in FlClash as a remote config; updating it pulls the latest
built file.

ZedSecure / v2rayNG-format share-link list (same 29 pool, no rules):

```
https://cdn.jsdelivr.net/gh/geniusppl/flclash-public-auto@main/nodes.txt
```

Import that URL in ZedSecure as a subscription; it only supports v2rayNG and
sing-box formats, not Clash YAML.

ZedSecure sing-box full config (same 29 pool, Douyin/private direct built in,
no per-app bypass needed; import it as a custom sing-box config, not as a
plain node subscription):

```
https://cdn.jsdelivr.net/gh/geniusppl/flclash-public-auto@main/sing-box.json
```

Note: sing-box conversion keeps fewer nodes than Clash (about 123 vs 148),
and this config only makes Douyin/private traffic direct by inline domain
rules; other domestic sites still go through the urltest proxy group.

No private credentials are in this repo — only public nodes.
