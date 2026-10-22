# math_engine.py
from datetime import datetime, timedelta
from config import (
    MIN_GEM_RATE_FLOOR,
    MIN_ROTI_DOLLARS_PER_HR,
    PSA_TIERS,
    TOUCH_TIME_HOURS_PER_CARD,
    UNICORN_MIN_GEM_RATE,
)


def evaluate_card_deal(card: dict, watch_cfg: dict) -> dict | None:
  tier_name = watch_cfg["tier"]
  t = PSA_TIERS[tier_name]
  psa_fee = t["fee"]
  gem_rate = watch_cfg["gem_rate"]

  psa9_floor = min(watch_cfg["last_3_psa9"])
  psa10_floor = min(watch_cfg["last_3_psa10"])

  ceiling_by_psa9 = (psa9_floor * 0.90) - psa_fee - 15.00
  ceiling_by_psa10 = (psa10_floor / 2.8) - psa_fee
  walk_away_ceiling = round(min(ceiling_by_psa9, ceiling_by_psa10), 2)
  if watch_cfg.get("is_offseason_dip", True):
    walk_away_ceiling = round(walk_away_ceiling * 0.92, 2)

  green_buy_max = round(walk_away_ceiling * 0.88, 2)
  target_offer = round(green_buy_max * 0.97, 2)

  raw_price = card["raw_price"]
  if raw_price > walk_away_ceiling:
    return None

  all_in = round(raw_price + psa_fee, 2)
  multiplier = round(psa10_floor / all_in, 2)
  psa10_net_payout = round(psa10_floor * 0.90, 2)
  psa10_net_profit = round(psa10_net_payout - all_in, 2)
  psa9_net_profit = round((psa9_floor * 0.90) - all_in, 2)
  roti_hr = round(psa10_net_profit / TOUCH_TIME_HOURS_PER_CARD)

  if roti_hr < MIN_ROTI_DOLLARS_PER_HR:
    return None

  if gem_rate >= MIN_GEM_RATE_FLOOR:
    if multiplier < 2.8 or psa10_net_profit < 280:
      return None
    gem_badge = "🎯 Gem Rate: " + str(int(gem_rate * 100)) + "% (Clears Floor)"
  elif gem_rate >= UNICORN_MIN_GEM_RATE:
    if multiplier < 3.3 or psa10_net_profit < 650 or psa9_net_profit < -10:
      return None
    gem_badge = "🦄 Gem Rate: " + str(int(gem_rate * 100)) + "% (Unicorn)"
  else:
    return None

  breakeven_psa10 = round(all_in / 0.90, 2)
  max_drop_pct = round(
      ((psa10_floor - breakeven_psa10) / psa10_floor) * 100, 1
  )
  crashed_30_net = round(((psa10_floor * 0.70) * 0.90) - all_in, 2)
  if crashed_30_net < 100:
    return None

  if raw_price <= green_buy_max:
    zone_status = "🟢 GREEN ZONE: INSTANT BUY"
    action_text = "BUY NOW AT $" + str(raw_price)
  else:
    zone_status = "🟡 YELLOW ZONE: OFFER ONLY"
    action_text = "FIRE OFFER"

  return_date = (datetime.now() + timedelta(days=t["cal_days"])).strftime(
      "%b %d, %Y"
  )

  alert_summary = (
      zone_status
      + "\n🃏 "
      + str(card["title"])
      + "\n💵 All-In: $"
      + str(all_in)
      + "\n💎 PSA 10 Floor: $"
      + str(psa10_floor)
      + " (Net: $"
      + str(psa10_net_profit)
      + ")"
      + "\n⏱️ Payback: "
      + return_date
  )

  return {
      **card,
      "tier": tier_name,
      "psa9_floor": psa9_floor,
      "psa10_floor": psa10_floor,
      "gem_rate": gem_rate,
      "zone_status": zone_status,
      "action_text": action_text,
      "alert_summary": alert_summary,
      "roti_hr": roti_hr,
      "psa10_net_profit": psa10_net_profit,
      "psa9_net_profit": psa9_net_profit,
  }
