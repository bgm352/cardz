# ebay_client.py
import base64
import os
import re
import xml.etree.ElementTree as ET
from config import MAX_SELLER_SLAB_RATIO, NEGATIVE_EBAY_KEYWORDS, RED_FLAG_DESCRIPTION_PHRASES
import requests


def get_ebay_oauth_token() -> str | None:
  app_id = os.environ.get("EBAY_APP_ID", "")
  cert_id = os.environ.get("EBAY_CERT_ID", "")
  if not app_id or not cert_id:
    return None
  url = "https://api.ebay.com/identity/v1/oauth2/token"
  encoded = base64.b64encode(f"{app_id}:{cert_id}".encode()).decode()
  headers = {
      "Content-Type": "application/x-www-form-urlencoded",
      "Authorization": f"Basic {encoded}",
  }
  data = {
      "grant_type": "client_credentials",
      "scope": "https://api.ebay.com/oauth/api_scope",
  }
  resp = requests.post(url, headers=headers, data=data, timeout=10)
  resp.raise_for_status()
  return resp.json()["access_token"]


def search_ebay_no_key_rss(query: str, max_ceiling: float) -> list[dict]:
  """Zero-Key Fallback: Pulls real, live eBay listings via eBay's public RSS feed

  when EBAY_APP_ID is not set yet.
  """
  clean_q = f"{query} -PSA -BGS -SGC -lot -reprint"
  url = "https://www.ebay.com/sch/i.html"
  params = {
      "_nkw": clean_q,
      "_sacat": "261328",
      "LH_ItemCondition": "4000",  # Strictly Ungraded Raw Cards
      "_udlo": "25",
      "_udhi": str(int(max_ceiling)),
      "_sop": "10",  # Newly listed
      "_rss": "1",
  }
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
  survivors = []
  try:
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
      return []
    root = ET.fromstring(resp.text)
    for item in root.findall(".//item")[:8]:
      title = item.findtext("title", "")
      link = item.findtext("link", "")
      desc = item.findtext("description", "")

      if any(p in title.lower() for p in RED_FLAG_DESCRIPTION_PHRASES):
        continue

      # Extract price and image URL from RSS description HTML
      price_match = re.search(r"\$([0-9,]+\.[0-9]{2})", desc)
      img_match = re.search(
          r'src="(https://i\.ebayimg\.com/[^"]+)"', desc
      )
      if not price_match or not img_match:
        continue

      raw_price = float(price_match.group(1).replace(",", ""))
      if raw_price > max_ceiling:
        continue

      high_res_img = re.sub(
          r"s-l\d+\.jpg", "s-l1600.jpg", img_match.group(1)
      )
      item_id_match = re.search(r"/itm/(\d+)", link)
      item_id = (
          item_id_match.group(1) if item_id_match else link[-12:]
      )

      survivors.append({
          "item_id": item_id,
          "title": title,
          "raw_price": raw_price,
          "image_url": high_res_img,
          "ebay_url": link,
          "seller_id": "Live eBay RSS (No-Key Mode)",
          "seller_slab_pct": 0.0,
      })
  except Exception:
    pass
  return survivors


def search_ultra_picky_raw_cards(
    query: str, max_ceiling: float, token: str | None = None
) -> list[dict]:
  # Automatically use Zero-Key RSS mode if no eBay API token is present!
  if not token:
    return search_ebay_no_key_rss(query, max_ceiling)

  url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
  headers = {
      "Authorization": f"Bearer {token}",
      "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
  }
  params = {
      "q": f"{query} {NEGATIVE_EBAY_KEYWORDS}",
      "category_ids": "261328",
      "filter": (
          f"conditionIds:{{4000}},price:[25..{max_ceiling}],priceCurrency:USD"
      ),
      "sort": "newlyListed",
      "limit": 10,
  }
  resp = requests.get(url, headers=headers, params=params, timeout=10)
  resp.raise_for_status()
  items = resp.json().get("itemSummaries", [])

  survivors = []
  for item in items:
    title_lower = item.get("title", "").lower()
    if any(phrase in title_lower for phrase in RED_FLAG_DESCRIPTION_PHRASES):
      continue
    if not item.get("additionalImages"):
      continue

    price = float(item.get("price", {}).get("value", 0))
    shipping = 0.0
    ship_opts = item.get("shippingOptions", [])
    if ship_opts and "shippingCost" in ship_opts[0]:
      shipping = float(ship_opts[0]["shippingCost"].get("value", 0))

    img_url = (
        item.get("image", {})
        .get("imageUrl", "")
        .replace("s-l225.jpg", "s-l1600.jpg")
    )

    survivors.append({
        "item_id": item.get("itemId"),
        "title": item.get("title"),
        "raw_price": round(price + shipping, 2),
        "image_url": img_url,
        "ebay_url": item.get("itemWebUrl"),
        "seller_id": item.get("seller", {}).get("username", "eBay Seller"),
        "seller_slab_pct": 0.0,
    })
  return survivors
