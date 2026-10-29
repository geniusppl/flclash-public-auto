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

ZedSecure / v2rayNG-format share-link list (same 29 pool, no FlClash rules):

```
https://cdn.jsdelivr.net/gh/geniusppl/flclash-public-auto@main/nodes.txt
```

Import that URL in ZedSecure as a subscription; it only supports v2rayNG and
sing-box formats, not Clash YAML.

No private credentials are in this repo — only public nodes.
