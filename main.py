import base64
import json
import os
import signal
import sys
import tkinter as tk
from io import BytesIO
from tkinter import YES
from typing import Tuple

from PIL import ImageTk, Image

from pic2str import explode


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class FloatingWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.resizable(False, False)

        if sys.platform != 'win32':
            self.wm_attributes('-type', 'splash')
        if sys.platform in ['darwin', 'win32']:
            self.overrideredirect(False)
            self.overrideredirect(True)
        self.wm_attributes('-alpha', sys.argv[2] if len(sys.argv) >= 3 else '1')

        self.frame = tk.Frame(self, width=750, height=421)
        self.frame.pack()
        self.frame.place(anchor='center', relx=0.5, rely=0.5)

        self.img_file = Image.open(BytesIO(base64.b64decode(explode)) if len(sys.argv) < 2 else sys.argv[1])
        self.img = ImageTk.PhotoImage(self.img_file)

        self.label = tk.Label(self.frame, image=self.img)
        self.label.pack(expand=YES)

        x, y = FloatingWindow.load_position()
        self.geometry(f'{self.img_file.width}x{self.img_file.height}+{x}+{y}')

        self.label.bind('<ButtonPress-1>', self.start_move)
        self.label.bind('<ButtonRelease-1>', self.stop_move)
        self.label.bind('<B1-Motion>', self.do_move)

    @staticmethod
    def save_position(x, y):
        if sys.platform == 'linux':
            config_path = os.path.expanduser('~/.config/image-widget/position')
        elif sys.platform == 'win32':
            config_path = os.path.expanduser('~/.image-widget/position')
        elif sys.platform == 'darwin':
            config_path = os.path.expanduser('~/.config/image-widget/position')
        else:
            return

        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w+') as config_file:
            config_file.write(json.dumps([x, y]))

    @staticmethod
    def load_position() -> Tuple[int, int]:
        if sys.platform == 'linux':
            config_path = os.path.expanduser('~/.config/image-widget/position')
        elif sys.platform == 'win32':
            config_path = os.path.expanduser('~/.image-widget/position')
        elif sys.platform == 'darwin':
            config_path = os.path.expanduser('~/.config/image-widget/position')
        else:
            return 0, 0

        if os.path.exists(config_path):
            with open(config_path, 'r') as config_file:
                return json.loads(config_file.read())

        return 0, 0

    def send_lower(self):
        self.lower()
        self.after(10, self.send_lower)

    def start_move(self, event):
        self.prev_x = event.x
        self.prev_y = event.y

    def stop_move(self, _):
        FloatingWindow.save_position(self.winfo_x(), self.winfo_y())
        self.prev_x = None
        self.prev_y = None

    def do_move(self, event):
        delta_x = event.x - self.prev_x
        delta_y = event.y - self.prev_y

        x = self.winfo_x() + delta_x
        y = self.winfo_y() + delta_y

        self.geometry(f'+{x}+{y}')

    def sigint_handler(self, sig, frame):
        self.quit()
        self.update()


def main(): 
    app = FloatingWindow()
    signal.signal(signal.SIGINT, app.sigint_handler)

    app.send_lower()
    app.mainloop()


if __name__ == '__main__':
    main()
