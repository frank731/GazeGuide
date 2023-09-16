from tkinter import *
import socket 

#RUNT HIS FIRST

class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)        
        self.master = master

        # widget can take all window
        self.pack(fill=BOTH, expand=1)

        # create button, link it to clickExitButton()
        exitButton = Button(self, text="Set Base Looking Direction", command=self.send_signal)
        
        # place button at (0,0)
        exitButton.place(x=0, y=0)
        exitButton.pack(fill=BOTH, expand=1)

    def clickExitButton(self):
        exit()

    def send_signal(self):
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect(("127.0.0.1", 12345))
        sender_socket.send(b"button_pressed")


root = Tk()
app = Window(root)
root.wm_title("Calibrate Glasses")
root.geometry("320x200")
root.mainloop()