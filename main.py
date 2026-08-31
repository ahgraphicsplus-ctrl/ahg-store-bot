import os
import sys
import logging
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, ADMIN_ID, ADMIN_USERNAME, EMOJIS, PAKISTAN_PAYMENTS, GLOBAL_PAYMENTS
from database import get_connection, init_db, generate_order_id

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# User states dictionary for manual input flows
USER_STATES = {}

# --- HELPER FUNCTIONS ---

def get_or_create_user(user_id, username, first_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name),
        )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
    conn.close()
    return dict(user)

def update_user_field(user_id, field, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()

# --- NAVIGATION KEYBOARDS ---

def get_main_menu_keyboard(user):
    region = user.get("region", "PK")
    currency_label = "PKR 🇵🇰" if region == "PK" else "USD 🌐"
    
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['store']} Products Store", callback_data="cat_all"),
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['profile']} Profile", callback_data="menu_profile"),
            InlineKeyboardButton(f"{EMOJIS['deposit']} Add Funds", callback_data="menu_deposit"),
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['orders']} My Orders", callback_data="menu_orders"),
            InlineKeyboardButton(f"{EMOJIS['replacement']} Claim Replacement", callback_data="menu_replacement"),
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['support']} Live Support", callback_data="menu_support"),
            InlineKeyboardButton(f"🌐 Region: {currency_label}", callback_data="menu_region"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- START & REGION SETUP ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = update.effective_user
    user = get_or_create_user(user_info.id, user_info.username, user_info.first_name)
    
    text = (
        f"👑 <b>AHG DIGITAL GRAPHICS & TOOLS STORE</b> 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 <b>Welcome, {user_info.first_name}!</b>\n\n"
        f"💎 <b>Your #1 Destination For Premium Accounts & Digital Tools</b>\n"
        f"⚡ <i>Instant Manual Delivery Engine | 24/7 Verified Warranties</i>\n\n"
        f"📍 <b>Please choose your currency region below to continue:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🇵🇰 Pakistan (PKR)", callback_data="set_region_PK"),
            InlineKeyboardButton("🌐 Global (USD)", callback_data="set_region_GLOBAL"),
        ]
    ]
    
    if update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_set_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    region = query.data.replace("set_region_", "")
    
    update_user_field(user_id, "region", region)
    user = get_or_create_user(user_id, query.from_user.username, query.from_user.first_name)
    
    curr = "PKR" if region == "PK" else "USD"
    text = (
        f"✅ **Region Set Successfully to {'Pakistan 🇵🇰' if region == 'PK' else 'Global 🌐'}!**\n"
        f"Prices will now be displayed in **{curr}**.\n\n"
        f"Choose an option below to get started:"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard(user))

# --- PROFILE & ORDERS ---

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = update.effective_user
    user = get_or_create_user(user_info.id, user_info.username, user_info.first_name)
    
    text = (
        f"👤 **USER PROFILE**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **User ID**: `{user['user_id']}`\n"
        f"👤 **Name**: {user['first_name']}\n"
        f"🌐 **Selected Region**: {'Pakistan 🇵🇰' if user['region'] == 'PK' else 'Global 🌐'}\n\n"
        f"💰 **PKR Balance**: `Rs. {user['balance_pkr']:.2f}`\n"
        f"💵 **USD Balance**: `${user['balance_usd']:.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['deposit']} Deposit Funds", callback_data="menu_deposit")],
        [InlineKeyboardButton(f"{EMOJIS['back']} Main Menu", callback_data="menu_main")]
    ]
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def my_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10", (user_id,))
    orders = cursor.fetchall()
    conn.close()
    
    if not orders:
        text = "📦 **My Orders**\n\nYou have not placed any orders yet!"
    else:
        text = "📦 **Your Recent Orders (Manual Delivery)**\n━━━━━━━━━━━━━━━━━━━\n\n"
        for o in orders:
            status_emoji = "⏳" if o['status'] == 'PENDING_DELIVERY' else "✅"
            text += (
                f"🆔 **Order ID**: `{o['order_id']}`\n"
                f"🛍️ **Item**: {o['product_name']}\n"
                f"💵 **Price**: {o['currency']} {o['price_paid']}\n"
                f"📌 **Status**: {status_emoji} `{o['status']}`\n"
                f"📅 **Date**: {o['created_at']}\n"
                f"-----------------------------------\n"
            )
            
    keyboard = [[InlineKeyboardButton(f"{EMOJIS['back']} Main Menu", callback_data="menu_main")]]
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# --- STORE & PRODUCTS ---

