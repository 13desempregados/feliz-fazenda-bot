# ========================
# Feliz Fazenda Bot - Parte 1 (main.py - início)
# ========================

import logging
import time
import threading
import json
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import requests

from config import TOKEN, NOWPAYMENTS_API_KEY, USDT_TRC20, USDT_BEP20

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
    {"emoji": "🐎", "name": "Cavalo", "price": 50000, "per_hour": 5000},
    {"emoji": "🐂", "name": "Boi", "price": 75000, "per_hour": 12500},
    {"emoji": "🦁", "name": "Leão", "price": 100000, "per_hour": 25000}
]

# ========================
# FUNÇÕES
# ========================

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(users_data, f)

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)
    args = context.args
    ref_id = args[0] if args else None

    if user_id not in users_data:
        users_data[user_id] = {
            'username': user.username,
            'bars': 20000,
            'animals': [],
            'ref_id': ref_id,
            'referrals': [],
            'balance': 0,
            'last_collected': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        # Paga bônus para referrer
        if ref_id and ref_id in users_data:
            users_data[ref_id]['bars'] += 1000
            if user_id not in users_data[ref_id]['referrals']:
                users_data[ref_id]['referrals'].append(user_id)
        save_data()

    keyboard = [
        [InlineKeyboardButton("🎮 Meus Animais", callback_data='my_animals')],
        [InlineKeyboardButton("🛒 Comprar Animais", callback_data='buy_animals')],
        [InlineKeyboardButton("💰 Meu Saldo", callback_data='my_balance')],
        [InlineKeyboardButton("➕ Adicionar Barras de Ouro", callback_data='add_gold')],
        [InlineKeyboardButton("📤 Sacar", callback_data='withdraw')],
        [InlineKeyboardButton("👥 Meus Indicados", callback_data='referrals')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"🌾 *Feliz Fazenda Bot*\n"
        f"👥 *45.915 monthly users*\n\n"
        f"🎁 Você ganhou *20.000 barras de ouro grátis*!\n"
        f"🐣 Indique amigos e ganhe bônus!\n"
        f"🏦 Depósitos automáticos — mínimo 1 USDT\n\n"
        f"Clique abaixo para começar 👇",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
# ========================
# Parte 2 - Funções dos botões
# ========================

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
    user_data = users_data.get(user_id, {})

    if query.data == 'my_animals':
        animals_list = user_data.get('animals', [])
        if not animals_list:
            msg = "🐾 Você ainda não possui animais.\n🛒 Compre na loja!"
        else:
            msg = "🐾 *Seus Animais:*\n\n"
            for animal in animals_list:
                msg += f"{animal['emoji']} {animal['name']} | {animal['per_hour']} barras/hora\n"
        query.edit_message_text(msg, parse_mode='Markdown')

    elif query.data == 'buy_animals':
        keyboard = []
        for animal in animals:
            keyboard.append([InlineKeyboardButton(
                f"{animal['emoji']} {animal['name']} — {animal['price']} barras",
                callback_data=f"buy_{animal['name'].lower()}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data='back')])
        query.edit_message_text("🛒 *Comprar Animais*\n\nEscolha um animal para comprar:",
                                reply_markup=InlineKeyboardMarkup(keyboard),
                                parse_mode='Markdown')

    elif query.data == 'my_balance':
        bars = user_data.get('bars', 0)
        referrals = user_data.get('referrals', [])
        msg = (
            f"💰 *Seu Saldo:*\n\n"
            f"💎 Barras de Ouro: {bars}\n"
            f"👥 Indicados Nível 1: {len(referrals)}\n"
            f"🚀 Produção por hora: {sum(a['per_hour'] for a in user_data.get('animals', []))}"
        )
        query.edit_message_text(msg, parse_mode='Markdown')

    elif query.data == 'add_gold':
        keyboard = [
            [InlineKeyboardButton("💳 USDT TRC20", callback_data='add_trc')],
            [InlineKeyboardButton("💳 USDT BEP20", callback_data='add_bep')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
        ]
        query.edit_message_text("➕ *Adicionar Barras de Ouro*\n\nEscolha a rede para pagamento:",
                                reply_markup=InlineKeyboardMarkup(keyboard),
                                parse_mode='Markdown')

    elif query.data == 'withdraw':
        bars = user_data.get('bars', 0)
        msg = (
            f"📤 *Saque*\n\n"
            f"💎 Saldo disponível: {bars}\n"
            f"💵 Taxa de conversão: 1M barras = 2 USDT\n"
            f"🔒 Saque mínimo: 1M barras\n\n"
            f"⚠️ Para solicitar saque, envie /withdraw VALOR (em USDT)."
        )
        query.edit_message_text(msg, parse_mode='Markdown')

    elif query.data == 'referrals':
        referrals = user_data.get('referrals', [])
        msg = (
            f"👥 *Meus Indicados*\n\n"
            f"Nível 1: {len(referrals)}\n\n"
            f"Seu link de convite:\n"
            f"https://t.me/{context.bot.username}?start={user_id}"
        )
        query.edit_message_text(msg, parse_mode='Markdown')

    elif query.data == 'back':
        start(update, context)

    elif query.data.startswith('buy_'):
        animal_name = query.data.split('_')[1].capitalize()
        animal = next((a for a in animals if a['name'] == animal_name), None)
        if animal and user_data['bars'] >= animal['price']:
            user_data['bars'] -= animal['price']
            user_data['animals'].append(animal)
            save_data()
            query.edit_message_text(
                f"✅ Você comprou {animal['emoji']} *{animal['name']}*!\n"
                f"🐾 Ele produzirá {animal['per_hour']} barras por hora.",
                parse_mode='Markdown'
            )
        else:
            query.edit_message_text("❌ Saldo insuficiente para comprar este animal.")

    elif query.data == 'add_trc':
        msg = (
            f"💳 *USDT TRC20*\n\n"
            f"Endereço:\n`{USDT_TRC20}`\n\n"
            f"✅ Depósitos automáticos\n"
            f"💵 Mínimo: 1 USDT\n"
            f"🎁 Bônus: +20% em barras de ouro\n\n"
            f"⚠️ Após enviar o pagamento, o saldo será creditado automaticamente."
        )
        query.edit_message_text(msg, parse_mode='Markdown')

    elif query.data == 'add_bep':
        msg = (
            f"💳 *USDT BEP20*\n\n"
            f"Endereço:\n`{USDT_BEP20}`\n\n"
            f"✅ Depósitos automáticos\n"
            f"💵 Mínimo: 1 USDT\n"
            f"🎁 Bônus: +20% em barras de ouro\n\n"
            f"⚠️ Após enviar o pagamento, o saldo será creditado automaticamente."
        )
        query.edit_message_text(msg, parse_mode='Markdown')

    save_data()
# ========================
# Parte 3 - Produção por hora + comandos admin
# ========================

def collect_production():
    while True:
        time.sleep(3600)  # a cada 1 hora
        for user_id, data in users_data.items():
            prod = sum(a['per_hour'] for a in data.get('animals', []))
            data['bars'] += prod
            data['last_collected'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        save_data()

def withdraw_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)
    user_data = users_data.get(user_id, {})
    bars = user_data.get('bars', 0)

    if not context.args:
        update.message.reply_text("❌ Use o comando: /withdraw VALOR (em USDT)\nExemplo: /withdraw 10")
        return

    try:
        amount_usdt = float(context.args[0])
    except:
        update.message.reply_text("❌ Valor inválido.")
        return

    needed_bars = int(amount_usdt * 500000)  # 1M barras = 2 USDT

    if bars < needed_bars:
        update.message.reply_text(
            f"❌ Você não tem barras suficientes.\n"
            f"💎 Saldo atual: {bars}\n"
            f"📝 Necessário: {needed_bars} barras para sacar {amount_usdt} USDT."
        )
        return

    # Marca saque pendente
    user_data['bars'] -= needed_bars
    save_data()

    update.message.reply_text(
        f"✅ Pedido de saque de {amount_usdt} USDT registrado!\n"
        f"⏳ Aguardando aprovação do administrador.\n\n"
        f"Seu saldo foi atualizado."
    )

    # Notifica admin
    context.bot.send_message(
        chat_id=ADMIN_ID,  # coloque seu ID de admin aqui no config.py
        text=(
            f"📤 NOVO PEDIDO DE SAQUE!\n\n"
            f"👤 @{user.username} (ID: {user_id})\n"
            f"💵 {amount_usdt} USDT solicitado\n"
            f"✅ Aprovar manualmente!"
        )
    )

# ========================
# Main do Bot
# ========================

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler('withdraw', withdraw_command))

    prod_thread = threading.Thread(target=collect_production)
    prod_thread.daemon = True
    prod_thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
