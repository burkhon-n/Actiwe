from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from database import engine, Base, SessionLocal
from models import Admin, ShopTheme
from routes import menu, auth, admin, api_admin, error, api_user
from config import SADMIN, URL
from bot import bot, Update
import contextlib
import logging

# --- Logging Configuration ---
# Sets up basic logging to see application events and errors in your console.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Create Database Tables ---
# This ensures that all tables defined in your models are created in the database
# when the application starts for the first time.
try:
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created or already exist.")
except Exception as e:
    logging.error(f"Error creating database tables: {e}")

# --- Initialize Super Admin ---
# On startup, this block checks if the super admin from the .env file exists.
# If not, it creates the user, which is crucial for the first run.
with contextlib.closing(SessionLocal()) as db:

    try:
        if not db.query(ShopTheme).first():
            default_theme = ShopTheme(name="Actiwe", logo="/static/logo.png")
            db.add(default_theme)
            db.commit()
            logging.info("Default shop theme created successfully.")
    except Exception as e:
        logging.error(f"Error creating default shop theme: {e}")
        db.rollback()


# --- FastAPI App Initialization ---
app = FastAPI(title="Telegram Shop")

# --- Static Files Mounting ---
# This makes the 'static' directory available to the web, so files like images
# can be accessed via URLs (e.g., /static/logo.png).
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Telegram Webhook Setup ---
@app.on_event("startup")
async def on_startup():
    """Sets the Telegram webhook when the FastAPI application starts."""
    try:
        webhook_url = f"{URL}/webhook"
        await bot.set_webhook(url=webhook_url)
        logging.info(f"Telegram webhook set to {webhook_url}")
    except Exception as e:
        logging.error(f"Failed to set Telegram webhook: {e}")

@app.post("/webhook")
async def webhook_handler(request: Request):
    """This endpoint receives all updates from Telegram and processes them."""
    try:
        json_data = await request.json()
        update = Update.de_json(json_data)
        await bot.process_new_updates([update])
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Error processing webhook update: {e}")
        return {"status": "error"}

# --- Root Endpoint ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main index.html, which redirects users based on their role."""
    with open("templates/index.html") as f:
        return HTMLResponse(content=f.read())

# --- Include Application Routers ---
# Connects all the separate route files to the main application.
app.include_router(menu.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(api_admin.router)
app.include_router(api_user.router)
app.include_router(error.router)

