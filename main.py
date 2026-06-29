import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
import os
from PIL import Image, ImageTk
import threading
from datetime import datetime
import json

photo_label = None
selected_color = "#1F6AA5"
capsules = []
selected_photos = []
USER_FILE = "users.json"
current_user = None
months = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

def get_capsule_file():
    return f"{current_user}_capsules.json"

def upload_photo():
    global selected_photos, photo_frame
    files = filedialog.askopenfilenames(
        title="Select Photos",
        filetypes=[
            ("Images", "*.png *.jpg *.jpeg *.gif")
        ]
    )
    selected_photos.extend(files)
    # Remove old previews
    for widget in photo_frame.winfo_children():
        widget.destroy()
    # Show new previews
    for photo_path in selected_photos:
        image = Image.open(photo_path)

        photo = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(80, 80)
        )

        label = ctk.CTkLabel(
            photo_frame,
            image=photo,
            text=""
        )
        label.image = photo
        label.pack(side="left", padx=5, pady=5)
    render_photos()

def render_photos():
    global photo_frame, selected_photos
    for widget in photo_frame.winfo_children():
        widget.destroy()
    for idx, photo_path in enumerate(selected_photos):
        container = ctk.CTkFrame(photo_frame, fg_color="transparent")
        container.pack(side="left", padx=5)
        img = Image.open(photo_path)
        photo = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(80, 80)
        )
        label = ctk.CTkLabel(container, image=photo, text="")
        label.image = photo
        label.pack()

        # 🔥 REMOVE BUTTON (this is what you lost)
        btn = ctk.CTkButton(
            container,
            text="Remove",
            width=35,
            height=35,
            fg_color="#8f0c00",
            command=lambda p=photo_path: remove_photo(p)
        )
        btn.pack()
def remove_photo(photo_path):
    global selected_photos
    selected_photos.remove(photo_path)
    render_photos()

def select_color(color):
    global selected_color

    selected_color = color

    if 'create_capsule_button' in globals():
        create_capsule_button.configure(
            fg_color=color
        )
# Delete capsule card
def delete_capsule(card, capsule_data):

    card.destroy()

    if capsule_data in capsules:
        capsules.remove(capsule_data)

        save_capsules()
        render_capsules()

# Toggle favorite status
def toggle_favorite(capsule, button):

    capsule["favorite"] = not capsule["favorite"]
    
    if capsule["favorite"]:
        button.configure(text="⭐")
    else:
        button.configure(text="☆")
    save_capsules()
def filter_capsules(filter_type):


    for widget in capsules_container.winfo_children():
        widget.destroy()

    filtered = []

    for capsule in capsules:
        update_capsule_status(capsule)

        if filter_type == "all":
            filtered.append(capsule)

        elif filter_type == "closed":
            if capsule["status"] == "🔒 Closed":
                filtered.append(capsule)

        elif filter_type == "opened":
            if capsule["status"] == "🔓 Opened":
                filtered.append(capsule)

        elif filter_type == "favorites":
            if capsule["favorite"]:
                filtered.append(capsule)

    render_capsules(filtered)
def save_capsules():
    data_to_save = []

    for capsule in capsules:
        copy = capsule.copy()
        copy.pop("card", None)

        # Save only the date
        if isinstance(copy["open_date"], datetime):
            copy["open_date"] = copy["open_date"].strftime("%Y-%m-%d")

        data_to_save.append(copy)

    with open(get_capsule_file(), "w") as file:
        json.dump(data_to_save, file, indent=4)

def load_capsules():
    global capsules
    try:
        with open(get_capsule_file(),"r") as file:
            capsules = json.load(file)
        for capsule in capsules:
            capsule["open_date"] = datetime.strptime(
                capsule["open_date"],
                "%Y-%m-%d"
            )
            capsule["favorite"] = capsule.get("favorite", False)
            capsule["photos"] = capsule.get("photos", [])
    except FileNotFoundError:
        capsules = []

    except Exception as e:
        print("Loading error:", e)
        capsules = []

    render_capsules()
