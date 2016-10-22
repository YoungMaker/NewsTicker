# -*- coding: utf-8 -*-

from Tkinter import Frame, Tk, Label
import tkFont
import praw
import webbrowser
import ConfigParser
import os
import urlparse


#program constants
MILLISECONDS_MIN = (1000*60)
PUBLIC_DATA=True
SUBREDDIT="news"
NUM_POSTS=3
STR_LENGTH=65
STR_SIZE=30
UNAME="YoungMaker"

CLIENT_ID = '_UU86a8zzGu-9Q'
CLIENT_SECRET = '_zpcqf3nFbG4q5VB4CnXklLxAGY'
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'


def start(news_object):
    global news_tick
    global root_frame
    global ticker_window

    news_tick = news_object
    root_frame = Tk()
    root_frame.resizable(0,0)
    ticker_window = Ticker(root_frame) #create instance of ticker frame window and pass in Tk root window
    root_frame.after(300, update_text)
    root_frame.after(MILLISECONDS_MIN*5, update_reddit)
    root_frame.mainloop()


class Ticker(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self._offsetx = 0
        self._offsety = 0
        self.parent = parent #sets parent frame, the default TK window.
        self.parent.title("TICKER WINDOW")
        #todo decide on proper font and color scheme
        font = tkFont.Font(family="Berlin Sans FB", size=STR_SIZE)
        #adapted from http://stackoverflow.com/questions/21840133/how-to-display-text-on-the-screen-without-a-window-using-python
        self.label = Label(self, text="", font=font, fg="#606060", bg="#646464") #sets bg color to 2 offset from the foreground color
        self.label.pack()
        self.configure(background="#646464")
        self.parent.overrideredirect(True)
        self.label.bind("<Button-1>", self.on_click)
        self.parent.bind("<Button-1>", self.on_click)
        self.parent.bind("<B1-Motion>", self.on_drag)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.label.bind("<Button-3>", self.on_exit)
        self.parent.wm_attributes("-transparentcolor", "#646464") #sets specific color as transparent.
        #self.parent.attributes('-alpha', 0.) #sets background alpha channel
        self.pack(expand=True) #pack frame

    def on_click(self, e):
        self._offsetx = e.x
        self._offsety = e.y
        #todo- open correct web url on shift+click
        #url = "http://www.reddit.com/r/news"
        #webbrowser.open(url, new=2) #opens URL in new tab

    def on_drag(self, e):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.parent.geometry('+{x}+{y}'.format(x=x, y=y))

    def update_label(self, string):
        self.label.config(text=string)
        #print "called"
        self.label.pack()
        self.pack(expand=True)

    def on_exit(self, e):
        #exit application
        self.parent.quit()

class TextObject: #for right now this will not support URL clicking. This is just a widget for displaying the text
    index=0
    start_index=0
    str_builder=""
    def __init__(self, string, max_letters=STR_LENGTH):
        self.string = string
        self.max_letters = max_letters
        self.index = max_letters
        self.str_builder = self.string[0:self.max_letters]

    def get_next_fragment(self): #
        if self.index < len(self.string):
            #print "%d" % self.index
            #adds chars one at a time to the str_builder string.
            # Every time it does this it also removes one from the front of the string
            self.str_builder =  self.str_builder[1:] + self.string[self.index]
            self.index += 1 #increase the string index to grab the next char
            return self.str_builder
        else:
            self.index=0
            #self.start_index=0
            #self.str_builder = " "
            return self.str_builder

#todo- figure out a way to register click on posts

def connect_to_reddit():
    #todo- filter sticked posts from subreddits when in public mode
    print "connecting to reddit"
    r = praw.Reddit("Reddit News Ticker")

    posts = r.get_subreddit(SUBREDDIT).get_hot(limit=4)
    title_string = ""
    for post in posts: #burns top three posts to single string
        title_string += post.title.upper() +  " " + u"\u25BA" + " "

    start(TextObject(title_string))

def connect_to_reddit_personal():
    global r
    r = praw.Reddit("Personalized reddit news ticker with OAuth")
    r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    authURL = r.get_authorize_url(UNAME, "identity read", True)

    webbrowser.open(authURL)
    #authCode = input("Enter the code: ")

    #accInfo = r.get_access_information(authCode)
    #posts = r.get_top()
    #title_string = ""
    #for post in posts:  # burns top three posts to single string
    #    title_string += post.title.upper() + " " + u"\u25BA" + " "

    #start(TextObject(title_string))

    url = os.environ["REQUEST_URI"]
    parsed = urlparse.urlparse(url)
    print urlparse.parse_qs(parsed.query)['param']


def update_reddit():
    connect_to_reddit() #re-connects to reddit and pulls new submissions
    root_frame.after(MILLISECONDS_MIN*5, update_reddit) #recurse after calls, update every 5 min

#called once every n milliseconds by the graphics thread, wakes this thread to start changing the text
def update_text():
    ticker_window.update_label(news_tick.get_next_fragment())
    ticker_window.after(300, update_text)


def config_to_dict(section): #taken from https://wiki.python.org/moin/ConfigParserExamples
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def parse_options():
    Config.read("settings.ini")
    settings = config_to_dict("main")

    #use global variables
    global PUBLIC_DATA
    global SUBREDDIT
    global NUM_POSTS
    global STR_SIZE
    global STR_LENGTH

    if settings.has_key('public'):
        PUBLIC_DATA = settings['public']
    if settings.has_key('subreddit'):
        SUBREDDIT = settings['subreddit']
    if settings.has_key('num'):
        NUM_POSTS = settings['num']
    if settings.has_key('size'):
        STR_SIZE = settings['size']
    if settings.has_key('length'):
        STR_LENGTH = settings['length']

    print "data = %s, subreddit = %s, num posts = %s, text size= %s, text length= %s" % (PUBLIC_DATA, SUBREDDIT, NUM_POSTS, STR_SIZE, STR_LENGTH)

#start window
r=None
news_tick=None
ticker_window=None
root_frame=None

Config = ConfigParser.ConfigParser()
parse_options()
if PUBLIC_DATA is "false" or "False" or "FALSE":
    connect_to_reddit_personal()
else:
    connect_to_reddit()




