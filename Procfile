"""
Badger Support Agent
Slack bot that categorizes, assigns, and tracks issues for Unlock Investment Operations
"""

import os
import json
import hmac
import hashlib
import logging
import time
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
import anthropic
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from rank_bm25 import BM25Okapi

from badger_domain_expansions import DOMAIN_EXPANSIONS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ── CONFIGURATION ──────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
SLACK_BOT_TOKEN      = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")

MODEL             = "claude-sonnet-4-6"
KB_DIR            = Path(__file__).parent / "kb"
DB_PATH           = Path(__file__).parent / "tickets.db"
CHUNK_SIZE        = 100
CHUNK_OVERLAP     = 20
TOP_K             = 20
MAX_CONTEXT_CHARS = 60_000

# ── CATEGORY / ASSIGNMENT CONFIG ───────────────────────────────────────────────

CATEGORIES = {
    "Badger":               {"assignee": "Jagat Shah",  "email": "jagat.shah@unlock.com"},
    "Excel Toolkits":       {"assignee": "Jagat Shah",  "email": "jagat.shah@unlock.com"},
    "Deal Data Quality":    {"assignee": "Brian Rubin", "email": "brian.rubin@unlock.com"},
    "Data Ad Hoc Request":  {"assignee": "Jagat Shah",  "email": "jagat.shah@unlock.com"},
}

AD_HOC_TEAMS = [
    "Investor", "Legal", "Servicing",
    "Capital Markets", "Accounting", "Portfolio Management",
]

TICKET_STATUSES = ["New", "Assigned", "In Progress", "Resolved"]

ANCHOR_KEYWORDS = {
    "logic_team_ownership.txt":    ["Jagat", "Brian"],
    "logic_system_operations.txt": ["KEY SLACK CHANNELS"],
}


