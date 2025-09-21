from fastapi import APIRouter, Depends, Request, HTTPException, status, Form, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from config import templates, validate, SADMIN
from models import Admin, Item, ShopTheme
from database import get_db
import os
import json
import uuid

# Ensure the upload directory exists
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter(prefix="/admin", tags=["Admin"])

# Dependency to get user role from Telegram init data
async def get_user_role_from_request(request: Request, db: Session = Depends(get_db)):
    try:
        init_data = request.query_params.get("initData")
        init_data_unsafe = request.query_params.get("initDataUnsafe")

        if not init_data or not init_data_unsafe:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Telegram data."
            )

        valid = validate(init_data)
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram data."
            )
        
        init_data_unsafe_dict = json.loads(init_data_unsafe)
        user_id = init_data_unsafe_dict["user"]["id"]

        if int(user_id) == int(SADMIN):
            admin_user = Admin(telegram_id=user_id, role='sadmin')
        else:
            admin_user = db.query(Admin).filter_by(telegram_id=user_id).first()

        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this page."
            )
        return admin_user.role
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Telegram data. Error: {e}"
        )

# Dependency to get user role from form data
async def get_user_role_from_form_data(
    initData: str = Form(...),
    initDataUnsafe: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        if not initData or not initDataUnsafe:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Telegram data."
            )
        
        valid = validate(initData)
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram data."
            )
        
        try:
            init_data_unsafe_dict = json.loads(initDataUnsafe)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Telegram data. Error: {e}"
            )
        
        user_id = init_data_unsafe_dict["user"]["id"]

        if int(user_id) == int(SADMIN):
            admin_user = Admin(user_id, 'sadmin')
        else:
            admin_user = db.query(Admin).filter_by(telegram_id=user_id).first()
        
        if not admin_user:
            return 'user'
        return admin_user.role
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

# A simplified check for admin access from form data
async def check_admin_access(role: str = Depends(get_user_role_from_request)):
    if role not in ['admin', 'sadmin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an admin to access this page."
        )

async def check_admin_access_form(role: str = Depends(get_user_role_from_form_data)):
    if role not in ['admin', 'sadmin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an admin to access this page."
        )

# Dependency to check for sadmin role
async def check_sadmin_access(role: str = Depends(get_user_role_from_request)):
    if role != 'sadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a super admin to access this page."
        )
# Dependency to check for sadmin role from form data
async def check_sadmin_access_form(role: str = Depends(get_user_role_from_form_data)):
    if role != 'sadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a super admin to access this page."
        )

@router.get("/")
async def admin_dashboard(request: Request, db: Session = Depends(get_db), _=Depends(check_admin_access)):
    """
    Serves the main admin dashboard.
    Users with the 'admin' role are redirected to this page from the root index.html.
    """
    shop_theme = db.query(ShopTheme).first()
    return templates.TemplateResponse("admin/index.html", {"request": request, "logo": shop_theme.logo if shop_theme else "/static/logo.png"})

@router.get("/super")
async def super_admin_dashboard(request: Request, db: Session = Depends(get_db), _=Depends(check_sadmin_access)):
    """
    Serves the super admin dashboard.
    Users with the 'sadmin' role are redirected to this page from the root index.html.
    """
    admins = db.query(Admin).all()
    shop_theme = db.query(ShopTheme).first()
    return templates.TemplateResponse("admin/super.html", {"request": request, "admins": admins, "logo": shop_theme.logo if shop_theme else "/static/logo.png"})

@router.get("/items/add")
async def add_item_page(request: Request, _=Depends(check_admin_access)):
    return templates.TemplateResponse("admin/item-form.html", {"request": request})

@router.get("/items/edit/{item_id}")
async def edit_item_page(item_id: int, request: Request, db: Session = Depends(get_db), _=Depends(check_admin_access)):
    item = Item.get(db, item_id)
    if not item:
        return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("admin/item-form.html", {"request": request, "item": item})

@router.post("/items/create")
async def create_item(
    title: str = Form(...),
    price: int = Form(...),
    sizes: str = Form(...),
    description: str = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(check_admin_access_form)
):
    try:
        # Generate a unique filename and save the file
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = str(uuid.uuid4()) + file_extension
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(image.file.read())

        # The image URL will be relative to the static directory
        image_url = f"/static/uploads/{unique_filename}"
        
        new_item = Item.create(
            session=db,
            title=title,
            price=price,
            image=image_url,
            sizes=sizes,
            description=description,
            category_id=1,
            created_by=1, # This should be replaced with the actual user ID
            updated_by=1  # This should be replaced with the actual user ID
        )
        db.commit()
        return JSONResponse(
            content={"success": True, "message": f"Item '{new_item.title}' created successfully."},
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            content={"success": False, "message": f"Failed to create item. Error: {e}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.put("/items/edit/{item_id}")
async def edit_item(
    item_id: int,
    title: str = Form(...),
    price: int = Form(...),
    sizes: str = Form(...),
    description: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    _=Depends(check_admin_access_form)
):
    try:
        existing_item = Item.get(db, item_id)
        if not existing_item:
            return JSONResponse(
                content={"success": False, "message": "Item not found."},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        image_url = existing_item.image
        if image:
            # Delete the old image if it exists
            if existing_item.image and os.path.exists(existing_item.image.lstrip('/')):
                os.remove(existing_item.image.lstrip('/'))

            # Generate a new unique filename and save the new file
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = str(uuid.uuid4()) + file_extension
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            with open(file_path, "wb") as f:
                f.write(image.file.read())
            
            image_url = f"/static/uploads/{unique_filename}"

        updated_item = Item.update(
            session=db,
            item_id=item_id,
            title=title,
            price=price,
            image=image_url,
            sizes=sizes,
            description=description,
        )
        db.commit()
        return JSONResponse(
            content={"success": True, "message": f"Item '{updated_item.title}' updated successfully."},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            content={"success": False, "message": f"Failed to update item. Error: {e}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

