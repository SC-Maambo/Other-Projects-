import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import numpy as np
from numpy import random
import json
import os

# --- Data ---
prefects = ["Alex", "Jessica", "Temwani", "Charlene", "Lincoln", "Olivia", "Luyando",
            "Mark", "Christian", "Sula", "Moses", "Hope", "Chipego", "Mainza", "Bukata",
            "Elika", "Thabo", "Swag", "Victor", "Alisa"]

boys = ["Alex", "Lincoln", "Mark", "Sula", "Moses", "Swag", "Victor", "Christian"]
girls = [x for x in prefects if x not in boys]

locations = ["Form 1 Red", "Form 1 Blue", "Grade 9 Red", "Grade 9 Blue",
              "Grade 10", "Grade 11 Red", "Grade 11 Blue",
             "Toilets", "Tuckshop", "Outside"]

# --- Files ---
DATA_FILE = "prefect_data.json"

# --- Global State ---
excluded_leaders = set()   # unified list: excluded + past leaders
leader_history = []        # stores confirmed leader pairs
last_layout = {}
current_layout = {}
current_leaders = ("No leader", "No leader")
ADMIN_PASSWORD = "#MAAMBO729"  # Change as needed

# --- Persistence Functions ---
def load_data():
    global excluded_leaders, leader_history, last_layout
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            excluded_leaders.update(data.get("excluded_leaders", []))
            leader_history.extend(data.get("leader_history", []))
            last_layout.update(data.get("last_layout", {}))

