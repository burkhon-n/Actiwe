from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import Admin, Item, ShopTheme
from database import get_db
from routes.dependencies import get_admin_user
import shutil
import uuid
import os

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