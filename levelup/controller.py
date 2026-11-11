"""Application actions shared by Qt views; no widget dependencies."""
from .core import FocusTimer


class Controller:
    def __init__(self, store, timer=None):
        self.store = store
        self.timer = timer if timer is not None else FocusTimer()
        self.status = 'Ready'

    def task(self, task_id):
        for task in self.store.tasks():
            if task['id'] == task_id:
                return task
        raise ValueError('Select a task first.')

    def guard_active(self, task_id):
        if self.timer.active and self.timer.task_id == task_id:
            raise ValueError('Stop and save this task’s session first.')

    def add(self, title):
        return self.store.add_task(title)

    def rename(self, task_id, title):
        self.task(task_id)
        self.store.rename_task(task_id, title)

    def toggle(self, task_id):
        task = self.task(task_id)
        self.guard_active(task_id)
        self.store.set_completed(task_id, not task['completed'])

    def delete(self, task_id):
        self.task(task_id)
        self.guard_active(task_id)
        self.store.delete_task(task_id)

    def start(self, task_id):
        if self.task(task_id)['completed']:
            raise ValueError('Reopen this task before starting a focus session.')
        self.timer.start(task_id)
        self.status = 'Focusing'

    def pause(self):
        if self.timer.running:
            self.timer.pause()
            self.status = 'Paused'
        elif self.timer.active:
            self.timer.resume()
            self.status = 'Focusing'

    def stop(self):
        if self.timer.active:
            self.timer.stop(self.store)
            self.status = 'Session saved'
