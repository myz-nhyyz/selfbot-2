# Nova Selfbot

A multi-token Discord selfbot with rich presence, voice auto-join, fake live, auto react, AFK tracker, snipe/edit log, and a full command suite. Supports per-token configuration for everything — RPC, custom status, voice, auto react, and command toggles.

> ⚠️ **Disclaimer** — Selfbots violate Discord's Terms of Service. Use at your own risk. This repo is for personal and educational use only.

---

## Table of Contents

- Features
- Requirements
- Installation
- File Structure
- Configuration
  - config.txt
  - stream.txt
  - nhay.txt
  - customstatus.txt
- Commands
- AFK Behaviour
- Auto React
- Delay Format
- Running
- Environment Variables
- Troubleshooting
- License

---

## Features

- **Multi-token** — run 1..N selfbot accounts from a single process
- **Rich Presence (RPC)** — Playing / Streaming / Listening / Watching / Competing, with images and buttons
- **Auto change stream** — rotate RPC content between slot A and slot B per token
- **Auto change custom status** — cycle custom statuses from customstatus.txt per token, with per-token delay
- **Voice auto-join** — join one or more voice channels and auto-rejoin when disconnected
- **Fake live** — appear as streaming inside a voice channel (with auto_join_voice)
- **AFK tracker** — track pings while AFK, reply with a random 1..5s delay, per-user cooldown, then summarise on return
- **Auto react** — react to messages automatically, per token, with 3 target modes
- **Snipe / Edit log** — view deleted messages and edit history, filter by user
- **Selfbot commands**:
  - `$menu`, `$farm`, `$nhay`, `$spam`, `$dm`, `$nuke`, `$purge`, `$afk`
  - `$snipe`, `$log`, `$guilds`, `$userinfo`, `$guild`, `$id`, `$av`
  - `$nick`, `$ping`

---

## Requirements

- Python 3.9+
- `requests`, `websocket-client`, `pytz`

```
pip install -r requirements.txt
```

---

## Installation

```
git clone https://github.com/yourname/yourrepo.git
cd yourrepo
pip install -r requirements.txt
# edit config.txt, stream.txt, nhay.txt, customstatus.txt
python main.py
```

---

## File Structure

```
.
├── main.py             # entry point
├── config.txt          # tokens, toggles, per-token options
├── stream.txt          # RPC content (slot A + slot B per token)
├── nhay.txt            # lines used by $nhay, per-token blocks
├── customstatus.txt    # rotating custom statuses
├── requirements.txt    # Python dependencies
├── LICENSE
└── README.md
```

---

## Configuration

### config.txt

Tokens, toggles, and per-token options. Any key suffixed with `_N` applies to token N. If `_N` is missing, the bot falls back to the base key (token 1 value).

| Key                          | Scope     | Description                                                                                 |
|------------------------------|-----------|---------------------------------------------------------------------------------------------|
| `token`, `token_2`, ...      | per-tok   | Discord user token                                                                          |
| `application_id`             | global    | App ID used for RPC external assets                                                         |
| `SELFBOT`, `SELFBOT_2`, ...  | per-tok   | `true` to enable commands for that token                                                    |
| `stream`, `stream_2`, ...    | per-tok   | `true` to enable RPC for that token                                                         |
| `rpc_type`, `rpc_type_2`, ...| per-tok   | `0`=Playing, `1`=Streaming, `2`=Listening, `3`=Watching, `5`=Competing                      |
| `rpc_name`, `rpc_name_2`, ...| per-tok   | App name shown in the RPC                                                                   |
| `autochangestream`, `_2`, ...| per-tok   | `true` to rotate RPC between slot A and slot B                                              |
| `start_time`                 | global    | RPC timer start: `now`, `elapsed`, `today`, `1y`, `3y`, `30d`, `180d`, or unix ms timestamp |
| `autochangecustomstatus`, `_2`, ... | per-tok | `true` to cycle custom statuses                                                        |
| `auto_join_voice`, `_2`, ... | per-tok   | `true` to auto-join voice channels                                                          |
| `guild_id` / `voice_channel_id` | per-tok | Voice target(s). Multiple pairs: `guild_id=(1),(2)` + `voice_channel_id=(a),(b)`            |
| `fakelive`, `fakelive_2`, ...| per-tok   | `true` to appear streaming inside voice (requires `auto_join_voice`)                        |
| `auto_react`, `_2`, `_3`     | per-tok   | `true` to enable auto react                                                                 |
| `auto_react_emojis`, `_2`, `_3` | per-tok | Comma-separated emoji list (e.g. `👀,🔥`)                                                  |
| `auto_react_target`, `_2`, `_3` | per-tok | `all`, `reply`, or comma-separated user IDs                                                |

