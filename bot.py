import json
import contextlib
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    Update, Message, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    CallbackQuery
)
from config import TOKEN, URL, CHANNEL_ID
from models import Item, Order
from database import get_db

bot = AsyncTeleBot(TOKEN)

# --- Yordamchi Funksiyalar ---

def get_incomplete_order(db, user_id: int):
    """Foydalanuvchining to'liq bo'lmagan buyurtmasini olish"""
    return (
        db.query(Order)
        .filter_by(user_id=user_id)
        .filter(
            (Order.user_name.is_(None)) |
            (Order.user_phone.is_(None)) |
            (Order.location.is_(None))
        )
        .first()
    )

async def ask_for_name(chat_id: int):
    await bot.send_message(
        chat_id,
        "To'liq ismingizni kiriting.\n<i>masalan: Burxon Nurmurodov</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

async def ask_for_phone(chat_id: int):
    await bot.send_message(
        chat_id, 
        "Iltimos, telefon raqamingizni kiriting.\n<i>masalan: +998(98)765-43-21</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton("☎️ Kontaktni Ulashish", request_contact=True)
        )
    )

async def ask_for_location(chat_id: int):
    await bot.send_message(
        chat_id,
        "Iltimos, joylashuvingizni ulashing.",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton("📍 Joylashuvni Ulashish", request_location=True)
        )
    )

async def send_confirmation(chat_id: int, order: Order):
    """Foydalanuvchiga tasdiqlash xabarini inline tugmalar bilan yuborish"""
    lat, lon = map(float, order.location.split(","))
    location_msg = await bot.send_location(
        chat_id, latitude=lat, longitude=lon, reply_markup=ReplyKeyboardRemove()
    )

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("👤 Ismni O'zgartirish", callback_data=f"change_name_{order.id}"),
        InlineKeyboardButton("☎️ Telefonni O'zgartirish", callback_data=f"change_phone_{order.id}"),
    )
    kb.row(
        InlineKeyboardButton("📍 Joylashuvni O'zgartirish", callback_data=f"change_location_{order.id}")
    )
    kb.row(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_order_{order.id}"),
        InlineKeyboardButton("❌ Bekor Qilish", callback_data=f"cancel_order_{order.id}")
    )

    await bot.send_message(
        chat_id,
        f"<b>Ma'lumotlaringizni tasdiqlang:</b>\n\n"
        f"👤 <b>Ism:</b> <code>{order.user_name}</code>\n"
        f"☎️ <b>Telefon:</b> <code>{order.user_phone}</code>\n",
        parse_mode="HTML",
        reply_to_message_id=location_msg.message_id,
        reply_markup=kb
    )

async def update_and_continue(chat_id: int, db, order: Order):
    """To'ldirilmagan maydonlarga qarab buyurtma jarayonini davom ettirish"""
    if not order.user_name:
        await ask_for_name(chat_id)
    elif not order.user_phone:
        await ask_for_phone(chat_id)
    elif not order.location:
        await ask_for_location(chat_id)
    else:
        await send_confirmation(chat_id, order)

# --- Handlerlar ---

@bot.message_handler(commands=['start'])
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Veb Ilovani Ochish", web_app=WebAppInfo(url=f"{URL}/menu/"))
    )
    await bot.send_message(message.chat.id, "Botga xush kelibsiz!", reply_markup=keyboard)

#Insert random Items into DB
@bot.message_handler(commands=['insert'])
async def insert_random_items(message: Message):
    with contextlib.closing(next(get_db())) as db:
        Item.insert_random_items(db, 10)
    
    await bot.send_message(message.chat.id, "Random Itmes have been added.")

@bot.message_handler(content_types=['text'])
async def text_handler(message: Message):
    with contextlib.closing(next(get_db())) as db:
        order = get_incomplete_order(db, message.chat.id)
        if not order:
            return

        if not order.user_name:
            order.user_name = message.text
        elif not order.user_phone:
            # If message is not number send warning
            if not all(c.isdigit() or c in "+-() " for c in message.text):
                await bot.send_message(message.chat.id, "Iltimos, telefon raqamingizni to'g'ri kiriting.\nMasalan: +998(98)765-43-21", parse_mode="HTML")
                return
            order.user_phone = message.text

        db.commit()
        await update_and_continue(message.chat.id, db, order)

@bot.message_handler(content_types=['contact'])
async def handle_contact(message: Message):
    with contextlib.closing(next(get_db())) as db:
        order = get_incomplete_order(db, message.chat.id)
        if not order:
            return

        if not order.user_phone:
            order.user_phone = message.contact.phone_number
            db.commit()
            await update_and_continue(message.chat.id, db, order)

@bot.message_handler(content_types=['location'])
async def handle_location(message: Message):
    with contextlib.closing(next(get_db())) as db:
        order = get_incomplete_order(db, message.chat.id)
        if not order:
            return

        if not order.location:
            order.location = f"{message.location.latitude},{message.location.longitude}"
            db.commit()
            await update_and_continue(message.chat.id, db, order)

@bot.callback_query_handler(func=lambda call: True)
async def callback_query_handler(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
    await bot.delete_message(call.message.chat.id, call.message.id)

    with contextlib.closing(next(get_db())) as db:
        order_id = call.data.split("_")[-1]
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return

        if call.data.startswith("change_name_"):
            order.user_name = None
            db.commit()
            await ask_for_name(call.message.chat.id)

        elif call.data.startswith("change_phone_"):
            order.user_phone = None
            db.commit()
            await ask_for_phone(call.message.chat.id)

        elif call.data.startswith("change_location_"):
            order.location = None
            db.commit()
            await ask_for_location(call.message.chat.id)

        elif call.data.startswith("confirm_order_"):
            text = (
                "<b>🛍️ YANGI BUYURTMA</b>\n\n"
                "<b>Foydalanuvchi:</b>\n"
                f"👤 <b>Ism:</b> <code>{order.user_name}</code>\n"
                f"📞 <b>Telefon:</b> <code>{order.user_phone}</code>\n\n"
                "---"
                "<b>Mahsulotlar:</b>\n"
            )
            order_items = json.loads(order.items)
            total = 0
            i = 0
            for key, quantity in order_items.items():
                i += 1
                item_id, size = key.split('-')
                item = Item.get(db, int(item_id))
                subtotal = int(item.price) * int(quantity)
                text += f"<b>{i}. {item.title}</b> <i>({size})</i>\n"
                text += f"   - Soni: {quantity} ta\n"
                text += f"   - Narxi: {subtotal} UZS\n"
                total += subtotal
            text += f"\n<b>Jami:</b> {total} UZS"

            order_msg = await bot.send_message(CHANNEL_ID, text, parse_mode="HTML")
            lat, lon = map(float, order.location.split(','))
            await bot.send_location(
                CHANNEL_ID, lat, lon, reply_to_message_id=order_msg.message_id
            )

            await bot.send_message(call.message.chat.id, "🎉 Buyurtmangiz qabul qilindi! Tez orada operatorlarimiz siz bilan bog'lanadi. Rahmat! 🙏")

        elif call.data.startswith("cancel_order_"):
            db.delete(order)
            db.commit()
            await bot.send_message(call.message.chat.id, "❌ Buyurtmangiz bekor qilindi.")
