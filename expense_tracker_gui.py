import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import os
import json
import matplotlib.pyplot as plt

# =========================
# FILES & DATA SETUP
# =========================
USERS_FILE = "users.json"
DATA_FILE = "expenses.csv"
COLUMNS = ["User", "Name", "Amount", "Category"]

# Load Users
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Global DataFrame Initialization
def load_csv_data():
    if os.path.exists(DATA_FILE):
        try:
            temp_df = pd.read_csv(DATA_FILE)
            if "User" in temp_df.columns:
                return temp_df
        except:
            pass
    return pd.DataFrame(columns=COLUMNS)

df = load_csv_data()
BUDGET_LIMIT = 0
current_user = None

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# =========================
# LOGIN WINDOW
# =========================
def login_screen():
    def login():
        u, p = user_entry.get(), pass_entry.get()
        if u in users and users[u] == p:
            global current_user
            current_user = u
            login_win.destroy()
            main_app()
        else:
            messagebox.showerror("Error", "Invalid login")

    def register():
        u, p = user_entry.get(), pass_entry.get()
        if not u or not p:
            messagebox.showerror("Error", "Enter username/password")
            return
        users[u] = p
        save_users()
        messagebox.showinfo("Success", "User registered")

    login_win = tk.Tk()
    login_win.title("Expense Tracker Login")
    login_win.geometry("320x250")
    login_win.configure(bg="#f7d6e0")

    tk.Label(login_win, text="Login System", font=("Segoe UI", 16, "bold"), bg="#f7d6e0").pack(pady=10)
    tk.Label(login_win, text="Username", bg="#f7d6e0").pack()
    user_entry = tk.Entry(login_win)
    user_entry.pack()
    tk.Label(login_win, text="Password", bg="#f7d6e0").pack()
    pass_entry = tk.Entry(login_win, show="*")
    pass_entry.pack()
    tk.Button(login_win, text="Login", bg="#cdb4db", command=login).pack(pady=5)
    tk.Button(login_win, text="Register", bg="#a2d2ff", command=register).pack()
    login_win.mainloop()

# =========================
# MAIN APPLICATION
# =========================
def main_app():
    root = tk.Tk()
    root.title("Pastel Expense Tracker")
    root.geometry("650x550")
    root.configure(bg="#e2ece9")

    # --- FUNCTIONS ---
    def add_expense():
        global df
        name, amount, cat = name_entry.get(), amount_entry.get(), category_entry.get()
        if not name or not amount:
            messagebox.showerror("Error", "Fill fields")
            return
        try:
            val = float(amount)
            new_row = pd.DataFrame([[current_user, name, val, cat]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            update_total()
            messagebox.showinfo("Saved", "Expense added")
        except:
            messagebox.showerror("Error", "Amount must be a number")

    def update_total():
        user_df = df[df["User"] == current_user]
        total = user_df["Amount"].sum()
        total_label.config(text=f"Total: {total:.2f}")
        if BUDGET_LIMIT > 0 and total > BUDGET_LIMIT:
            messagebox.showwarning("Budget Alert", "You exceeded your budget!")

    def set_budget():
        global BUDGET_LIMIT
        val = simpledialog.askfloat("Budget", "Enter monthly budget:")
        if val:
            BUDGET_LIMIT = val
            messagebox.showinfo("Saved", f"Budget set to {val}")

    def export_excel():
        user_df = df[df["User"] == current_user]
        user_df.to_excel(f"{current_user}_expenses.xlsx", index=False)
        messagebox.showinfo("Exported", "Excel file created")

    def show_pie():
        user_df = df[df["User"] == current_user]
        if user_df.empty: return
        cat_data = user_df.groupby("Category")["Amount"].sum()
        plt.figure(figsize=(6,6))
        plt.pie(cat_data, labels=cat_data.index, autopct="%1.1f%%")
        plt.title("Expense Distribution")
        plt.show()

    def show_graph():
        user_df = df[df["User"] == current_user]
        if user_df.empty: return
        plt.figure(figsize=(8,4))
        plt.plot(user_df["Name"], user_df["Amount"], marker="o", color="#ff8fab")
        plt.title("Expense Trend")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # --- UI LAYOUT ---
    tk.Label(root, text=f"Welcome {current_user}", font=("Segoe UI", 16, "bold"), bg="#e2ece9").pack(pady=10)
    
    form = tk.Frame(root, bg="#e2ece9")
    form.pack(pady=10)

    tk.Label(form, text="Expense Name", bg="#e2ece9").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(form)
    name_entry.grid(row=0, column=1)

    tk.Label(form, text="Amount", bg="#e2ece9").grid(row=1, column=0, padx=5, pady=5)
    amount_entry = tk.Entry(form)
    amount_entry.grid(row=1, column=1)

    tk.Label(form, text="Category", bg="#e2ece9").grid(row=2, column=0, padx=5, pady=5)
    category_entry = tk.Entry(form)
    category_entry.grid(row=2, column=1)

    # Buttons
    tk.Button(root, text="Add Expense", bg="#c7eae4", width=20, command=add_expense).pack(pady=3)
    tk.Button(root, text="Set Budget", bg="#ffd6a5", width=20, command=set_budget).pack(pady=3)
    tk.Button(root, text="Pie Chart", bg="#bde0fe", width=20, command=show_pie).pack(pady=3)
    tk.Button(root, text="Graph Chart", bg="#ffc8dd", width=20, command=show_graph).pack(pady=3)
    tk.Button(root, text="Export to Excel", bg="#d8f3dc", width=20, command=export_excel).pack(pady=3)

    total_label = tk.Label(root, text="Total: 0.0", font=("Segoe UI", 14, "bold"), bg="#e2ece9")
    total_label.pack(pady=20)

    update_total()
    root.mainloop()

if __name__ == "__main__":
    login_screen()