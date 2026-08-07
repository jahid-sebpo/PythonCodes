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
        <h1 class="text-xl font-bold text-indigo-400">Automation Management Dashboard</h1>
        <div class="flex items-center gap-4">
            <span class="text-sm text-gray-300">User: <strong class="text-white">{username}</strong> ({role})</span>
            {admin_link}
            <a href="/logout" class="bg-red-600 hover:bg-red-500 px-3 py-1.5 rounded text-xs font-semibold">Logout</a>
        </div>
    </nav>

    <main class="max-w-5xl mx-auto p-8 space-y-6">
        

        <!-- Generate Optimum Version Section -->
        <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
            <h2 class="text-xl font-bold text-indigo-400 mb-1">Generate Optimum version</h2>
            <p class="text-gray-400 text-sm mb-6">Select an Excel file and enter the sheet name to generate and download the optimized spreadsheet.</p>
            
            <form action="/upload-excel" method="POST" enctype="multipart/form-data" class="space-y-4 max-w-xl">
                <div>
                    <label class="block text-xs uppercase tracking-wider text-gray-400 mb-2 font-semibold">Choose Excel File</label>
                    <input type="file" name="file" accept=".xlsx, .xls" required 
                           class="w-full text-sm text-gray-300 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 bg-gray-700 border border-gray-600 rounded-lg p-1.5 cursor-pointer">
                </div>
                
                <div>
                    <label class="block text-xs uppercase tracking-wider text-gray-400 mb-2 font-semibold">Sheet Name</label>
                    <input type="text" name="sheet_name" placeholder="e.g. FT Matrix Output" required value="FT Matrix Output"
                           class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-indigo-500 text-white placeholder-gray-500 text-sm">
                </div>
                
                <button type="submit" class="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow transition duration-200 flex items-center justify-center gap-2 text-sm">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    Generate & Download
                </button>
            </form>
        </div>

        <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
            <h2 class="text-2xl font-semibold mb-2">Developing Portion</h2>
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
