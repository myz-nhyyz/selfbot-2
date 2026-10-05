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
import urllib.parse
from datetime import datetime
import pytz

try:
    import websocket
except ImportError:
    websocket = None


# ─── TRANSLATIONS ────────────────────────────────────────────────────────────

TRANSLATIONS = {
    "en": {
        # AFK
        "afk_on":              "**AFK ON{preview}** — type any message to see received pings.",
        "afk_summary_header":  ":stopwatch: Welcome back, **{name}**! You were AFK for {duration} and received **{n}** ping(s).",
        "afk_pings_section":   "**Received pings**",
        "afk_reply":           "**{name}** is currently AFK (<t:{ts}:R>){reason}",
        # Snipe / Log
        "snipe_header":        "**Snipe ({picked}/{total}):**",
        "snipe_empty":         "No recently deleted messages from {label}.",
        "log_header":          "**Edit log ({picked}/{total}):**",
        "log_empty":           "No edits recorded from {label}.",
        "log_before":          "**Before:**",
        "log_after":           "**After:**",
        "label_user":          "that user",
        "label_channel":       "this channel",
        # Info
        "userinfo_fail":       "❌ Could not fetch user info for `{uid}`.\n→ User not in cache, not in a shared guild, and /users failed.",
        "av_fail":             "❌ Could not fetch avatar for `{uid}`",
        "guild_fail":          "❌ Could not fetch guild info for `{gid}`",
        "guild_only":          "❌ This command only works in a server.",
        "id_invalid":          "❌ Could not parse. Use `$id @user` / `$id #channel` / `$id @role` / `$id <id>`.",
        # Spam / DM / Purge
        "spam_usage":          "❌ Usage: `$spam <count> <content>`",
        "spam_invalid":        "❌ $spam: invalid count",
        "dm_usage":            "❌ Usage: `$dm <user_id> <content>`",
        "dm_invalid":          "❌ $dm: invalid user_id",
        "dm_fail":             "❌ Could not open DM with {uid}",
        "dm_sent":             "✅ DM sent to {uid}",
        "nick_dm_only":        "❌ $nick only works in a server",
        # Nhay / Farm
        "nhay_no_mention":     "❌ $nhay: no user mentioned",
        "nhay_no_lines":       "❌ nhay.txt is empty or not found",
        "nhay_started":        "✅ Nhay started → {targets}",
        "nhay_stopped":        "✅ Nhay stopped",
        "farm_started":        "✅ Farm started",
        "farm_stopped":        "✅ Farm stopped",
        # Nuke
        "nuke_no_dm":          "❌ Cannot nuke in DM",
        "nuke_no_invite":      "❌ No invite provided",
        "nuke_bad_invite":     "❌ Could not resolve invite {invite}",
        "nuke_no_perm":        "❌ Cannot access this server (missing permissions)",
        "nuke_starting":       "⚔️ Nuking {guild} ({gid})",
        "nuke_done":           "✅ Nuke completed",
        "nuke_deleted":        "🗑️ Deleted all channels",
        "nuke_created":        "📁 Created #{name}",
        "nuke_webhook":        "🪝 Webhook created in #{name}",
        # Menu
        "menu_title":          "## Super Self Bot - {name}",
        "menu_commands_header":"**🛠️ Commands** :",
        "menu_info_header":    "**📋 Info** :",
        "menu_other_header":   "**🔧 Other** :",
        # Language
        "lang_current":        "🌐 Current language: **{lang}**",
        "lang_changed":        "✅ Language changed to **{lang}**",
        "lang_invalid":        "❌ Unsupported `{code}`. Only: vi, en",
        # Purge
        "purge_started":       "🗑️ Deleting {n} messages...",
        "purge_done":          "✅ Deleted {n} messages",
        # Misc
        "ping_wait":           "🏓 Ping: waiting for first heartbeat (~40s).",
        "ping_ok":             "🏓 Pong! Gateway latency: **{ms} ms**",
        "nick_ok":             "✅ Nickname changed",
        "nick_fail":           "❌ Failed to change nickname",
    },
    "vi": {
        # AFK
        "afk_on":              "**AFK bật{preview}** — nhắn tin lại để xem ping đã nhận.",
        "afk_summary_header":  ":stopwatch: Chào mừng bạn trở lại, **{name}**! Bạn đã AFK trong {duration} và nhận được **{n}** ping.",
        "afk_pings_section":   "**Các ping đã nhận**",
        "afk_reply":           "Hiện tại **{name}** đang AFK (<t:{ts}:R>){reason}",
        # Snipe / Log
        "snipe_header":        "**Snipe ({picked}/{total}):**",
        "snipe_empty":         "Không có tin nhắn nào bị xóa gần đây của {label}.",
        "log_header":          "**Edit log ({picked}/{total}):**",
        "log_empty":           "Chưa ghi nhận chỉnh sửa tin nhắn nào của {label}.",
        "log_before":          "**Cũ:**",
        "log_after":           "**Mới:**",
        "label_user":          "user đó",
        "label_channel":       "kênh này",
        # Info
        "userinfo_fail":       "❌ Không lấy được info user `{uid}`.\n→ User không trong cache, không cùng guild, và /users fail.",
        "av_fail":             "❌ Không lấy được avatar của `{uid}`",
        "guild_fail":          "❌ Không lấy được info guild `{gid}`",
        "guild_only":          "❌ Lệnh này chỉ dùng trong server.",
        "id_invalid":          "❌ Không nhận diện được. Dùng `$id @user` / `$id #channel` / `$id @role` / `$id <id>`.",
        # Spam / DM / Purge
        "spam_usage":          "❌ Dùng: `$spam <số> <nội dung>`",
        "spam_invalid":        "❌ $spam: số không hợp lệ",
        "dm_usage":            "❌ Dùng: `$dm <user_id> <nội dung>`",
        "dm_invalid":          "❌ $dm: user_id không hợp lệ",
        "dm_fail":             "❌ Không mở được DM với {uid}",
        "dm_sent":             "✅ Đã gửi DM tới {uid}",
        "nick_dm_only":        "❌ $nick chỉ dùng trong server",
        # Nhay / Farm
        "nhay_no_mention":     "❌ $nhay: Chưa tag user nào",
        "nhay_no_lines":       "❌ nhay.txt trống hoặc không tồn tại",
        "nhay_started":        "✅ Đã bắt đầu Nhay → {targets}",
        "nhay_stopped":        "✅ Đã dừng Nhay",
        "farm_started":        "✅ Đã bắt đầu Farm",
        "farm_stopped":        "✅ Đã dừng Farm",
        # Nuke
        "nuke_no_dm":          "❌ Không thể nuke trong DM",
        "nuke_no_invite":      "❌ Chưa nhập invite",
        "nuke_bad_invite":     "❌ Không resolve được invite {invite}",
        "nuke_no_perm":        "❌ Không có quyền truy cập server (thiếu permission)",
        "nuke_starting":       "⚔️ Đang nuke {guild} ({gid})",
        "nuke_done":           "✅ Nuke hoàn tất",
        "nuke_deleted":        "🗑️ Đã xóa toàn bộ channel",
        "nuke_created":        "📁 Đã tạo #{name}",
        "nuke_webhook":        "🪝 Webhook đã tạo trong #{name}",
        # Menu
        "menu_title":          "## Super Self Bot - {name}",
        "menu_commands_header":"**🛠️ Lệnh** :",
        "menu_info_header":    "**📋 Info** :",
        "menu_other_header":   "**🔧 Khác** :",
        # Language
        "lang_current":        "🌐 Ngôn ngữ hiện tại: **{lang}**",
        "lang_changed":        "✅ Đã đổi ngôn ngữ sang **{lang}**",
        "lang_invalid":        "❌ Không hỗ trợ `{code}`. Chỉ hỗ trợ: vi, en",
        # Purge
        "purge_started":       "🗑️ Đang xóa {n} tin nhắn...",
        "purge_done":          "✅ Đã xóa {n} tin nhắn",
        # Misc
        "ping_wait":           "🏓 Ping: đang chờ heartbeat đầu tiên (đợi ~40s).",
        "ping_ok":             "🏓 Pong! Gateway latency: **{ms} ms**",
        "nick_ok":             "✅ Đã đổi nickname",
        "nick_fail":           "❌ Đổi nickname thất bại",
    },
}

