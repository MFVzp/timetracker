import os
from time import sleep
import datetime
import tkinter as tk
from multiprocessing import Process, Queue

from mss import mss


class GUI:
    def __init__(self, queue):
        self.running = False
        self.master = tk.Tk()
        self.master.geometry('{}x{}'.format(200, 300))
        self.master.resizable(width=False, height=False)
        self.master.winfo_toplevel().title('Time tracker')
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.queue = queue
        self.time_variable = tk.StringVar()
        self.time_variable.set('Time: 00:00:00')
        self.time_label = tk.Label(
            self.master,
            font=("Times New Roman", 20),
            height=3,
            textvariable=self.time_variable
        )
        self.time_label.grid(row=0, column=0)

        buttons_width = 20
        buttons_height = 3

        self.start_button = tk.Button(
            self.master,
            text="Start tracking",
            width=buttons_width,
            height=buttons_height,
            command=self.start_tracking
        )
        self.start_button.grid(row=1, column=0)

        self.stop_button = tk.Button(
            self.master,
            text="Stop tracking",
            width=buttons_width,
            height=buttons_height,
            command=self.stop_tracking
        )
        self.stop_button.grid(row=2, column=0)

        self.screenshots_process = None
        self.time_tracking_process = None

        self.hour = self.minute = self.second = 0

    def update_time(self):
        if self.running:
            self.time_variable.set('Time: {}'.format(
                datetime.time(hour=self.hour, minute=self.minute, second=self.second).strftime('%H:%M:%S')
            ))
            self.master.after(1000, self.update_time)
            self.second += 1
            if self.second == 60:
                self.minute += 1
                self.second = 0
            if self.minute == 60:
                self.hour += 1
                self.minute = 0

    def on_closing(self):
        if self.screenshots_process:
            self.screenshots_process.terminate()
        self.master.destroy()

    def start_tracking(self):
        if self.running:
            return

        self.running = True

        self.screenshots_process = Process(target=making_screenshots, args=(self.queue,))
        self.screenshots_process.start()

        self.queue.put('start')

        self.update_time()

    def stop_tracking(self):
        if not self.running:
            return

        self.running = False
        self.hour = self.minute = self.second = 0

        self.time_variable.set('Time: {}'.format(
            datetime.time(hour=self.hour, minute=self.minute, second=self.second).strftime('%H:%M:%S')
        ))

        self.queue.put('stop')
        if self.screenshots_process:
            self.screenshots_process.terminate()


def making_screenshots(queue, period=60, destination_dir='screenshots'):
    try:
        os.mkdir(destination_dir)
    except FileExistsError:
        pass

    action = None

    with mss() as sct:
        while True:
            if not queue.empty():
                action = queue.get()
            if action == 'start':
                sct.shot(output='{}/{}.png'.format(destination_dir, datetime.datetime.now().time().strftime('%H-%M-%S')))
                sleep(period)


if __name__ == '__main__':
    queue = Queue()
    queue.cancel_join_thread()

    gui = GUI(queue)
    gui.master.mainloop()