async def show_store_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_or_create_user(user_id, query.from_user.username, query.from_user.first_name)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products WHERE active = 1")
    categories = [r['category'] for r in cursor.fetchall()]
    conn.close()
    
    keyboard = []
    for cat in categories:
        icon = "⚡"
        if "AI" in cat: icon = EMOJIS['ai']
        elif "Design" in cat: icon = EMOJIS['design']
        elif "Streaming" in cat: icon = EMOJIS['media']
        elif "VPN" in cat: icon = EMOJIS['vpn']
        
        keyboard.append([InlineKeyboardButton(f"{icon} {cat}", callback_data=f"show_cat_{cat}")])
        
    keyboard.append([InlineKeyboardButton(f"{EMOJIS['back']} Main Menu", callback_data="menu_main")])
    
    text = "🛍️ **AHG STORE CATALOG**\nSelect a category to view available digital products and accounts:"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("show_cat_", "")
    user_id = query.from_user.id
    user = get_or_create_user(user_id, query.from_user.username, query.from_user.first_name)
    region = user.get("region", "PK")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ? AND active = 1", (category,))
    products = cursor.fetchall()
    conn.close()
    
    keyboard = []
    for p in products:
        price_str = f"Rs. {p['price_pkr']:.0f}" if region == "PK" else f"${p['price_usd']:.2f}"
        btn_text = f"{p['icon']} {p['name']} - {price_str}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"prod_view_{p['product_id']}")])
        
    keyboard.append([InlineKeyboardButton(f"{EMOJIS['back']} Back to Categories", callback_data="cat_all")])
    
    text = f"📦 **Category: {category}**\nSelect a product to view details and purchase:"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def view_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.replace("prod_view_", ""))
    user_id = query.from_user.id
    user = get_or_create_user(user_id, query.from_user.username, query.from_user.first_name)
    region = user.get("region", "PK")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?", (prod_id,))
    p = cursor.fetchone()
    conn.close()
    
    if not p:
        await query.edit_message_text("Product not found.")
        return
        
    price = p['price_pkr'] if region == "PK" else p['price_usd']
    currency = "PKR" if region == "PK" else "USD"
    user_bal = user['balance_pkr'] if region == "PK" else user['balance_usd']
    
    text = (
        f"{p['icon']} **{p['name']}**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📝 **Description**: {p['description']}\n"
        f"💵 **Price**: `{currency} {price}`\n"
        f"📦 **Stock Status**: `{p['stock_count']} Available`\n"
        f"⚡ **Delivery**: `Manual Admin Delivery (Fast)`\n\n"
        f"👤 **Your Balance**: `{currency} {user_bal:.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    
    keyboard = [
        [InlineKeyboardButton(f"🛒 Buy Now ({currency} {price})", callback_data=f"prod_buy_{p['product_id']}")],
        [InlineKeyboardButton(f"{EMOJIS['deposit']} Add Funds", callback_data="menu_deposit")],
        [InlineKeyboardButton(f"{EMOJIS['back']} Back to Category", callback_data=f"show_cat_{p['category']}")]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# --- MANUAL BUY ENGINE ---

async def handle_buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.replace("prod_buy_", ""))
    user_id = query.from_user.id
    user = get_or_create_user(user_id, query.from_user.username, query.from_user.first_name)
    region = user.get("region", "PK")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?", (prod_id,))
    p = cursor.fetchone()
    
    if not p or p['stock_count'] <= 0:
        await query.edit_message_text("❌ Product out of stock!")
        conn.close()
        return

    price = p['price_pkr'] if region == "PK" else p['price_usd']
    currency = "PKR" if region == "PK" else "USD"
    user_bal = user['balance_pkr'] if region == "PK" else user['balance_usd']

    if user_bal < price:
        text = (
            f"❌ **Insufficient Funds!**\n\n"
            f"Required: `{currency} {price:.2f}`\n"
            f"Your Balance: `{currency} {user_bal:.2f}`\n\n"
            f"Please deposit funds into your account wallet to proceed."
        )
        keyboard = [
            [InlineKeyboardButton(f"{EMOJIS['deposit']} Add Funds Now", callback_data="menu_deposit")],
            [InlineKeyboardButton(f"{EMOJIS['back']} Product Details", callback_data=f"prod_view_{prod_id}")]
        ]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        conn.close()
        return

    # Deduct balance and create Order ID
    order_id = generate_order_id()
    new_bal = user_bal - price
    bal_field = "balance_pkr" if region == "PK" else "balance_usd"
    
    cursor.execute(f"UPDATE users SET {bal_field} = ? WHERE user_id = ?", (new_bal, user_id))
    cursor.execute("UPDATE products SET stock_count = stock_count - 1 WHERE product_id = ?", (prod_id,))
    cursor.execute(
        "INSERT INTO orders (order_id, user_id, product_name, price_paid, currency) VALUES (?, ?, ?, ?, ?)",
        (order_id, user_id, p['name'], price, currency)
    )
    conn.commit()
    conn.close()

    # Success Response to User
    text = (
        f"✅ **ORDER PLACED SUCCESSFULLY!**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **Order ID**: `{order_id}`\n"
        f"🛍️ **Product**: {p['name']}\n"
        f"💵 **Paid**: `{currency} {price}`\n"
        f"📌 **Status**: `PENDING MANUAL DELIVERY`\n\n"
        f"✨ Our admin team has been notified! Your account credentials will be delivered manually to your inbox shortly."
    )
    keyboard = [[InlineKeyboardButton(f"{EMOJIS['orders']} View My Orders", callback_data="menu_orders")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # Alert Admin For Manual Delivery
    admin_alert = (
        f"🚨 **NEW MANUAL DELIVERY ORDER RECEIVED!**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **Order ID**: `{order_id}`\n"
        f"👤 **Customer**: {user['first_name']} (@{user.get('username', 'N/A')})\n"
        f"🆔 **Customer ID**: `{user_id}`\n"
        f"📦 **Product**: {p['name']}\n"
        f"💵 **Price Paid**: {currency} {price}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"➡️ Please contact customer or fulfill order."
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_alert, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to alert admin: {e}")

# --- DEPOSIT / ADD FUNDS ---

async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_or_create_user(user_id, update.effective_user.username, update.effective_user.first_name)
    region = user.get("region", "PK")
    
    keyboard = []
    if region == "PK":
        for pkey, pval in PAKISTAN_PAYMENTS.items():
            keyboard.append([InlineKeyboardButton(f"💳 {pval['title']}", callback_data=f"dep_method_{pkey}")])
    else:
        for gkey, gval in GLOBAL_PAYMENTS.items():
            keyboard.append([InlineKeyboardButton(f"🌐 {gval['title']}", callback_data=f"dep_method_{gkey}")])
            
    keyboard.append([InlineKeyboardButton(f"{EMOJIS['back']} Main Menu", callback_data="menu_main")])
    
    text = (
        f"💳 **ADD FUNDS / WALLET DEPOSIT**\n"
        f"Region: **{'Pakistan 🇵🇰' if region == 'PK' else 'Global 🌐'}**\n\n"
        f"Select your preferred payment gateway below:"
    )
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_deposit_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = query.data.replace("dep_method_", "")
    user_id = query.from_user.id
    user = get_or_create_user(user_id, query.from_user.username, query.from_user.first_name)
    
    info_text = ""
    if method in PAKISTAN_PAYMENTS:
        p = PAKISTAN_PAYMENTS[method]
        info_text = (
            f"🇵🇰 **Payment Details for {p['title']}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Account Title**: `{p.get('account_title', 'AH GRAPHICS STORE')}`\n"
        )
        if "account_number" in p:
            info_text += f"📱 **Account Number**: `{p['account_number']}`\n"
        if "iban" in p:
            info_text += f"🏛️ **IBAN/Raast**: `{p['iban']}`\n"
        info_text += f"\n📝 **Instructions**: {p['instructions']}\n"
    else:
        g = GLOBAL_PAYMENTS.get(method, {})
        info_text = (
            f"🌐 **Payment Details for {g.get('title', method)}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
        )
        if "binance_id" in g:
            info_text += f"🆔 **Binance Pay ID**: `{g['binance_id']}`\n"
        if "address" in g:
            info_text += f"🪙 **USDT TRC20 Address**: `{g['address']}`\n"
        info_text += f"\n📝 **Instructions**: {g.get('instructions', '')}\n"

    info_text += (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📌 After sending payment, reply with your Transaction ID / Screenshot to Admin ({ADMIN_USERNAME})."
    )

    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['support']} Send Proof to Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@','')}")],
        [InlineKeyboardButton(f"{EMOJIS['back']} Back to Payment Methods", callback_data="menu_deposit")]
    ]
    await query.edit_message_text(info_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# --- REPLACEMENT CLAIM & SUPPORT ---

async def replacement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_STATES[user_id] = "WAITING_FOR_CLAIM_ORDER_ID"
    
    text = (
        f"🔄 **CLAIM REPLACEMENT / SUPPORT**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Please enter/type your **Order ID** (e.g. `AHG-XXXXX`) to start your replacement request:"
    )
    keyboard = [[InlineKeyboardButton(f"{EMOJIS['back']} Cancel", callback_data="menu_main")]]
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text_input = update.message.text.strip()
    
    state = USER_STATES.get(user_id)
    if state == "WAITING_FOR_CLAIM_ORDER_ID":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ? AND user_id = ?", (text_input, user_id))
        order = cursor.fetchone()
        conn.close()
        
        if not order:
            await update.message.reply_text("❌ Invalid Order ID or order does not belong to you. Please check and re-type:")
            return
            
        USER_STATES[user_id] = f"CLAIM_DETAILS_{text_input}"
        await update.message.reply_text(
            f"✅ Order `{text_input}` found!\nNow please describe the issue you are facing with this account:"
        )
    elif state and state.startswith("CLAIM_DETAILS_"):
        order_id = state.replace("CLAIM_DETAILS_", "")
        USER_STATES.pop(user_id, None)
        
        # Log to DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO replacements (order_id, user_id, issue_details) VALUES (?, ?, ?)",
            (order_id, user_id, text_input)
        )
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ **Replacement Request Submitted!**\n"
            f"Your ticket for Order `{order_id}` has been sent to our admin team."
        )
        
        # Alert Admin
        admin_text = (
            f"⚠️ **NEW REPLACEMENT CLAIM!**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **Order ID**: `{order_id}`\n"
            f"👤 **Customer**: {update.effective_user.first_name} (@{update.effective_user.username})\n"
            f"📝 **Issue**: {text_input}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"💬 **CUSTOMER SUPPORT & INQUIRIES**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"For custom orders, bulk inquiries, or payment support, contact our admin directly:\n\n"
        f"👤 **Admin TG**: {ADMIN_USERNAME}\n"
        f"🆔 **Admin ID**: `{ADMIN_ID}`"
    )
    keyboard = [
        [InlineKeyboardButton("💬 Chat With Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@','')}")],
        [InlineKeyboardButton(f"{EMOJIS['back']} Main Menu", callback_data="menu_main")]
    ]
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# --- ROUTER & CALLBACK HANDLER ---

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = get_or_create_user(query.from_user.id, query.from_user.username, query.from_user.first_name)
    
    if data == "menu_main":
        await query.answer()
        await start_command(update, context)
    elif data == "menu_profile":
        await query.answer()
        await profile_command(update, context)
    elif data == "menu_orders":
        await query.answer()
        await my_orders_command(update, context)
    elif data == "menu_deposit":
        await query.answer()
        await deposit_command(update, context)
    elif data == "menu_support":
        await query.answer()
        await support_command(update, context)
    elif data == "menu_replacement":
        await query.answer()
        await replacement_command(update, context)
    elif data == "menu_region" or data == "change_region":
        await query.answer()
        await start_command(update, context)
    elif data == "cat_all":
        await show_store_categories(update, context)
    elif data.startswith("show_cat_"):
        await show_category_products(update, context)
    elif data.startswith("prod_view_"):
        await view_product_details(update, context)
    elif data.startswith("prod_buy_"):
        await handle_buy_product(update, context)
    elif data.startswith("set_region_"):
        await handle_set_region(update, context)
    elif data.startswith("dep_method_"):
        await handle_deposit_method(update, context)

# --- BOT LAUNCHER ---

from telegram.request import HTTPXRequest

def main():
    init_db()
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("\n❌ ERROR: Please set your Telegram BOT_TOKEN in config.py or environment variable before running!\n")
        sys.exit(1)
        
    proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if proxy_url:
        request = HTTPXRequest(proxy_url=proxy_url, connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0)
    else:
        request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("orders", my_orders_command))
    app.add_handler(CommandHandler("deposit", deposit_command))
    app.add_handler(CommandHandler("support", support_command))
    app.add_handler(CommandHandler("claim_replacement", replacement_command))
    
    # Callback query and text message handlers
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_messages))
    
    print("🚀 AHG Digital Store Bot is running...")
    app.run_polling(bootstrap_retries=-1)

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
