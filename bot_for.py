import telebot
from telebot import types
import json
import os
from datetime import datetime
from dotenv import load_dotenv


# =========================
# НАСТРОЙКИ
# =========================

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

ORDERS_FILE = "orders.json"
SERVICES_FILE = "services.json"


# =========================
# БАЗА ЗАЯВОК
# =========================

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []

    try:
        with open(
            ORDERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except:
        return []


def save_orders(orders):
    with open(
        ORDERS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            orders,
            file,
            ensure_ascii=False,
            indent=2
        )


# =========================
# БАЗА УСЛУГ
# =========================

def load_services():
    if not os.path.exists(SERVICES_FILE):
        return []

    try:
        with open(
            SERVICES_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except:
        return []


def save_services(services):
    with open(
        SERVICES_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            services,
            file,
            ensure_ascii=False,
            indent=2
        )


# =========================
# ПРОВЕРКА АДМИНА
# =========================

def is_admin(message):
    return message.from_user.id == ADMIN_ID


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

def main_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton("📋 Услуги"),
        types.KeyboardButton("💰 Цены"),
        types.KeyboardButton("📝 Оставить заявку"),
        types.KeyboardButton("📞 Связаться")
    )

    return markup


# =========================
# АДМИН-МЕНЮ
# =========================

def admin_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton("📥 Новые заявки"),
        types.KeyboardButton("📊 Статистика"),
        types.KeyboardButton(
            "📋 Управление услугами"
        ),
        types.KeyboardButton(
            "🔙 Главное меню"
        )
    )

    return markup


# =========================
# МЕНЮ УПРАВЛЕНИЯ УСЛУГАМИ
# =========================

def services_admin_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton(
            "➕ Добавить услугу"
        ),
        types.KeyboardButton(
            "✏️ Изменить услугу"
        ),
        types.KeyboardButton(
            "🗑 Удалить услугу"
        ),
        types.KeyboardButton(
            "📋 Список услуг"
        ),
        types.KeyboardButton(
            "🔙 В админку"
        )
    )

    return markup


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать!\n\n"
        "Выберите нужный раздел:",
        reply_markup=main_menu()
    )


# =========================
# УСЛУГИ
# =========================

@bot.message_handler(
    func=lambda m: m.text == "📋 Услуги"
)
def services(message):

    services_list = load_services()

    if not services_list:

        bot.send_message(
            message.chat.id,
            "😔 Услуг пока нет."
        )

        return

    text = "📋 НАШИ УСЛУГИ\n\n"

    for service in services_list:

        text += (
            f"🔹 {service['name']}\n"
            f"💰 {service['price']} ₸\n\n"
        )

    bot.send_message(
        message.chat.id,
        text
    )


# =========================
# ЦЕНЫ
# =========================

@bot.message_handler(
    func=lambda m: m.text == "💰 Цены"
)
def prices(message):

    services_list = load_services()

    if not services_list:

        bot.send_message(
            message.chat.id,
            "😔 Услуг пока нет."
        )

        return

    text = "💰 ЦЕНЫ\n\n"

    for service in services_list:

        text += (
            f"🔹 {service['name']} — "
            f"{service['price']} ₸\n"
        )

    bot.send_message(
        message.chat.id,
        text
    )


# =========================
# КОНТАКТ
# =========================

@bot.message_handler(
    func=lambda m: m.text == "📞 Связаться"
)
def contact(message):

    bot.send_message(
        message.chat.id,
        "📞 Связаться с администратором:\n"
        "@USERNAME_АДМИНА"
    )


# =========================
# ЗАЯВКА
# =========================

@bot.message_handler(
    func=lambda m: m.text == "📝 Оставить заявку"
)
def application(message):

    msg = bot.send_message(
        message.chat.id,
        "📝 Оформим заявку.\n\n"
        "Как вас зовут?"
    )

    bot.register_next_step_handler(
        msg,
        get_name
    )


def get_name(message):

    name = message.text.strip()

    if not name:

        msg = bot.send_message(
            message.chat.id,
            "❌ Имя не может быть пустым.\n\n"
            "Как вас зовут?"
        )

        bot.register_next_step_handler(
            msg,
            get_name
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "📱 Отправьте номер телефона:",
        reply_markup=phone_keyboard()
    )

    bot.register_next_step_handler(
        msg,
        get_phone,
        name
    )


