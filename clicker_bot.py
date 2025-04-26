python
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from flask import Flask, request
import threading

app = Flask(name)

# ====== НАСТРОЙКИ ======
TOKEN = "ВАШ_ТОКЕН_БОТА"  # Замените на токен от @BotFather
GREEN_THEME = "🟢"        # Зелёный интерфейс

# ====== БАЗА ДАННЫХ ======
conn = sqlite3.connect('clicker.db', check_same_thread=False)
cursor = conn.cursor()

# Создаём таблицы
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    click_power INTEGER DEFAULT 1,
    auto_power INTEGER DEFAULT 0
)
''')
conn.commit()

# ====== МАГАЗИНЫ ======
CLICK_SHOP = {
    "Улучшенный клик": {"price": 700, "power": 2},
    "Мега клик": {"price": 1500, "power": 5},
    # Добавьте ещё 8 товаров...
}

AUTO_SHOP = {
    "Автоклик Lv1": {"price": 400, "power": 1},
    "Автоклик Lv2": {"price": 1000, "power": 3},
    # Добавьте ещё 8 товаров...
}

# ====== ФУНКЦИИ ======
def get_user_data(user_id):
    cursor.execute("SELECT coins, click_power, auto_power FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    if not data:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 0, 1, 0
    return data

# ====== КЛАВИАТУРЫ ======
def main_menu(user_id):
    coins, click_power, auto_power = get_user_data(user_id)
    buttons = [
        [InlineKeyboardButton(f"{GREEN_THEME} Клик (+{click_power})", callback_data="click")],
        [InlineKeyboardButton(f"{GREEN_THEME} Магазин кликов", callback_data="click_shop")],
        [InlineKeyboardButton(f"{GREEN_THEME} Магазин автокликов", callback_data="auto_shop")],
    ]
    return InlineKeyboardMarkup(buttons)

# ====== ОБРАБОТЧИКИ ======
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    update.message.reply_text(
        f"{GREEN_THEME} Добро пожаловать в кликер!",
        reply_markup=main_menu(user_id)
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "click":
        # Логика клика
        cursor.execute("UPDATE users SET coins = coins + click_power WHERE user_id=?", (user_id,))
        conn.commit()
        query.answer(f"+{get_user_data(user_id)[1]} coins!")
    
    # Обновляем меню
    query.edit_message_reply_markup(reply_markup=main_menu(user_id))

# ====== ЗАПУСК ======
def run_bot():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    updater.start_polling()
    updater.idle()

# ====== WEB-ИНТЕРФЕЙС (для Netlify) ======
@app.route('/')
def web_interface():
    return "Бот работает! Используйте Telegram для игры."

if name == 'main':
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot).start()
    # Запускаем Flask для Netlify
    app.run(host='0.0.0.0', port=8080)