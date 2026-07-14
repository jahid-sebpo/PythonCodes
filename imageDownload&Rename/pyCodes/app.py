import tkinter as tk
from tkinter import ttk
import datetime
from rename_images_from_excel_template import download_images_from_links
from rename_images_from_excel_template import rename_and_copy_images


# ==========================================
# 1. YOUR CUSTOM FUNCTIONS
# ==========================================

def execute_function_one():
    """
    This is the first function. 
    You can replace the logic inside this block with your own Python code.
    """
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    download_images_from_links()

    log_message(f"[{now}] 🚀 Function One Executed!\n"
                f"   - Processing task A...\n"
                f"   - Task complete!")

def execute_function_two():
    """
    This is the second function.
    You can replace the logic inside this block with your own Python code.
    """
    rename_and_copy_images()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message(f"[{now}] ⚙️ Function Two Executed!\n"
                f"   - Running diagnostics...\n"
                f"   - All systems operational!")


# ==========================================
# 2. GUI SETUP & DESIGN (Tkinter)
# ==========================================

# Helper function to print messages to the app's visual log
def log_message(message):
    output_box.config(state="normal")  # Temporarily enable editing
    output_box.insert(tk.END, message + "\n\n")
    output_box.see(tk.END)             # Auto-scroll to the bottom
    output_box.config(state="disabled") # Disable editing again

# Create the main window
root = tk.Tk()
root.title("Execution Panel")
root.geometry("500x450")
root.configure(bg="#1e1e2e") # Dark modern theme background

# Configure grid/resizing weights
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)

# Application Header
header_label = tk.Label(
    root, 
    text="Python Action Controller", 
    font=("Helvetica", 16, "bold"), 
    fg="#f5c2e7", 
    bg="#1e1e2e"
)
header_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

# Subheader instructions
subtitle_label = tk.Label(
    root, 
    text="Click a button below to trigger its corresponding function.", 
    font=("Helvetica", 10), 
    fg="#a6adc8", 
    bg="#1e1e2e"
)
subtitle_label.grid(row=1, column=0, pady=(0, 20), sticky="ew")

# Button Layout Container
button_frame = tk.Frame(root, bg="#1e1e2e")
button_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=1)

# Style configuration for buttons
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Primary.TButton",
    font=("Helvetica", 11, "bold"),
    background="#89b4fa",
    foreground="#11111b",
    borderwidth=0,
    focusthickness=0,
    focuscolor="none"
)
style.configure(
    "Secondary.TButton",
    font=("Helvetica", 11, "bold"),
    background="#a6e3a1",
    foreground="#11111b",
    borderwidth=0,
    focusthickness=0,
    focuscolor="none"
)

# Button 1
btn_one = ttk.Button(
    button_frame, 
    text="Download Images", 
    style="Primary.TButton", 
    command=execute_function_one
)
btn_one.grid(row=0, column=0, padx=10, pady=10, ipady=12, sticky="ew")

# Button 2
btn_two = ttk.Button(
    button_frame, 
    text="Rename Images", 
    style="Secondary.TButton", 
    command=execute_function_two
)
btn_two.grid(row=0, column=1, padx=10, pady=10, ipady=12, sticky="ew")

# Log/Console Label
log_label = tk.Label(
    root, 
    text="System Activity Log:", 
    font=("Helvetica", 10, "bold"), 
    fg="#cdd6f4", 
    bg="#1e1e2e", 
    anchor="w"
)
log_label.grid(row=3, column=0, padx=30, pady=(10, 2), sticky="ew")

# Visual Console Output Box
output_box = tk.Text(
    root, 
    height=10, 
    bg="#181825", 
    fg="#a6e3a1", 
    font=("Courier", 10), 
    borderwidth=1, 
    relief="solid",
    padx=10,
    pady=10,
    state="disabled" # Starts read-only
)
output_box.grid(row=4, column=0, padx=30, pady=(0, 25), sticky="nsew")

# Print initial greeting to console
log_message("System initialized. Click any button above to begin.")

# Run the app loop
root.mainloop()