**Example:**

```ini
token=MTIz...
token_2=NDU2...
token_3=Njc4...

application_id=1234567890

SELFBOT=true
SELFBOT_2=true
SELFBOT_3=true

stream=true
stream_2=true
stream_3=true

rpc_type=2
rpc_type_2=2
rpc_type_3=2

rpc_name=Nova
rpc_name_2=Myznhyzz
rpc_name_3=Thaowvyzz

autochangestream=false
start_time=now

auto_join_voice=true
guild_id=1111111111111111111
voice_channel_id=2222222222222222222

auto_join_voice_2=true
guild_id_2=3333333333333333333
voice_channel_id_2=4444444444444444444

fakelive=true
fakelive_2=true
fakelive_3=true

auto_react_1=true
auto_react_emojis_1=👀,🔥
auto_react_target_1=all

auto_react_2=false

auto_react_3=true
auto_react_emojis_3=❤️,✨
auto_react_target_3=reply

autochangecustomstatus=false
```

### stream.txt

RPC content split into slot A and slot B per token. When `autochangestream=true`, the bot alternates between the two slots every 5 seconds.

| Key pattern | Token | Slot |
|-------------|-------|------|
| `line1`, `line2`, ... | 1 | A |
| `line1_b`, ...        | 1 | B |
| `line1_2`, ...        | 2 | A |
| `line1_2_b`, ...      | 2 | B |
| `line1_3`, ...        | 3 | A |
| `line1_3_b`, ...      | 3 | B |

Fallback order for any key: `key_N_b` → `key_N` → `key_b` → `key`.

**Supported keys:**

| Key | Purpose |
|-----|---------|
| `line1` | Main line (largest text) — usually `Listening: <song>` |
| `line2` | Secondary line (state) |
| `line3` | Hover text on image |
| `button1_label` + `button1_url` | Button 1 |
| `button2_label` + `button2_url` | Button 2 |
| `image_url` | Large image on the activity |

**Placeholders:**
- `{date}` → `dd/mm/20yy` (VN time)
- `{time}` → `HH:MM:SS` (VN time)

**Example:**

```ini
image_url=https://i.imgur.com/z1e6skZ.png
image_url_2=https://i.imgur.com/gs6K29Z.png

line1=Listening:🌙 夜の音楽
line2=🎧 chillin' alone
line3=
button1_label=Profile
button1_url=https://example.com
button2_label=
button2_url=

line1_2=Watching: some anime
line2_2=just vibing
```

### nhay.txt

Lines used by `$nhay`. The file is split into per-token blocks using the prefix `nhay_N=`.

**Format:**

```
nhay_1=
cút
ngon thì vào
mày chạy đâu

nhay_2=
CHẬM VẬY 😂
BỊ RÉO CAY À
LẠY BỐ TAG NHANH LÊN

nhay_3=
mạnh lên
khóc chưa
```

**Rules:**

- Each line after `nhay_N=` belongs to token N until the next prefix
- Blank lines are ignored
- Content on the same line as the prefix is also accepted (`nhay_1=cút`)

**Fallback order:**

| Token | Order |
|-------|-------|
| 1 | `nhay_1` → `nhay_2` → `nhay_3` |
| 2 | `nhay_2` → `nhay_3` → `nhay_1` |
| 3 | `nhay_3` → `nhay_1` → `nhay_2` |

If no block is found for any token, `$nhay` prints a warning and does nothing.

### customstatus.txt

One status per line. The bot rotates through them in order, looping forever. Requires at least 2 lines and `autochangecustomstatus_N=true` for the target token.

```
đang chill
ăn cơm
đi ngủ
```

---

## Commands

Prefix: `$`.

| Command | Scope | Description |
|---------|-------|-------------|
| `$menu` | guild + DM | Show the command menu |
| `$ping` | guild + DM | Gateway latency in ms |
| `$afk [message]` | guild + DM | Toggle AFK — track pings, reply on return |
| *(any message)* | guild + DM | Disable AFK and print the ping summary |
| `$spam <count> <content>` | guild + DM | Spam content N times (max 100) |
| `$dm <user_id> <content>` | guild + DM | Send a DM |
| `$guilds` | guild + DM | List servers you're in |
| `$av [@user\|id]` | guild + DM | Avatar URL (1024px) |
| `$userinfo [@user\|id]` | guild + DM | User info (username, avatar, banner, join date, roles) |
| `$id [@user\|#channel\|@role]` | guild + DM | Resolve an ID |
| `$purge [count]` | guild + DM | Delete your own messages (default 10, max 200) |
| `$snipe [@user] [count]` | guild + DM | View recently deleted messages |
| `$log [@user] [count]` | guild + DM | View edit history |
| `$nhay @u1 @u2 ...` | guild + DM | Toggle multi-user mention spam |
| `$farm` | guild + DM | Toggle spam messages for exp bots |
| `$guild` | guild only | Current guild info (with human online count) |
| `$nick <name>` | guild only | Change nickname in the current server |
| `$nuke <invite>` | guild only | Nuke a server (irreversible) |