# =========================
# КНОПКА ТЕЛЕФОНА
# =========================

def phone_keyboard():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    markup.add(
        types.KeyboardButton(
            "📱 Отправить номер",
            request_contact=True
        )
    )

    return markup


# =========================
# ПОЛУЧЕНИЕ ТЕЛЕФОНА
# =========================

def get_phone(message, name):

    if not message.contact:

        msg = bot.send_message(
            message.chat.id,
            "❌ Пожалуйста, нажмите кнопку "
            "«📱 Отправить номер»."
        )

        bot.register_next_step_handler(
            msg,
            get_phone,
            name
        )

        return

    phone = message.contact.phone_number

    msg = bot.send_message(
        message.chat.id,
        "💬 Что вас интересует?",
        reply_markup=types.ReplyKeyboardRemove()
    )

    bot.register_next_step_handler(
        msg,
        get_request,
        name,
        phone
    )


# =========================
# ПОЛУЧЕНИЕ ЗАПРОСА
# =========================

def get_request(message, name, phone):

    request = message.text.strip()

    if not request:

        msg = bot.send_message(
            message.chat.id,
            "❌ Напишите, пожалуйста, что вас интересует."
        )

        bot.register_next_step_handler(
            msg,
            get_request,
            name,
            phone
        )

        return

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "не указан"
    )

    orders = load_orders()

    new_id = max(
        [
            order.get("id", 0)
            for order in orders
        ],
        default=0
    ) + 1

    order = {
        "id": new_id,
        "name": name,
        "phone": phone,
        "request": request,
        "username": username,
        "user_id": message.from_user.id,
        "date": datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )
    }

    orders.append(order)

    save_orders(orders)

    admin_text = (
        "🔥 НОВАЯ ЗАЯВКА\n\n"
        f"🆔 №{order['id']}\n"
        f"👤 Имя: {name}\n"
        f"📱 Телефон: {phone}\n"
        f"💬 Запрос: {request}\n"
        f"🔗 Username: {username}\n"
        f"🕐 {order['date']}"
    )

    bot.send_message(
        ADMIN_ID,
        admin_text
    )

    bot.send_message(
        message.chat.id,
        "✅ Заявка успешно отправлена!\n\n"
        "Администратор свяжется с вами.",
        reply_markup=main_menu()
    )


# =========================
# АДМИН
# =========================

@bot.message_handler(commands=["admin"])
def admin(message):

    if not is_admin(message):

        bot.send_message(
            message.chat.id,
            "⛔ Доступ запрещён."
        )

        return

    bot.send_message(
        message.chat.id,
        "⚙️ АДМИН-ПАНЕЛЬ\n\n"
        "Выберите действие:",
        reply_markup=admin_menu()
    )


# =========================
# НОВЫЕ ЗАЯВКИ
# =========================

@bot.message_handler(
    func=lambda m: m.text == "📥 Новые заявки"
)
def show_orders(message):

    if not is_admin(message):
        return

    orders = load_orders()

    if not orders:

        bot.send_message(
            message.chat.id,
            "📭 Заявок пока нет."
        )

        return

    text = "📥 ПОСЛЕДНИЕ ЗАЯВКИ\n\n"

    for order in orders[-10:]:

        text += (
            f"🆔 №{order['id']}\n"
            f"👤 {order['name']}\n"
            f"📱 {order['phone']}\n"
            f"💬 {order['request']}\n"
            f"🔗 {order.get('username', 'не указан')}\n"
            f"🕐 {order['date']}\n"
            "────────────\n"
        )

    bot.send_message(
        message.chat.id,
        text
    )


# =========================
# СТАТИСТИКА
# =========================

@bot.message_handler(
    func=lambda m: m.text == "📊 Статистика"
)
def statistics(message):

    if not is_admin(message):
        return

    orders = load_orders()

    unique_clients = len(
        set(
            order["user_id"]
            for order in orders
            if "user_id" in order
        )
    )

    bot.send_message(
        message.chat.id,
        "📊 СТАТИСТИКА\n\n"
        f"📥 Всего заявок: {len(orders)}\n"
        f"👥 Клиентов: {unique_clients}"
    )


