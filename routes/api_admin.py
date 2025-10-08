from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import Admin, Item, ShopTheme, Order, User
from database import get_db
from routes.dependencies import get_admin_user
from bot import bot
from config import DELIVERY_FEE
import shutil
import uuid
import os
import json

router = APIRouter(prefix="/api/admin", tags=["Admin API"])

def is_admin(telegram_id: int, db: Session):
    """Check if the given telegram_id belongs to an admin user."""
    admin_user = db.query(Admin).filter_by(telegram_id=telegram_id).first()
    return admin_user is not None

@router.post("/items")
async def get_items_for_admin(db: Session = Depends(get_db), _=Depends(get_admin_user(roles=['admin', 'sadmin']))):
    """
    Fetches all items for the admin dashboard.
    This endpoint is protected and only accessible by admin or super admin roles.
    """
    items = db.query(Item).order_by(Item.id).all()
    return items

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db), _=Depends(get_admin_user(roles=['admin', 'sadmin']))):
    """
    Deletes an item by its ID. It also cleans up by deleting the item's
    associated image file from the server's static folder.
    """
    item_to_delete = db.query(Item).filter(Item.id == item_id).first()

    if not item_to_delete:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item not found")

    # If the item has an image, delete the physical file from storage
    if item_to_delete.image:
        # Construct the full path to the image file to ensure correct deletion
        image_path = os.path.join(os.getcwd(), item_to_delete.image.lstrip('/'))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.delete(item_to_delete)
    db.commit()
    return JSONResponse(content={"success": True, "message": "Item deleted successfully"})

@router.post("/admins")
async def get_admins(db: Session = Depends(get_db), _=Depends(get_admin_user(roles=['sadmin']))):
    """
    Fetches a list of all administrators.
    This endpoint is protected and only accessible by the super admin role.
    """
    admins = db.query(Admin).order_by(Admin.id).all()
    # Return a list of dictionaries to ensure proper JSON serialization by FastAPI
    return [{"id": admin.id, "telegram_id": admin.telegram_id, "role": admin.role} for admin in admins]

@router.post("/add")
async def add_admin(request: Request, db: Session = Depends(get_db), _=Depends(get_admin_user(roles=['sadmin']))):
    """
    Adds a new administrator by their Telegram ID.
    This endpoint is protected and only accessible by the super admin role.
    """
    data = await request.json()
    telegram_id = data.get("telegram_id")
    role = data.get("role", "admin")

    if not telegram_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Telegram ID is required")

    print("Adding new admin with Telegram ID:", telegram_id)
    if db.query(Admin).filter_by(telegram_id=telegram_id).first():
        print("Admin with this Telegram ID already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin with this Telegram ID already exists")

    print("Creating new admin with role:", role)
    new_admin = Admin(telegram_id=telegram_id, role=role)
    db.add(new_admin)
    db.commit()
    print("New admin added successfully")
    return JSONResponse(content={"success": True, "message": f"Admin with Telegram ID {telegram_id} added successfully."})

@router.delete('/delete/{id}')
async def delete_admin(id: int, db: Session = Depends(get_db), _=Depends(get_admin_user(roles=['sadmin']))):
    admin = db.query(Admin).filter_by(id=id).first()
    print("Admin: ", admin)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    db.delete(admin)
    db.commit()
    return JSONResponse(content={"success": True, "message": f"Admin with ID: {id} has been deleted successfully!"})

@router.post("/logo/upload")
async def upload_logo(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user(roles=['sadmin']))
):
    """
    Uploads a new logo image.
    This endpoint is protected and only accessible by the super admin role.
    """
    try:
        # Create unique filename to avoid collisions
        file_name = uuid.uuid4().hex + os.path.splitext(image.filename)[1]
        UPLOAD_FOLDER = "static/uploads"
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        file_location = os.path.join(UPLOAD_FOLDER, file_name)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Update the logo path in .env
        LOGO_PATH = f"/static/uploads/{file_name}"

        # Delete old logo file if it exists and is not the default logo
        old_logo = db.query(ShopTheme).first()
        if old_logo and old_logo.logo and old_logo.logo != LOGO_PATH:
            old_logo_path = os.path.join(os.getcwd(), old_logo.logo.lstrip('/'))
            if os.path.exists(old_logo_path):
                os.remove(old_logo_path)

        # Update or create the ShopTheme entry
        shop_theme = db.query(ShopTheme).first()
        if shop_theme:
            shop_theme.logo = LOGO_PATH
        else:
            shop_theme = ShopTheme(logo=LOGO_PATH)
            db.add(shop_theme)
        db.commit()

        return JSONResponse(content={"success": True, "message": "Logo uploaded successfully."})
    except Exception as e:
        print("Error uploading logo:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error uploading logo")

