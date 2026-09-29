import os
import requests
import time
import random
import signal
import sys
import threading
import json
import string
import re
from datetime import datetime
import pytz

try:
    import websocket
except ImportError:
    websocket = None


# ─── LANGUAGE STRINGS ────────────────────────────────────────────────────────

STRINGS = {
    "en": {
        "menu_title"      : "Super Self Bot",
        "cmd_header"      : "🛠️ Commands",
        "info_header"     : "📋 Info",
        "misc_header"     : "🔧 Misc",
        "desc_farm"       : "Spam messages to get exp for OWO or another bot",
        "desc_nhay"       : "Spam tag multi users (toggle)",
        "desc_spam"       : "Spam the same content N times, optional delay (s/m/h/d)",
        "desc_dm"         : "Send a DM to one user",
        "desc_nuke"       : "Nuke the server",
        "desc_purge"      : "Delete your own messages (default 10)",
        "desc_afk"        : "Toggle AFK — track pings when you reply",
        "desc_snipe"      : "View deleted messages (filter by user)",
        "desc_log"        : "View message edit history",
        "desc_guilds"     : "List servers you are in",
        "desc_userinfo"   : "User info (with avatar) — works in DM",
        "desc_guild"      : "Current guild info",
        "desc_id"         : "Get ID",
        "desc_av"         : "Avatar link — works in DM",
        "desc_banner"     : "Banner link — works in DM",
        "desc_ping"       : "Gateway latency",
        "desc_nick"       : "Change nickname in this server",
        "desc_language"   : "Set bot language (en / vi)",
        "err_no_guilds"   : "❌ Could not fetch server list.",
        "err_av_fail"     : "❌ Could not fetch avatar for `{uid}`",
        "err_banner_fail" : "❌ Could not fetch banner for `{uid}`",
        "err_no_banner"   : "`{uid}` has no banner set.",
        "err_nick_dm"     : "❌ $nick only works in servers.",
        "err_guild_dm"    : "❌ This command only works in servers.",
        "err_guild_fail"  : "❌ Could not fetch guild info `{gid}`",
        "err_id_unknown"  : "❌ Not recognized. Use `$id @user` / `$id #channel` / `$id @role` / `$id <id>`.",
        "err_userinfo_fail": "❌ Could not fetch info for `{uid}`.\n→ User not in cache, not in same guild, and /users failed.",
        "err_dm_usage"    : "❌ Usage: $dm <user_id> <content>",
        "err_dm_invalid"  : "❌ $dm: invalid user_id",
        "err_dm_fail"     : "❌ Could not open DM with {uid}",
        "err_spam_usage"  : "❌ Usage: $spam <count> <content> [delay]",
        "err_spam_count"  : "❌ $spam: invalid count",
        "err_spam_delay"  : "❌ $spam: invalid delay (use s/m/h/d)",
        "err_nhay_none"   : "❌ $nhay: no user mentioned",
        "err_nhay_empty"  : "❌ nhay.txt is empty or missing",
        "ping_wait"       : "🏓 Ping: waiting for first heartbeat (~40s).",
        "ping_ok"         : "🏓 Pong! Gateway latency: **{ms} ms**",
        "afk_on"          : "**AFK on{preview}** — reply to see pings received.",
        "afk_reply"       : "Currently {name} is AFK (<t:{ts}:R>){reason}",
        "afk_welcome"     : ":stopwatch: Welcome back, **{name}**! You were AFK for {dur} and received **{n}** ping(s).",
        "afk_pings_header": "**Pings received**",
        "snipe_none"      : "No recent deleted messages from {label}.",
        "snipe_header"    : "**Snipe ({n}/{total}):**",
        "log_none"        : "No edits recorded for {label}.",
        "log_header"      : "**Edit log ({n}/{total}):**",
        "log_before"      : "**Before:** {v}",
        "log_after"       : "**After:** {v}",
        "label_user"      : "that user",
        "label_channel"   : "this channel",
        "id_chan_current" : "channel (current)",
        "lang_set"        : "Language set to **{lang}**.",
        "lang_usage"      : "Usage: $language <en|vi>",
        "lang_invalid"    : "❌ Invalid language. Use `en` or `vi`.",
        "user_info_header": "**User Info**",
        "u_username"      : "**Username:** `{v}`",
        "u_display"       : "**Display name:** {v}",
        "u_none"          : "*(none)*",
        "u_id"            : "**ID:** `{v}`",
        "u_bot"           : "**Bot:** {v}",
        "u_created"       : "**Account created:** {v}",
        "u_avatar"        : "**Avatar:** {v}",
        "u_banner"        : "**Banner:** {v}",
        "u_accent"        : "**Accent color:** `#{v}`",
        "u_nick"          : "**Nickname:** {v}",
        "u_join"          : "**Joined server:** {v}",
        "u_roles"         : "**Roles ({n}):** {v}",
        "guild_info"      : "**Guild Info**",
        "g_name"          : "**Name:** {v}",
        "g_id"            : "**ID:** `{v}`",
        "g_owner"         : "**Owner ID:** `{v}`",
        "g_created"       : "**Created:** {v}",
        "g_members"       : "**Members:** {v}",
        "g_online"        : "**Online:** {v}",
        "g_online_count"  : "**Online member:** {v}",
        "g_online_unknown": "**Online member:** `?` *(gateway has no presence data — large guild)*",
        "g_boost"         : "**Boost tier:** {tier} ({n} boost)",
        "g_region"        : "**Region:** {v}",
        "g_verif"         : "**Verification level:** {v}",
        "g_icon"          : "**Icon:** {v}",
        "g_banner"        : "**Banner:** {v}",
        "g_vanity"        : "**Vanity:** discord.gg/{v}",
        "g_features"      : "**Features:** {v}",
        "id_kind_role"    : "role",
        "id_kind_channel" : "channel",
        "id_kind_user"    : "user",
        "id_kind_id"      : "id",
    },
    "vi": {
        "menu_title"      : "Super Self Bot",
        "cmd_header"      : "🛠️ Lệnh",
        "info_header"     : "📋 Info",
        "misc_header"     : "🔧 Khác",
        "desc_farm"       : "Spam tin nhắn để lấy exp cho OWO hoặc bot khác",
        "desc_nhay"       : "Spam tag nhiều user (toggle)",
        "desc_spam"       : "Spam đúng nội dung đó N lần, delay tuỳ chọn (s/m/h/d)",
        "desc_dm"         : "Gửi DM cho 1 người",
        "desc_nuke"       : "Nuke server",
        "desc_purge"      : "Xóa tin nhắn của mình (mặc định 10)",
        "desc_afk"        : "Bật/tắt AFK — tự track ping khi bạn nhắn lại",
        "desc_snipe"      : "Xem tin nhắn bị xóa (lọc theo user)",
        "desc_log"        : "Xem lịch sử chỉnh sửa tin nhắn",
        "desc_guilds"     : "List server đang ở",
        "desc_userinfo"   : "Info user (kèm avatar) — DM OK",
        "desc_guild"      : "Info guild hiện tại",
        "desc_id"         : "Lấy ID",
        "desc_av"         : "Link avatar — DM OK",
        "desc_banner"     : "Link banner — DM OK",
        "desc_ping"       : "Độ trễ gateway",
        "desc_nick"       : "Đổi nickname trong server này",
        "desc_language"   : "Đổi ngôn ngữ bot (en / vi)",
        "err_no_guilds"   : "❌ Không lấy được list server.",
        "err_av_fail"     : "❌ Không lấy được avatar của `{uid}`",
        "err_banner_fail" : "❌ Không lấy được banner của `{uid}`",
        "err_no_banner"   : "`{uid}` không có banner.",
        "err_nick_dm"     : "❌ $nick chỉ dùng trong server.",
        "err_guild_dm"    : "❌ Lệnh này chỉ dùng trong server.",
        "err_guild_fail"  : "❌ Không lấy được info guild `{gid}`",
        "err_id_unknown"  : "❌ Không nhận diện được. Dùng `$id @user` / `$id #channel` / `$id @role` / `$id <id>`.",
        "err_userinfo_fail": "❌ Không lấy được info user `{uid}`.\n→ User không trong cache, không cùng guild, và /users fail.",
        "err_dm_usage"    : "❌ Dùng: $dm <user_id> <nội dung>",
        "err_dm_invalid"  : "❌ $dm: user_id không hợp lệ",
        "err_dm_fail"     : "❌ Không mở được DM với {uid}",
        "err_spam_usage"  : "❌ Dùng: $spam <số> <nội dung> [delay]",
        "err_spam_count"  : "❌ $spam: số không hợp lệ",
        "err_spam_delay"  : "❌ $spam: delay không hợp lệ (dùng s/m/h/d)",
        "err_nhay_none"   : "❌ $nhay: chưa mention user nào",
        "err_nhay_empty"  : "❌ nhay.txt rỗng hoặc không tồn tại",
        "ping_wait"       : "🏓 Ping: đang chờ heartbeat đầu tiên (đợi ~40s).",
        "ping_ok"         : "🏓 Pong! Gateway latency: **{ms} ms**",
        "afk_on"          : "**AFK bật{preview}** — nhắn tin lại để xem ping đã nhận.",
        "afk_reply"       : "Hiện tại {name} đang AFK (<t:{ts}:R>){reason}",
        "afk_welcome"     : ":stopwatch: Chào mừng bạn trở lại, **{name}**! Bạn đã AFK trong {dur} và nhận được **{n}** ping.",
        "afk_pings_header": "**Các ping đã nhận**",
        "snipe_none"      : "Không có tin nhắn nào bị xóa gần đây của {label}.",
        "snipe_header"    : "**Snipe ({n}/{total}):**",
        "log_none"        : "Chưa ghi nhận chỉnh sửa tin nhắn nào của {label}.",
        "log_header"      : "**Edit log ({n}/{total}):**",
        "log_before"      : "**Cũ:** {v}",
        "log_after"       : "**Mới:** {v}",
        "label_user"      : "user đó",
        "label_channel"   : "kênh này",
        "id_chan_current" : "channel (hiện tại)",
        "lang_set"        : "Đã đổi ngôn ngữ sang **{lang}**.",
        "lang_usage"      : "Dùng: $language <en|vi>",
        "lang_invalid"    : "❌ Ngôn ngữ không hợp lệ. Dùng `en` hoặc `vi`.",
        "user_info_header": "**User Info**",
        "u_username"      : "**Username:** `{v}`",
        "u_display"       : "**Display name:** {v}",
        "u_none"          : "*(không có)*",
        "u_id"            : "**ID:** `{v}`",
        "u_bot"           : "**Bot:** {v}",
        "u_created"       : "**Account tạo:** {v}",
        "u_avatar"        : "**Avatar:** {v}",
        "u_banner"        : "**Banner:** {v}",
        "u_accent"        : "**Accent color:** `#{v}`",
        "u_nick"          : "**Nickname:** {v}",
        "u_join"          : "**Join server:** {v}",
        "u_roles"         : "**Roles ({n}):** {v}",
        "guild_info"      : "**Guild Info**",
        "g_name"          : "**Name:** {v}",
        "g_id"            : "**ID:** `{v}`",
        "g_owner"         : "**Owner ID:** `{v}`",
        "g_created"       : "**Created:** {v}",
        "g_members"       : "**Members:** {v}",
        "g_online"        : "**Online:** {v}",
        "g_online_count"  : "**Online member:** {v}",
        "g_online_unknown": "**Online member:** `?` *(gateway không có presence data — guild lớn)*",
        "g_boost"         : "**Boost tier:** {tier} ({n} boost)",
        "g_region"        : "**Region:** {v}",
        "g_verif"         : "**Verification level:** {v}",
        "g_icon"          : "**Icon:** {v}",
        "g_banner"        : "**Banner:** {v}",
        "g_vanity"        : "**Vanity:** discord.gg/{v}",
        "g_features"      : "**Features:** {v}",
        "id_kind_role"    : "role",
        "id_kind_channel" : "channel",
        "id_kind_user"    : "user",
        "id_kind_id"      : "id",
    },
}


