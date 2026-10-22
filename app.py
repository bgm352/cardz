# app.py
import os
import sys

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

for secret_key in ["EBAY_APP_ID", "EBAY_CERT_ID", "GEMINI_API_KEY"]:
  if secret_key in st.secrets and not os.environ.get(secret_key):
    os.environ[secret_key] = st.secrets[secret_key]

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

with st.sidebar:
  st.header("⚡ Sniper Controls")
  has_keys = bool(
      os.environ.get("EBAY_APP_ID") and os.environ.get("EBAY_CERT_ID")
  )

  if has_keys:
    st.success("🔑 Full eBay API Connected")
  else:
    st.info("⚡ Running in Zero-Key Public RSS Mode (No API Key Needed!)")

  if st.button(
      "🔄 Scan Live eBay Now", type="primary", use_container_width=True
  ):
    with st.spinner("Scanning live eBay raw listings..."):
      token = get_ebay_oauth_token() if has_keys else None
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
      st.success(f"Scan complete! Pulled {added_count} qualifying steals.")
      st.rerun()

  st.divider()
  st.subheader("🧪 Manual Deal Tester (No Key Needed)")
  manual_title = st.selectbox(
      "Select Target Card Profile:", [w["query"] for w in WATCHLIST]
  )
  manual_price = st.number_input(
      "Listing Raw Price + Ship ($):", min_value=10.0, value=92.0, step=1.0
  )
  manual_img = st.text_input(
      "Paste eBay Image Address (Right-click card photo -> Copy image address):"
  )
  manual_url = st.text_input("Paste eBay Listing URL:")

  if st.button("➕ Evaluate & Add to Queue", use_container_width=True):
    cfg = next(w for w in WATCHLIST if w["query"] == manual_title)
    custom_card = {
        "item_id": f"manual_{int(manual_price)}_{len(manual_url)}",
        "title": f"{manual_title} (Live Manual Check)",
        "raw_price": float(manual_price),
        "image_url": (
            manual_img
            if manual_img
            else "https://i.ebayimg.com/images/g/placeholder/s-l1600.jpg"
        ),
        "ebay_url": manual_url if manual_url else "https://www.ebay.com",
        "seller_id": "Manual URL Check",
    }
    vetted = evaluate_card_deal(custom_card, cfg)
    if vetted:
      save_candidate(vetted)
      st.success("✅ Passed $800/hr & PSA 9 Floor! Added to queue.")
      st.rerun()
    else:
      st.error(
          "❌ WALK AWAY: Price is too high for the PSA 9 safety floor or"
          " $800/hr rule!"
      )

pending = fetch_pending_candidates()

if not pending:
  st.info(
      "🎯 **Queue is ready!** Click **'🔄 Scan Live eBay Now'** in the left"
      " sidebar or test any eBay listing in the **Manual Deal Tester**."
  )
else:
  st.write(f"**Showing 1 of {len(pending)} vetted candidates in queue:**")
  card = pending[0]
  col1, col2 = st.columns([1.2, 1.4])

  with col1:
    st.subheader("🔍 5-Second 4-Corner Zoom Strip + High-Res Scan")
    strip_img = generate_4_corner_zoom_strip(card["image_url"])
    if strip_img:
      st.image(
          strip_img,
          caption="3x Zoomed Corners: Top-L | Top-R | Bot-L | Bot-R",
          use_container_width=True,
      )
    st.image(
        card["image_url"],
        caption=f"Source: {card['seller_id']}",
        use_container_width=True,
    )

  with col2:
    st.markdown(card["alert_summary"])
    st.markdown(f"🔗 **[Open eBay Listing]({card['ebay_url']})**")
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