def update_capsule_status(capsule):
    if isinstance(capsule["open_date"], str):
        capsule["open_date"] = datetime.strptime(
            capsule["open_date"],
            "%Y-%m-%d"
        )

    now = datetime.now()

    if capsule["open_date"] > now:
        capsule["status"] = "🔒 Closed"
    else:
        capsule["status"] = "🔓 Opened"

    capsule["days_left"] = max(
        (capsule["open_date"] - now).days,
        0
    )
def render_capsules(capsule_list=None):
    if capsule_list is None:
        capsule_list = capsules

    for widget in capsules_container.winfo_children():
        widget.destroy()

    for i, capsule in enumerate(capsule_list):
        update_capsule_status(capsule)

        row = i // 3
        column = i % 3

        capsule_card = ctk.CTkFrame(
            capsules_container,
            width=270,
            height=150,
            corner_radius=15,
            fg_color=capsule.get("color", "#6C3EB8")
        )

        capsule_card.grid_propagate(False)
        capsule_card.pack_propagate(False)

        capsule_card.grid(
            row=row,
            column=column,
            padx=15,
            pady=15,
            sticky="nsew"
        )

        capsule["card"] = capsule_card

        capsule_card.bind(
            "<Button-1>",
            lambda e, c=capsule: open_capsule(c)
        )
        # CLOSED CAPSULE
        if capsule["status"] == "🔒 Closed":

            top_frame = ctk.CTkFrame(
                capsule_card,
                fg_color="transparent"
            )
            top_frame.pack(fill="x", padx=10, pady=(10, 0))

            favorite_button = ctk.CTkButton(
                top_frame,
                text="⭐" if capsule["favorite"] else "☆",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="#333333"
            )
            favorite_button.configure(
                command=lambda c=capsule, b=favorite_button:
                toggle_favorite(c, b)
            )
            favorite_button.pack(side="left")

            delete_button = ctk.CTkButton(
                top_frame,
                text="🗑",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="#333333",
                command=lambda c=capsule, card=capsule_card:
                delete_capsule(card, c)
            )
            delete_button.pack(side="right")

            center_frame = ctk.CTkFrame(
                capsule_card,
                fg_color="transparent"
            )
            center_frame.pack(expand=True)

            ctk.CTkLabel(
                center_frame,
                text=capsule["title"],
                font=("Avenir", 16, "bold")
            ).pack()

            ctk.CTkLabel(
                center_frame,
                text=f"🔐 Opens on\n{capsule['open_date'].strftime('%d %b %Y')}",
                font=("Avenir", 11),
                justify="center"
            ).pack()

            bottom_frame = ctk.CTkFrame(
                capsule_card,
                fg_color="transparent"
            )
            bottom_frame.pack(
                side="bottom",
                fill="x",
                padx=10,
                pady=5
            )

            ctk.CTkLabel(
                bottom_frame,
                text=f"⏳ {capsule['days_left']} days",
                font=("Avenir", 10)
            ).pack(side="left")

            ctk.CTkLabel(
                bottom_frame,
                text=capsule["status"],
                font=("Avenir", 10)
            ).pack(side="right")

        # OPENED CAPSULE
        else:

            top_frame = ctk.CTkFrame(
                capsule_card,
                fg_color="transparent"
            )
            top_frame.pack(fill="x", padx=10, pady=(10, 0))

            ctk.CTkLabel(
                top_frame,
                text=capsule["title"],
                font=("Avenir", 16, "bold")
            ).pack(side="left")

            favorite_button = ctk.CTkButton(
                top_frame,
                text="⭐" if capsule["favorite"] else "☆",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="#333333"
            )
            favorite_button.configure(
                command=lambda c=capsule, b=favorite_button:
                toggle_favorite(c, b)
            )
            favorite_button.pack(side="right")

            delete_button = ctk.CTkButton(
                top_frame,
                text="🗑",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="#333333",
                command=lambda c=capsule, card=capsule_card:
                delete_capsule(card, c)
            )
            delete_button.pack(side="right")

            bottom_frame = ctk.CTkFrame(
                capsule_card,
                fg_color="transparent"
            )
            bottom_frame.pack(
                side="bottom",
                fill="x",
                padx=10,
                pady=5
            )

            ctk.CTkLabel(
                bottom_frame,
                text=f"⏳ {capsule['days_left']} days",
                font=("Avenir", 10)
            ).pack(side="left")

            ctk.CTkLabel(
                bottom_frame,
                text=capsule["status"],
                font=("Avenir", 10)
            ).pack(side="right")

            line = ctk.CTkFrame(
                capsule_card,
                height=1,
                fg_color="white"
            )
            line.pack(fill="x", padx=10, pady=(5, 5))

            preview = capsule["message"].strip()[:30]

            ctk.CTkLabel(
                capsule_card,
                text=preview,
                font=("Avenir", 12)
            ).pack(anchor="w", padx=10)