def tr(lang, key, **kwargs):
    s = STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))
    try:
        return s.format(**kwargs) if kwargs else s
    except Exception:
        return s


# ─── TIME ────────────────────────────────────────────────────────────────────

def get_vn_time():
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(tz)


def replace_placeholders(text):
    if not text:
        return text
    now = get_vn_time()
    text = text.replace("{date}", now.strftime("%d/%m/20%y"))
    text = text.replace("{time}", now.strftime("%H:%M:%S"))
    return text


def parse_duration(value, default=5):
    if value is None:
        return default
    s = str(value).strip().lower()
    if not s:
        return default
    m = re.match(r"^(\d+(?:\.\d+)?)\s*([smhd]?)$", s)
    if not m:
        return None
    try:
        num = float(m.group(1))
    except ValueError:
        return None
    unit = m.group(2) or "s"
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    secs = int(num * mult)
    return max(1, secs)


def parse_duration_or_default(value, default=5):
    v = parse_duration(value, default=default)
    return default if v is None else v


def resolve_start_time(mode):
    now_s = int(time.time())
    mode = (mode or "now").strip().lower()

    if mode == "elapsed":
        return now_s - 60
    if mode == "now":
        return now_s
    if mode == "today":
        tz = pytz.timezone("Asia/Ho_Chi_Minh")
        d = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        return int(d.timestamp())
    if mode == "1y":
        return now_s - 365 * 24 * 3600
    if mode == "3y":
        return now_s - 3 * 365 * 24 * 3600
    if mode == "30d":
        return now_s - 30 * 24 * 3600
    if mode == "180d":
        return now_s - 180 * 24 * 3600
    try:
        val = int(mode)
        if val > 1_000_000_000_000:
            val = val // 1000
        return val
    except ValueError:
        return now_s


def snowflake_to_str(snowflake):
    try:
        ts = ((int(snowflake) >> 22) + 1420070400000) / 1000
        return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return "?"


def iso_to_str(iso_str):
    if not iso_str:
        return "?"
    try:
        from datetime import timezone, timedelta
        s = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        vn = dt.astimezone(timezone(timedelta(hours=7)))
        return vn.strftime("%Y-%m-%d %H:%M:%S (VN)")
    except Exception:
        return "?"


def ts_to_str(epoch_seconds):
    try:
        from datetime import timezone, timedelta
        dt = datetime.fromtimestamp(int(epoch_seconds), tz=timezone.utc)
        vn = dt.astimezone(timezone(timedelta(hours=7)))
        return vn.strftime("%Y-%m-%d %H:%M:%S (VN)")
    except Exception:
        return "?"


# ─── CONFIG ──────────────────────────────────────────────────────────────────

def load_config():
    config = {}
    with open("config.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


def parse_voice_pairs(guild_str, channel_str):
    import re as _re
    def extract(s):
        s = s.strip()
        ids = _re.findall(r"\(([^)]+)\)", s)
        if ids:
            return [i.strip() for i in ids if i.strip()]
        return [i.strip() for i in s.split(",") if i.strip()]

    guilds   = extract(guild_str   or "")
    channels = extract(channel_str or "")
    return [{"guild_id": g, "channel_id": c} for g, c in zip(guilds, channels)]


def get_per_token(config, key, index):
    if index == 1:
        return config.get(key, "")
    indexed = config.get(f"{key}_{index}", "")
    if indexed:
        return indexed
    return config.get(key, "")


def load_tokens(config):
    tokens = []
    token = config.get("token", "").strip()
    if token:
        tokens.append(token)
    i = 2
    while True:
        t = config.get(f"token_{i}", "").strip()
        if not t:
            break
        tokens.append(t)
        i += 1
    return tokens


# ─── DISCORD REST ────────────────────────────────────────────────────────────

def check_token(token):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    r = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
    if r.status_code == 200:
        data = r.json()
        username = data.get("username")
        discriminator = data.get("discriminator")
        user_id = data.get("id")
        if discriminator and discriminator != "0":
            return f"{username}#{discriminator}", user_id
        return username, user_id
    return None, None


def get_current_custom_status(token):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    r = requests.get("https://discord.com/api/v9/users/@me/settings", headers=headers)
    if r.status_code == 200:
        return r.json().get("custom_status", None)
    return None


def change_custom_status(token, text):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {"custom_status": {"text": text}}
    try:
        r = requests.patch(
            "https://discord.com/api/v9/users/@me/settings",
            headers=headers, json=payload, timeout=10
        )
        if r.status_code == 429:
            retry = r.json().get("retry_after", 1)
            time.sleep(retry)
            requests.patch(
                "https://discord.com/api/v9/users/@me/settings",
                headers=headers, json=payload, timeout=10
            )
    except requests.RequestException:
        pass


def restore_custom_status(token, original):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        requests.patch(
            "https://discord.com/api/v9/users/@me/settings",
            headers=headers, json={"custom_status": original}, timeout=10
        )
    except requests.RequestException:
        pass


def delete_message(token, channel_id, message_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        requests.delete(
            f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}",
            headers=headers, timeout=10
        )
    except requests.RequestException:
        pass


def edit_message(token, channel_id, message_id, content):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    if content and len(content) > 2000:
        content = content[:1997] + "..."
    try:
        requests.patch(
            f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}",
            headers=headers, json={"content": content}, timeout=10
        )
    except requests.RequestException:
        pass


def send_message(token, channel_id, content):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.post(
            f"https://discord.com/api/v9/channels/{channel_id}/messages",
            headers=headers, json={"content": content}, timeout=10
        )
        if r.status_code == 200:
            return r.json().get("id")
    except requests.RequestException:
        pass
    return None


def purge_messages(token, channel_id, user_id, count):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    deleted = 0
    last_id = None
    while deleted < count:
        params = {"limit": 100}
        if last_id:
            params["before"] = last_id
        try:
            r = requests.get(
                f"https://discord.com/api/v9/channels/{channel_id}/messages",
                headers=headers, params=params, timeout=10
            )
            if r.status_code != 200:
                break
            msgs = r.json()
            if not msgs:
                break
            last_id = msgs[-1]["id"]
            for msg in msgs:
                if deleted >= count:
                    break
                if msg["author"]["id"] == user_id:
                    try:
                        requests.delete(
                            f"https://discord.com/api/v9/channels/{channel_id}/messages/{msg['id']}",
                            headers=headers, timeout=10
                        )
                        deleted += 1
                        time.sleep(0.4)
                    except requests.RequestException:
                        pass
        except requests.RequestException:
            break
    return deleted


