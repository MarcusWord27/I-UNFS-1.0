"""Desktop app: import exports, protect accounts, and control bounded sessions."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from src.analyzer import nonmutual
from src.runner import UnfollowRunner

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("I-UNFS 1.0")
        self.geometry("760x550")
        self.followers = tk.StringVar()
        self.following = tk.StringVar()
        self.minimum = tk.IntVar(value=1)
        self.maximum = tk.IntVar(value=10)
        self.exclude_verified = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Load Instagram JSON exports to begin")
        self.runner = UnfollowRunner(self.report)
        self.queue = []
        for label, var in (("Followers JSON", self.followers), ("Following JSON", self.following)):
            row = ttk.Frame(self)
            row.pack(fill="x", padx=16, pady=6)
            ttk.Label(row, text=label, width=17).pack(side="left")
            ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
            ttk.Button(row, text="Browse", command=lambda v=var: v.set(filedialog.askopenfilename(filetypes=[("JSON", "*.json")]))).pack(side="left")
        row = ttk.Frame(self)
        row.pack(pady=8)
        for label, var in (("Min", self.minimum), ("Max", self.maximum)):
            ttk.Label(row, text=label).pack(side="left", padx=5)
            ttk.Spinbox(row, from_=1, to=10000, textvariable=var, width=7).pack(side="left")
        ttk.Checkbutton(self, text="Exclude verified accounts (mandatory safety check)", variable=self.exclude_verified, state="disabled").pack()
        ttk.Label(self, text="Protected usernames (comma separated)").pack()
        self.protected = ttk.Entry(self)
        self.protected.pack(fill="x", padx=16)
        buttons = ttk.Frame(self)
        buttons.pack(pady=10)
        for label, fn in (("Analyze", self.analyze), ("Start", self.start), ("Pause", self.runner.pause), ("Resume", self.runner.resume), ("Stop", self.runner.stop)):
            ttk.Button(buttons, text=label, command=fn).pack(side="left", padx=4)
        self.results = tk.Text(self, height=14, state="disabled")
        self.results.pack(fill="both", expand=True, padx=16, pady=8)
        ttk.Label(self, textvariable=self.status).pack(pady=5)
    def report(self, msg):
        self.after(0, lambda: self._report(msg))
    def _report(self, msg):
        self.status.set(msg)
        self.results.configure(state="normal")
        self.results.insert("end", msg + "\n")
        self.results.see("end")
        self.results.configure(state="disabled")
    def analyze(self):
        try:
            self.queue = nonmutual(self.followers.get(), self.following.get(), self.protected.get().split(","))
            self.report(f"Found {len(self.queue)} non-mutual accounts; verification status not yet known.")
        except Exception as exc:
            messagebox.showerror("Import error", str(exc))
    def start(self):
        try:
            low, high = self.minimum.get(), self.maximum.get()
            if low < 1 or high < low:
                raise ValueError("Require 1 <= minimum <= maximum")
            if not self.queue:
                raise ValueError("Analyze exports first")
            if not messagebox.askyesno("Confirm", f"Attempt at most {min(high, len(self.queue))} unfollows? Unofficial automation may restrict your account."):
                return
            threading.Thread(target=self.runner.run, args=(self.queue[:high], low), daemon=True).start()
        except Exception as exc:
            messagebox.showerror("Cannot start", str(exc))

if __name__ == "__main__":
    App().mainloop()
