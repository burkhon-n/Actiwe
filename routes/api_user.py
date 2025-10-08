from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import CartItem, Order, Item
from database import get_db
from .dependencies import get_user_id_from_init_data # Import the shared function
import json
from bot import bot, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton  # Assuming you have a bot instance for Telegram notifications
from config import URL, format_price, DELIVERY_FEE

router = APIRouter(prefix="/api", tags=["User API"])

@router.post("/cart/update")
async def update_cart(request: Request, db: Session = Depends(get_db)):
    """
    Efficiently synchronizes the user's cart in the database.
    Deletes, adds, or updates only the items that have changed.
    """
    data = await request.json()
    init_data_str = data.get("initData")
    cart_from_client = data.get("cart", {})
    
    # Use the central function to validate and get user_id
    user_id = get_user_id_from_init_data(init_data_str)

    # Fetch existing cart from DB to compare
    existing_cart_db = db.query(CartItem).filter_by(user_id=user_id).all()
    existing_cart_map = {}
    for item in existing_cart_db:
        if item.gender:
            existing_cart_map[f"{item.item_id}-{item.size}-{item.gender}"] = item
        else:
            existing_cart_map[f"{item.item_id}-{item.size}"] = item

    client_keys = set(cart_from_client.keys())
    db_keys = set(existing_cart_map.keys())

    # 1. Delete items that are in the DB but not in the client's cart
    keys_to_delete = db_keys - client_keys
    if keys_to_delete:
        for key in keys_to_delete:
            db.delete(existing_cart_map[key])

    # 2. Add or update items from the client's cart
    for key, quantity in cart_from_client.items():
        # Parse the key to extract item_id, size, and optional gender
        key_parts = key.split('-')
        item_id = int(key_parts[0])
        size = key_parts[1]
        gender = key_parts[2] if len(key_parts) > 2 else None
        
        if key in existing_cart_map:
            # Update existing item if quantity differs
            if existing_cart_map[key].quantity != quantity:
                existing_cart_map[key].quantity = quantity
        else:
            # Add new item
            new_cart_item = CartItem(user_id=user_id, item_id=item_id, size=size, quantity=quantity, gender=gender)
            db.add(new_cart_item)

    db.commit()
    return JSONResponse(content={"success": True, "message": "Cart synchronized."})


@router.post("/place-order")
async def place_order(request: Request, db: Session = Depends(get_db)):
    """
    Places a new order with the items from the user's cart.
    Clears the user's cart upon successful order placement.
    """
    data = await request.json()
    init_data_str = data.get("initData")
    cart = data.get("cart", {})
    
    # Use the central function to validate and get user_id
    user_id = get_user_id_from_init_data(init_data_str)

    if not cart:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    # Create a new order with a JSON string of the cart items
    new_order = Order(user_id=user_id, items=json.dumps(cart))
    db.add(new_order)

    text = "<b>🛍️ Sizning buyurtmalaringiz:</b>"
    i=0
    for key, value in cart.items():
        i+=1
        key_parts = key.split('-')
        item_id = int(key_parts[0])
        size = key_parts[1]
        gender = key_parts[2] if len(key_parts) > 2 else None
        
        item = Item.get(db, item_id)
        
        # Format the item display based on whether it has size and gender
        item_details = []
        if size != 'N/A':
            item_details.append(f"O'lcham: {size}")
        if gender:
            gender_text = "Erkak" if gender == "male" else "Ayol" if gender == "female" else ""
            if gender_text:
                item_details.append(gender_text)
        
        details_str = f" ({', '.join(item_details)})" if item_details else ""
        text += f"\n{i}. {item.title}{details_str} - {value} dona - {format_price(item.price * value)} so'm"
    
    subtotal = sum(Item.get(db, int(k.split('-')[0])).price * v for k, v in cart.items())
    total = subtotal + DELIVERY_FEE
    
    text += f"\n\n<b>Mahsulotlar: {format_price(subtotal)} so'm</b>"
    text += f"\n<b>Yetkazib berish: {format_price(DELIVERY_FEE)} so'm</b>"
    text += f"\n<b>Jami: {format_price(total)} so'm</b>"

    await bot.send_message(
        user_id,
        text,
        parse_mode='HTML'
    )
    
    # Clear the user's cart after placing the order
    db.query(CartItem).filter_by(user_id=user_id).delete()
    
    db.commit()

    await bot.send_message(
        user_id,
        "Buyurtmangizni tasdiqlash uchun iltimos, ism-familiyangizni kiriting.\n<i>Misol: Burxon Nurmurodov</i>",
        parse_mode='HTML'
    )

    return JSONResponse(content={"success": True, "message": "Order placed successfully."})

@router.post("/cancel-incomplete-order")
async def cancel_order(request: Request, db: Session = Depends(get_db)):
    """
    Cancels the user's incomplete order (if any).
    """
    data = await request.json()
    init_data_str = data.get("initData")
    
    # Use the central function to validate and get user_id
    user_id = get_user_id_from_init_data(init_data_str)

    incomplete_order = db.query(Order).filter(
        Order.user_id == user_id,
        (Order.user_name.is_(None)) | (Order.user_phone.is_(None)) | (Order.location.is_(None))
    ).first()

    if not incomplete_order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No incomplete order found")

    db.delete(incomplete_order)
    db.commit()

    await bot.send_message(
        user_id,
        "Buyurtmangiz bekor qilindi. Yangi buyurtma berish uchun davom eting.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("🛍️ Do'kon", web_app=WebAppInfo(url=URL+'/menu'))
        )
    )

    return JSONResponse(content={"success": True, "message": "Incomplete order cancelled."})