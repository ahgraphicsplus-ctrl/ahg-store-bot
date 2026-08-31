# AHGTOOLSSTORE Telegram Bot

A Telegram Digital Products Store Bot supporting manual delivery, multi-currency display (PKR / USD), Binance & Pakistan payment instructions, custom order IDs, and warranty replacement handling.

---

## 🚀 How to Launch Your Bot

### Step 1: Open `config.py`
Open `config.py` in your text editor and set your Telegram Bot Token from `@BotFather`:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
ADMIN_ID = 7760560490
ADMIN_USERNAME = "@AHGRAPHICSSTORE"
```

Also update your payment details in `config.py`:
- **EasyPaisa / JazzCash / Raast Bank Numbers**
- **Binance Pay ID / USDT TRC20 Address**

---

## 🏃 Running the Bot

Run the following command in your terminal inside this directory:

```bash
python main.py
```

---

## 🛠️ Features Included

1. **Onboarding & Currency Engine**:
   - **Pakistan 🇵🇰**: Shows prices in PKR, EasyPaisa, JazzCash, Raast transfer methods.
   - **Global 🌐**: Shows prices in USD, Binance Pay ID & USDT TRC20 crypto deposits.

2. **Digital Store & Accounts**:
   - Pre-populated with **ChatGPT Plus**, **Gemini Pro**, **Canva Pro**, **Envato Elements**, **CapCut Pro**, **Netflix 4K**, **Amazon Prime**, **HBO Max**, **Paramount+**, **IPTV**, **NordVPN**, **ExpressVPN**, **TunnelBear VPN**, and easy to add more.

3. **Manual Delivery Workflow**:
   - Customer places order -> Unique Order ID (e.g. `AHG-8F92K`) generated.
   - Immediate notification alert sent directly to your Telegram Admin ID (`7760560490`).

4. **Support & Claim Replacement System**:
   - `/claim_replacement` command prompts user for Order ID & issue details.
   - Instantly routes ticket alert to your Telegram Admin inbox.

5. **Menu Navigation**:
   - Full command list (`/start`, `/profile`, `/orders`, `/deposit`, `/support`, `/claim_replacement`).
   - Interactive Inline Keyboards with `⬅️ Back` buttons at all levels.
