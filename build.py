"""Build flclash.yaml and nodes.txt from upstream 29.txt.
Input: upstream share-link list (public nodes only, no private credentials).
Output: flclash.yaml with inline proxies, 2 groups, domestic/Douyin DIRECT rules,
and nodes.txt, the same pool as plain v2ray share links for ZedSecure.
"""
import sys, urllib.request, yaml

UPSTREAM = "https://raw.githubusercontent.com/Hidashimora/free-vpn-anti-rkn/main/configs/29.txt"
CONVERTER = "https://api.asailor.org/sub?target=clash&url=" + urllib.parse.quote(UPSTREAM, safe="") + "&list=true"

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

if __name__ == "__main__":
    main()