---

## AFK Behaviour

**Cooldowns (all random 1..5s):**

| Cooldown | Effect |
|----------|--------|
| Per-user | Same user ping during cooldown → **skip** reply |
| Per-channel | Tracked but does **not** block replies |
| Global | Tracked but does **not** block replies |
| Reply delay | Random 1..5s before sending the reply |

**Reply trigger — all of the following:**
- User mention (`<@you>`) by a real user
- Reply to one of your messages
- DM to you

**Skipped triggers:**
- Bot pings
- Role mention
- `@everyone` / `@here`

**Summary on return — printed when you type any non-`$afk` message:**

```
:stopwatch: Chào mừng bạn trở lại, username! Bạn đã AFK trong 23 phút và 39 giây và nhận được 3 ping.

Các ping đã nhận
Author 1
https://discord.com/channels/.../.../...
Author 2
https://discord.com/channels/.../.../...
```

---

## Auto React

Per-token. Config keys:

| Key | Value |
|-----|-------|
| `auto_react_N` | `true` / `false` |
| `auto_react_emojis_N` | Comma-separated emoji list |
| `auto_react_target_N` | `all` / `reply` / `<user_id>,<user_id>` |

**Target modes:**

| Mode | Behaviour |
|------|-----------|
| `all` | React to every message in every channel (except bot messages) |
| `reply` | React only when someone replies to one of your messages |
| `123,456` | React only when user IDs 123 or 456 send a message |

**Behaviour:**
- Reacts to **all** message types: text, stickers, images, embeds, files, voice messages
- Reacts to **your own messages** too
- Skips bot messages
- 0.4s delay between emojis to avoid rate limits

---

## Delay Format

Wherever a delay is accepted (`customstatus_delay`, `stream_rotate_delay`):

| Input | Meaning |
|-------|---------|
| `5` | 5 seconds |
| `30s` | 30 seconds |
| `5m` | 5 minutes |
| `2h` | 2 hours |
| `7d` | 7 days |

If no unit is given, seconds is assumed.

---

## Running

```
python main.py
```

Press **Ctrl+C** to shut down cleanly. The bot restores original custom statuses before exiting.

**Sample startup log:**

```
[*] start_time → 1726900000000 ms
[+] Loaded 2 image
[*] Token 1 loaded nhay block nhay_1 (5 lines)
[*] Token 2 loaded nhay block nhay_2 (3 lines)
[*] Token 3 loaded nhay block nhay_3 (3 lines)
[*] Connected | Nova | rpc_name=Nova | rpc_type=2 | stream=True | fakelive=True | commands=True
[*] [Nova] Auto join voice: 2222222222222222222
[*] [Nova] Fake live enabled
[*] [Nova] Auto react: ['👀', '🔥'] → all
```

---

## Environment Variables

Any of these override the corresponding `config.txt` value:

| Env var | Purpose |
|---------|---------|
| `SELFBOT` / `SELFBOT_2` / `SELFBOT_3` | Toggle commands per token |
| `GUILD_ID` / `GUILD_ID_2` / `GUILD_ID_3` | Voice guild per token |
| `VOICE_CHANNEL_ID` / `VOICE_CHANNEL_ID_2` / `VOICE_CHANNEL_ID_3` | Voice channel per token |
| `START_TIME` | RPC start timer — must be **milliseconds** (13 digits) |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `stream.txt missing or line1 not set` | Set at minimum `line1` in `stream.txt`, and `application_id` in `config.txt` |
| `Token N invalid` | Token expired or wrong — retrieve a fresh one from the browser |
| Voice not joining | Check `auto_join_voice=true`, valid `guild_id` + `voice_channel_id`, and CONNECT permission |
| Fake live not showing | Requires `auto_join_voice=true` and a valid voice channel |
| RPC images blank | Image URL must be reachable, `application_id` must match the token's app |
| Custom status not cycling | Requires `autochangecustomstatus_N=true` and at least 2 lines in `customstatus.txt` |
| Commands don't respond | Ensure `SELFBOT_N=true` in `config.txt` |
| `$userinfo` fails in DM | User not in cache, not in a shared guild → Discord API limitation |
| `$snipe` / `$log` empty after restart | Cache is in-memory and resets on startup |

---

## License

MIT — see [LICENSE](LICENSE).