# Capsule card
def create_capsule():

    title = title_entry.get()

    day = day_menu.get()
    month = month_menu.get()
    year = year_menu.get()

    try:
        open_date = datetime(
            int(year),
            months[month],
            int(day)
    )

    except ValueError:
        print("INVALID DATE")
        return
    
    today = datetime.now()

    time_left = open_date - today
    days_left = max(time_left.days, 0)

    if open_date > today:
        status = "🔒 Closed"
    else:
        status = "🔓 Opened"
    capsule = {
        "title": title,
        "message": message_box.get("1.0", "end").strip(),
        "open_date": open_date,
        "days_left": days_left,
        "status": status,
        "favorite": False,
        "color": selected_color,
        "photos": selected_photos,
    }
    capsules.append(capsule)
    save_capsules()
    
    capsule_card = ctk.CTkFrame(
        capsules_container,
        width=270,
        height=150,
        corner_radius=15,
        fg_color=selected_color
    )
    row = (len(capsules) - 1) // 3
    column = (len(capsules) - 1) % 3

    capsule_card.grid(
        row=row,
        column=column,
        padx=15,
        pady=15
)
    capsule_card.pack_propagate(False)
    capsule_card.grid_propagate(False)

    capsule["card"] = capsule_card

    capsule_card.bind(
        "<Button-1>",
        lambda e, c=capsule: open_capsule(c)
    )

    top_frame = ctk.CTkFrame(
        capsule_card,
        fg_color="transparent"
    )
    top_frame.pack(
        fill="x",
        padx=10,
        pady=(10, 0)
    )

    if status == "🔒 Closed":
        closed_frame = ctk.CTkFrame(
            capsule_card,
            fg_color="transparent"
        )
        closed_frame.pack(expand=True)

        ctk.CTkLabel(
            closed_frame,
            text=title,
            font=("Avenir", 16, "bold")
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            closed_frame,
            text=f"🔐 Opens on\n{open_date.strftime('%d %b %Y')}",
            font=("Avenir", 11),
            justify="center"
        ).pack()

    else:
        ctk.CTkLabel(
            top_frame,
            text=title,
            font=("Avenir", 16, "bold")
        ).pack(side="left")

    delete_button = ctk.CTkButton(
    top_frame,
    text="🗑",
    width=25,
    height=25,
    fg_color="transparent",
    hover_color="#333333",
    command=lambda: delete_capsule(
        capsule_card,
        capsule
))
    delete_button.pack(side="right")

    favorite_button = ctk.CTkButton(
        top_frame,
        text="☆",
        width=25,   
        height = 25,
        fg_color="transparent",
        hover_color= "#333333",
    )
    favorite_button.configure(
    command=lambda:
        toggle_favorite(capsule, favorite_button)
        )
    
    favorite_button.pack(side="right")

    if status == "🔒 Closed":
        favorite_button.pack(side="left")
        delete_button.pack(side="right")

    else:
        delete_button.pack(side="right")
        favorite_button.pack(side="right")

    if status == "🔓 Opened":
        line = ctk.CTkFrame(capsule_card,height=1,fg_color="white")

        line.pack(fill="x", padx=10, pady=(5, 5))

    message_preview = message_box.get("1.0", "end").strip()

    if status == "🔓 Opened":
        message_preview = message_box.get("1.0", "end").strip()

        if len(message_preview) > 30:
            message_preview = message_preview[:30] + "..."

        ctk.CTkLabel(
                    capsule_card,
                    text=message_preview,
                    font=("Avenir", 12),
                    justify="left"
                ).pack(anchor="w", padx=10, pady=(5, 0))

    
    bottom_frame = ctk.CTkFrame(
    capsule_card,
    fg_color="transparent"
)

    bottom_frame.pack(
        side="bottom",
        fill="x",
        padx=10,
        pady=5
    )

    ctk.CTkLabel(
    bottom_frame,
    text=f"⏳ {days_left} days",
    font=("Avenir", 10)
    ).pack(side="left")

    ctk.CTkLabel(
    bottom_frame,
    text=status,
    font=("Avenir", 10)
    ).pack(side="right")

    popup_frame.after(100, popup_frame.destroy)

