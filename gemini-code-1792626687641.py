# database.py
from datetime import datetime
import os
import sqlite3


def get_sqlite_conn():
  conn = sqlite3.connect("card_training_loop.db")
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS card_candidates (
            item_id TEXT PRIMARY KEY,
            title TEXT,
            raw_price REAL,
            tier TEXT,
            psa9_floor REAL,
            psa10_floor REAL,
            gem_rate REAL,
            zone_status TEXT,
            action_text TEXT,
            alert_summary TEXT,
            image_url TEXT,
            ebay_url TEXT,
            seller_id TEXT,
            user_decision TEXT DEFAULT 'PENDING',
            rejection_reason TEXT DEFAULT '',
            created_at TEXT
        )
    """)
  conn.commit()
  return conn


def save_candidate(card_data: dict):
  conn = get_sqlite_conn()
  c = conn.cursor()
  c.execute(
      """
        INSERT OR IGNORE INTO card_candidates
        (item_id, title, raw_price, tier, psa9_floor, psa10_floor, gem_rate,
         zone_status, action_text, alert_summary, image_url, ebay_url, seller_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          card_data["item_id"],
          card_data["title"],
          card_data["raw_price"],
          card_data["tier"],
          card_data["psa9_floor"],
          card_data["psa10_floor"],
          card_data["gem_rate"],
          card_data["zone_status"],
          card_data["action_text"],
          card_data["alert_summary"],
          card_data["image_url"],
          card_data["ebay_url"],
          card_data["seller_id"],
          datetime.now().isoformat(),
      ),
  )
  conn.commit()
  conn.close()


def fetch_pending_candidates() -> list[dict]:
  conn = get_sqlite_conn()
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute(
      "SELECT * FROM card_candidates WHERE user_decision = 'PENDING' ORDER BY"
      " created_at DESC"
  )
  rows = [dict(r) for r in c.fetchall()]
  conn.close()
  return rows


def record_user_decision(item_id: str, decision: str, reason: str = ""):
  conn = get_sqlite_conn()
  c = conn.cursor()
  c.execute(
      """
        UPDATE card_candidates
        SET user_decision = ?, rejection_reason = ?
        WHERE item_id = ?
    """,
      (decision, reason, item_id),
  )
  conn.commit()
  conn.close()