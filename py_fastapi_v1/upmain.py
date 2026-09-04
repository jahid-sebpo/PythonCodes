import io
import os
import sqlite3
from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from views import LOGIN_HTML, DASHBOARD_HTML, ADMIN_HTML
from databaseHandler import init_db, get_current_user, get_db, get_user_by_username, verify_password, hash_password, require_admin
from dotenv import load_dotenv
from datetime import datetime

from utils import generate_excel

load_dotenv()

# Secret key for signing session cookies

SECRET_KEY = os.getenv("SECRET_KEY", "")

DB_FILE = "users.db"

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Run database setup on startup
init_db()

app = FastAPI(title="FastAPI Cookie-Auth & Admin System")

# Enable session middleware for signed cookie authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_token",
    max_age=86400  # 1 day in seconds
)

# Exception handler to gracefully redirect unauthenticated users to /login
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in (status.HTTP_307_TEMPORARY_REDIRECT, status.HTTP_401_UNAUTHORIZED):
        redirect_url = exc.headers.get("Location", "/login") if exc.headers else "/login"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    return HTMLResponse(content=f"<h1>Error {exc.status_code}</h1><p>{exc.detail}</p>", status_code=exc.status_code)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """Renders the login HTML page. Redirects to dashboard if already logged in."""
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    error_msg = f'<div class="bg-red-900/50 border border-red-500 text-red-200 p-3 rounded mb-4 text-xs">{error}</div>' if error else ""
    return LOGIN_HTML.format(error_msg=error_msg)

@app.post("/login")
async def handle_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Authenticates credentials and sets the session cookie."""
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return RedirectResponse(url="/login?error=Invalid+username+or+password", status_code=status.HTTP_303_SEE_OTHER)
    
    if not user["is_active"]:
        return RedirectResponse(url="/login?error=Account+is+disabled", status_code=status.HTTP_303_SEE_OTHER)

    # Set session user ID
    request.session["user_id"] = user["id"]
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout(request: Request):
    """Clears the session cookie and redirects to login."""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(current_user=Depends(get_current_user)):
    """Protected dashboard page."""
    admin_link = '<a href="/admin" class="bg-amber-600 hover:bg-amber-500 px-3 py-1.5 rounded text-xs font-semibold">Admin Panel</a>' if current_user["role"] == "admin" else ""

    return DASHBOARD_HTML.format(
        username=current_user["username"],
        role=current_user["role"],
        admin_link=admin_link
    )



@app.get("/create")
async def create_route(current_user=Depends(get_current_user)):
    """Example protected create endpoint."""
    return {"status": "success", "action": "create", "user": current_user["username"]}

@app.get("/update")
async def update_route(current_user=Depends(get_current_user)):
    """Example protected update endpoint."""
    return {"status": "success", "action": "update", "user": current_user["username"]}

@app.get("/check")
async def check_route(current_user=Depends(get_current_user)):
    """Protected API check endpoint."""
    return {"status": "running", "authenticated_as": current_user["username"]}

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(admin_user=Depends(require_admin)):
    """Serves the user management admin panel."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, is_active FROM users ORDER BY id ASC")
        users = cursor.fetchall()

    rows_html = ""
    for u in users:
        role_badge = "bg-amber-900/60 text-amber-300" if u["role"] == "admin" else "bg-gray-700 text-gray-300"
        delete_btn = f'''
            <form action="/admin/users/delete/{u['id']}" method="POST" class="inline" onsubmit="return confirm('Delete user {u['username']}?')">
                <button type="submit" class="text-red-400 hover:text-red-300 font-semibold text-xs">Delete</button>
            </form>
        ''' if u["username"] != admin_user["username"] else '<span class="text-gray-500 text-xs">Current Admin</span>'

        rows_html += f"""
        <tr>
            <td class="p-4">{u['id']}</td>
            <td class="p-4 font-bold text-white">{u['username']}</td>
            <td class="p-4"><span class="px-2 py-1 rounded text-xs font-semibold {role_badge}">{u['role']}</span></td>
            <td class="p-4"><span class="text-green-400 text-xs font-semibold">Active</span></td>
            <td class="p-4 text-right">{delete_btn}</td>
        </tr>
        """

    return ADMIN_HTML.format(user_rows=rows_html)

@app.post("/admin/users/create")
async def admin_create_user(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    admin_user=Depends(require_admin)
):
    """Admin endpoint to create a new user."""
    hashed_pw = hash_password(password)
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
                (username, hashed_pw, role)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        pass  # User already exists
        
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/users/delete/{user_id}")
async def admin_delete_user(user_id: int, admin_user=Depends(require_admin)):
    """Admin endpoint to delete a user."""
    if user_id != admin_user["id"]:  # Prevent self-deletion
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)



@app.get('/t')
def test():
    current_time_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    print(current_time_str)  

    return current_time_str


@app.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    sheet_name: str = Form("FT Matrix Output"),
    current_user=Depends(get_current_user)
):
    """
    Receives an uploaded Excel file and target sheet name,
    processes/generates the optimum version, and returns it as a downloadable Excel file.
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")

    try:
        # Read raw binary contents directly from request stream
        file_bytes = await file.read()
        
        # Parse matrix data from byte stream
        excel_bytes = generate_excel(
            file_source=file_bytes,
            sheet_name=sheet_name,
            orient="records"
        )
        current_time_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        headers = {
            "Content-Disposition": f"attachment; filename=optimumOutput-{current_time_str}.xlsx"
        }
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err)
        )
    except HTTPException:
        raise
    except Exception as err:
        print(f"❌ Unexpected Error: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating Excel file."
        )