# ── DATABASE ───────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at     TEXT NOT NULL,
            submitted_by   TEXT NOT NULL,
            description    TEXT NOT NULL,
            category       TEXT NOT NULL,
            sub_category   TEXT,
            assignee       TEXT NOT NULL,
            assignee_email TEXT NOT NULL,
            status         TEXT NOT NULL DEFAULT 'New',
            slack_channel  TEXT,
            thread_ts      TEXT
        )
    """)
    conn.commit()
    conn.close()


def create_ticket(submitted_by, description, category, sub_category, slack_channel, thread_ts):
    cat = CATEGORIES[category]
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.execute("""
        INSERT INTO tickets (created_at, submitted_by, description, category,
                             sub_category, assignee, assignee_email, status,
                             slack_channel, thread_ts)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'New', ?, ?)
    """, (datetime.utcnow().isoformat(), submitted_by, description, category,
          sub_category, cat["assignee"], cat["email"], slack_channel, thread_ts))
    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def get_tickets():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM tickets ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_ticket_status(ticket_id, status):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE tickets SET status=? WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()


# ── KB / BM25 ──────────────────────────────────────────────────────────────────

def load_kb_chunks():
    corpus, meta = [], []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for fpath in sorted(KB_DIR.rglob("*")):
        if not fpath.is_file():
            continue
        try:
            text = fpath.read_text(errors="replace")
        except Exception:
            continue
        lines = text.splitlines()
        for i in range(0, max(1, len(lines) - CHUNK_OVERLAP), step):
            chunk = "\n".join(lines[i: i + CHUNK_SIZE])
            corpus.append(chunk.lower().split())
            meta.append({"file": fpath.name, "start": i, "text": chunk})
    log.info(f"Loaded {len(corpus)} KB chunks")
    return corpus, meta


def build_anchor_chunks(meta):
    seen, anchors = set(), []
    for m in meta:
        for kw in ANCHOR_KEYWORDS.get(m["file"], []):
            if kw.lower() in m["text"].lower():
                h = hashlib.md5(m["text"].encode()).hexdigest()
                if h not in seen:
                    seen.add(h)
                    anchors.append(m["text"])
                break
    return anchors


# ── GLOBAL STATE ───────────────────────────────────────────────────────────────

_bm25:         Optional[BM25Okapi] = None
_meta:         list                = []
_anchors:      list                = []
_seen_events:  dict                = {}
_pending_adhoc: dict               = {}  # (channel, user) → {description, thread_ts}

slack_client  = WebClient(token=SLACK_BOT_TOKEN)
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bm25, _meta, _anchors
    init_db()
    corpus, _meta = load_kb_chunks()
    _bm25 = BM25Okapi(corpus)
    _anchors = build_anchor_chunks(_meta)
    log.info(f"Ready. {len(_meta)} chunks, {len(_anchors)} anchors.")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── CLASSIFICATION ─────────────────────────────────────────────────────────────

CLASSIFY_PROMPT = """\
You are a ticket classifier for Unlock Technologies Badger servicing system.
Classify the issue into exactly one category:
  - Badger           (system errors, application issues, asset imports, Badger app bugs)
  - Excel Toolkits   (macro errors, #NAME? errors, PopulateAsset failures, calculator issues)
  - Deal Data Quality (missing or incorrect deal/asset data, tradeline issues, credit data)
  - Data Ad Hoc Request (one-off data pulls, report requests, data extracts)

Respond with ONLY valid JSON. No markdown. No explanation.
Example: {"category": "Badger"}
"""

def classify_issue(description):
    try:
        r = claude_client.messages.create(
            model=MODEL, max_tokens=50,
            system=CLASSIFY_PROMPT,
            messages=[{"role": "user", "content": description}],
        )
        data = json.loads(r.content[0].text.strip())
        cat  = data.get("category", "")
        if cat in CATEGORIES:
            return cat
    except Exception as e:
        log.error(f"Classification error: {e}")
    return "Badger"


# ── SLACK HELPERS ──────────────────────────────────────────────────────────────

def verify_slack_signature(body, timestamp, signature):
    base     = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = "v0=" + hmac.new(SLACK_SIGNING_SECRET.encode(), base.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)


def is_duplicate(event_id):
    now = time.time()
    for k in [k for k, v in _seen_events.items() if now - v > 300]:
        del _seen_events[k]
    if event_id in _seen_events:
        return True
    _seen_events[event_id] = now
    return False


def post_reply(channel, text, thread_ts=None):
    try:
        slack_client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
    except SlackApiError as e:
        log.error(f"Slack error: {e.response['error']}")


def get_display_name(user_id):
    try:
        return slack_client.users_info(user=user_id)["user"]["real_name"] or user_id
    except Exception:
        return user_id


# ── MESSAGE HANDLER ────────────────────────────────────────────────────────────

def handle_message(text, channel, user, thread_ts):
    clean = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
    if not clean:
        return

    key = (channel, user)

    # Pending ad hoc — user is answering "which team?"
    if key in _pending_adhoc:
        pending = _pending_adhoc.pop(key)
        matched = next((t for t in AD_HOC_TEAMS if t.lower() in clean.lower()), clean.title())
        ticket_id = create_ticket(
            submitted_by=get_display_name(user),
            description=pending["description"],
            category="Data Ad Hoc Request",
            sub_category=matched,
            slack_channel=channel,
            thread_ts=thread_ts,
        )
        cat = CATEGORIES["Data Ad Hoc Request"]
        post_reply(channel,
            f":white_check_mark: Ticket #{ticket_id} created.\n"
            f"*Category:* Data Ad Hoc Request — {matched}\n"
            f"*Assigned to:* {cat['assignee']} ({cat['email']})\n"
            f"*Status:* New",
            thread_ts)
        return

    # New issue
    category = classify_issue(clean)

    if category == "Data Ad Hoc Request":
        _pending_adhoc[key] = {"description": clean, "thread_ts": thread_ts}
        post_reply(channel,
            f":pencil: This looks like a *Data Ad Hoc Request*.\n"
            f"Which team is requesting this? ({', '.join(AD_HOC_TEAMS)})",
            thread_ts)
        return

    ticket_id = create_ticket(
        submitted_by=get_display_name(user),
        description=clean,
        category=category,
        sub_category=None,
        slack_channel=channel,
        thread_ts=thread_ts,
    )
    cat = CATEGORIES[category]
    post_reply(channel,
        f":white_check_mark: Ticket #{ticket_id} created.\n"
        f"*Category:* {category}\n"
        f"*Assigned to:* {cat['assignee']} ({cat['email']})\n"
        f"*Status:* New",
        thread_ts)


# ── API ROUTES ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "chunks": len(_meta)}

@app.get("/tickets")
async def tickets_list():
    return JSONResponse(get_tickets())

@app.patch("/tickets/{ticket_id}/status")
async def update_status(ticket_id: int, request: Request):
    body   = await request.json()
    status = body.get("status", "")
    if status not in TICKET_STATUSES:
        raise HTTPException(400, detail=f"Status must be one of: {TICKET_STATUSES}")
    update_ticket_status(ticket_id, status)
    return {"ok": True, "ticket_id": ticket_id, "status": status}

@app.post("/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    body_bytes = await request.body()
    try:
        body = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(400, detail="Invalid JSON")

    if body.get("type") == "url_verification":
        return JSONResponse({"challenge": body["challenge"]})

    if SLACK_SIGNING_SECRET:
        if not verify_slack_signature(
            body_bytes,
            request.headers.get("X-Slack-Request-Timestamp", ""),
            request.headers.get("X-Slack-Signature", ""),
        ):
            raise HTTPException(403, detail="Invalid signature")

    event_id = body.get("event_id", "")
    if event_id and is_duplicate(event_id):
        return JSONResponse({"ok": True})

    event = body.get("event", {})
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return JSONResponse({"ok": True})

    if event.get("type") in ("message", "app_mention"):
        background_tasks.add_task(
            handle_message,
            event.get("text", ""),
            event.get("channel", ""),
            event.get("user", "unknown"),
            event.get("thread_ts") or event.get("ts"),
        )

    return JSONResponse({"ok": True})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
