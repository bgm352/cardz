# app.py
import os
import sys

# Ensure root directory imports work cleanly on Streamlit Cloud
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
  sys.path.append(ROOT_DIR)

import streamlit as st
from config import WATCHLIST
from database import (
    fetch_pending_candidates,
    record_user_decision,
    save_candidate,
)
from ebay_client import get_ebay_oauth_token, search_ultra_picky_raw_cards
from math_engine import evaluate_card_deal
from vision_screener import generate_4_corner_zoom_strip

st.set_page_config(page_title="800/Hr Card Arbitrage Sniper", layout="wide")

# Sync Streamlit Cloud Secrets into os.environ automatically if present
for secret_key in [
    "EBAY_APP_ID",
    "EBAY_CERT_ID",
    "GEMINI_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
]:
  if secret_key in st.secrets and not os.environ.get(secret_key):
    os.environ[secret_key] = st.secrets[secret_key]

# Earl Nightingale Mindset Banner
st.markdown(
    """
<div style="background-color:#111827; padding:16px; border-radius:10px; border-left: 6px solid #10B981; margin-bottom:20px;">
    <p style="color:#F9FAFB; font-size:16px; font-weight:700; margin:0;">
        ✨ "We become what we think about." — Protect the $800/hr floor. Keep the wide-eyed kid energy alive!
    </p>
    <p style="color:#9CA3AF; font-size:13px; margin:5px 0 0 0;">
        🎯 Mission: Zero-cost automated engines | Debt-Free by 40 | Freedom, Travel & Presence with the Girls 🚀
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar Controls for Live eBay Scanning
with st.sidebar:
  st.header("⚡ Sniper Controls")
  has_keys = bool(
      os.environ.get("EBAY_APP_ID") and os.environ.get("EBAY_CERT_ID")
  )

  if has_keys:
    st.success("🔑 eBay API Keys Connected")
  else:
    st.warning("⚠️ Add EBAY_APP_ID & EBAY_CERT_ID in Streamlit Settings -> Secrets")

  if st.button(
      "🔄 Scan Live eBay Now",
      type="primary",
      use_container_width=True,
      disabled=not has_keys,
  ):
    with st.spinner(
        "Scanning eBay Condition 4000 raw listings & checking seller slab"
        " ratios..."
    ):
      try:
        token = get_ebay_oauth_token()
        added_count = 0
        for watch_cfg in WATCHLIST:
          approx_max = min(watch_cfg["last_3_psa9"]) * 0.85
          raw_items = search_ultra_picky_raw_cards(
              watch_cfg["query"], approx_max, token
          )
          for item in raw_items:
            vetted = evaluate_card_deal(item, watch_cfg)
            if vetted:
              save_candidate(vetted)
              added_count += 1
        st.success(f"Scan complete! Found {added_count} new Green/Yellow steals.")
        st.rerun()
      except Exception as e:
        st.error(f"eBay API Error: {e}")

  st.divider()
  st.caption("📋 **Active Watchlist Targets:**")
  for w in WATCHLIST:
    st.caption(f"• {w['query']} ({w['tier']})")

# Main Queue Display (Strictly Real eBay Listings Only)
pending = fetch_pending_candidates()

if not pending:
  st.info(
      "🎯 **No pending cards in queue.** Click **'🔄 Scan Live eBay Now'** in"
      " the left sidebar (once your eBay keys are in Secrets) to pull real"
      " eBay listings!"
  )
else:
  st.write(f"**Showing 1 of {len(pending)} vetted eBay candidates in queue:**")
  card = pending[0]
  col1, col2 = st.columns([1.2, 1.4])

  with col1:
    st.subheader("🔍 5-Second 4-Corner Zoom Strip + eBay Scan")
    strip_img = generate_4_corner_zoom_strip(card["image_url"])
    if strip_img:
      st.image(
          strip_img,
          caption="3x Zoomed Corners: Top-L | Top-R | Bot-L | Bot-R",
          use_container_width=True,
      )
    st.image(
        card["image_url"],
        caption=f"Seller: {card['seller_id']}",
        use_container_width=True,
    )

  with col2:
    st.markdown(card["alert_summary"])
    st.markdown(f"🔗 **[View Live eBay Listing]({card['ebay_url']})**")
    st.divider()

    reason = st.selectbox(
        "If rejecting ('Bugger'), tag flaw to train AI:",
        [
            "Clean Copy (Approve)",
            "Off-Center >52/48",
            "Back Corner White Spec",
            "Surface Dimple",
            "Overpriced",
        ],
    )
    b1, b2 = st.columns(2)
    with b1:
      if st.button(
          f"✅ {card['action_text']}", type="primary", use_container_width=True
      ):
        record_user_decision(card["item_id"], "APPROVED", "Clean Gem Candidate")
        st.rerun()
    with b2:
      if st.button(
          "❌ BUGGER (REJECT & NEXT)", use_container_width=True
      ):
        record_user_decision(card["item_id"], "REJECTED", reason)
        st.rerun()
