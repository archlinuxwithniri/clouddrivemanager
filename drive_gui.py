#!/usr/bin/env python3
import subprocess
import json
import tkinter as tk
import threading

def to_gib(v):
    return round(v / (1024 ** 3), 2)

def get_drive_info(remote):
    try:
        res = subprocess.run(
            ["rclone", "about", remote, "--json"],
            capture_output=True,
            text=True
        )
        if res.returncode != 0 or not res.stdout:
            return None

        data = json.loads(res.stdout)
        total = to_gib(data.get("total", 0))
        used = to_gib(data.get("used", 0) + data.get("other", 0))
        free = to_gib(data.get("free", 0))
        return total, used, free
    except Exception:
        return None

def list_remotes():
    try:
        res = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        if res.returncode != 0:
            return []
        return res.stdout.split()
    except Exception:
        return []

# ---------------- Main Window ----------------
root = tk.Tk()
root.title("Google Drive Lobby")
root.geometry("1100x650")
root.configure(bg="#1e1e1e")

tk.Label(root, text="Google Drive Lobby",
         font=("Segoe UI", 20, "bold"),
         fg="white", bg="#1e1e1e").pack(pady=(10, 5))

# ---------------- Canvas + Scrollbar ----------------
canvas_frame = tk.Frame(root, bg="#1e1e1e")
canvas_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(canvas_frame, bg="#1e1e1e", highlightthickness=0)
vscroll = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vscroll.set)

vscroll.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# ---------------- Data Tracking ----------------
canvas_items = []
drive_infos = {}
drive_order = []

BLOCK_W = 260
BLOCK_H = 200
X_PAD = 20
Y_PAD = 20
SUMMARY_HEIGHT = 220
SUMMARY_PER_DRIVE = 15
SUMMARY_MARGIN_RATIO = 0.1

summary_widget = None
summary_bar = None

resize_after_id = None
all_remotes = []

# ---------------- Drive Block ----------------
def create_drive_block(index, name, info):
    box = tk.Frame(canvas, bg="#252525", highlightbackground="#666", highlightthickness=1,
                   width=BLOCK_W, height=BLOCK_H)
    box.pack_propagate(False)

    tk.Label(box, text=f"{index}) {name.replace(':','')}", fg="white",
             bg="#252525", font=("Segoe UI", 14, "bold"), anchor="w").pack(anchor="w", padx=12, pady=(10,4))

    if info is None:
        tk.Label(box, text="Cannot access", fg="#ff4444", bg="#252525",
                 font=("Segoe UI",12)).pack(anchor="w", padx=12)
        return box

    total, used, free = info
    tk.Label(box, text=f"Total: {total} GiB", fg="white", bg="#252525", font=("Segoe UI",12)).pack(anchor="w", padx=12)
    tk.Label(box, text=f"Used: {used} GiB", fg="white", bg="#252525", font=("Segoe UI",12)).pack(anchor="w", padx=12)
    tk.Label(box, text=f"Free: {free} GiB", fg="white", bg="#252525", font=("Segoe UI",12)).pack(anchor="w", padx=12)

    # Usage bar
    bar = tk.Canvas(box, width=BLOCK_W-20, height=18, bg="#1e1e1e", highlightthickness=0)
    bar.pack(pady=(8,0), padx=10, anchor="w")
    if total > 0:
        used_w = int((used/total)*(BLOCK_W-20))
        bar.create_rectangle(0,0,used_w,18,fill="#4A90E2",width=0)
        bar.create_rectangle(used_w,0,BLOCK_W-20,18,fill="#555555",width=0)
    else:
        bar.create_rectangle(0,0,BLOCK_W-20,18,fill="#444444",width=0)
    return box

