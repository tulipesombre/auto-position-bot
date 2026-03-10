import json
import os

CONFIG_PATH = os.environ.get("CONFIG_PATH", "config.json")

DEFAULT = {
    "capital": 1000.0,
    "risk_pct": 1.0,
    "r_target": 2.0,
    "sl_type": "structural",   # "structural" | "chod"
    "setups": "both",          # "S1" | "S2" | "both"
    "assets": {
        "BTC": True,
        "ETH": True,
        "SOL": True,
        "HYPE": True
    },
    "dr_filter": "off",        # "off" | "soft" | "strict"
    "max_leverage": 40,
    "bot_active": True
}


def load() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        # Merge missing keys with defaults
        for k, v in DEFAULT.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    return DEFAULT.copy()


def save(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def get(key: str, default=None):
    return load().get(key, default)


def set_val(key: str, value) -> dict:
    cfg = load()
    cfg[key] = value
    save(cfg)
    return cfg