#create capsule popup
def open_create_capsule():

    global popup_frame
    global selected_photos
    selected_photos = []

    popup_frame = ctk.CTkFrame(
        root,
        width=700,
        height=750,
        corner_radius=20,
        fg_color="#222222",
        border_color="black"
    )

    popup_frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )
    popup_frame.pack_propagate(False)

    scroll_frame = ctk.CTkScrollableFrame(
    popup_frame,
    width=650,
    height=700
)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Popup Title
    popup_title = ctk.CTkLabel(
        scroll_frame,
        text="Create Capsule",
        font=("Avenir", 24, "bold")
    )
    popup_title.pack(pady=(20, 10))

    # Title Label
    title_label = ctk.CTkLabel(
        scroll_frame,
        text="✎TITLE",
        font=("Avenir", 16, "bold"),
        text_color="white"
    )
    title_label.pack(anchor="w", padx=30)

    # Title Entry
    global title_entry

    title_entry = ctk.CTkEntry(
        scroll_frame,
        width=500,
        height=40
)
    title_entry.pack(pady=10)

    # Message Label
    message_label = ctk.CTkLabel(
        scroll_frame,
        text="📝MESSAGE",
        font=("Avenir", 16, "bold"),
        text_color="white"
    )
    message_label.pack(anchor="w", padx=30, pady=(10, 0))

    # Message Box
    global message_box

    message_box = ctk.CTkTextbox(
        scroll_frame,
        width=500,
        height=200,
        fg_color="#1A1A1A",
        border_color="#444444",
        corner_radius=10
)
    message_box.pack(pady=10)

    # Color label
    color_label = ctk.CTkLabel(
    scroll_frame,
    text="🎨 CAPSULE COLOR",
    font=("Avenir", 16,"bold"),
    text_color="white"
)
    color_label.pack(anchor="w", padx=30, pady=(15, 5))

    # Color Frame
    color_frame = ctk.CTkFrame(
    scroll_frame,
    fg_color="transparent"
)
    color_frame.pack(anchor="w", padx=30, pady=5)

    # Color Buttons
    pink_btn = ctk.CTkButton(
    color_frame,
    text="Pink",
    width=80,
    fg_color="#6A1B3F",
    command=lambda: select_color("#6A1B3F")
)
    pink_btn.pack(side="left", padx=5)

    purple_btn = ctk.CTkButton(
        color_frame,
        text="Purple",
        width=80,
        fg_color="#4C1D95",
        command=lambda: select_color("#4C1D95")
    )
    purple_btn.pack(side="left", padx=5)

    green_btn = ctk.CTkButton(
        color_frame,
        text="Green",
        width=80,
        fg_color="#065F46",
        command=lambda: select_color("#065F46")
    )
    green_btn.pack(side="left", padx=5)

    burgundy_btn = ctk.CTkButton(
        color_frame,
        text="Burgundy",
        width=80,
        fg_color="#7F1D1D",
        command=lambda: select_color("#7F1D1D")
    )
    burgundy_btn.pack(side="left", padx=5)

    brown_btn = ctk.CTkButton(
        color_frame,
        text="Brown",
        width=80,
        fg_color="#4B3621",
        command=lambda: select_color("#4B3621")
    )
    brown_btn.pack(side="left", padx=5)

    color_frame.pack(pady=(10, 25))

    # Date Section
    date_label = ctk.CTkLabel(
    scroll_frame,
    text="📅 Open Date",
    font=("Avenir", 16, "bold")
)
    date_label.pack(anchor="w", padx=30, pady=(10, 5))

    date_frame = ctk.CTkFrame(
    scroll_frame,
    fg_color="transparent"
)
    date_frame.pack(anchor="w", padx=30)

    global day_menu

    day_menu = ctk.CTkOptionMenu(
    date_frame,
    values=[str(i) for i in range(1, 32)]
)
    day_menu.pack(side="left", padx=5)

    global month_menu

    month_menu = ctk.CTkOptionMenu(
        date_frame,
        values=[
            "Jan","Feb","Mar","Apr",
            "May","Jun","Jul","Aug",
            "Sep","Oct","Nov","Dec"
        ]
    )
    month_menu.pack(side="left", padx=5)

    global year_menu

    year_menu = ctk.CTkOptionMenu(
        date_frame,
        values=[
            "2026","2027","2028",
            "2029","2030"
        ]
    )
    year_menu.pack(side="left", padx=5)


    # Photo Preview Area
    global photo_frame

    photo_header = ctk.CTkFrame(
    scroll_frame,
    fg_color="transparent"
)
    photo_header.pack(fill="x", padx=30, pady=(10,5))

    # Photo title
    photo_title = ctk.CTkLabel(
    photo_header,
    text="📷 PHOTOS",
    font=("Avenir", 16, "bold")
)
    photo_title.pack(side="left")

    # Photo Upload Button
    photo_button = ctk.CTkButton(
        photo_header,
        text="Add+",
        width=90,
        command=upload_photo
)
    photo_button.pack(side="right")

    #Photo frame
    photo_frame = ctk.CTkFrame(
        scroll_frame,
        width=500,
        height=190,
        corner_radius=10,
        fg_color="#1A1A1A",
        border_width=1,
        border_color="#444444"
    )
    photo_frame.pack(padx=30, pady=(0,15))   
    photo_frame.pack_propagate(False)

    # Bottom Frame
    bottom_frame = ctk.CTkFrame(
    scroll_frame,
    fg_color="transparent"
)
    bottom_frame.pack(fill="x", padx=30, pady=20)

    # Delete button
    delete_button = ctk.CTkButton(
    bottom_frame,
    text="🗑 Delete",
    width=150,
    fg_color="#B22222",
    command=popup_frame.destroy
)
    delete_button.pack(side="left")

    # Save Button
    global create_capsule_button

    create_capsule_button = ctk.CTkButton(
    bottom_frame,
    text="🚀 Create Capsule",
    width=180,
    fg_color=selected_color,
    command=create_capsule
)
    create_capsule_button.pack(side="right")
