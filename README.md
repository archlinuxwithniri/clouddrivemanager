# **Rclone Storage Dashboard**

---

## **What This Program Does**
This Python script launches a graphical dashboard that automatically detects all **rclone-configured cloud drives** and displays their storage usage including **total, used, and free space**, along with a **visual usage bar** for each drive. It allows quick monitoring of multiple cloud drives in a clean interface.

---

## **In-Short Summary**
> A GUI tool to view storage usage of every rclone remote (Google Drive, OneDrive, Mega, etc.) in one window.

---

## **Requirements**
To run `drive_gui.py`, you must have:

| Requirement | Details |
|------------|---------|
| Python 3 | Version 3.7 or newer |
| Tkinter | GUI library for Python |
| rclone | Installed on the system |
| Configured rclone remotes | At least one remote added via `rclone config` |
| OS Support | Windows / Linux / macOS |

---

## **Install Dependencies**


---

### Linux
```bash
# Install Python & Tkinter
sudo apt install python3 python3-tk -y

# Install rclone
curl https://rclone.org/install.sh | sudo bash

# (Arch Linux alternative)
sudo pacman -S rclone python tk
```

---

### macOS
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python-tk

# Install rclone
brew install rclone
```

---

### Windows
```bash
# Install Python (includes Tkinter)
https://www.python.org/downloads/

# Install rclone
https://rclone.org/downloads/

# Verify rclone
rclone version
```

##  **Running the Program**
```bash
python3 drive_gui.py
```

---

##  **Screenshot**
I blured some of my personal data , but this is what it looks like 
![Screenshot](/pictures/screenshot.png)  



---

##  **Notes**
- Click **Refresh** to update drive information without restarting the app.
- Works with all rclone-supported cloud providers (Google Drive, OneDrive, Dropbox, Mega, S3, etc.).
- Runs on Windows, Linux, and Mac as long as Tkinter and rclone are installed. (made in linux) , haven't tested on other os than linux ubuntu
- The summary block summarise and shows the total storage used and free
- The lobby.sh was made for debugging purpose , what it does is that its prints all rclone remote data in terminal
- if any error that says something about gdown , install gdown , i am not sure if rclone uses gdown , it seems not,
- i might make a release on this soon , for all os .
 

---

##  Enjoy the Dashboard
Monitor all your cloud drives in one place — clean, fast, and visual.
