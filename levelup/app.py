"""LevelUp desktop entry point: python -m levelup."""
import os
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from .core import FocusTimer, Store


def default_database():
    base = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share'))
    return base / 'LevelUp' / 'levelup.sqlite3'


class Application:
    def __init__(self, root, store):
        self.root, self.store = root, store
        self.timer = FocusTimer()
        root.title('LevelUp — Focus & Tasks')
        root.geometry('760x540')
        root.minsize(620, 420)
        panel = ttk.Frame(root, padding=20)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='LevelUp', font=('Segoe UI', 24, 'bold')).pack(anchor='w')
        ttk.Label(panel, text='Choose a task. Build your focus.').pack(anchor='w', pady=(0, 16))
        entry_row = ttk.Frame(panel)
        entry_row.pack(fill='x')
        self.title = ttk.Entry(entry_row)
        self.title.pack(side='left', fill='x', expand=True)
        self.title.bind('<Return>', lambda event: self.safe(self.add))
        ttk.Button(entry_row, text='Add task', command=lambda: self.safe(self.add)).pack(side='left', padx=(8, 0))
        self.tree = ttk.Treeview(panel, columns=('status',), selectmode='browse')
        self.tree.heading('#0', text='Task')
        self.tree.heading('status', text='Status')
        self.tree.column('status', width=100, stretch=False)
        self.tree.pack(fill='both', expand=True, pady=12)
        actions = ttk.Frame(panel)
        actions.pack(fill='x')
        for label, action in [('Rename', self.rename), ('Complete / Reopen', self.toggle), ('Delete', self.delete)]:
            ttk.Button(actions, text=label, command=lambda a=action: self.safe(a)).pack(side='left', padx=(0, 8))
        self.focus_label = ttk.Label(panel, text='No active session')
        self.focus_label.pack(anchor='w', pady=(18, 0))
        self.clock_label = ttk.Label(panel, text='00:00:00', font=('Segoe UI', 28))
        self.clock_label.pack(anchor='w')
        controls = ttk.Frame(panel)
        controls.pack(fill='x')
        for label, action in [('Start', self.start), ('Pause / Resume', self.pause), ('Stop & Save', self.stop)]:
            ttk.Button(controls, text=label, command=lambda a=action: self.safe(a)).pack(side='left', padx=(0, 8))
        self.status = ttk.Label(panel, text='Ready')
        self.status.pack(anchor='w', pady=(10, 0))
        root.protocol('WM_DELETE_WINDOW', lambda: self.safe(self.close))
        self.refresh()
        self.tick()

    def safe(self, action):
        try:
            action()
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror('LevelUp', str(error), parent=self.root)

    def selected(self):
        selected = self.tree.selection()
        if not selected:
            raise ValueError('Select a task first.')
        return int(selected[0])

    def refresh(self):
        selected = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        for task in self.store.tasks():
            self.tree.insert('', 'end', iid=str(task['id']), text=task['title'],
                             values=('Done' if task['completed'] else 'Open',))
        if selected and self.tree.exists(selected[0]):
            self.tree.selection_set(selected[0])

    def add(self):
        self.store.add_task(self.title.get())
        self.title.delete(0, 'end')
        self.refresh()

    def rename(self):
        task_id = self.selected()
        title = simpledialog.askstring('Rename task', 'Task title:',
                                       initialvalue=self.tree.item(str(task_id), 'text'), parent=self.root)
        if title is not None:
            self.store.rename_task(task_id, title)
            self.refresh()

    def toggle(self):
        task_id = self.selected()
        self.guard_active(task_id)
        completed = self.tree.item(str(task_id), 'values')[0] == 'Done'
        self.store.set_completed(task_id, not completed)
        self.refresh()

    def guard_active(self, task_id):
        if self.timer.active and self.timer.task_id == task_id:
            raise ValueError('Stop and save this task’s session first.')

    def delete(self):
        task_id = self.selected()
        self.guard_active(task_id)
        if messagebox.askyesno('Delete task', 'Delete this task? Saved focus sessions will be kept.', parent=self.root):
            self.store.delete_task(task_id)
            self.refresh()

    def start(self):
        task_id = self.selected()
        if self.tree.item(str(task_id), 'values')[0] == 'Done':
            raise ValueError('Reopen this task before starting a focus session.')
        self.timer.start(task_id)
        self.status.config(text='Focusing')

    def pause(self):
        if self.timer.running:
            self.timer.pause()
            self.status.config(text='Paused')
        elif self.timer.active:
            self.timer.resume()
            self.status.config(text='Focusing')

    def stop(self):
        if self.timer.active:
            self.timer.stop(self.store)
            self.status.config(text='Session saved')

    def tick(self):
        seconds = int(self.timer.elapsed)
        self.clock_label.config(text=f'{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}')
        text = self.tree.item(str(self.timer.task_id), 'text') if self.timer.active else 'No active session'
        self.focus_label.config(text=text)
        self.root.after(200, self.tick)

    def close(self):
        if self.timer.active:
            if not messagebox.askyesno('Close LevelUp', 'Save the current focus session and exit?', parent=self.root):
                return
            self.stop()
        self.store.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        store = Store(default_database())
        Application(root, store)
    except (OSError, sqlite3.Error) as error:
        messagebox.showerror('LevelUp startup failed', str(error), parent=root)
        root.destroy()
        return
    root.mainloop()
