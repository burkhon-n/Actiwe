import json
import contextlib
import logging
import traceback
from typing import Optional
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    Update, Message, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    CallbackQuery
)
from telebot.apihelper import ApiTelegramException
from config import TOKEN, URL, CHANNEL_ID, SADMIN, logger
from models import Item, Order
from database import get_db, DatabaseSessionManager

# Configure bot with better error handling
bot = AsyncTeleBot(
    TOKEN,
    parse_mode="HTML",
    disable_web_page_preview=True
)

# Bot logging
bot_logger = logging.getLogger("telebot")
bot_logger.setLevel(logging.INFO)

# --- Error Handler ---
async def handle_bot_error(message: Message, error: Exception, context: str = ""):
    """Handle bot errors gracefully."""
    error_msg = f"Bot error in {context}: {error}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())
    
    try:
        await bot.send_message(
            message.chat.id,
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring yoki administrator bilan bog'laning.",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Failed to send error message: {e}")

# --- Helper Functions ---
def get_incomplete_order(db, user_id: int) -> Optional[Order]:
    """Get user's incomplete order."""
    try:
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
    except Exception as e:
        logger.error(f"Error getting incomplete order for user {user_id}: {e}")
        return None

async def ask_for_name(chat_id: int):
    """Ask user for their full name."""
    try:
        await bot.send_message(
            chat_id,
            "To'liq ismingizni kiriting.\n<i>masalan: Burxon Nurmurodov</i>",
            reply_markup=ReplyKeyboardRemove()
        )
    except ApiTelegramException as e:
        logger.error(f"Failed to ask for name (chat_id: {chat_id}): {e}")

async def ask_for_phone(chat_id: int):
    """Ask user for their phone number."""
    try:
        await bot.send_message(
            chat_id, 
            "Iltimos, telefon raqamingizni kiriting.\n<i>masalan: +998(98)765-43-21</i>",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton("☎️ Kontaktni Ulashish", request_contact=True)
            )
        )
    except ApiTelegramException as e:
        logger.error(f"Failed to ask for phone (chat_id: {chat_id}): {e}")

async def ask_for_location(chat_id: int):
    """Ask user for their location."""
    try:
        await bot.send_message(
            chat_id,
            "Iltimos, joylashuvingizni ulashing.",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton("📍 Joylashuvni Ulashish", request_location=True)
            )
        )
    except ApiTelegramException as e:
        logger.error(f"Failed to ask for location (chat_id: {chat_id}): {e}")

async def send_confirmation(chat_id: int, order: Order):
    """Send order confirmation message with inline buttons."""
    try:
        # Validate location format
        if not order.location or "," not in order.location:
            logger.error(f"Invalid location format for order {order.id}: {order.location}")
            await bot.send_message(
                chat_id,
                "❌ Joylashuv ma'lumotlari noto'g'ri. Iltimos, qayta urinib ko'ring.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
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
            reply_to_message_id=location_msg.message_id,
            reply_markup=kb
        )
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing location for order {order.id}: {e}")
        await bot.send_message(
            chat_id,
            "❌ Joylashuv ma'lumotlari noto'g'ri. Iltimos, qayta urinib ko'ring.",
            reply_markup=ReplyKeyboardRemove()
        )
    except ApiTelegramException as e:
        logger.error(f"Failed to send confirmation (chat_id: {chat_id}, order_id: {order.id}): {e}")
    except Exception as e:
        logger.error(f"Unexpected error in send_confirmation: {e}")
        logger.error(traceback.format_exc())

async def update_and_continue(chat_id: int, db, order: Order):
    """Continue order process based on missing fields."""
    try:
        if not order.user_name:
            await ask_for_name(chat_id)
        elif not order.user_phone:
            await ask_for_phone(chat_id)
        elif not order.location:
            await ask_for_location(chat_id)
        else:
            await send_confirmation(chat_id, order)
    except Exception as e:
        logger.error(f"Error in update_and_continue for user {chat_id}: {e}")
        await bot.send_message(
            chat_id,
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
            reply_markup=ReplyKeyboardRemove()
        )

# --- Message Handlers ---