SUPPORTED_LANGS = {"vi": "Tiếng Việt", "en": "English"}
DEFAULT_LANG = "en"


def t(key, lang=None, **kwargs):
    """Look up a translated string. Falls back to EN, then to the key itself."""
    lang = lang if lang in TRANSLATIONS else DEFAULT_LANG
    text = TRANSLATIONS.get(lang, {}).get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANG].get(key)
    if text is None:
        return key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


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


def resolve_start_time(mode):
    """Return UNIX milliseconds. Priority: env START_TIME > config start_time > now."""
    _env_st = os.environ.get("START_TIME", "").strip().strip('"').strip("'")
    if _env_st:
        try:
            v = int(_env_st)
            if v < 1_000_000_000_000:
                v = v * 1000
            return v
        except ValueError:
            print(f"[!] START_TIME={_env_st!r} is not a number — using config/default")

    mode = (mode or "now").strip().strip('"').strip("'").lower()
    now_ms = int(time.time() * 1000)

    if mode == "elapsed":
        return now_ms - 60_000
    if mode == "now" or not mode:
        return now_ms
    if mode == "today":
        tz = pytz.timezone("Asia/Ho_Chi_Minh")
        d = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        return int(d.timestamp() * 1000)
    if mode == "1y":
        return now_ms - 365 * 24 * 3600 * 1000
    if mode == "3y":
        return now_ms - 3 * 365 * 24 * 3600 * 1000
    if mode == "30d":
        return now_ms - 30 * 24 * 3600 * 1000
    if mode == "180d":
        return now_ms - 180 * 24 * 3600 * 1000
    try:
        v = int(mode)
        if v < 1_000_000_000_000:
            v = v * 1000
        return v
    except ValueError:
        return now_ms


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
    def extract(s):
        s = s.strip()
        ids = re.findall(r"\(([^)]+)\)", s)
        if ids:
            return [i.strip() for i in ids if i.strip()]
        return [i.strip() for i in s.split(",") if i.strip()]

    guilds   = extract(guild_str   or "")
    channels = extract(channel_str or "")
    return [{"guild_id": g, "channel_id": c} for g, c in zip(guilds, channels)]


