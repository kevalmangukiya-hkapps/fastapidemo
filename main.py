from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    # client = MongoClient("mongodb+srv://keval12345:keval12345@notesapp.ngmxhfw.mongodb.net/")
db = client.get_database("test_db")
users_collection = db.get_collection("users")


async def get_user(email: str):
    user = await users_collection.find_one({"email": email})
    return user


async def create_user(email: str, password: str):
    hashed_password = pwd_context.hash(password)
    user = {"email": email, "password": hashed_password}
    await users_collection.insert_one(user)


@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_user(request: Request, email: str = Form(...), password: str = Form(...)):
    user = await get_user(email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    await create_user(email, password)
    return templates.TemplateResponse("success.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    user = await get_user(email)
    if not user or not pwd_context.verify(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return templates.TemplateResponse("success.html", {"request": request})


@app.get("/static/{path:path}", response_class=HTMLResponse)
async def static_files(request: Request, path: str):
    return templates.TemplateResponse(f"static/{path}", {"request": request})
