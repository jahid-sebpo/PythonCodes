import os
import sqlite3
from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext

# Secret key for signing session cookies
SECRET_KEY = "super-secret-session-key-change-in-production"
DB_FILE = "users.db"

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    """Connects to SQLite database and returns a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Creates the users table if it doesn't exist and seeds a default admin."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)
        
        # Check if default admin exists; if not, create one
        cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            hashed_pw = pwd_context.hash("admin123")
            cursor.execute(
                "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
                ("admin", hashed_pw, "admin")
            )
            print("--> Seeded default admin user: 'admin' / password: 'admin123'")
        conn.commit()

# Run database setup on startup
init_db()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hashes a password string using bcrypt."""
    return pwd_context.hash(password)

def get_user_by_id(user_id: int):
    """Retrieves a user row from the database by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, is_active FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

def get_user_by_username(username: str):
    """Retrieves a user row from the database by username."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

async def get_current_user(request: Request):
    """
    Dependency that retrieves the currently logged-in user from session cookie.
    Redirects unauthenticated users to the /login page.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    
    user = get_user_by_id(user_id)
    if not user or not user["is_active"]:
        # Clear invalid session and redirect
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return user

async def require_admin(current_user=Depends(get_current_user)):
    """Dependency ensuring the authenticated user has an 'admin' role."""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin privileges required."
        )
    return current_user

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

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - Excel CRM System</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white flex items-center justify-center min-h-screen">
    <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-gray-700">
        <div class="text-center mb-6">
            <h1 class="text-2xl font-bold text-indigo-400">Welcome Back</h1>
            <p class="text-gray-400 text-sm mt-1">Please log in to access your dashboard</p>
        </div>
        
        {error_msg}

        <form action="/login" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs uppercase tracking-wider text-gray-400 mb-1">Username</label>
                <input type="text" name="username" required class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-indigo-500 text-white">
            </div>
            <div>
                <label class="block text-xs uppercase tracking-wider text-gray-400 mb-1">Password</label>
                <input type="password" name="password" required class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-indigo-500 text-white">
            </div>
            <button type="submit" class="w-full py-3 bg-indigo-600 hover:bg-indigo-500 font-semibold rounded-lg shadow-lg transition duration-200">
                Sign In
            </button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <nav class="bg-gray-800 border-b border-gray-700 px-6 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold text-indigo-400">Excel & CRM Management Dashboard</h1>
        <div class="flex items-center gap-4">
            <span class="text-sm text-gray-300">User: <strong class="text-white">{username}</strong> ({role})</span>
            {admin_link}
            <a href="/logout" class="bg-red-600 hover:bg-red-500 px-3 py-1.5 rounded text-xs font-semibold">Logout</a>
        </div>
    </nav>

    <main class="max-w-5xl mx-auto p-8">
        <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
            <h2 class="text-2xl font-semibold mb-2">System Status</h2>
            <p class="text-gray-400">You are securely logged in using Cookie-Based Session authentication.</p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <a href="/create" class="block p-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-center font-medium">
                    + Create Action (/create)
                </a>
                <a href="/update" class="block p-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-center font-medium">
                    ⚙ Update Action (/update)
                </a>
                <a href="/check" class="block p-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-center font-medium">
                    🔍 API Check (/check)
                </a>
            </div>
        </div>
    </main>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Panel - User Management</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <nav class="bg-gray-800 border-b border-gray-700 px-6 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold text-amber-400">Admin Control Panel</h1>
        <div class="flex items-center gap-4">
            <a href="/dashboard" class="text-sm text-gray-300 hover:text-white">← Return to Dashboard</a>
            <a href="/logout" class="bg-red-600 hover:bg-red-500 px-3 py-1.5 rounded text-xs font-semibold">Logout</a>
        </div>
    </nav>

    <main class="max-w-6xl mx-auto p-8 space-y-8">
        <!-- Add New User Form -->
        <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
            <h2 class="text-lg font-bold text-indigo-400 mb-4">Create New User</h2>
            <form action="/admin/users/create" method="POST" class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <input type="text" name="username" placeholder="Username" required class="px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                <input type="password" name="password" placeholder="Password" required class="px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                <select name="role" class="px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>
                <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 font-bold py-2 rounded">Create User</button>
            </form>
        </div>

        <!-- Existing Users Table -->
        <div class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-700">
                <h2 class="text-lg font-bold">Existing Users</h2>
            </div>
            <table class="w-full text-left text-sm text-gray-300">
                <thead class="bg-gray-700 text-gray-400 uppercase text-xs">
                    <tr>
                        <th class="p-4">ID</th>
                        <th class="p-4">Username</th>
                        <th class="p-4">Role</th>
                        <th class="p-4">Status</th>
                        <th class="p-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-700">
                    {user_rows}
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

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