def get_per_token(config, key, index):
    indexed = config.get(f"{key}_{index}", "")
    if indexed:
        return indexed
    if index == 1:
        return config.get(key, "")
    return config.get(key, "")


def load_tokens(config):
    tokens = []
    token = config.get("token", "").strip()
    if token:
        tokens.append(token)
    i = 2
    while True:
        t_ = config.get(f"token_{i}", "").strip()
        if not t_:
            break
        tokens.append(t_)
        i += 1
    return tokens


def parse_emoji_list(raw):
    if not raw:
        return []
    return [e.strip() for e in raw.split(",") if e.strip()]


def parse_react_target(raw):
    raw = (raw or "all").strip().lower()
    if raw == "all":
        return {"mode": "all"}
    if raw == "reply":
        return {"mode": "reply"}
    ids = re.findall(r"\d+", raw)
    if ids:
        return {"mode": "user", "ids": ids}
    return {"mode": "all"}


def load_nhay(token_index):
    """
    Parse nhay.txt by nhay_N= blocks.
    Fallback rotation:
      token 1: 1 → 2 → 3
      token 2: 2 → 3 → 1
      token 3: 3 → 1 → 2
    """
    blocks = {}
    current = None

    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n").rstrip("\r")
                stripped = line.strip()

                m = re.match(r"^nhay_(\d+)\s*=\s*(.*)$", stripped)
                if m:
                    current = int(m.group(1))
                    blocks.setdefault(current, [])
                    tail = m.group(2).strip()
                    if tail:
                        blocks[current].append(tail)
                    continue

                if current is not None and stripped:
                    blocks[current].append(stripped)
    except FileNotFoundError:
        print(f"[!] nhay.txt not found")
        return []

    if token_index == 1:
        order = [1, 2, 3]
    elif token_index == 2:
        order = [2, 3, 1]
    elif token_index == 3:
        order = [3, 1, 2]
    else:
        order = [1, 2, 3]

    for i in order:
        lines = blocks.get(i, [])
        if lines:
            print(f"[*] Token {token_index} loaded nhay block nhay_{i} ({len(lines)} lines)")
            return lines

    print(f"[!] Token {token_index}: no nhay block found in nhay.txt")
    return []


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


def add_reaction(token, channel_id, message_id, emoji):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    emoji_enc = urllib.parse.quote(emoji)
    try:
        r = requests.put(
            f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
            f"/reactions/{emoji_enc}/@me",
            headers=headers, timeout=10
        )
        if r.status_code == 429:
            retry = r.json().get("retry_after", 1)
            time.sleep(retry)
            requests.put(
                f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
                f"/reactions/{emoji_enc}/@me",
                headers=headers, timeout=10
            )
        return r.status_code in (200, 204)
    except requests.RequestException:
        return False


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
        print(f"[!] /users/{user_id} -> HTTP {r.status_code}")
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
            print(f"[!] /guilds/{guild_id}/members/{user_id} -> HTTP {r.status_code}")
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
                print(f"[!] /guilds/{guild_id}/members -> HTTP {r.status_code}")
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