@router.get("/users/stats")
async def get_user_stats(db: Session = Depends(get_db), _=Depends(get_admin_user(roles=['admin', 'sadmin']))):
    """Get user statistics"""
    try:
        print("=== DEBUG: get_user_stats called ===")
        
        # Count all users
        total_users = db.query(User).count()
        print(f"DEBUG: total_users query result: {total_users}")
        
        # Count active users (last seen within 30 days)
        # Convert 30 days to epoch timestamp for comparison
        import time
        from datetime import datetime, timedelta
        thirty_days_ago_timestamp = int((datetime.utcnow() - timedelta(days=30)).timestamp())
        print(f"DEBUG: thirty_days_ago_timestamp: {thirty_days_ago_timestamp}")
        
        active_users = db.query(User).filter(User.last_interaction > thirty_days_ago_timestamp).count()
        print(f"DEBUG: active_users query result: {active_users}")
        
        stats = {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        }
        
        print(f"DEBUG: returning stats: {stats}")
        return stats
        
    except Exception as e:
        print(f"DEBUG: Error in get_user_stats: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user statistics: {str(e)}"
        )

# Test endpoint without authentication
@router.get("/test/users/stats")
async def test_get_user_stats(db: Session = Depends(get_db)):
    """Test endpoint to get user statistics without authentication"""
    try:
        print("=== DEBUG: test_get_user_stats called ===")
        
        # Count all users
        total_users = db.query(User).count()
        print(f"DEBUG: total_users query result: {total_users}")
        
        # Get all users for debugging
        all_users = db.query(User).all()
        print(f"DEBUG: all_users count: {len(all_users)}")
        for user in all_users:
            print(f"DEBUG: User - telegram_id: {user.telegram_id}, language_code: {user.language_code}, created_at: {user.created_at}, last_interaction: {user.last_interaction}")
        
        # Count active users (last seen within 30 days)
        # Convert 30 days to epoch timestamp for comparison
        import time
        from datetime import datetime, timedelta
        thirty_days_ago_timestamp = int((datetime.utcnow() - timedelta(days=30)).timestamp())
        print(f"DEBUG: thirty_days_ago_timestamp: {thirty_days_ago_timestamp}")
        
        active_users = db.query(User).filter(User.last_interaction > thirty_days_ago_timestamp).count()
        print(f"DEBUG: active_users query result: {active_users}")
        
        stats = {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
            "debug_users": [{"telegram_id": u.telegram_id, "language_code": u.language_code, "last_interaction": u.last_interaction} for u in all_users]
        }
        
        print(f"DEBUG: returning stats: {stats}")
        return stats
        
    except Exception as e:
        print(f"DEBUG: Error in test_get_user_stats: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user statistics: {str(e)}"
        )

@router.get("/users")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_admin_user(roles=['admin', 'sadmin']))):
    """Get list of users."""
    try:
        print(f"DEBUG: Getting users with skip={skip}, limit={limit}")
        users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        total = db.query(User).count()
        print(f"DEBUG: Found {len(users)} users, total={total}")
        
        users_data = []
        for user in users:
            # Convert epoch timestamps to ISO format for frontend
            from datetime import datetime
            created_at_iso = datetime.fromtimestamp(user.created_at).isoformat() if user.created_at else None
            last_interaction_iso = datetime.fromtimestamp(user.last_interaction).isoformat() if user.last_interaction else None
            
            user_data = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "display_name": f"User {user.telegram_id}",
                "is_active": user.is_active,
                "language_code": user.language_code,
                "created_at": created_at_iso,
                "last_interaction": last_interaction_iso
            }
            users_data.append(user_data)
            print(f"DEBUG: User data: {user_data}")
        
        result = {
            "users": users_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        print(f"DEBUG: Returning result: {result}")
        return result
    except Exception as e:
        print(f"DEBUG: Error in get_users: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting users: {str(e)}")

@router.get("/orders")
async def get_orders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), _=Depends(get_admin_user(roles=['admin', 'sadmin']))):
    """Get recent orders for admin panel."""
    try:
        orders = db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        orders_data = []
        for order in orders:
            # Calculate total amount from order items
            try:
                cart = json.loads(order.items)
                subtotal = sum(Item.get(db, int(k.split('-')[0])).price * v for k, v in cart.items())
                total_amount = subtotal + DELIVERY_FEE
            except:
                total_amount = 0
            
            orders_data.append({
                "id": order.id,
                "user_id": order.user_id,
                "name": order.user_name or f"User {order.user_id}",
                "phone": order.user_phone or "Not provided",
                "total_amount": total_amount,
                "created_at": order.created_at
            })
        
        return {
            "orders": orders_data,
            "total": db.query(Order).count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting orders: {str(e)}")