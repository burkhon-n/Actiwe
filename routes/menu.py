from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from config import templates
from models import Item, ShopTheme
from database import get_db

router = APIRouter(tags=["Menu"])

@router.get("/menu")
async def menu_page(request: Request, db: Session = Depends(get_db)):
    """
    Serves the main shop/menu page.
    OPTIMIZED: Fetches all items and passes the logo path to the template,
    which is required by the updated menu.html.
    """
    items = Item.get_all(db)
    logo = db.query(ShopTheme).first().logo if db.query(ShopTheme).first() else None
    return templates.TemplateResponse("menu.html", {
        "request": request, 
        "items": items,
        "logo": logo if logo else "/static/logo.png"
    })