# =========================
# УПРАВЛЕНИЕ УСЛУГАМИ
# =========================

@bot.message_handler(
    func=lambda m:
    m.text == "📋 Управление услугами"
)
def manage_services(message):

    if not is_admin(message):
        return

    bot.send_message(
        message.chat.id,
        "📋 УПРАВЛЕНИЕ УСЛУГАМИ\n\n"
        "Выберите действие:",
        reply_markup=services_admin_menu()
    )


# =========================
# СПИСОК УСЛУГ
# =========================

@bot.message_handler(
    func=lambda m:
    m.text == "📋 Список услуг"
)
def services_list_admin(message):

    if not is_admin(message):
        return

    services_list = load_services()

    if not services_list:

        bot.send_message(
            message.chat.id,
            "📭 Услуг пока нет."
        )

        return

    text = "📋 СПИСОК УСЛУГ\n\n"

    for service in services_list:

        text += (
            f"🆔 ID: {service['id']}\n"
            f"🔹 {service['name']}\n"
            f"💰 {service['price']} ₸\n"
            "────────────\n"
        )

    bot.send_message(
        message.chat.id,
        text
    )


# =========================
# ДОБАВЛЕНИЕ УСЛУГИ
# =========================

@bot.message_handler(
    func=lambda m:
    m.text == "➕ Добавить услугу"
)
def add_service_start(message):

    if not is_admin(message):
        return

    msg = bot.send_message(
        message.chat.id,
        "➕ ДОБАВЛЕНИЕ УСЛУГИ\n\n"
        "Введите название услуги:"
    )

    bot.register_next_step_handler(
        msg,
        add_service_name
    )


def add_service_name(message):

    if not is_admin(message):
        return

    name = message.text.strip()

    if not name:

        msg = bot.send_message(
            message.chat.id,
            "❌ Название не может быть пустым.\n\n"
            "Введите название:"
        )

        bot.register_next_step_handler(
            msg,
            add_service_name
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "💰 Теперь введите цену в тенге:\n\n"
        "Например: 5000"
    )

    bot.register_next_step_handler(
        msg,
        add_service_price,
        name
    )


def add_service_price(message, name):

    if not is_admin():
        return

    try:

        price = int(
            message.text.strip()
        )

        if price < 0:
            raise ValueError

    except ValueError:

        msg = bot.send_message(
            message.chat.id,
            "❌ Цена должна быть целым "
            "положительным числом.\n\n"
            "Например: 5000"
        )

        bot.register_next_step_handler(
            msg,
            add_service_price,
            name
        )

        return

    services_list = load_services()

    new_id = max(
        [
            service["id"]
            for service in services_list
        ],
        default=0
    ) + 1

    new_service = {
        "id": new_id,
        "name": name,
        "price": price
    }

    services_list.append(
        new_service
    )

    save_services(
        services_list
    )

    bot.send_message(
        message.chat.id,
        "✅ Услуга добавлена!\n\n"
        f"🆔 ID: {new_id}\n"
        f"🔹 {name}\n"
        f"💰 {price} ₸",
        reply_markup=services_admin_menu()
    )


# =========================
# УДАЛЕНИЕ УСЛУГИ
# =========================

@bot.message_handler(
    func=lambda m:
    m.text == "🗑 Удалить услугу"
)
def delete_service_start(message):

    if not is_admin(message):
        return

    services_list = load_services()

    if not services_list:

        bot.send_message(
            message.chat.id,
            "📭 Услуг для удаления нет."
        )

        return

    text = "🗑 УДАЛЕНИЕ УСЛУГИ\n\n"

    for service in services_list:

        text += (
            f"🆔 {service['id']} — "
            f"{service['name']} — "
            f"{service['price']} ₸\n"
        )

    text += (
        "\nВведите ID услуги, "
        "которую хотите удалить:"
    )

    msg = bot.send_message(
        message.chat.id,
        text
    )

    bot.register_next_step_handler(
        msg,
        delete_service
    )


