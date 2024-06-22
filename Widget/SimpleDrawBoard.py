import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor
from tkinter import messagebox
from PIL import Image, ImageDraw


class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("绘画软件")

        self.pen_color = "black"
        self.eraser_color = "white"  # 橡皮擦的颜色
        self.old_x = None
        self.old_y = None
        self.eraser_mode = False

        self.canvas = tk.Canvas(root, bg="white", width=600, height=400)
        self.canvas.pack()

        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(pady=10)

        self.pen_button = ttk.Button(self.button_frame, text="选择颜色", command=self.choose_color)
        self.pen_button.grid(row=0, column=0)

        self.eraser_button = ttk.Button(self.button_frame, text="橡皮擦", command=self.toggle_eraser)
        self.eraser_button.grid(row=0, column=1)

        self.clear_button = ttk.Button(self.button_frame, text="清空画布", command=self.clear_canvas)
        self.clear_button.grid(row=0, column=3)

        self.canvas.bind("<Button-1>", self.start_paint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.end_paint)

    def choose_color(self):
        color = askcolor(color=self.pen_color)[1]
        if color:
            self.pen_color = color

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode
        if self.eraser_mode:
            self.eraser_button.config(text="画笔模式")
        else:
            self.eraser_button.config(text="橡皮擦")

    def clear_canvas(self):
        self.canvas.delete("all")

    def start_paint(self, event):
        self.old_x = event.x
        self.old_y = event.y

    def paint(self, event):
        if self.old_x and self.old_y:
            x, y = event.x, event.y
            if self.eraser_mode:
                self.canvas.create_line(self.old_x, self.old_y, x, y, fill=self.eraser_color, width=10,
                                        capstyle=tk.ROUND, smooth=tk.TRUE)
            else:
                self.canvas.create_line(self.old_x, self.old_y, x, y, fill=self.pen_color, width=2, capstyle=tk.ROUND,
                                        smooth=tk.TRUE)
            self.old_x = x
            self.old_y = y

    def end_paint(self, event):
        self.old_x = None
        self.old_y = None


if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()