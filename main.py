# ================================
# Feliz Fazenda Bot — main.py
# ================================

import logging
import time
import threading
import json
import os
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters
)
import requests

from config import TOKEN, NOWPAYMENTS_API_KEY, USDT_TRC20, USDT_BEP20

logging.basicConfig(
    format='%(asctime)s — %(name)s — %(levelname)s — %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DATA_FILE = 'users_data.json'

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        users_data = json.load(f)
else:
    users_data = {}

# TABELA DE PLANOS DE BARRAS
plans = [
    {"usdt": 10, "bars": 10000},
    {"usdt": 30, "bars": 30000},
    {"usdt": 50, "bars": 50000},
    {"usdt": 75, "bars": 75000},
    {"usdt": 100, "bars": 100000}
]

# ANIMAIS
animals = [
    {"emoji": "🐱", "name": "Gato", "price": 10000, "per_hour": 500},
    {"emoji": "🐶", "name": "Cachorro", "price": 30000, "per_hour": 1500},
    {"emoji": "🐴", "name": "Cavalo", "price": 50000, "per_hour": 5000},
    {"emoji": "🐮", "name": "Boi", "price": 75000, "per_hour": 12500},
    {"emoji": "🦁", "name": "Leão", "price": 100000, "per_hour": 25000}
]

# COMANDO /start DO BOT
def start(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)

    if user_id not in users_data:
        users_data[user_id] = {
            "bars": 0,
            "animals": [],
            "last_collect": str(datetime.utcnow())
        }
        save_data()

    keyboard = [
        [InlineKeyboardButton("🐾 Comprar Animais", callback_data='buy_animals')],
        [InlineKeyboardButton("💰 Ver Saldo", callback_data='check_balance')],
        [InlineKeyboardButton("📊 Planos de Barras", callback_data='view_plans')],
        [InlineKeyboardButton("💵 Depositar", callback_data='deposit')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("🐮 Bem-vindo à sua Fazenda Feliz!\nEscolha uma opção abaixo:", reply_markup=reply_markup)

# Função para salvar os dados em JSON
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

# CONFIGURAÇÃO DO BOT
def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