@bot.message_handler(commands=['start'])
async def start_handler(message: Message):
    """Handle /start command."""
    try:
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🛍️ Do'konni ochish", web_app=WebAppInfo(url=f"{URL}/menu/"))
        )
        
        welcome_text = (
            "🎉 <b>Actiwe do'koniga xush kelibsiz!</b>\n\n"
            "Bu yerda sifatli kiyimlar va aksessuarlarni topishingiz mumkin.\n"
            "Do'konni ochib, buyurtma berishni boshlang! 👇"
        )
        
        await bot.send_message(
            message.chat.id, 
            welcome_text, 
            reply_markup=keyboard
        )
        
        logger.info(f"Start command handled for user {message.from_user.id}")
        
    except ApiTelegramException as e:
        logger.error(f"Failed to handle start command for user {message.from_user.id}: {e}")
    except Exception as e:
        await handle_bot_error(message, e, "start_handler")

@bot.message_handler(commands=['insert'])
async def insert_random_items(message: Message):
    """Insert random items for testing (admin only)."""
    try:
        # Simple admin check (you might want to improve this)
        if str(message.from_user.id) != SADMIN:
            await bot.send_message(message.chat.id, "❌ Sizga bu buyruqni ishlatish huquqi yo'q.")
            return
        
        with DatabaseSessionManager() as db:
            Item.insert_random_items(db, 10)
        
        await bot.send_message(message.chat.id, "✅ Tasodifiy mahsulotlar qo'shildi.")
        
    except Exception as e:
        await handle_bot_error(message, e, "insert_random_items")

