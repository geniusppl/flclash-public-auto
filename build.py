"""Build flclash.yaml, nodes.txt and sing-box.json from upstream 29.txt.
Input: upstream share-link list (public nodes only, no private credentials).
Output: flclash.yaml with inline proxies, 2 groups, domestic/Douyin DIRECT rules,
nodes.txt, the same pool as plain v2ray share links for ZedSecure,
and sing-box.json, a full sing-box config whose route rules send Douyin and
private traffic direct and everything else to the urltest group, so ZedSecure
does not need a per-app bypass for Douyin.
"""
import sys, urllib.request, yaml, json

UPSTREAM = "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/29.txt"
CONVERTER = "https://api.asailor.org/sub?target=clash&url=" + urllib.parse.quote(UPSTREAM, safe="") + "&list=true"
CONVERTER_SINGBOX = "https://api.asailor.org/sub?target=singbox&url=" + urllib.parse.quote(UPSTREAM, safe="") + "&list=true"

def main():
    with urllib.request.urlopen(UPSTREAM, timeout=120) as r:
        raw = r.read().decode()
    schemes = ("vless://", "trojan://", "vmess://", "ss://", "ssr://",
               "hysteria2://", "hy2://", "tuic://", "socks://")
    links = [line.strip() for line in raw.splitlines()
             if line.strip().startswith(schemes)]
    if len(links) < 10:
        raise SystemExit(f"too few share links: {len(links)}")
    with open("nodes.txt", "w") as f:
        f.write("\n".join(links) + "\n")
    print(f"wrote nodes.txt with {len(links)} links")
    with urllib.request.urlopen(CONVERTER, timeout=120) as r:
        data = yaml.safe_load(r.read().decode())
    proxies = data.get("proxies", [])
    if len(proxies) < 10:
        raise SystemExit(f"too few proxies: {len(proxies)}")
    names = [p["name"] for p in proxies]
    cfg = {
        "mixed-port": 7890, "allow-lan": False, "mode": "rule", "log-level": "info", "ipv6": False,
        "dns": {"enable": True, "ipv6": False,
                "default-nameserver": ["223.5.5.5", "119.29.29.29"],
                "nameserver": ["223.5.5.5", "119.29.29.29"],
                "fallback": ["8.8.8.8", "1.1.1.1"],
                "fallback-filter": {"geoip": True, "geoip-code": "CN"}},
        "proxies": proxies,
        "proxy-groups": [
            {"name": "手动选择", "type": "select", "proxies": ["自动选择", "DIRECT"] + names},
            {"name": "自动选择", "type": "url-test", "url": "https://www.gstatic.com/generate_204", "interval": 300, "tolerance": 50, "proxies": names},
        ],
        "rules": [
            "GEOSITE,private,DIRECT", "GEOIP,private,DIRECT,no-resolve",
            "DOMAIN-KEYWORD,douyin,DIRECT", "DOMAIN-KEYWORD,bytedance,DIRECT",
            "DOMAIN-KEYWORD,pstatp,DIRECT", "DOMAIN-KEYWORD,volces,DIRECT", "DOMAIN-KEYWORD,volcvideo,DIRECT",
            "DOMAIN-SUFFIX,douyin.com,DIRECT", "GEOSITE,cn,DIRECT", "GEOIP,cn,DIRECT,no-resolve", "MATCH,手动选择",
        ],
    }
    header = "# FlClash / Mihomo - public 29 auto-built, do not edit by hand, regenerated every 30 minutes by GitHub Actions\n"
    with open("flclash.yaml", "w") as f:
        f.write(header + yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    print(f"wrote flclash.yaml with {len(proxies)} proxies")
    with urllib.request.urlopen(CONVERTER_SINGBOX, timeout=120) as r:
        sb = json.loads(r.read().decode())
    sb_outbounds = sb.get("outbounds", [])
    if len(sb_outbounds) < 10:
        raise SystemExit(f"too few sing-box outbounds: {len(sb_outbounds)}")
    sb_tags = [o["tag"] for o in sb_outbounds]
    singbox = {
        "log": {"level": "info", "timestamp": True},
        "dns": {"servers": [
            {"tag": "dns-direct", "address": "223.5.5.5", "detour": "direct"},
            {"tag": "dns-proxy", "address": "tls://1.1.1.1", "detour": "自动选择"},
        ], "final": "dns-proxy", "strategy": "ipv4_only"},
        "inbounds": [
            {"type": "mixed", "tag": "mixed-in", "listen": "127.0.0.1", "listen_port": 7890},
            {"type": "tun", "tag": "tun-in", "address": ["172.19.0.1/30"],
             "auto_route": True, "strict_route": True, "stack": "mixed"},
        ],
        "outbounds": [{"type": "direct", "tag": "direct"}] + sb_outbounds + [
            {"type": "selector", "tag": "手动选择",
             "outbounds": ["自动选择", "direct"] + sb_tags},
            {"type": "urltest", "tag": "自动选择",
             "url": "https://www.gstatic.com/generate_204",
             "interval": "5m", "tolerance": 50, "outbounds": sb_tags},
        ],
        "route": {"rules": [
            {"action": "sniff"},
            {"protocol": "dns", "action": "hijack-dns"},
            {"domain_keyword": ["douyin", "bytedance", "pstatp", "volces", "volcvideo"],
             "action": "route", "outbound": "direct"},
            {"domain_suffix": ["douyin.com"], "action": "route", "outbound": "direct"},
            {"ip_is_private": True, "action": "route", "outbound": "direct"},
        ], "final": "自动选择", "auto_detect_interface": True},
    }
    with open("sing-box.json", "w") as f:
        json.dump(singbox, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote sing-box.json with {len(sb_outbounds)} node outbounds")

if __name__ == "__main__":
    main()
