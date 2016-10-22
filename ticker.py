from Tkinter import Frame, Tk, Label
import tkFont


class Ticker(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self._offsetx = 0
        self._offsety = 0
        self.parent = parent #sets parent frame, the default TK window.
        self.parent.title("TICKER WINDOW")
        font = tkFont.Font(family="Hasteristico light", size=80, weight="bold")
        self.label = Label(self, text="", font=font, fg="#606060", bg="#646464")
        self.label.pack()
        self.configure(background="#646464")
        self.parent.overrideredirect(True)
        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.parent.wm_attributes("-transparentcolor", "#646464")
        self.parent.attributes('-alpha', 0.9) #sets background alpha channel
        self.pack(expand=True) #pack frame

    def on_click(self, e):
        self._offsetx = e.x
        self._offsety = e.y

    def on_drag(self, e):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.parent.geometry('+{x}+{y}'.format(x=x, y=y))

    def update_label(self, string):
        self.label.config(text=string)
        #print "called"
        self.label.pack()
        self.pack(expand=True)


class NewsObject:
    index=0
    str_builder=""
    def __init__(self, string, url=""):
        self.string = string
        self.url=url

    def get_next_fragment(self): #todo, remove a letter from the beginning after MAX_LETTERS has been added
        if self.index < len(self.string):
            self.str_builder += self.string[self.index]
            self.index+=1
            return self.str_builder
        else:
            self.index=0
            self.str_builder = " "
            return self.str_builder



def update_event():
    ticker_window.update_label(news_tick.get_next_fragment())
    ticker_window.after(600, update_event)

#start window
news_tick = NewsObject("Trump Ruined Ur Mums Pussy")
root_frame = Tk()
root_frame.resizable(0,0)
ticker_window = Ticker(root_frame) #create instance of ticker frame window and pass in Tk root window
root_frame.after(600, update_event)
root_frame.mainloop()



