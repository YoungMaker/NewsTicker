from Tkinter import Frame, Tk

class Ticker(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self.parent = parent #sets parent frame, the default TK window.
        self.parent.title("TICKER WINDOW")
        self.parent.geometry("%dx%d" % (1200, 200))
        self.parent.attributes('-alpha', 0.0) #sets background alpha channel to almost full transparency
        self.pack() #pack frame


def main():
    root_frame = Tk()
    ticker_window = Ticker(root_frame) #create instance of ticker frame window and pass in Tk root window
    root_frame.mainloop()
    #todo, start window



if __name__ == '__main__':
    main()