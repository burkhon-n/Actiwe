from fastapi import Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Admin
from config import validate, SADMIN
import json
from urllib.parse import parse_qsl, unquote

def get_user_id_from_init_data(init_data_str: str) -> int:
    """
    Central helper function to validate initData and extract the user ID.
    Used for authenticating regular users.
    """
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

def get_admin_user(form: bool = False, roles: list[str] = None):
    """
    Dependency factory to authenticate and authorize an admin user from Telegram initData.
    Can read from request body (JSON) or form data based on the 'form' flag.
    """
    print("Admin dependency invoked")
    if roles is None:
        roles = ['admin', 'sadmin']
        print("Default roles applied:", roles)

    async def _get_user_data_from_request(request: Request, initData: str = Form(None)):
        print("Getting user data from request")

        try:
            # Try to parse JSON first
            body = await request.json()
            print("Request body:", body)
            return body.get("initData")

        except Exception as e:
            # Handle "Stream consumed" (multipart already parsed)
            if "Stream consumed" in str(e):
                if initData:
                    print("Falling back to form initData:", initData)
                    return initData
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="initData required in form data for multipart requests",
                )

            # Handle invalid JSON
            print("Error getting initData from request:", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON or form data in request",
            )


    async def _get_user_data_from_form(initData: str = Form(...)):
        print("Getting user data from form")
        return initData

    async def _verify_user(
        db: Session = Depends(get_db),
        init_data_str: str = Depends(_get_user_data_from_form if form else _get_user_data_from_request)
    ):
        print("Verifying user with initData:", init_data_str)
        user_id = get_user_id_from_init_data(init_data_str) # Reuse the user validation logic
        
        if int(user_id) == int(SADMIN):
            admin_user = Admin(user_id, 'sadmin')
        else:
            admin_user = db.query(Admin).filter_by(telegram_id=user_id).first()
            
        print("Admin user fetched from DB:", admin_user)
        if not admin_user or admin_user.role not in roles:
            print("User role not authorized:", admin_user.role if admin_user else "No admin user")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied. Admin access required.")

        print("User authorized as admin with role:", admin_user.role)
        return admin_user

    print("Admin dependency created with form =", form, "and roles =", roles)
    return _verify_user

