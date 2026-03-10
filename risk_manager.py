import logging
from config_manager import load

logger = logging.getLogger(__name__)

# TradingView ticker → Hyperliquid coin name
TICKER_MAP = {
    "BTCUSDT.P":  "BTC",
    "ETHUSDT.P":  "ETH",
    "SOLUSDT.P":  "SOL",
    "HYPEUSDT.P": "HYPE",
}

# Coin size precision (decimal places) and minimum size on Hyperliquid
COIN_PRECISION = {
    "BTC":  5,
    "ETH":  4,
    "SOL":  2,
    "HYPE": 1,
}

COIN_MIN_SIZE = {
    "BTC":  0.0001,
    "ETH":  0.001,
    "SOL":  0.1,
    "HYPE": 1.0,
}


def get_coin(ticker: str) -> str:
    return TICKER_MAP.get(ticker, ticker.replace("USDT.P", "").replace("USDT", ""))


def should_trade(setup: str, ticker: str, dr_detail: str) -> tuple[bool, str]:
    cfg = load()

    if not cfg["bot_active"]:
        return False, "🔴 Bot en pause"

    coin = get_coin(ticker)
    if not cfg["assets"].get(coin, False):
        return False, f"🔴 {coin} désactivé dans la config"

    # Setup filter
    setups = cfg["setups"]
    if setups != "both" and setup != setups:
        return False, f"🔴 Setup {setup} désactivé (actif : {setups})"

    # DR filter
    dr_filter = cfg["dr_filter"]
    if dr_filter == "soft" and "contraire" in dr_detail:
        return False, f"🔴 DR contraire bloqué (mode soft)"
    if dr_filter == "strict" and "✓" not in dr_detail:
        return False, f"🔴 DR non aligné bloqué (mode strict)"

    return True, "✅ OK"


def calc_max_safe_leverage(entry: float, sl: float, is_long: bool, safety: float = 0.8) -> int:
    """
    Calcule le levier maximum pour que la liquidation reste au-delà du SL.
    Pour un long : liq ≈ entry * (1 - 1/lev)  → on veut liq < sl
    safety = 0.8 donne 20% de marge supplémentaire.
    """
    if is_long:
        dist_pct = (entry - sl) / entry
    else:
        dist_pct = (sl - entry) / entry

    if dist_pct <= 0:
        return 1

    max_lev = safety / dist_pct
    return max(1, int(max_lev))


def calc_position(entry: float, sl: float, balance: float) -> dict:
    cfg = load()
    is_long = sl < entry
    risk_usd = balance * (cfg["risk_pct"] / 100)
    sl_dist = abs(entry - sl)
    sl_pct = sl_dist / entry

    if sl_pct == 0:
        raise ValueError("Distance SL = 0, impossible de calculer la position")

    # Position value = risk / sl% → size en coins
    position_usd = risk_usd / sl_pct
    size_raw = position_usd / entry

    r = cfg["r_target"]
    tp = entry + sl_dist * r if is_long else entry - sl_dist * r

    # Levier : minimum entre max safe et max configuré
    max_safe = calc_max_safe_leverage(entry, sl, is_long)
    max_cfg = cfg.get("max_leverage", 40)
    leverage = max(1, min(max_safe, max_cfg))

    return {
        "size_raw":     size_raw,
        "position_usd": round(position_usd, 2),
        "risk_usd":     round(risk_usd, 2),
        "tp":           tp,
        "sl":           sl,
        "entry":        entry,
        "leverage":     leverage,
        "is_long":      is_long,
        "sl_pct":       round(sl_pct * 100, 3),
        "r_target":     r,
    }


def round_size(coin: str, size_raw: float) -> float:
    """Arrondit la taille au pas du coin et vérifie le minimum."""
    precision = COIN_PRECISION.get(coin, 4)
    min_size  = COIN_MIN_SIZE.get(coin, 0.001)
    size = round(size_raw, precision)
    if size < min_size:
        raise ValueError(f"Taille calculée ({size}) inférieure au minimum ({min_size}) pour {coin}")
    return size