def open_capsule(capsule):
    update_capsule_status(capsule)
    save_capsules()
    
    popup = ctk.CTkToplevel(root)
    capsule_color = capsule.get("color", "#6C3EB8")
    inner_colors = {
        "#6C3EB8": "#4B2B80",   # purple
        "#0F7A4F": "#0B5A3A",   # green
        "#8B1E1E": "#641515",   # burgundy
        "#6B4423": "#4E3119",   # brown
        "#C2185B": "#8A1140"    # pink
    }
    inner_color = inner_colors.get(capsule_color, "#2B2B2B")
    popup.configure(fg_color=capsule_color)
    popup.transient(root)
    popup.grab_set()

    if capsule["status"] == "🔒 Closed":
        popup.title(capsule["title"])
        popup.geometry("300x150")

        ctk.CTkLabel(
            popup,  
            text=f"This Capsule is Closed!!\n\nOpens on: {capsule['open_date']}",
            font=("Avenir", 18),
            justify="center"
        ).pack(expand=True)

    else:
        popup.title(capsule["title"])
        capsule_color = capsule.get("color", "#6C3EB8")
        popup.configure(fg_color=capsule_color)
        popup.geometry("700x550")

        ctk.CTkLabel(
            popup,
            text=capsule["title"],
            font=("Avenir", 28, "bold"),
            text_color="white"
        ).pack(pady=(25, 10))

        line = ctk.CTkFrame(
            popup,
            height=2,
            fg_color="white"
        )
        line.pack(fill="x", padx=30, pady=(0, 20))

        message_frame = ctk.CTkFrame(
            popup,
            fg_color=inner_color,
            corner_radius=15
        )
        message_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        ctk.CTkLabel(
            message_frame,
            text=capsule["message"],
            font=("Avenir", 16),
            text_color="white",
            wraplength=550,
            justify="left"
        ).pack(
            padx=20,
            pady=20,
            anchor="nw"
        )
        photo_display_frame = ctk.CTkFrame(
            popup,
            fg_color="transparent"
        )
        photo_display_frame.pack(pady=15)
        for photo_path in capsule.get("photos", []):

            image = Image.open(photo_path)

            photo = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(120, 120)
            )

            label = ctk.CTkLabel(
                photo_display_frame,
                image=photo,
                text=""
            )
            label.image = photo
            label.pack(side="left", padx=10)

    if capsule["status"] == "🔓 Opened":
        ctk.CTkLabel(
            popup,
            text=f"Opened on: {capsule['open_date']}",
            font=("Avenir", 12),
            text_color="white"
        ).pack(pady=(5, 15))

    ctk.CTkButton(
                popup,
                text="Close",
                width=150,
                height=40,
                corner_radius=20,
                fg_color=inner_color,
                hover_color=capsule_color,
                command=popup.destroy
        ).pack(pady=(0, 25))   
