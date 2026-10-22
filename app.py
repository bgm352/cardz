# app.py
from datetime import datetime
from config import WATCHLIST
from database import (
    fetch_pending_candidates,
    record_user_decision,
    save_candidate,
)
from math_engine import evaluate_card_deal
import streamlit as st
from vision_screener import generate_4_corner_zoom_strip

st.set_page_config(page_title="800/Hr Card Arbitrage Sniper", layout="wide")

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

pending = fetch_pending_candidates()
if not pending:
  demo_raw = {
      "item_id": "demo_ohtani_2021",
      "title": (
          "Shohei Ohtani 2021 Topps Game Within The Game #25 Raw (Centered)"
      ),
      "raw_price": 92.00,
      "image_url": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1000&q=85",
      "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=Shohei+Ohtani+2021+Topps+Game+Within+The+Game",
      "seller_id": "socal_estate_finds (0% slabs)",
  }
  demo_eval = evaluate_card_deal(demo_raw, WATCHLIST[0])
  if demo_eval:
    save_candidate(demo_eval)
    pending = fetch_pending_candidates()

if not pending:
  st.success(
      "🎉 Morning queue clear! Overnight bot is hunting for Green-Zone"
      " steals..."
  )
else:
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
        caption=f"Seller: {card['seller_id']}",
        use_container_width=True,
    )

  with col2:
    st.markdown(card["alert_summary"])
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
        st.markdown(
            f"### 👉 [Open eBay Listing to Complete]({card['ebay_url']})"
        )
        st.rerun()
    with b2:
      if st.button(
          "❌ BUGGER (REJECT & TRAIN AI)", use_container_width=True
      ):
        record_user_decision(card["item_id"], "REJECTED", reason)
        st.rerun()