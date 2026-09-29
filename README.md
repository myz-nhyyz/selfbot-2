# Discord Multi-Token Selfbot

A multi-token Discord selfbot with rich presence, voice auto-join, fake live, and a full command suite. Supports per-token configuration for status rotation, custom status cycling, language, and more.

Selfbot Discord đa token với rich presence, tự động vào voice, fake live, và bộ lệnh đầy đủ. Hỗ trợ cấu hình riêng cho từng token: đổi RPC, đổi custom status, ngôn ngữ, và nhiều hơn nữa.

> ⚠️ **Disclaimer / Cảnh báo** — Selfbots violate Discord's Terms of Service. Use at your own risk. This repo is for personal / educational use only. / Selfbot vi phạm Điều khoản dịch vụ của Discord. Dùng tự chịu rủi ro. Repo này chỉ dành cho mục đích cá nhân / học tập.

---

## Table of Contents / Mục lục

- [Features / Tính năng](#features--tính-năng)
- [Requirements / Yêu cầu](#requirements--yêu-cầu)
- [Installation / Cài đặt](#installation--cài-đặt)
- [File Structure / Cấu trúc file](#file-structure--cấu-trúc-file)
- [Configuration / Cấu hình](#configuration--cấu-hình)
  - [config.txt](#configtxt)
  - [stream.txt](#streamtxt)
  - [customstatus.txt](#customstatustxt)
  - [nhay.txt](#nhaytxt)
- [Commands / Lệnh](#commands--lệnh)
- [Delay Format / Định dạng delay](#delay-format--định-dạng-delay)
- [Running / Chạy](#running--chạy)
- [Environment Variables / Biến môi trường](#environment-variables--biến-môi-trường)
- [Troubleshooting / Xử lý lỗi](#troubleshooting--xử-lý-lỗi)

---

## Features / Tính năng

- **Multi-token** — run 1..N selfbot accounts from a single process / chạy 1..N account selfbot trong 1 process
- **Rich Presence (RPC)** — Playing / Streaming / Listening / Watching / Competing, with images and buttons / có ảnh và button
- **Auto change stream** — rotate RPC content between slot A and slot B per token / luân phiên nội dung RPC giữa slot A và slot B cho từng token
- **Auto change custom status** — cycle custom statuses from `customstatus.txt` per token, with per-token delay / luân phiên custom status từ `customstatus.txt`, delay riêng cho từng token
- **Voice auto-join** — join one or more voice channels and auto-rejoin when disconnected / vào nhiều voice channel, tự rejoin khi bị ngắt
- **Fake live** — appear as streaming inside a voice channel (with `auto_join_voice`) / hiện như đang stream trong voice (cần `auto_join_voice`)
- **Language switch** — per-token EN / VI, changeable at runtime with `$language` / EN / VI cho từng token, đổi runtime bằng `$language`
- **Selfbot commands / Lệnh selfbot**:
  - `$menu`, `$farm`, `$nhay`, `$spam`, `$dm`, `$nuke`, `$purge`, `$afk`
  - `$snipe`, `$log`, `$guilds`, `$userinfo`, `$guild`, `$id`, `$av`, `$banner`
  - `$nick`, `$ping`, `$language`

---

## Requirements / Yêu cầu

- Python 3.9+
- `requests`, `websocket-client`, `pytz`

```
pip install requests websocket-client pytz
```

---

## Installation / Cài đặt

```
git clone https://github.com/yourname/yourrepo.git
cd yourrepo
pip install -r requirements.txt
# edit config.txt, stream.txt, customstatus.txt, nhay.txt
# sửa config.txt, stream.txt, customstatus.txt, nhay.txt
python main.py
```

---

## File Structure / Cấu trúc file

```
.
├── main.py             # entry point / file chạy chính
├── config.txt          # tokens, toggles, per-token options / token, toggle, tuỳ chọn từng token
├── stream.txt          # RPC content (slot A + slot B per token) / nội dung RPC (slot A + slot B mỗi token)
├── customstatus.txt    # rotating custom statuses / các status luân phiên
├── nhay.txt            # lines used by $nhay / các dòng dùng cho $nhay
└── README.md
```

---

## Configuration / Cấu hình

### config.txt

Tokens, toggles, and per-token options. Any key suffixed with `_N` applies to token N. If `_N` is missing, the bot falls back to the base key (token 1 value).

Token, toggle, và tuỳ chọn từng token. Key có hậu tố `_N` áp cho token N. Nếu thiếu `_N`, bot fallback về key gốc (giá trị của token 1).

| Key                          | Scope / Phạm vi | Description / Mô tả                                                                  |
|------------------------------|-----------------|--------------------------------------------------------------------------------------|
| `token`, `token_2`, ...      | per-tok         | Discord user token / Token user Discord                                              |
| `application_id`             | global          | App ID used for RPC external assets / App ID dùng cho RPC external assets            |
| `language`, `language_2`, ...| per-tok         | `en` or `vi`. Default `en`. Changeable at runtime with `$language` / `en` hoặc `vi`. Mặc định `en`. Đổi runtime bằng `$language` |
| `autochangecustomstatus`     | per-tok         | `true` to cycle custom statuses / `true` để luân phiên custom status                 |
| `customstatus_delay`         | per-tok         | Delay between status changes, supports `s/m/h/d` / Delay giữa các lần đổi, hỗ trợ `s/m/h/d` (vd `5`, `30s`, `5m`, `1d`) |
| `autochangestream`           | per-tok         | `true` to rotate RPC between slot A and slot B / `true` để luân phiên RPC giữa slot A và slot B |
| `stream_rotate_delay`        | per-tok         | Rotate delay, supports `s/m/h/d` / Delay rotate, hỗ trợ `s/m/h/d`                    |
| `stream`                     | per-tok         | `true` to enable RPC for that token / `true` để bật RPC cho token đó                 |
| `auto_join_voice`            | per-tok         | `true` to auto-join voice channels / `true` để tự vào voice                          |
| `guild_id` / `voice_channel_id` | per-tok      | Voice target(s). Multiple pairs: `guild_id=(1)(2)`, `voice_channel_id=(1)(2)` / Voice target. Nhiều cặp: `guild_id=(1)(2)`, `voice_channel_id=(1)(2)` |
| `fakelive`                   | per-tok         | `true` to appear streaming inside voice (requires `auto_join_voice`) / `true` để hiện như đang stream trong voice (cần `auto_join_voice`) |
| `SELFBOT`                    | per-tok         | `true` to enable commands for that token / `true` để bật lệnh cho token đó           |
| `start_time`                 | global          | RPC timer start: `now`, `elapsed`, `today`, `1y`, `3y`, `30d`, `180d`, or unix ts / Timer RPC: `now`, `elapsed`, `today`, `1y`, `3y`, `30d`, `180d`, hoặc unix ts |
| `rpc_type`                   | per-tok         | `0`=Playing, `1`=Streaming, `2`=Listening, `3`=Watching, `5`=Competing               |
| `rpc_name`                   | per-tok         | App name shown in the RPC / Tên app hiện trên RPC                                    |

### stream.txt

RPC content split into **slot A** and **slot B** per token. When `autochangestream=true`, the bot alternates between the two slots every `stream_rotate_delay` seconds.

Nội dung RPC chia thành **slot A** và **slot B** cho từng token. Khi `autochangestream=true`, bot luân phiên giữa 2 slot mỗi `stream_rotate_delay` giây.

| Key pattern / Mẫu key | Token | Slot |
|-----------------------|-------|------|
| `line1`, `line2`, ... | 1     | A    |
| `line1_b`, ...        | 1     | B    |
| `line1_2`, ...        | 2     | A    |
| `line1_2_b`, ...      | 2     | B    |
| `line1_3`, ...        | 3     | A    |
| `line1_3_b`, ...      | 3     | B    |

Fallback order for any key: `key_N_b` → `key_N` → `key_b` → `key`. / Thứ tự fallback: `key_N_b` → `key_N` → `key_b` → `key`.

Placeholders: `{date}` → `dd/mm/20yy`, `{time}` → `HH:MM:SS` (VN time / giờ VN).

### customstatus.txt

One status per line. The bot rotates through them in order, looping forever. Requires **at least 2 lines** and `autochangecustomstatus_N=true` for the target token. Delay is set via `customstatus_delay_N` in `config.txt`.

Mỗi dòng 1 status. Bot luân phiên theo thứ tự, lặp vô hạn. Cần **ít nhất 2 dòng** và `autochangecustomstatus_N=true` cho token tương ứng. Delay đặt trong `config.txt` qua `customstatus_delay_N`.

### nhay.txt

One line per message. `$nhay` picks a random line and appends mentions of all targeted users.

Mỗi dòng 1 câu. `$nhay` chọn random 1 dòng rồi thêm mention của tất cả user bị target.

---

## Commands / Lệnh

| Command / Lệnh                   | Description / Mô tả                                                                    |
|----------------------------------|----------------------------------------------------------------------------------------|
| `$menu`                          | Show the command menu (in the token's language) / Hiện menu lệnh (theo ngôn ngữ token) |
| `$farm`                          | Toggle spam messages (for OWO / exp bots) / Bật/tắt spam tin nhắn (cho OWO / bot exp)  |
| `$nhay @u1 @u2 ...`              | Toggle multi-user mention spam / Bật/tắt spam tag nhiều user                           |
| `$spam <count> <content> [delay]`| Spam content N times, optional delay (`s/m/h/d`) / Spam nội dung N lần, delay tuỳ chọn (`s/m/h/d`) |
| `$dm <user_id> <content>`        | Send a DM / Gửi DM                                                                     |
| `$nuke <invite>`                 | Nuke a server (irreversible — confirm before use) / Nuke server (không thể hoàn tác — xác nhận trước khi dùng) |
| `$purge [count]`                 | Delete your own messages (default 10) / Xoá tin nhắn của mình (mặc định 10)            |
| `$afk [message]`                 | Toggle AFK — track pings while AFK, reply when you type again / Bật/tắt AFK — track ping khi AFK, nhắn lại thì trả summary |
| `$snipe [@user] [count]`         | View recently deleted messages / Xem tin nhắn bị xoá gần đây                           |
| `$log [@user] [count]`           | View recent edit history of messages / Xem lịch sử chỉnh sửa tin nhắn                  |
| `$guilds`                        | List servers you're in / List server đang ở                                            |
| `$userinfo [@user\|id]`          | User info (with avatar and banner) — works in DM / Info user (kèm avatar và banner) — DM OK |
| `$guild`                         | Current guild info / Info guild hiện tại                                               |
| `$id [@user\|#channel\|@role]`   | Resolve an ID / Phân giải ID                                                           |
| `$av [@user\|id]`                | Avatar URL / Link avatar                                                               |
| `$banner [@user\|id]`            | Banner URL / Link banner                                                               |
| `$nick <name>`                   | Change nickname in the current server / Đổi nickname trong server hiện tại             |
| `$ping`                          | Gateway latency / Độ trễ gateway                                                       |
| `$language <en\|vi>`             | Change bot language at runtime / Đổi ngôn ngữ runtime                                  |

---

## Delay Format / Định dạng delay

Anywhere `delay`, `customstatus_delay`, or `stream_rotate_delay` is accepted. / Bất kỳ chỗ nào nhận `delay`, `customstatus_delay`, hay `stream_rotate_delay`.

| Input / Nhập | Meaning / Ý nghĩa |
|--------------|-------------------|
| `5`          | 5 seconds / 5 giây |
| `30s`        | 30 seconds / 30 giây |
| `5m`         | 5 minutes / 5 phút |
| `2h`         | 2 hours / 2 giờ |
| `7d`         | 7 days / 7 ngày |

If no unit is given, seconds is assumed. / Nếu không ghi đơn vị, mặc định là giây.

---

## Running / Chạy

```
python main.py
```

Press `Ctrl+C` to shut down cleanly — the bot restores original custom statuses before exiting.

Nhấn `Ctrl+C` để tắt sạch — bot sẽ khôi phục custom status gốc trước khi thoát.

---

## Environment Variables / Biến môi trường

Any of these override the corresponding `config.txt` value. / Các biến sau override giá trị tương ứng trong `config.txt`:

- `SELFBOT`, `SELFBOT_2`, `SELFBOT_3` — toggle commands per token / bật/tắt lệnh cho từng token
- `GUILD_ID`, `GUILD_ID_2`, `GUILD_ID_3` — voice guild per token / guild voice cho từng token
- `VOICE_CHANNEL_ID`, `VOICE_CHANNEL_ID_2`, `VOICE_CHANNEL_ID_3` — voice channel per token / voice channel cho từng token
- `START_TIME` — RPC start timer mode / chế độ timer RPC

---

## Troubleshooting / Xử lý lỗi

- **`stream.txt missing or line1 not set`** — set `line1` at minimum, and `application_id` in config. / Set ít nhất `line1`, và `application_id` trong config.
- **Custom status not cycling** — need `autochangecustomstatus_N=true` **and** ≥2 lines in `customstatus.txt`. / Cần `autochangecustomstatus_N=true` **và** ≥2 dòng trong `customstatus.txt`.
- **Fake live not showing** — requires `auto_join_voice=true` and a valid voice channel. / Cần `auto_join_voice=true` và voice channel hợp lệ.
- **Voice not rejoining** — check bot has `CONNECT` on the target channel. / Kiểm tra bot có quyền `CONNECT` ở channel đích.
- **RPC images blank** — image URL must be reachable and `application_id` must match the token's app. / URL ảnh phải truy cập được và `application_id` phải trùng app của token.