def get_channel_info(token, channel_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(
            f"https://discord.com/api/v9/channels/{channel_id}",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


def resolve_invite(token, invite_code):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(
            f"https://discord.com/api/v9/invites/{invite_code}?with_counts=true",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


def get_guild_channels(token, guild_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(
            f"https://discord.com/api/v9/guilds/{guild_id}/channels",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


def get_guild_name(token, guild_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(
            f"https://discord.com/api/v9/guilds/{guild_id}",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json().get("name", "Unknown")
    except requests.RequestException:
        pass
    return "Unknown"


def delete_channel(token, channel_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.delete(
            f"https://discord.com/api/v9/channels/{channel_id}",
            headers=headers, timeout=10
        )
        return r.status_code in (200, 204)
    except requests.RequestException:
        return False


def create_channel(token, guild_id, name):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.post(
            f"https://discord.com/api/v9/guilds/{guild_id}/channels",
            headers=headers, json={"name": name, "type": 0}, timeout=10
        )
        if r.status_code in (200, 201):
            return r.json()
    except requests.RequestException:
        pass
    return None


def create_webhook(token, channel_id, name):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.post(
            f"https://discord.com/api/v9/channels/{channel_id}/webhooks",
            headers=headers, json={"name": name}, timeout=10
        )
        if r.status_code in (200, 201):
            data = r.json()
            return f"https://discord.com/api/webhooks/{data['id']}/{data['token']}"
    except requests.RequestException:
        pass
    return None


def spam_webhook(url, content):
    while True:
        try:
            r = requests.post(url, json={"content": content}, timeout=10)
            if r.status_code == 404:
                break
            if r.status_code == 429:
                retry = r.json().get("retry_after", 0.1)
                time.sleep(retry)
        except requests.RequestException:
            break


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def create_dm(token, user_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.post(
            "https://discord.com/api/v9/users/@me/channels",
            headers=headers, json={"recipient_id": str(user_id)}, timeout=10
        )
        if r.status_code == 200:
            return r.json().get("id")
    except requests.RequestException:
        pass
    return None


def get_self_guilds(token):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(
            "https://discord.com/api/v9/users/@me/guilds",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


def get_user_info(token, user_id, guild_id=None):
    headers = {"Authorization": token, "Content-Type": "application/json"}

    try:
        r = requests.get(
            f"https://discord.com/api/v9/users/{user_id}",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json()
        print(f"[!] /users/{user_id} → HTTP {r.status_code}")
    except requests.RequestException as e:
        print(f"[!] /users/{user_id} exception: {e}")

    if guild_id:
        try:
            r = requests.get(
                f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}",
                headers=headers, timeout=10
            )
            if r.status_code == 200:
                mem = r.json()
                user = mem.get("user")
                if user:
                    merged = dict(user)
                    merged["_member"] = mem
                    return merged
            print(f"[!] /guilds/{guild_id}/members/{user_id} → HTTP {r.status_code}")
        except requests.RequestException as e:
            print(f"[!] member lookup exception: {e}")

    return None


def resolve_user_info(token, user_id, guild_id=None, channel_id=None, user_cache=None):
    uid = str(user_id)

    if user_cache and uid in user_cache:
        return dict(user_cache[uid])

    if channel_id and not guild_id:
        ch_info = get_channel_info(token, channel_id)
        if ch_info and ch_info.get("type") in (1, 3):
            for r in ch_info.get("recipients", []) or []:
                if str(r.get("id")) == uid:
                    return r

    info = get_user_info(token, uid, guild_id=guild_id)
    if info:
        return info

    return None


def get_guild_member(token, guild_id, user_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(
            f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


def get_guild_info(token, guild_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(
            f"https://discord.com/api/v9/guilds/{guild_id}?with_counts=true",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


def get_guild_bot_ids(token, guild_id, max_pages=20):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    bot_ids = set()
    after = "0"
    for _ in range(max_pages):
        try:
            r = requests.get(
                f"https://discord.com/api/v9/guilds/{guild_id}/members",
                headers=headers, params={"limit": 1000, "after": after}, timeout=20
            )
            if r.status_code != 200:
                print(f"[!] /guilds/{guild_id}/members → HTTP {r.status_code}")
                break
            members = r.json()
            if not members:
                break
            for m in members:
                u = m.get("user") or {}
                if u.get("bot") and u.get("id"):
                    bot_ids.add(u["id"])
            if len(members) < 1000:
                break
            after = members[-1]["user"]["id"]
        except requests.RequestException as e:
            print(f"[!] get_guild_bot_ids exception: {e}")
            break
    return bot_ids


def change_nick(token, guild_id, nick):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.patch(
            f"https://discord.com/api/v9/guilds/{guild_id}/members/@me",
            headers=headers, json={"nick": nick or None}, timeout=10
        )
        return r.status_code in (200, 204)
    except requests.RequestException:
        return False


def build_avatar_url(user_id, avatar_hash):
    if avatar_hash:
        ext = "gif" if avatar_hash.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{ext}?size=1024"
    idx = (int(user_id) >> 22) % 6
    return f"https://cdn.discordapp.com/embed/avatars/{idx}.png"


def build_banner_url(user_id, banner_hash):
    if not banner_hash:
        return None
    ext = "gif" if banner_hash.startswith("a_") else "png"
    return f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{ext}?size=1024"


def parse_snipe_args(content, cmd_prefix):
    rest = content[len(cmd_prefix):].strip()
    target_uid = None
    count = None

    m_user = re.search(r"<@!?(\d+)>", rest)
    if m_user:
        target_uid = m_user.group(1)

    m_num = re.search(r"\b(\d{1,3})\b", rest)
    if m_num:
        try:
            count = int(m_num.group(1))
        except ValueError:
            count = None

    if count is None:
        count = 10 if target_uid else 1

    count = max(1, min(count, 20))
    return target_uid, count


# ─── NUKE ────────────────────────────────────────────────────────────────────

def nuke_server(token, guild_id, ad_invite, rpc_name):
    print("[*] Nuking server...")
    spam_content = (
        f"# your trash server got fucked by {rpc_name}\U0001f62d\U0001f602cry and report it to your mom\n"
        f"# {rpc_name} | little rat cry now \U0001f602\n"
        f"{ad_invite}\n{ad_invite}\n{ad_invite}\n{ad_invite}\n@everyone"
    )
    channel_names = [
        "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
        for _ in range(6)
    ]
    create_index = [0]
    lock = threading.Lock()
    spam_threads = []

    def delete_all_channels():
        channels = get_guild_channels(token, guild_id)
        if channels:
            for ch in channels:
                delete_channel(token, ch["id"])
        print("[+] Deleted all channels")

    def create_and_spam():
        while True:
            with lock:
                if create_index[0] >= len(channel_names):
                    break
                idx = create_index[0]
                create_index[0] += 1
            name = channel_names[idx]
            ch = create_channel(token, guild_id, name)
            if ch:
                print(f"[+] Created #{name}")
                wh = create_webhook(token, ch["id"], "alex_raid")
                if wh:
                    print(f"[+] Webhook in #{name}")
                    t = threading.Thread(target=spam_webhook, args=(wh, spam_content), daemon=True)
                    t.start()
                    spam_threads.append(t)

    dt = threading.Thread(target=delete_all_channels, daemon=True)
    dt.start()
    workers = [threading.Thread(target=create_and_spam, daemon=True) for _ in range(3)]
    for w in workers:
        w.start()
    dt.join()
    for w in workers:
        w.join()
    for t in spam_threads:
        t.join()
    print("[+] Nuke completed")


# ─── ASSETS ──────────────────────────────────────────────────────────────────

SMALL_IMAGE_URL = "https://media.tenor.com/oJwNPShUJnwAAAAj/discord-verification-verification.gif"


def register_asset(token, app_id, url):
    try:
        headers = {"Authorization": token, "Content-Type": "application/json"}
        r = requests.post(
            f"https://discord.com/api/v9/applications/{app_id}/external-assets",
            headers=headers, json={"urls": [url]}, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            if data:
                path = data[0].get("external_asset_path", "")
                if path:
                    return f"mp:{path}"
    except Exception:
        pass
    return url


def preload_assets(token, app_id, image_url):
    cache = {}
    loaded = 0
    resolved_large = register_asset(token, app_id, image_url)
    cache["large"] = resolved_large
    if resolved_large.startswith("mp:"):
        loaded += 1
    resolved_small = register_asset(token, app_id, SMALL_IMAGE_URL)
    cache["small"] = resolved_small
    if resolved_small.startswith("mp:"):
        loaded += 1
    print(f"[*] Loaded {loaded} image")
    return cache


# ─── STREAM CONFIG ───────────────────────────────────────────────────────────

def load_stream_config():
    config = {}
    try:
        with open("stream.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        return None
    return config


def load_custom_statuses():
    try:
        with open("customstatus.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def load_nhay():
    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


# ─── ACTIVITY BUILDER ────────────────────────────────────────────────────────

def build_activity_from_slot(sc, slot, app_id, asset_cache, start_time, rpc_type=2, rpc_name="Nova", token_index=1):
    ti = "" if token_index == 1 else f"_{token_index}"
    sl = "_b" if slot == 2 else ""

    def get(key):
        for k in [f"{key}{ti}{sl}", f"{key}{ti}", f"{key}{sl}", key]:
            v = sc.get(k, "")
            if v:
                return v
        return ""

    line1      = replace_placeholders(get("line1"))
    line2      = replace_placeholders(get("line2"))
    line3      = replace_placeholders(get("line3"))
    btn1_label = replace_placeholders(get("button1_label"))
    btn1_url   = get("button1_url")
    btn2_label = replace_placeholders(get("button2_label"))
    btn2_url   = get("button2_url")

    start_ms = (start_time or int(time.time())) * 1000

    activity = {
        "type": rpc_type,
        "name": rpc_name,
        "timestamps": {"start": start_ms},
    }

    if rpc_type == 2:
        activity["url"] = "https://www.twitch.tv/lucas_the_vampire"

    if line1:
        activity["details"] = line1
    if line2:
        activity["state"] = line2

    asset_text = line3 if line3 else "​"
    activity["assets"] = {
        "large_image": asset_cache.get("large", ""),
        "large_text": asset_text,
        "small_image": asset_cache.get("small", ""),
        "small_text": asset_text,
    }

    buttons = []
    button_urls = []
    if btn1_label and btn1_url:
        buttons.append(btn1_label)
        button_urls.append(btn1_url)
    if btn2_label and btn2_url:
        buttons.append(btn2_label)
        button_urls.append(btn2_url)
    if buttons:
        activity["buttons"] = buttons
        activity["metadata"] = {"button_urls": button_urls}

    if app_id:
        activity["application_id"] = app_id

    return activity


# ─── FARM / NHAY / SPAM ──────────────────────────────────────────────────────

RANDOM_EMOJIS = [
    "\U0001f602", "\U0001f525", "\U0001f480", "\U0001f62d",
    "\U0001f427", "\U0001f338", "\U0001f4af", "\U0001f389",
    "\U0001f60e", "\U0001f921", "\U0001f47e", "\U0001fae1",
    "\U0001f976", "\U0001f923", "\U0001f608", "\U0001f440",
    "\U0001f441", "\U0001f636",
]


def random_farm_message(rpc_name):
    emojis = "".join(random.choices(RANDOM_EMOJIS, k=3))
    return f"{rpc_name} On Top {emojis}"


def farm_loop(token, channel_id, stop_event, rpc_name):
    while not stop_event.is_set():
        for _ in range(4):
            if stop_event.is_set():
                return
            send_message(token, channel_id, random_farm_message(rpc_name))
            time.sleep(0.5)
        stop_event.wait(5)


def nhay_loop(token, channel_id, target_user_ids, nhay_lines, stop_event):
    while not stop_event.is_set():
        if stop_event.is_set():
            return
        random_line = random.choice(nhay_lines)
        mentions = " ".join([f"<@{uid}>" for uid in target_user_ids])
        send_message(token, channel_id, f"{random_line} {mentions}")
        stop_event.wait(random.uniform(1, 2))


def spam_loop(token, channel_id, text, count, delay=0.7):
    for _ in range(count):
        send_message(token, channel_id, text)
        time.sleep(delay)


# ─── AFK HELPERS ─────────────────────────────────────────────────────────────

def _format_duration(seconds, lang="en"):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    if lang == "vi":
        if m and s:
            return f"{m} phút và {s} giây"
        if m:
            return f"{m} phút"
        return f"{s} giây"
    else:
        if m and s:
            return f"{m} min and {s} sec"
        if m:
            return f"{m} min"
        return f"{s} sec"


def build_afk_summary(display_name, duration, pings, lang="en"):
    dur_text = _format_duration(duration, lang)

    lines = [
        tr(lang, "afk_welcome", name=display_name, dur=dur_text, n=len(pings)),
    ]

    if pings:
        lines.append("")
        lines.append(tr(lang, "afk_pings_header"))
        for p in pings:
            lines.append(f"**{p['author']}**")
            lines.append(p["jump_url"])
            lines.append("")
        lines.pop()

    return "\n".join(lines)


def is_user_mention_of(mentions, my_id):
    for m in mentions or []:
        if m.get("id") != my_id:
            continue
        if m.get("username") is not None or m.get("discriminator") is not None:
            return True
    return False


# ─── GATEWAY ─────────────────────────────────────────────────────────────────

class DiscordGateway:
    def __init__(self, token, user_id, account_name, activity=None,
                 stream_config=None, app_id=None, auto_change_stream=False,
                 asset_cache=None, start_time=None,
                 auto_join_voice=False, guild_id=None, voice_channel_id=None,
                 fakelive=False, rpc_type=2, rpc_name="Nova", token_index=1,
                 commands_enabled=True, stream_rotate_delay=5,
                 language="en"):
        self.token            = token
        self.user_id          = user_id
        self.account_name     = account_name
        self.activity         = activity
        self.stream_config    = stream_config
        self.app_id           = app_id
        self.auto_change_stream = auto_change_stream
        self.asset_cache      = asset_cache or {}
        self.start_time       = start_time if start_time else int(time.time())
        self.ws               = None
        self.heartbeat_interval = None
        self.sequence         = None
        self.running          = True
        self.current_voice    = None
        self.pending_live     = {}
        self.session_id       = None
        self.rejoining_guilds = set()
        self.rpc_type         = rpc_type
        self.rpc_name         = rpc_name
        self.token_index      = token_index
        self.commands_enabled = commands_enabled
        self.stream_rotate_delay = max(1, int(stream_rotate_delay))
        self.language         = language if language in ("en", "vi") else "en"
        # Farm
        self.farm_stop_event  = None
        self.farm_thread      = None
        self.farm_channel     = None
        # Stream rotate
        self.stream_slot      = 1
        self.stream_lock      = threading.Lock()
        # Voice
        self.auto_join_voice  = auto_join_voice
        self.voice_channels   = []
        self.current_voice_list = []
        self.is_rejoining     = False
        if guild_id and voice_channel_id:
            self.voice_channels = parse_voice_pairs(guild_id, voice_channel_id)
        # Fake live
        self.fakelive = fakelive
        # Nhay
        self.nhay_lines      = load_nhay()
        self.nhay_stop_event = None
        self.nhay_thread     = None
        self.nhay_channel    = None
        self.nhay_targets    = []
        # Snipe + Edit log
        self.msg_cache       = {}
        self.snipe_cache     = {}
        self.edit_cache      = {}
        # AFK
        self.afk_enabled     = False
        self.afk_message     = ""
        self.afk_start_time  = None
        self.afk_pings       = []
        self.afk_auto_reply  = True
        self.afk_auto_reply_msg_id = None
        # Ping
        self.last_hb_sent    = 0.0
        self.last_hb_ack     = 0.0
        # Online member tracking (presences)
        self.guild_online    = {}
        self.guild_bot_ids   = {}
        self.guild_bot_ts    = {}
        # User cache
        self.user_cache      = {}

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()
        if self.auto_change_stream and self.stream_config:
            threading.Thread(target=self._stream_rotate_loop, daemon=True).start()

    def _get_ping_ms(self):
        if self.last_hb_ack and self.last_hb_sent:
            return int((self.last_hb_ack - self.last_hb_sent) * 1000)
        return -1

    def _stream_rotate_loop(self):
        while self.running:
            time.sleep(self.stream_rotate_delay)
            if not self.running:
                break
            with self.stream_lock:
                self.stream_slot = 2 if self.stream_slot == 1 else 1
                self.activity = build_activity_from_slot(
                    self.stream_config, self.stream_slot, self.app_id,
                    self.asset_cache, self.start_time,
                    self.rpc_type, self.rpc_name, token_index=self.token_index
                )
            self._update_presence()

    def _update_presence(self):
        try:
            if self.ws and self.running:
                self.ws.send(json.dumps({
                    "op": 3,
                    "d": {
                        "activities": [self.activity] if self.activity else [],
                        "status": "online",
                        "since": 0,
                        "afk": False,
                    }
                }))
        except Exception:
            pass

    def _run(self):
        while self.running:
            try:
                self.ws = websocket.WebSocket()
                self.ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
                hello = json.loads(self.ws.recv())
                self.heartbeat_interval = hello["d"]["heartbeat_interval"] / 1000
                threading.Thread(target=self._heartbeat, daemon=True).start()
                self._identify()
                while self.running:
                    msg = self.ws.recv()
                    if msg:
                        data = json.loads(msg)
                        if data.get("op") == 11:
                            self.last_hb_ack = time.time()
                        if data.get("s"):
                            self.sequence = data["s"]
                        self._handle_event(data)
            except Exception:
                if self.running:
                    time.sleep(5)

    def _heartbeat(self):
        while self.running:
            try:
                time.sleep(self.heartbeat_interval)
                if self.ws and self.running:
                    self.last_hb_sent = time.time()
                    self.ws.send(json.dumps({"op": 1, "d": self.sequence}))
            except Exception:
                break

    def _identify(self):
        self.ws.send(json.dumps({
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {"os": "windows", "browser": "Discord Client", "device": ""},
                "presence": {
                    "activities": [self.activity] if self.activity else [],
                    "status": "online",
                    "since": 0,
                    "afk": False,
                },
            }
        }))

    def _auto_join_voice(self):
        if not self.auto_join_voice:
            return

        def _join_all_sequential():
            for v in self.voice_channels:
                if not self.running:
                    return
                guild_id   = v["guild_id"]
                channel_id = v["channel_id"]
                try:
                    time.sleep(2)
                    if not self.ws or not self.running:
                        return
                    self.ws.send(json.dumps({
                        "op": 4,
                        "d": {
                            "guild_id": guild_id,
                            "channel_id": channel_id,
                            "self_mute": True,
                            "self_deaf": True,
                        }
                    }))
                    if v not in self.current_voice_list:
                        self.current_voice_list.append(v)
                    print(f"[+] [{self.account_name}] Auto joined voice: {channel_id} ({guild_id})")
                    if self.fakelive:
                        time.sleep(3)
                        self.start_fake_live(guild_id, channel_id)
                        time.sleep(3)
                except Exception as e:
                    print(f"[!] [{self.account_name}] Auto join failed {channel_id}: {e}")

        threading.Thread(target=_join_all_sequential, daemon=True).start()

    def start_fake_live(self, guild_id, channel_id):
        try:
            self.ws.send(json.dumps({
                "op": 18,
                "d": {
                    "type": "guild",
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "preferred_region": "singapore"
                }
            }))
            time.sleep(1)
            self.ws.send(json.dumps({
                "op": 4,
                "d": {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "self_mute": True,
                    "self_deaf": True,
                    "self_stream": True,
                    "self_video": False,
                }
            }))
            self.pending_live.pop(guild_id, None)
            print(f"[+] [{self.account_name}] Fake live started in {channel_id}")
        except Exception:
            pass

    def _handle_event(self, data):
        event = data.get("t")
        d = data.get("d")
        if not d:
            return

        if event == "READY":
            self.session_id = d.get("session_id")
            me = d.get("user") or {}
            if me.get("id"):
                self.user_cache[str(me["id"])] = me
            for g in d.get("guilds") or []:
                gid = g.get("id")
                if not gid:
                    continue
                pres = g.get("presences") or []
                s = set()
                for p in pres:
                    u_data = p.get("user") or {}
                    u = u_data.get("id")
                    st = p.get("status")
                    if u:
                        self.user_cache[str(u)] = u_data
                        if st and st != "offline":
                            s.add(u)
                self.guild_online[gid] = s
            if self.auto_join_voice:
                threading.Thread(target=self._auto_join_voice, daemon=True).start()

        if event == "PRESENCE_UPDATE":
            gid = d.get("guild_id")
            u_data = d.get("user") or {}
            u   = u_data.get("id")
            st  = d.get("status")
            if u:
                self.user_cache[str(u)] = u_data
            if gid and u:
                s = self.guild_online.setdefault(gid, set())
                if st == "offline":
                    s.discard(u)
                else:
                    s.add(u)

        if event == "VOICE_STATE_UPDATE":
            if d.get("user_id") == self.user_id:
                event_guild   = d.get("guild_id", "")
                event_channel = d.get("channel_id")

                if event_channel and event_guild in self.pending_live:
                    self.pending_live.pop(event_guild, None)

                is_stream_event = d.get("self_stream", False)
                if not event_channel and event_guild and not is_stream_event:
                    if event_guild in self.rejoining_guilds:
                        pass
                    else:
                        target = None
                        for v in self.voice_channels:
                            if v["guild_id"] == event_guild:
                                target = v
                                break
                        if not target and self.current_voice and self.current_voice.get("guild_id") == event_guild:
                            target = self.current_voice
                            self.current_voice = None
                        if target:
                            self.current_voice_list = [
                                v for v in self.current_voice_list
                                if v["guild_id"] != event_guild
                            ]
                            self.pending_live.pop(event_guild, None)
                            print(f"[*] [{self.account_name}] Left voice: {target['channel_id']} ({event_guild})")
                            if self.auto_join_voice:
                                self.rejoining_guilds.add(event_guild)
                                def _do_rejoin(v, gid):
                                    time.sleep(2)
                                    try:
                                        if self.ws and self.running:
                                            self.ws.send(json.dumps({
                                                "op": 4,
                                                "d": {
                                                    "guild_id": v["guild_id"],
                                                    "channel_id": v["channel_id"],
                                                    "self_mute": True,
                                                    "self_deaf": True,
                                                }
                                            }))
                                            if v not in self.current_voice_list:
                                                self.current_voice_list.append(v)
                                            print(f"[+] [{self.account_name}] Rejoined voice: {v['channel_id']} ({v['guild_id']})")
                                            if self.fakelive:
                                                self.pending_live[v["guild_id"]] = v
                                                time.sleep(3)
                                                self.start_fake_live(v["guild_id"], v["channel_id"])
                                    except Exception:
                                        pass
                                    finally:
                                        self.rejoining_guilds.discard(gid)
                                threading.Thread(target=_do_rejoin, args=(target, event_guild), daemon=True).start()

        if event == "MESSAGE_DELETE":
            ch  = d.get("channel_id")
            mid = d.get("id")
            cached = self.msg_cache.get(ch, {}).pop(mid, None)
            if cached:
                if ch not in self.snipe_cache:
                    self.snipe_cache[ch] = []
                cached["deleted_at"] = int(time.time())
                self.snipe_cache[ch].insert(0, cached)
                self.snipe_cache[ch] = self.snipe_cache[ch][:30]

        if event == "MESSAGE_UPDATE":
            ch  = d.get("channel_id")
            mid = d.get("id")
            new_content = d.get("content")
            author      = d.get("author") or {}

            if new_content is None:
                return

            ch_cache = self.msg_cache.get(ch, {})
            old = ch_cache.get(mid)
            if old:
                if ch not in self.edit_cache:
                    self.edit_cache[ch] = []
                self.edit_cache[ch].insert(0, {
                    "author"    : old.get("author", author.get("username", "Unknown")),
                    "author_id" : old.get("author_id", author.get("id", "0")),
                    "before"    : old.get("content", ""),
                    "after"     : new_content,
                    "edited_at" : int(time.time()),
                })
                self.edit_cache[ch] = self.edit_cache[ch][:30]
                old["content"] = new_content

        if event == "MESSAGE_CREATE":
            author = d.get("author", {})
            msg_channel = d.get("channel_id")
            msg_content = d.get("content", "")
            msg_author  = d.get("author", {})
            msg_id      = d.get("id", "")
            L = self.language

            if msg_author.get("id"):
                self.user_cache[str(msg_author["id"])] = msg_author

            for m in d.get("mentions", []) or []:
                if m.get("id"):
                    self.user_cache[str(m["id"])] = m

            if msg_content and msg_id:
                if msg_channel not in self.msg_cache:
                    self.msg_cache[msg_channel] = {}
                ch_cache = self.msg_cache[msg_channel]
                if len(ch_cache) > 500:
                    ch_cache.pop(next(iter(ch_cache)), None)
                ch_cache[msg_id] = {
                    "content"  : msg_content,
                    "author"   : msg_author.get("global_name")
                                 or msg_author.get("username", "Unknown"),
                    "author_id": msg_author.get("id", "0"),
                    "timestamp": d.get("timestamp", ""),
                }

            # ─── AFK ────────────────────────────────────────────────────
            if self.afk_enabled:
                sender_id  = msg_author.get("id")
                is_self    = sender_id == self.user_id
                is_bot     = msg_author.get("bot", False)

                is_user_mention = is_user_mention_of(
                    d.get("mentions", []), self.user_id
                )
                is_dm = d.get("guild_id") is None
                ref = d.get("referenced_message") or {}
                ref_author_id = (ref.get("author") or {}).get("id")
                is_reply_to_me = ref_author_id == self.user_id

                if not is_self and not is_bot and (is_user_mention or is_dm or is_reply_to_me):
                    gid = d.get("guild_id") or "@me"
                    jump_url = f"https://discord.com/channels/{gid}/{msg_channel}/{msg_id}"

                    display_name = (
                        msg_author.get("global_name")
                        or msg_author.get("display_name")
                        or msg_author.get("username")
                        or "Unknown"
                    )

                    self.afk_pings.append({
                        "author"    : display_name,
                        "jump_url"  : jump_url,
                        "channel_id": msg_channel,
                        "message_id": msg_id,
                    })
                    print(f"[AFK] {display_name} ping {self.account_name} -> {jump_url}")

                    if self.afk_auto_reply:
                        reason_part = f": **{self.afk_message}**" if self.afk_message else ""
                        reply_text  = tr(L, "afk_reply",
                                         name=self.account_name,
                                         ts=self.afk_start_time,
                                         reason=reason_part)
                        self.afk_auto_reply_msg_id = send_message(
                            self.token, msg_channel, reply_text
                        )

            if author.get("id") != self.user_id:
                return

            content    = d.get("content", "").strip()
            channel_id = d.get("channel_id")
            message_id = d.get("id")
            guild_id   = d.get("guild_id")

            if (self.afk_enabled
                    and message_id != self.afk_auto_reply_msg_id
                    and not content.startswith("$afk")):
                pings_copy = list(self.afk_pings)
                duration   = int(time.time() - (self.afk_start_time or time.time()))
                display    = self.account_name

                self.afk_enabled           = False
                self.afk_start_time        = None
                self.afk_message           = ""
                self.afk_pings             = []
                self.afk_auto_reply_msg_id = None

                summary = build_afk_summary(display, duration, pings_copy, L)
                send_message(self.token, channel_id, summary)

            if not self.commands_enabled:
                return

            # ─── COMMANDS ────────────────────────────────────────────────

            if content == "$menu":
                edit_message(self.token, channel_id, message_id, (
                    f"## {tr(L, 'menu_title')} - {self.rpc_name}\n\n"
                    f"**{tr(L, 'cmd_header')}** :\n"
                    f"`$farm` : {tr(L, 'desc_farm')}\n"
                    f"`$nhay @user1 @user2 ...` : {tr(L, 'desc_nhay')}\n"
                    f"`$spam <count> <content> [delay]` : {tr(L, 'desc_spam')}\n"
                    f"`$dm <user_id> <content>` : {tr(L, 'desc_dm')}\n"
                    f"`$nuke [invite]` : {tr(L, 'desc_nuke')}\n"
                    f"`$purge [count]` : {tr(L, 'desc_purge')}\n"
                    f"`$afk [message]` : {tr(L, 'desc_afk')}\n"
                    f"`$snipe [@user] [count]` : {tr(L, 'desc_snipe')}\n"
                    f"`$log [@user] [count]` : {tr(L, 'desc_log')}\n"
                    f"`$guilds` : {tr(L, 'desc_guilds')}\n\n"
                    f"**{tr(L, 'info_header')}** :\n"
                    f"`$userinfo [@user|id]` : {tr(L, 'desc_userinfo')}\n"
                    f"`$guild` : {tr(L, 'desc_guild')}\n"
                    f"`$id [@user|#channel|@role]` : {tr(L, 'desc_id')}\n"
                    f"`$av [@user|id]` : {tr(L, 'desc_av')}\n"
                    f"`$banner [@user|id]` : {tr(L, 'desc_banner')}\n"
                    f"`$ping` : {tr(L, 'desc_ping')}\n\n"
                    f"**{tr(L, 'misc_header')}** :\n"
                    f"`$nick <name>` : {tr(L, 'desc_nick')}\n"
                    f"`$language <en|vi>` : {tr(L, 'desc_language')}\n\n"
                    f"<@{self.user_id}>"
                ))

            elif content.startswith("$language"):
                parts = content.split(maxsplit=1)
                arg = parts[1].strip().lower() if len(parts) > 1 else ""
                if not arg:
                    edit_message(self.token, channel_id, message_id, tr(L, "lang_usage"))
                elif arg in ("en", "vi"):
                    self.language = arg
                    edit_message(self.token, channel_id, message_id,
                                 tr(arg, "lang_set", lang=arg.upper()))
                else:
                    edit_message(self.token, channel_id, message_id, tr(L, "lang_invalid"))

            elif content == "$nhay" or content.startswith("$nhay "):
                delete_message(self.token, channel_id, message_id)
                if self.nhay_thread and self.nhay_thread.is_alive():
                    self.nhay_stop_event.set()
                    self.nhay_thread.join()
                    self.nhay_stop_event = None
                    self.nhay_thread = None
                    self.nhay_channel = None
                    self.nhay_targets = []
                    print(f"[+] [{self.account_name}] Stopped Nhay")
                    return
                mentions = re.findall(r"<@!?(\d+)>", content)
                if not mentions:
                    print(f"[!] [{self.account_name}] $nhay: no user mentioned")
                    return
                if not self.nhay_lines:
                    print(f"[!] [{self.account_name}] nhay.txt is empty or not found")
                    return
                self.nhay_stop_event = threading.Event()
                self.nhay_channel    = channel_id
                self.nhay_targets    = mentions
                self.nhay_thread = threading.Thread(
                    target=nhay_loop,
                    args=(self.token, channel_id, mentions, self.nhay_lines, self.nhay_stop_event),
                    daemon=True
                )
                self.nhay_thread.start()
                targets_str = " ".join([f"<@{uid}>" for uid in mentions])
                print(f"[+] [{self.account_name}] Started Nhay -> {targets_str}")

            elif content == "$farm":
                delete_message(self.token, channel_id, message_id)
                if self.farm_thread and self.farm_thread.is_alive():
                    self.farm_stop_event.set()
                    self.farm_thread.join()
                    self.farm_stop_event = None
                    self.farm_thread = None
                    self.farm_channel = None
                    print(f"[+] [{self.account_name}] Stopped Farm")
                else:
                    self.farm_stop_event = threading.Event()
                    self.farm_channel    = channel_id
                    self.farm_thread = threading.Thread(
                        target=farm_loop,
                        args=(self.token, channel_id, self.farm_stop_event, self.rpc_name),
                        daemon=True
                    )
                    self.farm_thread.start()
                    print(f"[+] [{self.account_name}] Started Farm")

            elif content.startswith("$spam "):
                delete_message(self.token, channel_id, message_id)
                rest = content[len("$spam "):].strip()
                m = re.match(r"^(\d+)\s+(.+?)(?:\s+(\d+(?:\.\d+)?\s*[smhd]?))?$", rest)
                if not m:
                    print(f"[!] {tr(L, 'err_spam_usage')}")
                    return
                try:
                    count = int(m.group(1))
                    count = max(1, min(count, 100))
                except ValueError:
                    print(f"[!] {tr(L, 'err_spam_count')}")
                    return
                spam_text = m.group(2).strip()
                delay_raw = m.group(3)
                if delay_raw:
                    parsed = parse_duration(delay_raw, default=None)
                    if parsed is None:
                        print(f"[!] {tr(L, 'err_spam_delay')}")
                        return
                    delay = parsed
                else:
                    delay = 0.7
                threading.Thread(
                    target=spam_loop,
                    args=(self.token, channel_id, spam_text, count, delay),
                    daemon=True
                ).start()
                print(f"[+] [{self.account_name}] Spam {count}x delay={delay}s")

            elif content.startswith("$dm "):
                delete_message(self.token, channel_id, message_id)
                parts = content.split(" ", 2)
                if len(parts) < 3:
                    print(f"[!] {tr(L, 'err_dm_usage')}")
                    return
                try:
                    target_uid = int(parts[1])
                except ValueError:
                    print(f"[!] {tr(L, 'err_dm_invalid')}")
                    return
                dm_text = parts[2]
                def _do_dm(tk, uid, txt):
                    dm_ch = create_dm(tk, uid)
                    if dm_ch:
                        send_message(tk, dm_ch, txt)
                        print(f"[+] DM sent to {uid}")
                    else:
                        print(f"[!] {tr(L, 'err_dm_fail', uid=uid)}")
                threading.Thread(target=_do_dm, args=(self.token, target_uid, dm_text), daemon=True).start()

            elif content == "$guilds":
                guilds = get_self_guilds(self.token)
                if not guilds:
                    edit_message(self.token, channel_id, message_id, tr(L, "err_no_guilds"))
                    return
                lines = [f"**{g.get('name', '?')}** — `{g.get('id')}`" for g in guilds]
                text = "\n".join(lines)
                chunks = [text[i:i+1900] for i in range(0, len(text), 1900)] or [text]
                edit_message(self.token, channel_id, message_id, chunks[0])
                for extra in chunks[1:]:
                    send_message(self.token, channel_id, extra)

            elif content.startswith("$av"):
                parts = content.split()
                target_uid = None
                if len(parts) >= 2:
                    m = re.search(r"(\d+)", parts[1])
                    if m:
                        target_uid = m.group(1)
                if not target_uid:
                    target_uid = self.user_id

                def _do_av(tk, uid, ch, mid, gid, cid, uc, lang):
                    info = resolve_user_info(tk, uid, guild_id=gid, channel_id=cid, user_cache=uc)
                    if not info:
                        edit_message(tk, ch, mid, tr(lang, "err_av_fail", uid=uid))
                        return
                    url = build_avatar_url(uid, info.get("avatar"))
                    edit_message(tk, ch, mid, url)

                threading.Thread(
                    target=_do_av,
                    args=(self.token, target_uid, channel_id, message_id,
                          guild_id, channel_id, self.user_cache, L),
                    daemon=True
                ).start()

            elif content.startswith("$banner"):
                parts = content.split()
                target_uid = None
                if len(parts) >= 2:
                    m = re.search(r"(\d+)", parts[1])
                    if m:
                        target_uid = m.group(1)
                if not target_uid:
                    target_uid = self.user_id

                def _do_banner(tk, uid, ch, mid, gid, cid, uc, lang):
                    info = resolve_user_info(tk, uid, guild_id=gid, channel_id=cid, user_cache=uc)
                    if not info:
                        edit_message(tk, ch, mid, tr(lang, "err_banner_fail", uid=uid))
                        return
                    url = build_banner_url(uid, info.get("banner"))
                    if not url:
                        edit_message(tk, ch, mid, tr(lang, "err_no_banner", uid=uid))
                        return
                    edit_message(tk, ch, mid, url)

                threading.Thread(
                    target=_do_banner,
                    args=(self.token, target_uid, channel_id, message_id,
                          guild_id, channel_id, self.user_cache, L),
                    daemon=True
                ).start()

            elif content.startswith("$nick "):
                delete_message(self.token, channel_id, message_id)
                if not guild_id:
                    print(f"[!] {tr(L, 'err_nick_dm')}")
                    return
                new_nick = content[len("$nick "):].strip()
                def _do_nick(tk, gid, nick):
                    ok = change_nick(tk, gid, nick)
                    print(f"[+] Nick change {'OK' if ok else 'FAIL'}")
                threading.Thread(target=_do_nick, args=(self.token, guild_id, new_nick), daemon=True).start()

            elif content == "$ping":
                ping_ms = self._get_ping_ms()
                if ping_ms < 0:
                    msg = tr(L, "ping_wait")
                else:
                    msg = tr(L, "ping_ok", ms=ping_ms)
                edit_message(self.token, channel_id, message_id, msg)

            elif content.startswith("$id"):
                parts = content.split(maxsplit=1)
                target = parts[1].strip() if len(parts) > 1 else ""

                result_id = None
                kind = ""

                if not target:
                    result_id = channel_id
                    kind = tr(L, "id_chan_current")
                else:
                    m_role = re.match(r"<@&(\d+)>", target)
                    m_user = re.match(r"<@!?(\d+)>", target)
                    m_chan = re.match(r"<#(\d+)>", target)
                    m_num  = re.match(r"^(\d+)$", target)

                    if m_role:
                        result_id = m_role.group(1); kind = tr(L, "id_kind_role")
                    elif m_chan:
                        result_id = m_chan.group(1); kind = tr(L, "id_kind_channel")
                    elif m_user:
                        result_id = m_user.group(1); kind = tr(L, "id_kind_user")
                    elif m_num:
                        result_id = m_num.group(1); kind = tr(L, "id_kind_id")

                if result_id:
                    edit_message(self.token, channel_id, message_id, f"`{kind}` → `{result_id}`")
                else:
                    edit_message(self.token, channel_id, message_id, tr(L, "err_id_unknown"))

            elif content.startswith("$userinfo"):
                parts = content.split(maxsplit=1)
                target_uid = self.user_id
                if len(parts) > 1:
                    m = re.search(r"(\d+)", parts[1])
                    if m:
                        target_uid = m.group(1)

                def _do_userinfo(tk, uid, ch, mid, gid, cid, uc, lang):
                    info = resolve_user_info(tk, uid, guild_id=gid, channel_id=cid, user_cache=uc)
                    if not info:
                        edit_message(tk, ch, mid, tr(lang, "err_userinfo_fail", uid=uid))
                        return

                    mem = info.pop("_member", None)

                    lines = [
                        tr(lang, "user_info_header"),
                        tr(lang, "u_username", v=info.get("username", "?")),
                        tr(lang, "u_display", v=info.get("global_name") or tr(lang, "u_none")),
                        tr(lang, "u_id", v=uid),
                        tr(lang, "u_bot", v=("✅" if info.get("bot") else "❌")),
                        tr(lang, "u_created", v=snowflake_to_str(uid)),
                    ]
                    av_url = build_avatar_url(uid, info.get("avatar"))
                    lines.append(tr(lang, "u_avatar", v=av_url))
                    banner_url = build_banner_url(uid, info.get("banner"))
                    if banner_url:
                        lines.append(tr(lang, "u_banner", v=banner_url))
                    if info.get("accent_color"):
                        lines.append(tr(lang, "u_accent", v=f"{info['accent_color']:06x}"))

                    if mem is None and gid:
                        mem = get_guild_member(tk, gid, uid)

                    if mem:
                        if mem.get("nick"):
                            lines.append(tr(lang, "u_nick", v=mem["nick"]))
                        if mem.get("joined_at"):
                            lines.append(tr(lang, "u_join", v=iso_to_str(mem["joined_at"])))
                        roles = mem.get("roles", [])
                        if roles:
                            role_str = " ".join([f"<@&{r}>" for r in roles[:20]])
                            lines.append(tr(lang, "u_roles", n=len(roles), v=role_str))

                    edit_message(tk, ch, mid, "\n".join(lines))

                threading.Thread(
                    target=_do_userinfo,
                    args=(self.token, target_uid, channel_id, message_id,
                          guild_id, channel_id, self.user_cache, L),
                    daemon=True
                ).start()

            elif content == "$guild":
                if not guild_id:
                    edit_message(self.token, channel_id, message_id, tr(L, "err_guild_dm"))
                    return

                def _do_guild(tk, gid, ch, mid, gw_self, lang):
                    info = get_guild_info(tk, gid)
                    if not info:
                        edit_message(tk, ch, mid, tr(lang, "err_guild_fail", gid=gid))
                        return

                    online_set = gw_self.guild_online.get(gid, set())

                    now_ts = time.time()
                    bot_ids = gw_self.guild_bot_ids.get(gid)
                    if bot_ids is None or (now_ts - gw_self.guild_bot_ts.get(gid, 0) > 600):
                        bot_ids = get_guild_bot_ids(tk, gid)
                        gw_self.guild_bot_ids[gid] = bot_ids
                        gw_self.guild_bot_ts[gid] = now_ts

                    online_humans = len(online_set - bot_ids)
                    approx_total = info.get("approximate_presence_count", "?")
                    if not online_set and isinstance(approx_total, int) and approx_total > 0:
                        online_line = tr(lang, "g_online_unknown")
                    else:
                        online_line = tr(lang, "g_online_count", v=online_humans)

                    lines = [
                        tr(lang, "guild_info"),
                        tr(lang, "g_name", v=info.get("name", "?")),
                        tr(lang, "g_id", v=gid),
                        tr(lang, "g_owner", v=info.get("owner_id", "?")),
                        tr(lang, "g_created", v=snowflake_to_str(gid)),
                        tr(lang, "g_members", v=info.get("approximate_member_count", "?")),
                        tr(lang, "g_online", v=info.get("approximate_presence_count", "?")),
                        online_line,
                        tr(lang, "g_boost", tier=info.get("premium_tier", 0),
                           n=info.get("premium_subscription_count", 0)),
                        tr(lang, "g_region", v=info.get("region", "?")),
                        tr(lang, "g_verif", v=info.get("verification_level", "?")),
                    ]
                    if info.get("icon"):
                        ext = "gif" if info["icon"].startswith("a_") else "png"
                        lines.append(tr(lang, "g_icon",
                                         v=f"https://cdn.discordapp.com/icons/{gid}/{info['icon']}.{ext}?size=1024"))
                    if info.get("banner"):
                        ext = "gif" if info["banner"].startswith("a_") else "png"
                        lines.append(tr(lang, "g_banner",
                                         v=f"https://cdn.discordapp.com/banners/{gid}/{info['banner']}.{ext}?size=1024"))
                    if info.get("vanity_url_code"):
                        lines.append(tr(lang, "g_vanity", v=info["vanity_url_code"]))
                    feats = info.get("features", [])
                    if feats:
                        lines.append(tr(lang, "g_features", v=", ".join(feats[:10])))

                    edit_message(tk, ch, mid, "\n".join(lines))

                threading.Thread(
                    target=_do_guild,
                    args=(self.token, guild_id, channel_id, message_id, self, L),
                    daemon=True
                ).start()

            elif content.startswith("$nuke "):
                delete_message(self.token, channel_id, message_id)
                if not guild_id:
                    print("Cannot nuke in DM")
                    return
                parts = content.split(" ", 1)
                if len(parts) < 2 or not parts[1].strip():
                    print("Cannot find invite")
                    return
                invite_input = parts[1].strip()
                invite_code  = (invite_input
                                .replace("https://discord.gg/", "")
                                .replace("https://discord.com/invite/", "")
                                .replace("discord.gg/", ""))
                if not resolve_invite(self.token, invite_code):
                    print(f"Cannot find invite {invite_input}")
                    return
                channels = get_guild_channels(self.token, guild_id)
                if channels is None:
                    print("Cannot access this server (missing permissions)")
                    return
                guild_name = get_guild_name(self.token, guild_id)
                print(f"[+] Nuking {guild_name} ({guild_id})")
                threading.Thread(
                    target=nuke_server,
                    args=(self.token, guild_id, f"https://discord.gg/{invite_code}", self.rpc_name),
                    daemon=True
                ).start()

            elif content.startswith("$purge"):
                delete_message(self.token, channel_id, message_id)
                parts = content.split(" ", 1)
                try:
                    count = int(parts[1].strip()) if len(parts) > 1 else 10
                    count = max(1, min(count, 200))
                except ValueError:
                    count = 10
                def _do_purge(ch, uid, n):
                    deleted = purge_messages(self.token, ch, uid, n)
                    print(f"[+] [{self.account_name}] Purged {deleted} messages")
                threading.Thread(target=_do_purge, args=(channel_id, self.user_id, count), daemon=True).start()

            elif content.startswith("$afk"):
                parts  = content.split(" ", 1)
                reason = parts[1].strip() if len(parts) > 1 else ""
                self.afk_enabled    = True
                self.afk_message    = reason
                self.afk_start_time = int(time.time())
                self.afk_pings      = []
                self.afk_auto_reply_msg_id = None
                preview = f" ({reason})" if reason else ""
                edit_message(self.token, channel_id, message_id,
                             tr(L, "afk_on", preview=preview))
                threading.Thread(
                    target=lambda: (time.sleep(3), delete_message(self.token, channel_id, message_id)),
                    daemon=True
                ).start()

            elif content.startswith("$snipe"):
                delete_message(self.token, channel_id, message_id)
                target_uid, count = parse_snipe_args(content, "$snipe")

                pool = self.snipe_cache.get(channel_id, [])
                if target_uid:
                    pool = [s for s in pool if str(s.get("author_id")) == str(target_uid)]

                picked = pool[:count]

                if not picked:
                    label = tr(L, "label_user") if target_uid else tr(L, "label_channel")
                    msg_id_sent = send_message(
                        self.token, channel_id,
                        tr(L, "snipe_none", label=label)
                    )
                else:
                    lines = [tr(L, "snipe_header", n=len(picked), total=len(pool))]
                    for i, s in enumerate(picked, 1):
                        ts  = s.get("timestamp", "")[:19].replace("T", " ") if s.get("timestamp") else "?"
                        lines.append(f"**{i}. {s.get('author', '?')}** `{ts}`:\n{s.get('content', '')}")
                    body = "\n\n".join(lines)
                    if len(body) > 1900:
                        body = body[:1897] + "..."
                    msg_id_sent = send_message(self.token, channel_id, body)

                if msg_id_sent:
                    threading.Thread(
                        target=lambda mid=msg_id_sent: (time.sleep(20), delete_message(self.token, channel_id, mid)),
                        daemon=True
                    ).start()

            elif content.startswith("$log"):
                delete_message(self.token, channel_id, message_id)
                target_uid, count = parse_snipe_args(content, "$log")
                if not target_uid:
                    count = max(count, 10)

                pool = self.edit_cache.get(channel_id, [])
                if target_uid:
                    pool = [e for e in pool if str(e.get("author_id")) == str(target_uid)]

                picked = pool[:count]

                if not picked:
                    label = tr(L, "label_user") if target_uid else tr(L, "label_channel")
                    msg_id_sent = send_message(
                        self.token, channel_id,
                        tr(L, "log_none", label=label)
                    )
                else:
                    lines = [tr(L, "log_header", n=len(picked), total=len(pool))]
                    for i, e in enumerate(picked, 1):
                        ts = ts_to_str(e.get("edited_at", 0))
                        before = e.get("before", "")
                        after  = e.get("after", "")
                        if len(before) > 400: before = before[:397] + "..."
                        if len(after) > 400:  after  = after[:397] + "..."
                        lines.append(
                            f"**{i}. {e.get('author', '?')}** `{ts}`:\n"
                            f"{tr(L, 'log_before', v=before)}\n"
                            f"{tr(L, 'log_after', v=after)}"
                        )
                    body = "\n\n".join(lines)
                    if len(body) > 1900:
                        body = body[:1897] + "..."
                    msg_id_sent = send_message(self.token, channel_id, body)

                if msg_id_sent:
                    threading.Thread(
                        target=lambda mid=msg_id_sent: (time.sleep(20), delete_message(self.token, channel_id, mid)),
                        daemon=True
                    ).start()

    def stop(self):
        if self.farm_stop_event:
            self.farm_stop_event.set()
        if self.nhay_stop_event:
            self.nhay_stop_event.set()
        self.running = False
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass


# ─── CUSTOM STATUS LOOP ──────────────────────────────────────────────────────

def custom_status_loop(token, custom_texts, delay=5, stop_event=None):
    if not custom_texts:
        return
    index = 0
    while True:
        if stop_event is not None and stop_event.is_set():
            return
        change_custom_status(token, custom_texts[index])
        index = (index + 1) % len(custom_texts)
        if stop_event is not None:
            if stop_event.wait(delay):
                return
        else:
            time.sleep(delay)


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    config = load_config()

    if websocket is None:
        print("Cannot find websocket-client (pip install websocket-client)")
        return

    tokens = load_tokens(config)
    if not tokens:
        print("[!] No token found in config.txt")
        return

    app_id           = config.get("application_id", "").strip()
    _env_st = os.environ.get("START_TIME", "").strip().strip('"').strip("'")
    _cfg_st = config.get("start_time", "now").strip().strip('"').strip("'")
    start_time_mode  = _env_st or _cfg_st or "now"
    start_time       = resolve_start_time(start_time_mode)
    _src = "Railway env" if _env_st else "config.txt"
    print(f"[*] start_time: {start_time_mode!r} (from {_src}) → {start_time} seconds")

    sc          = None
    asset_cache = {}
    if app_id:
        sc = load_stream_config()
        if sc is None or not sc.get("line1"):
            sc = None
            print("[!] stream.txt missing or line1 not set — stream disabled for all tokens")

    gateways    = []
    first_token = None
    custom_threads = []
    original_custom_map = {}
    custom_token_map = {}

    for idx, token in enumerate(tokens, start=1):
        account_name, user_id = check_token(token)
        if not account_name:
            print(f"[!] Token {idx} invalid — skipped")
            continue

        rpc_type      = int(get_per_token(config, "rpc_type", idx) or "2")
        rpc_name      = get_per_token(config, "rpc_name", idx) or "Nova"
        auto_voice    = get_per_token(config, "auto_join_voice", idx).lower() == "true"
        guild_id      = get_per_token(config, "guild_id", idx)
        voice_ch      = get_per_token(config, "voice_channel_id", idx)
        token_stream  = get_per_token(config, "stream",   idx).lower() == "true"
        token_fakelive= get_per_token(config, "fakelive", idx).lower() == "true"

        token_autochangestream = (
            get_per_token(config, "autochangestream", idx).lower() == "true"
        )
        token_rotate_delay = parse_duration_or_default(
            get_per_token(config, "stream_rotate_delay", idx) or "5",
            default=5
        )

        token_autocustom = (
            get_per_token(config, "autochangecustomstatus", idx).lower() == "true"
        )
        token_custom_delay = parse_duration_or_default(
            get_per_token(config, "customstatus_delay", idx) or "5",
            default=5
        )

        token_lang = (get_per_token(config, "language", idx) or "en").strip().lower()
        if token_lang not in ("en", "vi"):
            token_lang = "en"

        _sb_suffix    = "" if idx == 1 else f"_{idx}"
        _sb_val       = (os.environ.get(f"SELFBOT{_sb_suffix}", "").strip().lower()
                         or os.environ.get("SELFBOT", "true").strip().lower())
        token_commands= _sb_val not in ("false", "0", "off", "no")
        env_suffix = "" if idx == 1 else f"_{idx}"
        guild_id   = os.environ.get(f"GUILD_ID{env_suffix}", "").strip() or guild_id
        voice_ch   = os.environ.get(f"VOICE_CHANNEL_ID{env_suffix}", "").strip() or voice_ch

        cur_cache = {}
        if token_stream and sc:
            ti_str = "" if idx == 1 else f"_{idx}"
            image_url = sc.get(f"image_url{ti_str}", "") or sc.get("image_url", "")
            cur_cache = preload_assets(token, app_id, image_url)

        activity = None
        if token_stream and sc:
            activity = build_activity_from_slot(
                sc, 1, app_id, cur_cache, start_time, rpc_type, rpc_name, token_index=idx
            )

        gw = DiscordGateway(
            token=token,
            user_id=user_id,
            account_name=account_name,
            activity=activity,
            stream_config=sc if token_stream else None,
            app_id=app_id if token_stream else None,
            auto_change_stream=token_autochangestream if token_stream else False,
            asset_cache=cur_cache,
            start_time=start_time,
            auto_join_voice=auto_voice,
            guild_id=guild_id,
            voice_channel_id=voice_ch,
            fakelive=token_fakelive,
            rpc_type=rpc_type,
            rpc_name=rpc_name,
            token_index=idx,
            commands_enabled=token_commands,
            stream_rotate_delay=token_rotate_delay,
            language=token_lang,
        )
        gw.start()
        gateways.append(gw)

        print(f"[*] Connected | {account_name} | rpc_name={rpc_name} | rpc_type={rpc_type} | stream={token_stream} | autochangestream={token_autochangestream} | rotate_delay={token_rotate_delay}s | fakelive={token_fakelive} | lang={token_lang} | start_time={start_time}")
        if auto_voice:
            print(f"[*] [{account_name}] Auto join voice: {voice_ch}")
        if token_fakelive:
            print(f"[*] [{account_name}] Fake live enabled")
        if token_autocustom:
            print(f"[*] [{account_name}] Auto change custom status enabled | delay={token_custom_delay}s")

        if idx == 1:
            first_token = token

        if token_autocustom:
            custom_texts = load_custom_statuses()
            if len(custom_texts) <= 1:
                print(f"[!] customstatus.txt needs at least 2 lines — token {idx} custom status disabled")
            else:
                original_custom_map[token] = get_current_custom_status(token)
                custom_token_map[token]   = custom_texts
                stop_ev = threading.Event()
                th = threading.Thread(
                    target=custom_status_loop,
                    args=(token, custom_texts, token_custom_delay, stop_ev),
                    daemon=True
                )
                th.start()
                custom_threads.append((th, stop_ev))

    if not gateways:
        print("[!] No valid tokens. Exiting.")
        return

    def restore(sig, frame):
        for gw in gateways:
            gw.stop()
        for th, ev in custom_threads:
            ev.set()
        for tok, orig in original_custom_map.items():
            if orig is not None:
                restore_custom_status(tok, orig)
        sys.exit(0)

    signal.signal(signal.SIGINT, restore)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
