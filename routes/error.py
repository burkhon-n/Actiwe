from fastapi import APIRouter, Request, HTTPException
from config import templates

router = APIRouter(prefix="/errors", tags=["Errors"])

@router.get("/not-found")
async def not_found(request: Request):
    return templates.TemplateResponse("errors/not-found.html", {"request": request})

@router.get("/not-telegram")
async def not_telegram(request: Request):
    return templates.TemplateResponse("errors/not-telegram.html", {"request": request})

@router.get("/incomplete-order")
async def incomplete_order(request: Request):
    return templates.TemplateResponse("errors/incomplete-order.html", {"request": request})