def save_data():
    data = {
        "excluded_leaders": list(excluded_leaders),
        "leader_history": leader_history,
        "last_layout": last_layout
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- Prefect Logic Functions ---
def select_pairs():
    local_boys = boys.copy()
    local_girls = girls.copy()
    pairs = []

    for _ in range(len(local_boys)):
        if not local_girls:
            break
        chosen_boy = random.choice(local_boys)
        local_boys.remove(chosen_boy)
        chosen_girl = random.choice(local_girls)
        local_girls.remove(chosen_girl)
        pairs.append((chosen_boy, chosen_girl))

    while len(local_girls) >= 2:
        g1 = random.choice(local_girls)
        local_girls.remove(g1)
        g2 = random.choice(local_girls)
        local_girls.remove(g2)
        pairs.append((g1, g2))

    return pairs

def assign_locations(pairs):
    shuffled_locations = locations.copy()
    random.shuffle(shuffled_locations)
    assignments = {}
    for i, pair in enumerate(pairs[:len(shuffled_locations)]):
        assignments[shuffled_locations[i]] = pair
    return assignments

def get_leaders(assignments):
    candidate_pair = assignments.get("Toilets", ("No leader", "No leader"))
    c1, c2 = candidate_pair

    available_prefects = [p for p in prefects if p not in excluded_leaders]
    available_male_prefects = [p for p in boys if p not in excluded_leaders]
    available_female_prefects = [p for p in girls if p not in excluded_leaders]
    if c1 in excluded_leaders and c2 in excluded_leaders:
        if available_prefects:
            if available_male_prefects:
                leader1 = available_male_prefects[0]
                if available_female_prefects:
                    remaining_girls = [p for p in available_female_prefects]
                    leader2 = remaining_girls[0] 
                    return (leader1, leader2)
                else: 
                    for x in excluded_leaders:
                        if x in girls:
                            excluded_leaders.remove(x)
            else:
                for x in excluded_leaders:
                    if x in boys:
                        excluded_leaders.remove(x)
        else:
            return ("No leader", "No leader")
    elif c1 in excluded_leaders:
        leader1 = c2
        remaining = [p for p in available_prefects if p != leader1]
        leader2 = remaining[0] if remaining else leader1
        return (leader1, leader2)
    elif c2 in excluded_leaders:
        leader1 = c1
        remaining = [p for p in available_prefects if p != leader1]
        leader2 = remaining[0] if remaining else leader1
        return (leader1, leader2)
    else:
        return candidate_pair

# --- GUI Functions ---
def generate_prefects():
    global current_layout, current_leaders
    pairs = select_pairs()
    assignments = assign_locations(pairs)
    leaders = get_leaders(assignments)

    current_layout = {loc: pair for loc, pair in assignments.items()}
    current_leaders = leaders

    # Clear previous display
    for widget in frame_results.winfo_children():
        widget.destroy()

    # Show leaders
    lbl_leaders.config(text=f"Leaders: {leaders[0]} and {leaders[1]}")

    # Show all pairs and locations
    for loc, pair in assignments.items():
        tk.Label(frame_results, text=f"{loc}: {pair[0]} and {pair[1]}", font=("Arial", 10), bg="white").pack(anchor="w")

def confirm_layout():
    global last_layout, leader_history, excluded_leaders
    if not current_layout:
        messagebox.showwarning("Warning", "No layout generated yet!")
        return

    last_layout = current_layout.copy()
    leader_history.append(list(current_leaders))
    excluded_leaders.update(current_leaders)
    save_data()
    messagebox.showinfo("Confirmed", f"Layout confirmed.\nLeaders: {current_leaders[0]} and {current_leaders[1]}")

def exclude_names():
    names = entry_exclude.get().split(",")
    names = [name.strip() for name in names if name.strip()]
    if not names:
        return
    excluded_leaders.update(names)
    entry_exclude.delete(0, tk.END)
    save_data()
    messagebox.showinfo("Excluded", f"Excluded from leadership: {', '.join(names)}")

def manage_exclusions():
    pw = simpledialog.askstring("Authentication", "Enter admin password:", show="*")
    if pw != ADMIN_PASSWORD:
        messagebox.showerror("Error", "Incorrect password!")
        return

    manage_win = tk.Toplevel(root)
    manage_win.title("Manage Excluded Leaders")
    manage_win.geometry("400x400")
    manage_win.config(bg="white")

    tk.Label(manage_win, text="Currently Excluded Names:", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
    listbox = tk.Listbox(manage_win, width=40, height=12)
    listbox.pack(pady=5)
    for name in excluded_leaders:
        listbox.insert(tk.END, name)

    tk.Label(manage_win, text="Add Name to Exclusion:", font=("Arial", 12), bg="white").pack(pady=5)
    entry_add = tk.Entry(manage_win, width=30)
    entry_add.pack(pady=5)

    def add_name():
        name = entry_add.get().strip()
        if name and name not in excluded_leaders:
            excluded_leaders.add(name)
            listbox.insert(tk.END, name)
            entry_add.delete(0, tk.END)
            save_data()

    btn_add = tk.Button(manage_win, text="Add", command=add_name)
    btn_add.pack(pady=5)

    def remove_name():
        selected = listbox.curselection()
        if selected:
            name = listbox.get(selected[0])
            excluded_leaders.remove(name)
            listbox.delete(selected[0])
            save_data()

    btn_remove = tk.Button(manage_win, text="Remove Selected", command=remove_name)
    btn_remove.pack(pady=5)

    # --- Reset App Button ---
    def reset_app():
        pw_reset = simpledialog.askstring("Authentication", "Enter admin password to reset app:", show="*")
        if pw_reset != ADMIN_PASSWORD:
            messagebox.showerror("Error", "Incorrect password!")
            return
        if messagebox.askyesno("Confirm Reset", "This will erase all leader history and excluded names. Are you sure?"):
            excluded_leaders.clear()
            leader_history.clear()
            last_layout.clear()
            save_data()
            messagebox.showinfo("Reset", "App has been reset successfully.")

    btn_reset = tk.Button(manage_win, text="Reset App", fg="red", command=reset_app)
    btn_reset.pack(pady=10)

def view_leader_history():
    history_win = tk.Toplevel(root)
    history_win.title("Leader History")
    history_win.geometry("400x300")
    history_win.config(bg="white")
    tk.Label(history_win, text="Leader History (and exclusions):", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
    listbox = tk.Listbox(history_win, width=40, height=12)
    listbox.pack(pady=5)
    for leaders in leader_history:
        listbox.insert(tk.END, f"{leaders[0]} and {leaders[1]}")

# --- Loading Screen ---
def start_main_app():
    load_data()
    loading_screen.destroy()
    root.deiconify()

loading_screen = tk.Tk()
loading_screen.overrideredirect(True)
loading_screen.geometry("500x250+450+250")

tk.Label(loading_screen, text="Kalulushi Trust School".upper(), font=("Arial", 18, "bold")).pack(pady=30)

progress = ttk.Progressbar(loading_screen, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=20)

tk.Label(loading_screen, text="MAAMBO", font=("Arial", 20, "bold")).pack(side="bottom", anchor="e", padx=10, pady=10)

def fill_progress(value=0):
    if value <= 100:
        progress['value'] = value
        loading_screen.update_idletasks()
        loading_screen.after(20, fill_progress, value + 1)
    else:
        start_main_app()

fill_progress()

# --- Main App Window ---
root = tk.Tk()
root.title("KTS Prefect Assignment")
root.geometry("1000x1000")
root.config(bg="white")
root.withdraw()

tk.Label(root, text="Kalulushi Trust School".upper(), font=("Arial", 20, "bold"), bg="white").grid(row=0, column=0, columnspan= 5, pady=20, rowspan=2)

btn_generate = tk.Button(root, text="Generate Prefect Assignments", font=("Arial", 12), command=generate_prefects, width=30)
btn_generate.grid(row=2, column = 0, pady=5, sticky='w')

btn_confirm = tk.Button(root, text="Confirm Layout", font=("Arial", 12), command=confirm_layout, width=30, activebackground= 'green')
btn_confirm.grid(row=3, column=0, pady=5, sticky='w')

lbl_leaders = tk.Label(root, text="", font=("Arial", 17, "bold"), bg="white")
lbl_leaders.grid(row=6 ,column =0, sticky='W' )

# Exclusion terminal
frame_exclude = tk.Frame(root, bg="white")
tk.Label(frame_exclude, text="Exclude Names (comma-separated):", font=("Arial", 12), bg="white").grid(row= 2, column=3,  padx=10)
entry_exclude = tk.Entry(frame_exclude, width=30)
entry_exclude.grid(row=2, column=4, padx=5)
btn_exclude = tk.Button(frame_exclude, text="Exclude", command=exclude_names)
btn_exclude.grid(row=2, column=5,  padx=5)
frame_exclude.grid(row=2,column=4)

btn_manage = tk.Button(root, text="Manage Excluded Leaders", font=("Arial", 12), command=manage_exclusions, width=30)
btn_manage.grid(row=4, column=0,pady=5, padx=5, sticky='w' )

btn_history = tk.Button(root, text="View Leader History", font=("Arial", 12),width=30, command=view_leader_history)
btn_history.grid(row =5, column=0,pady=5, padx=5, sticky='w' )

frame_results = tk.Frame(root, bg="white", width=100, height=20)
frame_results.grid(row= 7, column=0, sticky='w')

lbl_maambo = tk.Label(root, text="MAAMBO", font=("Arial", 20, "bold"), bg="white")
lbl_maambo.grid(row=1, column=6, padx=10, pady=5, sticky='e')

root.mainloop()