def nuke_server(token, guild_id, ad_invite, rpc_name, lang="en"):
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
        print(t("nuke_deleted", lang))

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
                print(t("nuke_created", lang, name=name))
                wh = create_webhook(token, ch["id"], "alex_raid")
                if wh:
                    print(t("nuke_webhook", lang, name=name))
                    tt = threading.Thread(target=spam_webhook, args=(wh, spam_content), daemon=True)
                    tt.start()
                    spam_threads.append(tt)

    dt = threading.Thread(target=delete_all_channels, daemon=True)
    dt.start()
    workers = [threading.Thread(target=create_and_spam, daemon=True) for _ in range(3)]
    for w in workers:
        w.start()
    dt.join()
    for w in workers:
        w.join()
    for tt in spam_threads:
        tt.join()
    print(t("nuke_done", lang))


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

    activity = {
        "type": rpc_type,
        "name": rpc_name,
        "timestamps": {"start": start_time},
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
        stop_event.wait(random.uniform(1, 3))


def spam_loop(token, channel_id, text, count):
    for _ in range(count):
        send_message(token, channel_id, text)
        time.sleep(0.7)


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
            return f"{m} minute(s) and {s} second(s)"
        if m:
            return f"{m} minute(s)"
        return f"{s} second(s)"


def build_afk_summary(display_name, duration, pings, lang="en"):
    dur_text = _format_duration(duration, lang)

    lines = [
        t("afk_summary_header", lang, name=display_name, duration=dur_text, n=len(pings)),
    ]

    if pings:
        lines.append("")
        lines.append(t("afk_pings_section", lang))
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
                 commands_enabled=True, lang="en",
                 auto_react=False, auto_react_emojis=None, auto_react_target=None):
        self.token            = token
        self.user_id          = user_id
        self.account_name     = account_name
        self.activity         = activity
        self.stream_config    = stream_config
        self.app_id           = app_id
        self.auto_change_stream = auto_change_stream
        self.asset_cache      = asset_cache or {}
        self.start_time       = start_time if start_time else int(time.time() * 1000)
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
        self.lang             = lang if lang in SUPPORTED_LANGS else DEFAULT_LANG
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
        self.nhay_lines      = load_nhay(token_index)
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
        # AFK cooldown
        self.afk_user_cd     = {}
        self.afk_channel_cd  = {}
        self.afk_global_cd   = 0.0
        self.afk_pending     = {}
        self.afk_lock        = threading.Lock()
        # Ping
        self.last_hb_sent    = 0.0
        self.last_hb_ack     = 0.0
        # Online member tracking
        self.guild_online    = {}
        self.guild_bot_ids   = {}
        self.guild_bot_ts    = {}
        # User cache
        self.user_cache      = {}
        # Auto react
        self.auto_react        = auto_react
        self.auto_react_emojis = auto_react_emojis or ["👀", "🔥"]
        self.auto_react_target = auto_react_target or {"mode": "all"}

    # ─── SHORTCUT ─────────────────────────────────────────────────────────
    def t(self, key, **kwargs):
        return t(key, self.lang, **kwargs)

    # ─── LIFECYCLE ────────────────────────────────────────────────────────
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
            time.sleep(5)
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

    # ─── VOICE ────────────────────────────────────────────────────────────
    def _auto_join_voice(self):
        if not self.auto_join_voice:
            return

        def _join_all_sequential():
            for v in self.voice_channels:
                if not self.running:
                    return
                gid = v["guild_id"]
                cid = v["channel_id"]
                try:
                    time.sleep(2)
                    if not self.ws or not self.running:
                        return
                    self.ws.send(json.dumps({
                        "op": 4,
                        "d": {
                            "guild_id": gid,
                            "channel_id": cid,
                            "self_mute": True,
                            "self_deaf": True,
                        }
                    }))
                    if v not in self.current_voice_list:
                        self.current_voice_list.append(v)
                    print(f"[+] [{self.account_name}] Auto joined voice: {cid} ({gid})")
                    if self.fakelive:
                        time.sleep(3)
                        self.start_fake_live(gid, cid)
                        time.sleep(3)
                except Exception as e:
                    print(f"[!] [{self.account_name}] Auto join failed {cid}: {e}")

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

    # ─── AFK ──────────────────────────────────────────────────────────────
    def _afk_do_reply(self, uid, channel_id, jump_url, display_name):
        with self.afk_lock:
            now = time.time()
            if not self.afk_enabled:
                self.afk_pending.pop(uid, None)
                return
            if self.afk_user_cd.get(uid, 0) > now:
                self.afk_pending.pop(uid, None)
                return

        reason_part = f": **{self.afk_message}**" if self.afk_message else ""
        reply_text = self.t("afk_reply",
                            name=self.account_name,
                            ts=self.afk_start_time,
                            reason=reason_part)

        msg_id = send_message(self.token, channel_id, reply_text)

        with self.afk_lock:
            now = time.time()
            self.afk_auto_reply_msg_id = msg_id
            self.afk_user_cd[uid]       = now + random.uniform(1, 5)
            self.afk_channel_cd[channel_id] = now + random.uniform(1, 5)
            self.afk_global_cd          = now + random.uniform(1, 5)
            self.afk_pending.pop(uid, None)

    def _afk_handle_ping(self, uid, channel_id, jump_url, display_name):
        with self.afk_lock:
            now = time.time()

            if self.afk_user_cd.get(uid, 0) > now:
                return

            if uid in self.afk_pending:
                try:
                    self.afk_pending[uid].cancel()
                except Exception:
                    pass
                self.afk_pending.pop(uid, None)

            delay = random.uniform(1, 5)
            timer = threading.Timer(
                delay,
                self._afk_do_reply,
                args=(uid, channel_id, jump_url, display_name)
            )
            timer.daemon = True
            self.afk_pending[uid] = timer
            timer.start()

    def _afk_cancel_all_timers(self):
        with self.afk_lock:
            for t in self.afk_pending.values():
                try:
                    t.cancel()
                except Exception:
                    pass
            self.afk_pending.clear()

    # ─── EVENT HANDLER ────────────────────────────────────────────────────
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

            # ─── AUTO REACT ─────────────────────────────────────────────
            if (self.auto_react
                    and not msg_author.get("bot", False)
                    and msg_channel
                    and msg_id
                    and self.auto_react_emojis):
                should_react = False
                target = self.auto_react_target or {"mode": "all"}
                sender_id = msg_author.get("id", "")
                mode = target.get("mode", "all")

                if mode == "all":
                    should_react = True
                elif mode == "user":
                    if str(sender_id) in [str(x) for x in target.get("ids", [])]:
                        should_react = True
                elif mode == "reply":
                    ref = d.get("referenced_message") or {}
                    ref_author_id = (ref.get("author") or {}).get("id")
                    if str(ref_author_id) == str(self.user_id):
                        should_react = True

                if should_react:
                    def _react_all(tk, ch, mid, emojis):
                        for e in emojis:
                            add_reaction(tk, ch, mid, e)
                            time.sleep(0.4)
                    threading.Thread(
                        target=_react_all,
                        args=(self.token, msg_channel, msg_id, list(self.auto_react_emojis)),
                        daemon=True
                    ).start()

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
                        self._afk_handle_ping(
                            sender_id, msg_channel, jump_url, display_name
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

                with self.afk_lock:
                    self.afk_user_cd.clear()
                    self.afk_channel_cd.clear()
                    self.afk_global_cd = 0.0
                self._afk_cancel_all_timers()

                summary = build_afk_summary(display, duration, pings_copy, self.lang)
                send_message(self.token, channel_id, summary)

            if not self.commands_enabled:
                return

            # ─── COMMANDS ────────────────────────────────────────────────

            if content == "$menu":
                menu = (
                    f"{self.t('menu_title', name=self.rpc_name)}\n\n"
                    f"{self.t('menu_commands_header')}\n"
                    f"`$farm` : Spam messages for exp bots\n"
                    f"`$nhay @user1 @user2 ...` : Spam tag multiple users (toggle)\n"
                    f"`$spam <count> <content>` : Spam the content N times\n"
                    f"`$dm <user_id> <content>` : Send a DM\n"
                    f"`$nuke <invite>` : Nuke the server\n"
                    f"`$purge [count]` : Delete your own messages (default 10)\n"
                    f"`$afk [message]` : Toggle AFK — track pings on return\n"
                    f"`$snipe [@user] [count]` : View deleted messages\n"
                    f"`$log [@user] [count]` : View message edit history\n"
                    f"`$guilds` : List servers you are in\n\n"
                    f"{self.t('menu_info_header')}\n"
                    f"`$userinfo [@user|id]` : User info — DM OK\n"
                    f"`$guild` : Current guild info\n"
                    f"`$id [@user|#channel|@role]` : Resolve ID\n"
                    f"`$av [@user|id]` : Avatar URL — DM OK\n"
                    f"`$ping` : Gateway latency\n\n"
                    f"{self.t('menu_other_header')}\n"
                    f"`$nick <name>` : Change nickname in this server\n"
                    f"`$language <en|vi>` : Change bot language\n\n"
                    f"<@{self.user_id}>"
                )
                edit_message(self.token, channel_id, message_id, menu)

            elif content.startswith("$language"):
                parts = content.split(maxsplit=1)
                if len(parts) < 2 or not parts[1].strip():
                    msg = self.t("lang_current", lang=SUPPORTED_LANGS.get(self.lang, self.lang))
                else:
                    code = parts[1].strip().lower()
                    if code in SUPPORTED_LANGS:
                        self.lang = code
                        msg = self.t("lang_changed", lang=SUPPORTED_LANGS[code])
                    else:
                        msg = self.t("lang_invalid", code=code)
                edit_message(self.token, channel_id, message_id, msg)

            elif content == "$nhay" or content.startswith("$nhay "):
                delete_message(self.token, channel_id, message_id)
                if self.nhay_thread and self.nhay_thread.is_alive():
                    self.nhay_stop_event.set()
                    self.nhay_thread.join()
                    self.nhay_stop_event = None
                    self.nhay_thread = None
                    self.nhay_channel = None
                    self.nhay_targets = []
                    send_message(self.token, channel_id, self.t("nhay_stopped"))
                    return
                mentions = re.findall(r"<@!?(\d+)>", content)
                if not mentions:
                    send_message(self.token, channel_id, self.t("nhay_no_mention"))
                    return
                if not self.nhay_lines:
                    send_message(self.token, channel_id, self.t("nhay_no_lines"))
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
                send_message(self.token, channel_id, self.t("nhay_started", targets=targets_str))

            elif content == "$farm":
                delete_message(self.token, channel_id, message_id)
                if self.farm_thread and self.farm_thread.is_alive():
                    self.farm_stop_event.set()
                    self.farm_thread.join()
                    self.farm_stop_event = None
                    self.farm_thread = None
                    self.farm_channel = None
                    send_message(self.token, channel_id, self.t("farm_stopped"))
                else:
                    self.farm_stop_event = threading.Event()
                    self.farm_channel    = channel_id
                    self.farm_thread = threading.Thread(
                        target=farm_loop,
                        args=(self.token, channel_id, self.farm_stop_event, self.rpc_name),
                        daemon=True
                    )
                    self.farm_thread.start()
                    send_message(self.token, channel_id, self.t("farm_started"))

            elif content.startswith("$spam "):
                delete_message(self.token, channel_id, message_id)
                parts = content.split(" ", 2)
                if len(parts) < 3:
                    send_message(self.token, channel_id, self.t("spam_usage"))
                    return
                try:
                    count = int(parts[1])
                    count = max(1, min(count, 100))
                except ValueError:
                    send_message(self.token, channel_id, self.t("spam_invalid"))
                    return
                spam_text = parts[2]
                threading.Thread(
                    target=spam_loop,
                    args=(self.token, channel_id, spam_text, count),
                    daemon=True
                ).start()

            elif content.startswith("$dm "):
                delete_message(self.token, channel_id, message_id)
                parts = content.split(" ", 2)
                if len(parts) < 3:
                    send_message(self.token, channel_id, self.t("dm_usage"))
                    return
                try:
                    target_uid = int(parts[1])
                except ValueError:
                    send_message(self.token, channel_id, self.t("dm_invalid"))
                    return
                dm_text = parts[2]
                def _do_dm(tk, uid, txt, ch, lang):
                    dm_ch = create_dm(tk, uid)
                    if dm_ch:
                        send_message(tk, dm_ch, txt)
                        send_message(tk, ch, t("dm_sent", lang, uid=uid))
                    else:
                        send_message(tk, ch, t("dm_fail", lang, uid=uid))
                threading.Thread(
                    target=_do_dm,
                    args=(self.token, target_uid, dm_text, channel_id, self.lang),
                    daemon=True
                ).start()

            elif content == "$guilds":
                guilds = get_self_guilds(self.token)
                if not guilds:
                    edit_message(self.token, channel_id, message_id, "❌")
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
                        edit_message(tk, ch, mid, t("av_fail", lang, uid=uid))
                        return
                    url = build_avatar_url(uid, info.get("avatar"))
                    edit_message(tk, ch, mid, url)

                threading.Thread(
                    target=_do_av,
                    args=(self.token, target_uid, channel_id, message_id,
                          guild_id, channel_id, self.user_cache, self.lang),
                    daemon=True
                ).start()

            elif content.startswith("$nick "):
                delete_message(self.token, channel_id, message_id)
                if not guild_id:
                    send_message(self.token, channel_id, self.t("nick_dm_only"))
                    return
                new_nick = content[len("$nick "):].strip()
                def _do_nick(tk, gid, nick, ch, lang):
                    ok = change_nick(tk, gid, nick)
                    send_message(tk, ch, t("nick_ok", lang) if ok else t("nick_fail", lang))
                threading.Thread(
                    target=_do_nick,
                    args=(self.token, guild_id, new_nick, channel_id, self.lang),
                    daemon=True
                ).start()

            elif content == "$ping":
                ping_ms = self._get_ping_ms()
                if ping_ms < 0:
                    msg = self.t("ping_wait")
                else:
                    msg = self.t("ping_ok", ms=ping_ms)
                edit_message(self.token, channel_id, message_id, msg)

            elif content.startswith("$id"):
                parts = content.split(maxsplit=1)
                target = parts[1].strip() if len(parts) > 1 else ""

                result_id = None
                kind = ""

                if not target:
                    result_id = channel_id
                    kind = "channel"
                else:
                    m_role = re.match(r"<@&(\d+)>", target)
                    m_user = re.match(r"<@!?(\d+)>", target)
                    m_chan = re.match(r"<#(\d+)>", target)
                    m_num  = re.match(r"^(\d+)$", target)

                    if m_role:
                        result_id = m_role.group(1); kind = "role"
                    elif m_chan:
                        result_id = m_chan.group(1); kind = "channel"
                    elif m_user:
                        result_id = m_user.group(1); kind = "user"
                    elif m_num:
                        result_id = m_num.group(1); kind = "id"

                if result_id:
                    edit_message(self.token, channel_id, message_id, f"`{kind}` → `{result_id}`")
                else:
                    edit_message(self.token, channel_id, message_id, self.t("id_invalid"))

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
                        edit_message(tk, ch, mid, t("userinfo_fail", lang, uid=uid))
                        return

                    mem = info.pop("_member", None)

                    lines = [
                        f"**User Info**",
                        f"**Username:** `{info.get('username', '?')}`",
                        f"**Display name:** {info.get('global_name') or '*(none)*'}",
                        f"**ID:** `{uid}`",
                        f"**Bot:** {'✅' if info.get('bot') else '❌'}",
                        f"**Created:** {snowflake_to_str(uid)}",
                    ]
                    av_url = build_avatar_url(uid, info.get("avatar"))
                    lines.append(f"**Avatar:** {av_url}")
                    if info.get("banner"):
                        ext = "gif" if info["banner"].startswith("a_") else "png"
                        lines.append(f"**Banner:** https://cdn.discordapp.com/banners/{uid}/{info['banner']}.{ext}?size=1024")
                    if info.get("accent_color"):
                        lines.append(f"**Accent color:** `#{info['accent_color']:06x}`")

                    if mem is None and gid:
                        mem = get_guild_member(tk, gid, uid)

                    if mem:
                        if mem.get("nick"):
                            lines.append(f"**Nickname:** {mem['nick']}")
                        if mem.get("joined_at"):
                            lines.append(f"**Joined:** {iso_to_str(mem['joined_at'])}")
                        roles = mem.get("roles", [])
                        if roles:
                            role_str = " ".join([f"<@&{r}>" for r in roles[:20]])
                            lines.append(f"**Roles ({len(roles)}):** {role_str}")

                    edit_message(tk, ch, mid, "\n".join(lines))

                threading.Thread(
                    target=_do_userinfo,
                    args=(self.token, target_uid, channel_id, message_id,
                          guild_id, channel_id, self.user_cache, self.lang),
                    daemon=True
                ).start()

            elif content == "$guild":
                if not guild_id:
                    edit_message(self.token, channel_id, message_id, self.t("guild_only"))
                    return

                def _do_guild(tk, gid, ch, mid, gw_self, lang):
                    info = get_guild_info(tk, gid)
                    if not info:
                        edit_message(tk, ch, mid, t("guild_fail", lang, gid=gid))
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
                        online_line = f"**Online member:** `?` *(no presence data - large guild)*"
                    else:
                        online_line = f"**Online member:** {online_humans}"

                    lines = [
                        f"**Guild Info**",
                        f"**Name:** {info.get('name', '?')}",
                        f"**ID:** `{gid}`",
                        f"**Owner ID:** `{info.get('owner_id', '?')}`",
                        f"**Created:** {snowflake_to_str(gid)}",
                        f"**Members:** {info.get('approximate_member_count', '?')}",
                        f"**Online:** {info.get('approximate_presence_count', '?')}",
                        online_line,
                        f"**Boost tier:** {info.get('premium_tier', 0)} ({info.get('premium_subscription_count', 0)} boost)",
                        f"**Region:** {info.get('region', '?')}",
                        f"**Verification level:** {info.get('verification_level', '?')}",
                    ]
                    if info.get("icon"):
                        ext = "gif" if info["icon"].startswith("a_") else "png"
                        lines.append(f"**Icon:** https://cdn.discordapp.com/icons/{gid}/{info['icon']}.{ext}?size=1024")
                    if info.get("banner"):
                        ext = "gif" if info["banner"].startswith("a_") else "png"
                        lines.append(f"**Banner:** https://cdn.discordapp.com/banners/{gid}/{info['banner']}.{ext}?size=1024")
                    if info.get("vanity_url_code"):
                        lines.append(f"**Vanity:** discord.gg/{info['vanity_url_code']}")
                    feats = info.get("features", [])
                    if feats:
                        lines.append(f"**Features:** {', '.join(feats[:10])}")

                    edit_message(tk, ch, mid, "\n".join(lines))

                threading.Thread(
                    target=_do_guild,
                    args=(self.token, guild_id, channel_id, message_id, self, self.lang),
                    daemon=True
                ).start()

            elif content.startswith("$nuke "):
                delete_message(self.token, channel_id, message_id)
                if not guild_id:
                    send_message(self.token, channel_id, self.t("nuke_no_dm"))
                    return
                parts = content.split(" ", 1)
                if len(parts) < 2 or not parts[1].strip():
                    send_message(self.token, channel_id, self.t("nuke_no_invite"))
                    return
                invite_input = parts[1].strip()
                invite_code  = (invite_input
                                .replace("https://discord.gg/", "")
                                .replace("https://discord.com/invite/", "")
                                .replace("discord.gg/", ""))
                if not resolve_invite(self.token, invite_code):
                    send_message(self.token, channel_id, self.t("nuke_bad_invite", invite=invite_input))
                    return
                channels = get_guild_channels(self.token, guild_id)
                if channels is None:
                    send_message(self.token, channel_id, self.t("nuke_no_perm"))
                    return
                guild_name = get_guild_name(self.token, guild_id)
                send_message(self.token, channel_id, self.t("nuke_starting", guild=guild_name, gid=guild_id))
                threading.Thread(
                    target=nuke_server,
                    args=(self.token, guild_id, f"https://discord.gg/{invite_code}", self.rpc_name, self.lang),
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
                def _do_purge(ch, uid, n, tk, lang):
                    send_message(tk, ch, t("purge_started", lang, n=n))
                    deleted = purge_messages(tk, ch, uid, n)
                    send_message(tk, ch, t("purge_done", lang, n=deleted))
                threading.Thread(
                    target=_do_purge,
                    args=(channel_id, self.user_id, count, self.token, self.lang),
                    daemon=True
                ).start()

            elif content.startswith("$afk"):
                parts  = content.split(" ", 1)
                reason = parts[1].strip() if len(parts) > 1 else ""
                self.afk_enabled    = True
                self.afk_message    = reason
                self.afk_start_time = int(time.time())
                self.afk_pings      = []
                self.afk_auto_reply_msg_id = None
                with self.afk_lock:
                    self.afk_user_cd.clear()
                    self.afk_channel_cd.clear()
                    self.afk_global_cd = 0.0
                preview = f" ({reason})" if reason else ""
                edit_message(self.token, channel_id, message_id, self.t("afk_on", preview=preview))
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
                    label = self.t("label_user") if target_uid else self.t("label_channel")
                    msg_id_sent = send_message(
                        self.token, channel_id,
                        self.t("snipe_empty", label=label)
                    )
                else:
                    lines = [self.t("snipe_header", picked=len(picked), total=len(pool))]
                    for i, s in enumerate(picked, 1):
                        ts  = s.get("timestamp", "")[:19].replace("T", " ") if s.get("timestamp") else "?"
                        lines.append(f"**{i}. {s.get('author', '?')}** @ `{ts}`:\n{s.get('content', '')}")
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
                    label = self.t("label_user") if target_uid else self.t("label_channel")
                    msg_id_sent = send_message(
                        self.token, channel_id,
                        self.t("log_empty", label=label)
                    )
                else:
                    lines = [self.t("log_header", picked=len(picked), total=len(pool))]
                    for i, e in enumerate(picked, 1):
                        ts = ts_to_str(e.get("edited_at", 0))
                        before = e.get("before", "")
                        after  = e.get("after", "")
                        if len(before) > 400: before = before[:397] + "..."
                        if len(after) > 400:  after  = after[:397] + "..."
                        lines.append(
                            f"**{i}. {e.get('author', '?')}** @ `{ts}`:\n"
                            f"{self.t('log_before')} {before}\n"
                            f"{self.t('log_after')} {after}"
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
        self._afk_cancel_all_timers()
        self.running = False
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass


# ─── CUSTOM STATUS LOOP ──────────────────────────────────────────────────────

def custom_status_loop(token, custom_texts):
    index = 0
    while True:
        try:
            change_custom_status(token, custom_texts[index])
            index = (index + 1) % len(custom_texts)
        except Exception:
            pass
        time.sleep(1)


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
    auto_custom      = config.get("autochangecustomstatus", "False").lower() == "true"
    auto_change_stream = config.get("autochangestream", "False").lower() == "true"
    start_time       = resolve_start_time(config.get("start_time", "now"))
    print(f"[*] start_time -> {start_time} ms")

    sc = None
    if app_id:
        sc = load_stream_config()
        if sc is None or not sc.get("line1"):
            sc = None
            print("[!] stream.txt missing or line1 not set - stream disabled for all tokens")

    gateways    = []
    first_token = None

    for idx, token in enumerate(tokens, start=1):
        account_name, user_id = check_token(token)
        if not account_name:
            print(f"[!] Token {idx} invalid - skipped")
            continue

        rpc_type      = int(get_per_token(config, "rpc_type", idx) or "2")
        rpc_name      = get_per_token(config, "rpc_name", idx) or "Nova"
        auto_voice    = get_per_token(config, "auto_join_voice", idx).lower() == "true"
        guild_id      = get_per_token(config, "guild_id", idx)
        voice_ch      = get_per_token(config, "voice_channel_id", idx)
        token_stream  = get_per_token(config, "stream",   idx).lower() == "true"
        token_fakelive= get_per_token(config, "fakelive", idx).lower() == "true"

        _sb_cfg = get_per_token(config, "SELFBOT", idx).strip().lower()
        _sb_env = os.environ.get(f"SELFBOT_{idx}" if idx > 1 else "SELFBOT", "").strip().lower()
        _sb_val = _sb_cfg or _sb_env or "true"
        token_commands = _sb_val not in ("false", "0", "off", "no")

        # Language per token
        lang_raw = get_per_token(config, "language", idx).strip().lower()
        lang = lang_raw if lang_raw in SUPPORTED_LANGS else DEFAULT_LANG

        ar_enabled = get_per_token(config, "auto_react", idx).strip().lower() == "true"
        ar_emojis_raw = get_per_token(config, "auto_react_emojis", idx).strip()
        ar_emojis = parse_emoji_list(ar_emojis_raw) or ["👀", "🔥"]
        ar_target_raw = get_per_token(config, "auto_react_target", idx).strip()
        ar_target = parse_react_target(ar_target_raw) if ar_target_raw else {"mode": "all"}

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
            auto_change_stream=auto_change_stream if token_stream else False,
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
            lang=lang,
            auto_react=ar_enabled,
            auto_react_emojis=ar_emojis,
            auto_react_target=ar_target,
        )
        gw.start()
        gateways.append(gw)

        print(f"[*] Connected | {account_name} | rpc_name={rpc_name} | rpc_type={rpc_type} | stream={token_stream} | fakelive={token_fakelive} | commands={token_commands} | lang={lang}")
        if auto_voice:
            print(f"[*] [{account_name}] Auto join voice: {voice_ch}")
        if token_fakelive:
            print(f"[*] [{account_name}] Fake live enabled")
        if ar_enabled:
            tgt = ar_target.get("mode", "all")
            if tgt == "user":
                tgt += " " + ",".join(ar_target.get("ids", []))
            print(f"[*] [{account_name}] Auto react: {ar_emojis} -> {tgt}")

        if idx == 1:
            first_token = token

    if not gateways:
        print("[!] No valid tokens. Exiting.")
        return

    original_custom = None
    if auto_custom and first_token:
        custom_texts = load_custom_statuses()
        if len(custom_texts) <= 1:
            print("[!] customstatus.txt needs at least 2 lines - disabled")
            auto_custom = False
        else:
            original_custom = get_current_custom_status(first_token)

    def restore(sig, frame):
        for gw in gateways:
            gw.stop()
        if auto_custom and first_token and original_custom is not None:
            restore_custom_status(first_token, original_custom)
        sys.exit(0)

    signal.signal(signal.SIGINT, restore)

    if auto_custom and first_token:
        custom_status_loop(first_token, custom_texts)
    else:
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()