# ---------------- Summary ----------------
def update_summary():
    global summary_widget, summary_bar
    total_drives = len(all_remotes)
    total_storage = total_drives * SUMMARY_PER_DRIVE

    total_used = 0
    total_free = 0
    for n in all_remotes:
        info = drive_infos.get(n)
        if info:
            t,u,f = info
            total_used += u
            total_free += f

    if summary_widget:
        summary_widget.destroy()

    cw = canvas.winfo_width()
    margin = int(cw*SUMMARY_MARGIN_RATIO)
    width = max(cw - 2*margin, 500)

    summary_widget = tk.Frame(canvas, bg="#252525",
                              highlightbackground="#999", highlightthickness=1,
                              width=width, height=SUMMARY_HEIGHT)
    summary_widget.pack_propagate(False)

    # Put summary in canvas
    summary_id = canvas.create_window(margin, Y_PAD, anchor="nw", window=summary_widget)

    tk.Label(summary_widget, text="Summary", fg="white", bg="#252525",
             font=("Segoe UI",16,"bold")).pack(anchor="w", padx=16, pady=(12,6))

    lblfont = ("Segoe UI",13)
    tk.Label(summary_widget, text=f"Total drives: {total_drives}", fg="white", bg="#252525", font=lblfont).pack(anchor="w", padx=16)
    tk.Label(summary_widget, text=f"Total storage: {total_storage} GiB", fg="white", bg="#252525", font=lblfont).pack(anchor="w", padx=16)
    tk.Label(summary_widget, text=f"Total used: {round(total_used,2)} GiB", fg="white", bg="#252525", font=lblfont).pack(anchor="w", padx=16)
    tk.Label(summary_widget, text=f"Total free: {round(total_free,2)} GiB", fg="white", bg="#252525", font=lblfont).pack(anchor="w", padx=16)

    # Dynamic usage bar ~80% width of summary
    bar_width = int(width*0.9)
    bar_height = 18
    summary_bar = tk.Canvas(summary_widget, width=bar_width, height=bar_height,
                            bg="#1e1e1e", highlightthickness=0)
    summary_bar.pack(pady=(10,4), padx=16, anchor="w")
    if total_storage>0:
        used_w = int((total_used/total_storage)*bar_width)
        summary_bar.create_rectangle(0,0,used_w,bar_height,fill="#4A90E2",width=0)
        summary_bar.create_rectangle(used_w,0,bar_width,bar_height,fill="#555555",width=0)
    else:
        summary_bar.create_rectangle(0,0,bar_width,bar_height,fill="#444444",width=0)

# ---------------- Layout ----------------
def layout_blocks(event=None):
    if not canvas_items:
        canvas.configure(scrollregion=(0,0,0,0))
        return

    cw = canvas.winfo_width()
    block_plus_pad = BLOCK_W + X_PAD
    cols = max(1, cw // block_plus_pad)
    total_width = cols*BLOCK_W + (cols-1)*X_PAD
    start_x = (cw - total_width)//2
    y = Y_PAD + SUMMARY_HEIGHT + Y_PAD

    for i,item in enumerate(canvas_items):
        col = i % cols
        row = i // cols
        x = start_x + col*(BLOCK_W+X_PAD)
        yy = y + row*(BLOCK_H+Y_PAD)
        canvas.coords(item['id'], x, yy)

    rows = (len(canvas_items)+cols-1)//cols
    total_height = y + rows*(BLOCK_H+Y_PAD)
    canvas.configure(scrollregion=(0,0,cw,total_height))

def layout(event=None):
    global resize_after_id
    if resize_after_id:
        root.after_cancel(resize_after_id)
    resize_after_id = root.after(80,_apply_layout)

def _apply_layout():
    update_summary()
    layout_blocks()

# ---------------- Mouse wheel ----------------
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def _on_mousewheel_linux(event):
    if event.num==4: canvas.yview_scroll(-3,"units")
    elif event.num==5: canvas.yview_scroll(3,"units")

canvas.bind_all("<MouseWheel>",_on_mousewheel)
canvas.bind_all("<Button-4>",_on_mousewheel_linux)
canvas.bind_all("<Button-5>",_on_mousewheel_linux)

# ---------------- Blocks ----------------
def push_block(name, info):
    drive_order.append(name)
    drive_infos[name]=info
    w = create_drive_block(len(canvas_items)+1, name, info)
    wid = canvas.create_window(0,0,anchor="nw",window=w)
    canvas_items.append({"id":wid})
    _apply_layout()

def worker(name):
    info = get_drive_info(name)
    root.after(0, lambda: push_block(name,info))

def load_blocks():
    global all_remotes
    for item in canvas_items:
        canvas.delete(item['id'])
    canvas_items.clear()
    drive_infos.clear()
    drive_order.clear()

    all_remotes = list_remotes()
    if not all_remotes:
        return

    for r in all_remotes:
        threading.Thread(target=worker,args=(r,),daemon=True).start()

# ---------------- Buttons ----------------
bottom = tk.Frame(root, bg="#1e1e1e")
bottom.pack(side="bottom", pady=10)
btncfg = dict(font=("Segoe UI",12), bg="#333", fg="white",
              activebackground="#444", relief="solid", bd=1, width=12)

tk.Button(bottom, text="Refresh", command=load_blocks, **btncfg).grid(row=0,column=0,padx=20)
tk.Button(bottom, text="Exit", command=root.destroy, **btncfg).grid(row=0,column=1,padx=20)

canvas.bind("<Configure>", layout)

# ---------------- Start ----------------
load_blocks()
root.mainloop()