def show_dashboard(username):

    # Remove login widgets
    title_label.destroy()
    name_label.destroy()
    name_entry.destroy()

    password_label.destroy()
    password_entry.destroy()

    continue_btn.destroy()

    # ======================
    # TOP BAR
    # ======================

    top_frame = ctk.CTkFrame(
        root,
        height=120,
        corner_radius=20,
        fg_color="#1F6AA5"
    )
    top_frame.pack(fill="x", padx=15, pady=15)

    top_frame.pack_propagate(False) #to avoid resizing based on content

    app_title = ctk.CTkLabel(
        top_frame,
        text="TIME CAPSULE 🚀",
        font=("Avenir", 28, "bold"),
        text_color="white"
    )
    app_title.pack(side="left", padx=25, pady=35)

    welcome_label = ctk.CTkLabel(
        top_frame,
        text=f"Welcome!!, {username},save your memories here!",
        font=("Avenir", 18),
        text_color="white"
    )
    welcome_label.pack(side="right", padx=25)

    # ======================
    # CONTENT AREA
    # ======================

    content_frame = ctk.CTkFrame(
        root,
        fg_color="transparent"
    )
    content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    # ======================
    # SIDEBAR
    # ======================

    left_frame = ctk.CTkFrame(
        content_frame,
        width=250,
        corner_radius=20,
        fg_color="#1A1A1A"
    )
    left_frame.pack(side="left", fill="y", padx=(0, 15))

    left_frame.pack_propagate(False)

    all_button = ctk.CTkButton(
    left_frame,
    text="📂 All Capsules",
    font=("Avenir", 16, "bold"),
    fg_color="transparent",
    hover_color="#333333",
    command=lambda: filter_capsules("all")
)
    all_button.pack(pady=(40, 20))

    closed_button = ctk.CTkButton(
    left_frame,
    text="🔒 Closed",
    font=("Avenir", 16, "bold"),   
    fg_color="transparent",
    hover_color="#333333",
    command=lambda: filter_capsules("closed")
)
    closed_button.pack(pady=15)

    opened_button = ctk.CTkButton(
    left_frame,
    text="🔓Opened",
    font=("Avenir", 16, "bold"),    
    fg_color="transparent",
    hover_color="#333333",
    command=lambda: filter_capsules("opened")
)
    opened_button.pack(pady=15)

    favorite_button = ctk.CTkButton(
    left_frame,
    text="⭐ Favorites",
    font=("Avenir", 16, "bold"),
    fg_color="transparent",
    hover_color="#333333",
    command=lambda: filter_capsules("favorites")
)
    favorite_button.pack(pady=15)

    # ======================
    # MAIN AREA
    # ======================
    global main_frame
    main_frame = ctk.CTkFrame(
        content_frame,
        corner_radius=20,
        fg_color="#111111"
    )
    main_frame.pack( side="left",fill="both",expand=True)

    global capsules_container

    capsules_container = ctk.CTkFrame(
    main_frame,
    fg_color="transparent"
)
    capsules_container.pack(fill="both", expand=True, padx=20, pady=(10,0))

    for i in range(3):
        capsules_container.grid_columnconfigure(
            i,
            weight=0,
            minsize=300
        )

    create_button = ctk.CTkButton(
        main_frame,
        text="+ Create Capsule",
        width=220,
        height=55,
        corner_radius=15,
        font=("Avenir", 18, "bold"),
        command=open_create_capsule
    )
    create_button.pack(pady=20)
    load_capsules()
    render_capsules()

