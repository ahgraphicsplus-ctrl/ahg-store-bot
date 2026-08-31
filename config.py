import os

# Telegram Bot Credentials & Admin Info
BOT_TOKEN = os.getenv("BOT_TOKEN", "8936159404:AAE9N-dVSaAW6hmO1Tv1UoJPQHgQBMiHjFk")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7760560490"))
ADMIN_USERNAME = "@AHGRAPHICSSTORE" # Update with your exact TG username

# Currency Settings
DEFAULT_PKR_TO_USD_RATE = 280.0  # 1 USD = 280 PKR (adjustable)

# Telegram Premium Animated Emoji IDs (placeholders / configurable)
# Format: <tg-emoji emoji-id="5368324170671202286">⚡</tg-emoji>
EMOJIS = {
    "welcome": '<tg-emoji emoji-id="5368324170671202286">⚡</tg-emoji>',
    "store": '<tg-emoji emoji-id="5469910609355938830">🛍️</tg-emoji>',
    "profile": '<tg-emoji emoji-id="5429177114674457492">👤</tg-emoji>',
    "deposit": '<tg-emoji emoji-id="5467576288766925574">💳</tg-emoji>',
    "support": '<tg-emoji emoji-id="5472147746973361171">💬</tg-emoji>',
    "replacement": '<tg-emoji emoji-id="5463131758655250438">🔄</tg-emoji>',
    "orders": '<tg-emoji emoji-id="5472097092145851419">📦</tg-emoji>',
    "back": '<tg-emoji emoji-id="5427009714743026179">⬅️</tg-emoji>',
    "star": '<tg-emoji emoji-id="5467576288766925574">⭐</tg-emoji>',
    "sparkles": '<tg-emoji emoji-id="5368324170671202286">✨</tg-emoji>',
    "check": '<tg-emoji emoji-id="5427009714743026179">✅</tg-emoji>',
    "cross": '<tg-emoji emoji-id="5463131758655250438">❌</tg-emoji>',
    "fire": '<tg-emoji emoji-id="5467576288766925574">🔥</tg-emoji>',
    "vpn": '<tg-emoji emoji-id="5469910609355938830">🛡️</tg-emoji>',
    "ai": '<tg-emoji emoji-id="5368324170671202286">🤖</tg-emoji>',
    "media": '<tg-emoji emoji-id="5472097092145851419">🎬</tg-emoji>',
    "design": '<tg-emoji emoji-id="5429177114674457492">🎨</tg-emoji>',
    "crown": '<tg-emoji emoji-id="5467576288766925574">👑</tg-emoji>',
    "diamond": '<tg-emoji emoji-id="5368324170671202286">💎</tg-emoji>',
}

# Pakistan Payment Details (Easypaisa / JazzCash / Raast Bank)
PAKISTAN_PAYMENTS = {
    "EasyPaisa": {
        "title": "EasyPaisa",
        "account_title": "AH GRAPHICS STORE",
        "account_number": "03XXXXXXXXX",
        "instructions": "Send amount to EasyPaisa and submit TxID / Screenshot reference."
    },
    "JazzCash": {
        "title": "JazzCash",
        "account_title": "AH GRAPHICS STORE",
        "account_number": "03XXXXXXXXX",
        "instructions": "Send amount to JazzCash and submit TxID / Screenshot reference."
    },
    "Raast / Bank": {
        "title": "Bank Transfer / Raast",
        "bank_name": "Meezan Bank",
        "account_title": "AH GRAPHICS STORE",
        "iban": "PK00MEEZ0000000000000000",
        "instructions": "Transfer to IBAN/Raast ID and upload reference number."
    }
}

# Global Payment Details (Binance Pay / Crypto)
GLOBAL_PAYMENTS = {
    "Binance Pay": {
        "title": "Binance Pay",
        "binance_id": "7760560490", # or your Binance Pay ID
        "instructions": "Send USDT via Binance Pay ID and submit order TxID/Order ID."
    },
    "USDT (TRC20)": {
        "title": "USDT (TRC20)",
        "address": "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "instructions": "Send USDT (TRC20) to address and submit transaction hash."
    }
}
