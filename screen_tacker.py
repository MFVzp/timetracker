import os
from time import sleep
import datetime
import tkinter as tk
from multiprocessing import Process, Queue

from mss import mss
import requests


class GUI:
    def __init__(self, command_queue, save_screenshots_queue):
        self.running = False
        self.master = tk.Tk()
        self.master.geometry('{}x{}'.format(290, 400))
        self.master.resizable(width=False, height=False)
        self.master.winfo_toplevel().title('Time tracker')
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        row = 0
        self.time_variable = tk.StringVar()
        self.time_variable.set('00:00:00')
        self.time_label = tk.Label(
            self.master,
            font=("Times New Roman", 20),
            height=2,
            width=19,
            textvariable=self.time_variable
        )
        self.time_label.grid(row=row, sticky=tk.W + tk.E)
        self.master.grid_rowconfigure(row, minsize=70)
        row += 1
        
        self.description_title_label = tk.Label(
            self.master,
            font=("Times New Roman", 16),
            text='Description:',
            anchor=tk.W
        )
        self.description_title_label.grid(row=row, sticky=tk.W + tk.E)
        row += 1
        
        self.description_variable = tk.StringVar()
        self.description = tk.Text(
            self.master,
            font=("Times New Roman", 11),
            height=4,
            width=10
        )
        self.description.grid(row=row, sticky=tk.W + tk.E + tk.N + tk.S)
        self.description.bind('<Return>', self.add_description)
        self.description.bind('<FocusOut>', self.add_description)
        self.description.bind('<Button-1>', self.change_description)
        self.master.grid_rowconfigure(row, minsize=50)
        row += 1

        buttons_height = 4
        self.start_button = tk.Button(
            self.master,
            text="Start tracking",
            height=buttons_height,
            command=self.start_tracking
        )
        self.start_button.grid(row=row, sticky=tk.W + tk.E + tk.S)
        self.master.grid_rowconfigure(row, minsize=110)
        row += 1
        self.stop_button = tk.Button(
            self.master,
            text="Stop tracking",
            height=buttons_height,
            command=self.stop_tracking
        )
        self.stop_button.grid(row=row, sticky=tk.W + tk.E)
        row += 1
        
        self.command_queue = command_queue
        self.save_screenshots_queue = save_screenshots_queue
        
        self.screenshots_process = self.screenshots_sender = None
        self.time_tracking_process = None

        self.hour = self.minute = self.second = 0

    def add_description(self, *args):
        self.description_variable.set(self.description.get('0.0', tk.END))
        self.description.config(state=tk.DISABLED)
    
    def change_description(self, *args):
        if not self.running:
            self.description.config(state=tk.NORMAL)

    def update_time(self):
        if self.running:
            self.time_variable.set(
                datetime.time(hour=self.hour, minute=self.minute, second=self.second).strftime('%H:%M:%S')
            )
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
            
        if self.screenshots_sender:
            self.screenshots_sender.terminate()
            
        self.master.destroy()

    def start_tracking(self):
        if self.running:
            return
        
        self.add_description()
        self.running = True

        self.screenshots_process = Process(
            target=making_screenshots,
            args=(self.command_queue, self.save_screenshots_queue)
        )
        self.screenshots_process.start()

        self.screenshots_sender = Process(
            target=sending_screenshots,
            args=(self.save_screenshots_queue, self.description_variable.get())
        )
        self.screenshots_sender.start()

        self.command_queue.put('start')

        self.update_time()

    def stop_tracking(self):
        if not self.running:
            return

        self.running = False
        self.hour = self.minute = self.second = 0

        self.time_variable.set(
            datetime.time(hour=self.hour, minute=self.minute, second=self.second).strftime('%H:%M:%S')
        )

        self.command_queue.put('stop')
        if self.screenshots_process:
            self.screenshots_process.terminate()
        
        if self.screenshots_sender:
            self.screenshots_sender.terminate()


def making_screenshots(command_queue, save_screenshots_queue, period=600, destination_dir='screenshots'):
    try:
        os.mkdir(destination_dir)
    except FileExistsError:
        pass

    action = None
    sleep(3)

    with mss() as sct:
        while True:
            if not command_queue.empty():
                action = command_queue.get()
            if action == 'start':
                date = datetime.datetime.now()
                filename = '{}/{}.png'.format(
                    destination_dir,
                    date.strftime('%M-%H-%d-%m-%Y')
                )
                sct.shot(output=filename)
                save_screenshots_queue.put((date.strftime('%Y-%m-%dT%H:%M'), filename))
                sleep(period)


def sending_screenshots(save_screenshots_queue, description):
    
    url = 'http://127.0.0.1:8000/work_diary/api/upload_screenshots/'
    
    while True:
        if not save_screenshots_queue.empty():
            create_date, filename = save_screenshots_queue.get()
            with open(filename, 'rb') as file:
                resp = requests.post(
                    url=url,
                    data={
                        'description': description or str(),
                        'create_date': create_date
                    },
                    files={
                        'image': (filename, file)
                    }
                )
            if resp.json()['status'] == 'success':
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass
            

if __name__ == '__main__':
    command_queue = Queue()
    save_screenshots_queue = Queue()
    
    command_queue.cancel_join_thread()
    save_screenshots_queue.cancel_join_thread()

    gui = GUI(command_queue=command_queue, save_screenshots_queue=save_screenshots_queue)
    gui.master.mainloop()