@bot.message_handler(content_types=['text'])
async def text_handler(message: Message):
    """Handle text messages for order completion."""
    try:
        with DatabaseSessionManager() as db:
            order = get_incomplete_order(db, message.chat.id)
            if not order:
                # No incomplete order, send help message
                await bot.send_message(
                    message.chat.id,
                    "🤖 Buyurtma berish uchun web ilovadan foydalaning.\n"
                    "/start buyrug'ini bosing.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return

            if not order.user_name:
                # Validate name (basic validation)
                if len(message.text.strip()) < 2:
                    await bot.send_message(
                        message.chat.id,
                        "❌ Ism juda qisqa. Iltimos, to'liq ismingizni kiriting."
                    )
                    return
                order.user_name = message.text.strip()
                
            elif not order.user_phone:
                # Validate phone number
                phone_text = message.text.strip()
                if not all(c.isdigit() or c in "+-() " for c in phone_text) or len(phone_text) < 9:
                    await bot.send_message(
                        message.chat.id,
                        "❌ Telefon raqam noto'g'ri formatda.\n"
                        "Iltimos, to'g'ri formatda kiriting: +998(98)765-43-21"
                    )
                    return
                order.user_phone = phone_text

            await update_and_continue(message.chat.id, db, order)
            
    except Exception as e:
        await handle_bot_error(message, e, "text_handler")

@bot.message_handler(content_types=['contact'])
async def handle_contact(message: Message):
    """Handle contact sharing for phone number."""
    try:
        with DatabaseSessionManager() as db:
            order = get_incomplete_order(db, message.chat.id)
            if not order:
                return

            if not order.user_phone:
                order.user_phone = message.contact.phone_number
                await update_and_continue(message.chat.id, db, order)
                
    except Exception as e:
        await handle_bot_error(message, e, "handle_contact")

@bot.message_handler(content_types=['location'])
async def handle_location(message: Message):
    """Handle location sharing."""
    try:
        with DatabaseSessionManager() as db:
            order = get_incomplete_order(db, message.chat.id)
            if not order:
                return

            if not order.location:
                # Validate location
                lat, lon = message.location.latitude, message.location.longitude
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    await bot.send_message(
                        message.chat.id,
                        "❌ Noto'g'ri joylashuv ma'lumotlari. Iltimos, qayta urinib ko'ring."
                    )
                    return
                
                order.location = f"{lat},{lon}"
                await update_and_continue(message.chat.id, db, order)
                
    except Exception as e:
        await handle_bot_error(message, e, "handle_location")

@bot.callback_query_handler(func=lambda call: True)
async def callback_query_handler(call: CallbackQuery):
    """Handle inline keyboard callbacks."""
    try:
        # Answer callback query to remove loading state
        await bot.answer_callback_query(call.id)
        
        # Safely delete messages
        try:
            if call.message.reply_to_message:
                await bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
            await bot.delete_message(call.message.chat.id, call.message.id)
        except ApiTelegramException as e:
            logger.warning(f"Failed to delete messages: {e}")

        with DatabaseSessionManager() as db:
            try:
                order_id = int(call.data.split("_")[-1])
            except (ValueError, IndexError):
                logger.error(f"Invalid callback data format: {call.data}")
                return
                
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                await bot.send_message(
                    call.message.chat.id,
                    "❌ Buyurtma topilmadi. Buyurtma allaqachon bekor qilingan bo'lishi mumkin."
                )
                return

            if call.data.startswith("change_name_"):
                order.user_name = None
                await ask_for_name(call.message.chat.id)

            elif call.data.startswith("change_phone_"):
                order.user_phone = None
                await ask_for_phone(call.message.chat.id)

            elif call.data.startswith("change_location_"):
                order.location = None
                await ask_for_location(call.message.chat.id)

            elif call.data.startswith("confirm_order_"):
                await process_order_confirmation(call.message.chat.id, order, db)

            elif call.data.startswith("cancel_order_"):
                db.delete(order)
                await bot.send_message(
                    call.message.chat.id, 
                    "❌ Buyurtmangiz bekor qilindi.\n"
                    "Yangi buyurtma berish uchun /start tugmasini bosing."
                )
                
    except Exception as e:
        await handle_bot_error(call.message, e, "callback_query_handler")

async def process_order_confirmation(chat_id: int, order: Order, db):
    """Process order confirmation and send to channel."""
    try:
        # Build order message
        text = (
            "<b>🛍️ YANGI BUYURTMA</b>\n\n"
            "<b>Mijoz ma'lumotlari:</b>\n"
            f"👤 <b>Ism:</b> <code>{order.user_name}</code>\n"
            f"📞 <b>Telefon:</b> <code>{order.user_phone}</code>\n"
            f"🆔 <b>User ID:</b> <code>{order.user_id}</code>\n\n"
            "<b>Buyurtma tafsilotlari:</b>\n"
        )
        
        try:
            order_items = json.loads(order.items)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse order items for order {order.id}: {e}")
            await bot.send_message(chat_id, "❌ Buyurtma ma'lumotlarida xatolik. Iltimos, qayta urinib ko'ring.")
            return
            
        total = 0
        item_count = 0
        
        for key, quantity in order_items.items():
            item_count += 1
            
            # Parse key format (could be item_id-size or item_id-size-gender)
            key_parts = key.split('-')
            if len(key_parts) < 2:
                logger.error(f"Invalid item key format: {key}")
                continue
                
            item_id = int(key_parts[0])
            size = key_parts[1]
            gender = key_parts[2] if len(key_parts) > 2 else None
            
            item = Item.get(db, item_id)
            if not item:
                logger.error(f"Item not found: {item_id}")
                continue
                
            subtotal = int(item.price) * int(quantity)
            
            text += f"<b>{item_count}. {item.title}</b>\n"
            text += f"   📏 <b>O'lcham:</b> {size}\n"
            if gender:
                text += f"   👫 <b>Jins:</b> {gender}\n"
            text += f"   📦 <b>Soni:</b> {quantity} ta\n"
            text += f"   💰 <b>Narxi:</b> {subtotal:,} UZS\n\n"
            total += subtotal
            
        text += f"<b>💳 Jami summa:</b> {total:,} UZS"

        # Send order to channel
        try:
            order_msg = await bot.send_message(CHANNEL_ID, text)
            
            # Send location if available
            if order.location and "," in order.location:
                lat, lon = map(float, order.location.split(','))
                await bot.send_location(
                    CHANNEL_ID, lat, lon, reply_to_message_id=order_msg.message_id
                )
        except ApiTelegramException as e:
            logger.error(f"Failed to send order to channel: {e}")
            await bot.send_message(
                chat_id,
                "❌ Buyurtmani yuborishda xatolik yuz berdi. Iltimos, administrator bilan bog'laning."
            )
            return

        # Delete the completed order
        db.delete(order)
        
        # Send success message to user
        await bot.send_message(
            chat_id,
            "🎉 <b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
            "Tez orada operatorlarimiz siz bilan bog'lanadi.\n"
            "Rahmat! 🙏\n\n"
            "Yangi buyurtma berish uchun /start tugmasini bosing."
        )
        
        logger.info(f"Order {order.id} processed successfully for user {chat_id}")
        
    except Exception as e:
        logger.error(f"Error processing order confirmation: {e}")
        logger.error(traceback.format_exc())
        await bot.send_message(
            chat_id,
            "❌ Buyurtmani qayta ishlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
        )
