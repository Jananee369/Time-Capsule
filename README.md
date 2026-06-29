# 🚀 Time Capsule Desktop Application

A beautiful **Time Capsule Desktop Application** built using **Python** and **CustomTkinter** that allows users to create digital capsules and open them in the future.

---

## ✨ Features

* 👤 Multi-user login system
* 📦 Create personal time capsules
* 🔒 Lock capsules until a future date
* 🔓 Automatically unlock capsules when the date arrives
* ⭐ Mark favorite capsules
* 🗑️ Delete unwanted capsules
* 📷 Upload and store photos inside capsules
* 🎨 Choose custom colors for each capsule
* 📂 Filter capsules:

  * All Capsules
  * Closed Capsules
  * Opened Capsules
  * Favorites
* 💾 Persistent storage using JSON files

---

## 🛠️ Technologies Used

* Python 3
* CustomTkinter
* Tkinter
* PIL (Pillow)
* JSON
* Datetime

---

## 📸 Application Preview

The application allows users to:

1. Create an account or log in.
2. Create a new capsule with:

   * Title
   * Message
   * Future opening date
   * Photos
   * Custom color
3. Save memories and open them when the selected date arrives.

---

## 📂 Project Structure

```text
Time Capsule/
│
├── main.py
├── users.json
├── capsules_<username>.json
├── assets/
└── README.md
```

---

## 💡 What I Learned

Building this project helped me learn:

* GUI development using CustomTkinter
* Working with JSON for data persistence
* Managing multiple users and authentication
* File handling in Python
* Building interactive pop-ups and custom interfaces
* Debugging and improving user experience

---

## 🚀 Future Improvements

* Password encryption
* Search functionality
* Capsule sharing between users
* Notifications when a capsule opens
* Export capsules as PDF

---

## ▶️ How to Run

1. Clone the repository:

```bash
git clone <repository-link>
```

2. Install dependencies:

```bash
pip install customtkinter pillow
```

3. Run the application:

```bash
python main.py
```

---

## 🌟 About The Project

Time Capsule is more than just a programming project—it's a place to preserve memories, messages, and moments for your future self.

*"The best thing about memories is making them and rediscovering them later."*
