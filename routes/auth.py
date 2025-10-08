import json
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session
from urllib.parse import parse_qsl, unquote

from database import get_db
from models import CartItem, Item, Order, Admin
from config import validate, SADMIN, DELIVERY_FEE
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_user_id_from_init_data(init_data_str: str) -> int:
    """Central helper function to validate initData and extract the user ID."""
    if not init_data_str or not validate(init_data_str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing initData")
    
    try:
        user_data_str = dict(parse_qsl(unquote(init_data_str))).get('user', '{}')
        user_data = json.loads(user_data_str)
        user_id = user_data.get("id")
        if not user_id:
            raise ValueError("User ID not found in initData")
        return user_id
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid user data format: {e}")

@router.post("/")
async def auth(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    init_data_str = data.get("initData")
    user_id = get_user_id_from_init_data(init_data_str)

    # Check for incomplete orders
    if db.query(Order).filter(Order.user_id == user_id, or_(Order.user_name.is_(None), Order.user_phone.is_(None), Order.location.is_(None))).first():
        return JSONResponse(
            content={'success': False, 'detail': 'You have an incomplete order.'}, 
            status_code=status.HTTP_409_CONFLICT
        )

    # Get all items and format them correctly for the frontend
    items_from_db = Item.get_all(db)
    items = {}
    for item in items_from_db:
        items[str(item.id)] = {
            "id": item.id,  # <-- THE FIX: Ensure the id is included in the item object
            "title": item.title,
            "price": item.price,
            "image": item.image,
            "sizes": item.sizes,
            "gender_neutral": item.gender_neutral,
            "description": item.description
        }

    # Get user's cart items - now including gender information
    cart_items_db = CartItem.get_by_user(db, user_id)
    cart_items = {}
    for ci in cart_items_db:
        if ci.gender:
            cart_items[f"{ci.item_id}-{ci.size}-{ci.gender}"] = ci.quantity
        else:
            cart_items[f"{ci.item_id}-{ci.size}"] = ci.quantity
    
    return JSONResponse(content={
        'success': True, 
        'items': items, 
        'cart_items': cart_items,
        'delivery_fee': DELIVERY_FEE
    })

@router.post("/check_role")
async def check_role(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    init_data_str = data.get("initData")
    user_id = get_user_id_from_init_data(init_data_str)

    if int(user_id) == int(SADMIN):
        admin = Admin(user_id, 'sadmin')
    else:
        admin = db.query(Admin).filter_by(telegram_id=user_id).first()

    return JSONResponse(content={'success': True, 'role': admin.role if admin else 'user'})