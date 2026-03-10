# Auto Position Bot

Bot de trading automatisé pour Hyperliquid, piloté par des alertes TradingView.

---

## Architecture

```
TradingView (PineScript M5)
  ├─ SETUP_ARMED ──→ Railway /webhook → forward Discord
  └─ ENTRY       ──→ Railway /webhook → trade Hyperliquid + notif Discord
```

---

## Installation

### 1. Créer le bot Discord

1. Va sur https://discord.com/developers/applications
2. "New Application" → donne un nom
3. Onglet "Bot" → "Add Bot" → copie le **Token**
4. Onglet "OAuth2" → "URL Generator"
   - Scopes : `bot` + `applications.commands`
   - Bot Permissions : `Send Messages` + `Embed Links` + `Use Slash Commands`
5. Copie l'URL générée → ouvre dans ton navigateur → invite le bot sur ton serveur
6. Dans Discord : clic droit sur le channel de trading → "Copy Channel ID" (active le mode développeur si besoin dans Paramètres > Avancés)

### 2. Déployer sur Railway

1. Push ce repo sur GitHub
2. Sur Railway : "New Project" → "Deploy from GitHub repo"
3. Dans "Variables" du projet Railway, ajouter :

| Variable | Valeur |
|---|---|
| `HL_PRIVATE_KEY` | Ta clé privée Hyperliquid |
| `DISCORD_BOT_TOKEN` | Token du bot Discord |
| `DISCORD_CHANNEL_ID` | ID du channel de trading |

4. Le déploiement se fait automatiquement — note l'URL du projet (ex: `auto-position-bot-production.up.railway.app`)

### 3. Configurer les alertes TradingView

Pour chaque asset crypto (BTC, ETH, SOL, HYPE) :

1. Sur le chart M5 avec l'indicateur
2. Créer une alerte → "Tout appel de la fonction alerte()"
3. Dans "Notifications" → activer Webhook
4. URL du webhook : `https://auto-position-bot-production.up.railway.app/webhook`
5. **Ne pas cocher Discord** — le bot s'en charge

---

## Commandes Discord

| Commande | Description |
|---|---|
| `/config` | Voir la configuration actuelle |
| `/set param value` | Modifier un paramètre |
| `/toggle_asset BTC` | Activer/désactiver un asset |
| `/pause` | Mettre le bot en pause |
| `/resume` | Reprendre le bot |
| `/positions` | Voir les positions ouvertes |
| `/balance` | Voir le solde du compte |

### Paramètres configurables via `/set`

| Paramètre | Valeurs | Défaut |
|---|---|---|
| `capital` | montant USDC | 1000 |
| `risk_pct` | % du capital risqué | 1.0 |
| `r_target` | ratio TP (ex: 2) | 2.0 |
| `sl_type` | `structural` / `chod` | `structural` |
| `setups` | `S1` / `S2` / `both` | `both` |
| `dr_filter` | `off` / `soft` / `strict` | `off` |
| `max_leverage` | nombre entier | 40 |

### Filtre DR

| Mode | Comportement |
|---|---|
| `off` | Rentre peu importe le DR |
| `soft` | Bloque si DR explicitement contraire |
| `strict` | N'entre que si DR aligné (✓ ou ✓✓) |

---

## Boutons interactifs

Chaque trade ouvert génère un embed Discord avec :

- **🛡️ SL au BE** : déplace le Stop-Loss au prix d'entrée
- **❌ Fermer position** : ferme la position au marché + annule SL/TP

---

## Note sur la persistance de la config

La config est stockée dans `config.json` sur le filesystem Railway.
Elle **survit aux redémarrages** mais se réinitialise à chaque **redéploiement**.

Pour une persistance totale, activer un **Persistent Volume** dans Railway :
- Railway Dashboard → ton projet → "Add Volume" → monter sur `/app`
- Puis mettre `CONFIG_PATH=/app/config.json` dans les variables d'environnement

---

## Structure du projet

```
├── main.py                 ← Point d'entrée
├── webhook.py              ← Flask + routing des alertes TradingView
├── discord_bot.py          ← Bot Discord, commandes slash, boutons
├── hyperliquid_client.py   ← API Hyperliquid (ordres, positions)
├── risk_manager.py         ← Calcul position, sizing, validation
├── config_manager.py       ← Lecture/écriture config.json
├── config.json             ← Config par défaut
├── requirements.txt
├── Procfile
└── .env.example
```
