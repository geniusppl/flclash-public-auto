"""Build flclash.yaml, nodes.txt and sing-box.json from upstream 29.txt.
Input: upstream share-link list (public nodes only, no private credentials).
Output: flclash.yaml with inline proxies, 2 groups, domestic/Douyin DIRECT rules,
nodes.txt, the same pool as plain v2ray share links for ZedSecure,
and sing-box.json, a full sing-box config whose route rules send Douyin and
private traffic direct and everything else to the urltest group, so ZedSecure
does not need a per-app bypass for Douyin.
"""
import sys, urllib.request, urllib.parse, base64, yaml, json

# Mainland-China nodes cannot reach the outside internet, so drop them.
# Hong Kong / Taiwan / Macau are NOT filtered: they can proxy out.
_CN_CITIES = ("beijing", "shanghai", "guangzhou", "shenzhen", "chengdu",
    "hangzhou", "wuhan", "nanjing", "tianjin", "chongqing", "xi'an", "xian",
    "suzhou", "changsha", "zhengzhou", "qingdao", "dalian", "xiamen",
    "ningbo", "hefei", "fuzhou", "shenyang", "harbin", "kunming", "jinan",
    "changchun", "nanchang", "guiyang", "lanzhou", "taiyuan", "shijiazhuang",
    "haikou", "urumqi", "hohhot")

def is_china(name, server=""):
    if server and str(server).lower().endswith(".cn"):
        return True
    if not name:
        return False
    if "🇨🇳" in name:
        return True
    n = name.lower()
    if "china" in n:
        return True
    return any(c in n for c in _CN_CITIES)

def link_name(link):
    if link.startswith("vmess://"):
        try:
            payload = link[len("vmess://"):].split("?")[0]
            payload += "=" * (-len(payload) % 4)
            return json.loads(base64.urlsafe_b64decode(payload)).get("ps", "")
        except Exception:
            return ""
    frag = link.rsplit("#", 1)[-1] if "#" in link else ""
    return urllib.parse.unquote(frag)

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
    links = [l for l in links if not is_china(link_name(l))]
    print(f"filtered mainland-China share links, kept {len(links)}")
    if len(links) < 10:
        raise SystemExit(f"too few share links: {len(links)}")
    with open("nodes.txt", "w") as f:
        f.write("\n".join(links) + "\n")
    print(f"wrote nodes.txt with {len(links)} links")
    with urllib.request.urlopen(CONVERTER, timeout=120) as r:
        data = yaml.safe_load(r.read().decode())
    proxies = data.get("proxies", [])
    proxies = [p for p in proxies
               if not is_china(p.get("name", ""), p.get("server", ""))]
    print(f"filtered mainland-China clash proxies, kept {len(proxies)}")
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
    sb_outbounds = [o for o in sb_outbounds
                    if not is_china(o.get("tag", ""), o.get("server", ""))]
    print(f"filtered mainland-China sing-box outbounds, kept {len(sb_outbounds)}")
    if len(sb_outbounds) < 10:
        raise SystemExit(f"too few sing-box outbounds: {len(sb_outbounds)}")
    sb_tags = [o["tag"] for o in sb_outbounds]
    singbox = {
        "log": {"level": "info", "timestamp": True},
        "dns": {"servers": [
            # sing-box 1.12+ new DNS server format (ZedSecure embeds
            # >= 1.14, where the legacy {"address": ...} format is
            # removed and the config fails to start): each server needs
            # a "type" and a bare "server" address, no URL scheme.
            {"type": "udp", "tag": "dns-direct", "server": "223.5.5.5", "detour": "direct"},
            {"type": "tls", "tag": "dns-proxy", "server": "1.1.1.1", "detour": "自动选择"},
        ], "rules": [
            # Chinese domains resolve via Alibaba DNS direct, so their
            # answers (and the IPs they point at) stay domestic.
            {"rule_set": "geosite-cn", "server": "dns-direct"},
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
        "route": {
        # sing-box 1.12+ requires a domain resolver for outbound
        # server domains (removed in 1.14, the core ZedSecure embeds):
        # without this, the config fails to start. dns-direct
        # (223.5.5.5, direct, no proxy) avoids a circular dependency.
        "default_domain_resolver": "dns-direct",
        "rule_set": [
            # Same geosite:cn / geoip:cn lists ZedSecure's "中国白名单"
            # preset uses, but fetched as sing-box .srs rule sets so the
            # config does not depend on ZedSecure's missing geo files.
            # jsDelivr (already used for this config) is reachable direct
            # from China, so download_detour is "direct", not a proxy.
            {"type": "remote", "tag": "geosite-cn", "format": "binary",
             "url": "https://cdn.jsdelivr.net/gh/SagerNet/sing-geosite@rule-set/geosite-cn.srs",
             "download_detour": "direct"},
            {"type": "remote", "tag": "geoip-cn", "format": "binary",
             "url": "https://cdn.jsdelivr.net/gh/SagerNet/sing-geoip@rule-set/geoip-cn.srs",
             "download_detour": "direct"},
        ], "rules": [
            {"action": "sniff"},
            {"protocol": "dns", "action": "hijack-dns"},
            {"domain_keyword": ["douyin", "bytedance", "pstatp", "volces", "volcvideo"],
             "action": "route", "outbound": "direct"},
            {"domain_suffix": ["douyin.com"], "action": "route", "outbound": "direct"},
            {"ip_is_private": True, "action": "route", "outbound": "direct"},
            {"rule_set": "geosite-cn", "action": "route", "outbound": "direct"},
            {"rule_set": "geoip-cn", "action": "route", "outbound": "direct"},
        ], "final": "自动选择", "auto_detect_interface": True},
    }
    with open("sing-box.json", "w") as f:
        json.dump(singbox, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote sing-box.json with {len(sb_outbounds)} node outbounds")

if __name__ == "__main__":
    main()