def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)
def login_user(username, password):

    users = load_users()

    for user in users:

        if (
            user["username"] == username
            and
            user["password"] == password
        ):
            return True

    return False

def load_users():

    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)

    except:
        return []
def continue_to_dashboard():

    global current_user

    username = name_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        return

    users = load_users()

    # Check if user already exists
    for user in users:

        if user["username"] == username:

            if user["password"] == password:
                current_user = username
                show_dashboard(username)
                return

            popup = ctk.CTkToplevel(root)
            popup.title("Error")
            popup.geometry("350x180")

            ctk.CTkLabel(
                popup,
                text="❌ Wrong Password\nThis username already exists.",
                font=("Avenir", 16),
                justify="center"
            ).pack(expand=True)

            ctk.CTkButton(
                popup,
                text="OK",
                command=popup.destroy
            ).pack(pady=10)

            return

    # New user → create account automatically
    users.append({
        "username": username,
        "password": password
    })

    save_users(users)

    current_user = username
    show_dashboard(username)

root = ctk.CTk() #creates main window
root.title("Time Capsule")
root.geometry("700x500")
root.configure(fg_color="black")

# App Title
title_label = ctk.CTkLabel(
    root,
    text="TIME CAPSULE🚀",
    font=("Times New Roman", 40, "bold"),
    fg_color="black",
    text_color="#1F6AA5"

)
title_label.pack(pady=50)

# Name Label
name_label = ctk.CTkLabel(
    root,
    text="Enter Your Name",
    font=("Avenir", 15, "bold"),
    text_color="#1F6AA5"
)
name_label.pack()

# Name Entry
name_entry = ctk.CTkEntry(
    root,
    text_color="#1F6AA5",
    font=("Avenir", 16),
    width=250,
    height= 40,
    fg_color="black",
    corner_radius=10

)
name_entry.pack(pady=10)

password_label = ctk.CTkLabel(
    root,
    text="Enter Password",
    font=("Avenir", 15, "bold"),
    text_color="#1F6AA5",

)
password_label.pack()

password_entry = ctk.CTkEntry(
    root,
    width=250,
    height=40,
    show="*",
    fg_color="black",
    text_color="#1F6AA5",
    font=("Avenir", 16),
    corner_radius=10
)
password_entry.pack(pady=10)

# Continue Button
continue_btn = ctk.CTkButton(
    root,
    text="Continue",
    text_color="white",
    font=("Avenir", 16),
    width=150,
    height = 40,
    corner_radius=10,
    command=continue_to_dashboard
)
continue_btn.pack(pady=20)
root.mainloop()