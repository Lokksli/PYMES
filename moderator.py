"""Moderator module"""

import badwords_db as bdb
import bans_db as bans
import messages_db as mdb
import time
import re
from typing import Dict
import olama_client
import os


def init():
    try:
        bans.init_db()
    except Exception:
        pass


def _contains_badword(message: str):
    if not message:
        return False
    for entry in bdb.get_all_words():
        w = entry.get('word')
        if not w:
            continue
        if entry.get('is_regex'):
            try:
                if re.search(w, message, flags=re.IGNORECASE):
                    print(f"[Moderator] Regex match: {w}")
                    return True
            except re.error:
                continue
        else:
            if w.lower() in message.lower():
                print(f"[Moderator] Keyword match: {w}")
                return True
    return False


def check_and_handle_message(username: str, message: str, ban_seconds: int = 300) -> Dict:
    try:
        bans.init_db()
    except Exception:
        pass

    # Check if user is already banned
    is_b, secs_left = bans.is_banned(username)
    if is_b:
        return {'action': 'user_banned', 'reason': 'user currently banned', 'seconds_left': secs_left}

    bad = False
    reason = None

    # FIX 1: AI is now ON by default. Set OLAMA_ENABLED=0 to disable it.
    ai_enabled = os.environ.get('OLAMA_ENABLED', '1').lower() not in ('0', 'false', 'no')

    if ai_enabled:
        try:
            ai_decision = olama_client.analyze_message_with_olama(message)
            print(f"[Moderator] AI decision: {ai_decision}")
        except Exception as e:
            print(f"[Moderator] AI call failed: {e}")
            ai_decision = None

        if isinstance(ai_decision, dict) and 'ban' in ai_decision:
            try:
                min_conf = float(os.environ.get('OLAMA_MIN_CONF', '0.7'))
            except Exception:
                min_conf = 0.7

            ban_flag = bool(ai_decision.get('ban'))
            try:
                confidence = float(ai_decision.get('confidence') or 0.0)
            except Exception:
                confidence = 0.0

            bad = ban_flag and confidence >= min_conf
            reason = ai_decision.get('reason')
            print(f"[Moderator] ban={ban_flag}, confidence={confidence:.2f}, threshold={min_conf}")
        else:
            # AI unavailable — fall back to keyword filter
            print("[Moderator] AI unavailable, falling back to keyword filter")
            bad = _contains_badword(message)


    if bad:
        try:
            bans.ban_user(username, ban_seconds)
        except Exception:
            pass
        return {
            'action': 'banned',
            'reason': reason or 'violated chat policy',
            'ban_seconds': ban_seconds
        }

    return {'action': 'ok', 'reason': 'no issues'}


if __name__ == '__main__':
    init()