def delete_service(message):

    if not is_admin(message):
        return

    try:

        service_id = int(
            message.text.strip()
        )

    except ValueError:

        bot.send_message(
            message.chat.id,
            "❌ ID должен быть числом."
        )

        return

    services_list = load_services()

    service = next(
        (
            s for s in services_list
            if s["id"] == service_id
        ),
        None
    )

    if service is None:

        bot.send_message(
            message.chat.id,
            "❌ Услуга с таким ID "
            "не найдена."
        )

        return

    services_list.remove(
        service
    )

    save_services(
        services_list
    )

    bot.send_message(
        message.chat.id,
        "✅ Услуга удалена!\n\n"
        f"🗑 {service['name']}",
        reply_markup=services_admin_menu()
    )


# =========================
# ИЗМЕНЕНИЕ УСЛУГИ
# =========================

@bot.message_handler(
    func=lambda m:
    m.text == "✏️ Изменить услугу"
)
def edit_service_start(message):

    if not is_admin(message):
        return

    services_list = load_services()

    if not services_list:

        bot.send_message(
            message.chat.id,
            "📭 Услуг пока нет."
        )

        return

    text = "✏️ ИЗМЕНЕНИЕ УСЛУГИ\n\n"

    for service in services_list:

        text += (
            f"🆔 {service['id']} — "
            f"{service['name']} — "
            f"{service['price']} ₸\n"
        )

    text += "\nВведите ID услуги:"

    msg = bot.send_message(
        message.chat.id,
        text
    )

    bot.register_next_step_handler(
        msg,
        edit_service_id
    )


def edit_service_id(message):

    if not is_admin(message):
        return

    try:

        service_id = int(
            message.text.strip()
        )

    except ValueError:

        bot.send_message(
            message.chat.id,
            "❌ ID должен быть числом."
        )

        return

    services_list = load_services()

    service = next(
        (
            s for s in services_list
            if s["id"] == service_id
        ),
        None
    )

    if service is None:

        bot.send_message(
            message.chat.id,
            "❌ Услуга не найдена."
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "🔹 Введите новое название:"
    )

    bot.register_next_step_handler(
        msg,
        edit_service_name,
        service_id
    )


def edit_service_name(
    message,
    service_id
):

    if not is_admin(message):
        return

    name = message.text.strip()

    if not name:

        msg = bot.send_message(
            message.chat.id,
            "❌ Название не может быть пустым.\n\n"
            "Введите новое название:"
        )

        bot.register_next_step_handler(
            msg,
            edit_service_name,
            service_id
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "💰 Введите новую цену:"
    )

    bot.register_next_step_handler(
        msg,
        edit_service_price,
        service_id,
        name
    )


def edit_service_price(
    message,
    service_id,
    name
):

    if not is_admin(message):
        return

    try:

        price = int(
            message.text.strip()
        )

        if price < 0:
            raise ValueError

    except ValueError:

        msg = bot.send_message(
            message.chat.id,
            "❌ Цена должна быть "
            "целым числом."
        )

        bot.register_next_step_handler(
            msg,
            edit_service_price,
            service_id,
            name
        )

        return

    services_list = load_services()

    for service in services_list:

        if service["id"] == service_id:

            service["name"] = name
            service["price"] = price

            break

    save_services(
        services_list
    )

    bot.send_message(
        message.chat.id,
        "✅ Услуга изменена!\n\n"
        f"🆔 ID: {service_id}\n"
        f"🔹 {name}\n"
        f"💰 {price} ₸",
        reply_markup=services_admin_menu()
    )


# =========================
# ВОЗВРАТ В АДМИНКУ
# =========================

@bot.message_handler(
    func=lambda m:
    m.text == "🔙 В админку"
)
def back_to_admin(message):

    if not is_admin(message):
        return

    bot.send_message(
        message.chat.id,
        "⚙️ АДМИН-ПАНЕЛЬ\n\n"
        "Выберите действие:",
        reply_markup=admin_menu()
    )


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

@bot.message_handler(
    func=lambda m:
    m.text == "🔙 Главное меню"
)
def back(message):

    bot.send_message(
        message.chat.id,
        "Главное меню:",
        reply_markup=main_menu()
    )


# =========================
# ЗАПУСК
# =========================

from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Denko Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=10000)

print("🤖 Бот запущен!")

Thread(target=run).start()

bot.infinity_polling()
