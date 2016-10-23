# -*- coding: utf-8 -*-

from Tkinter import Frame, Tk, Label
from flask import Flask, request
import tkFont
import praw
import webbrowser
import ConfigParser
import threading

app = Flask(__name__)

#program constants
MILLISECONDS_MIN = (1000*60)
PUBLIC_DATA=True
SUBREDDIT="news"
NUM_POSTS=3
STR_LENGTH=65
STR_SIZE=30
UNAME="UNAME"
TOKEN=""

CLIENT_ID = '7VtgybHThXJPSA'
CLIENT_SECRET = 'ltt7Bd1d-E4p3liCrjzNudnsHGA'
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

thread=None

@app.route('/')
def homepage():
    return "<h3>Login Callback Page</h3>"

@app.route('/authorize_callback')
def authorized():
    global thread
    state = request.args.get('state', '')
    auth_code = request.args.get('code', '')

    accInfo = main.r.get_access_information(auth_code)
    print auth_code
    #todo- save auth code in ini file
    posts = main.r.get_front_page(limit=4)
    title_string = ""
    for post in posts:  # burns top three posts to single string
        title_string += post.title.upper() + " " + u"\u25BA" + " "
    main.news_tick = TextObject(title_string)
    main.start_ticking()
    return "<h3>Login Success, the ticker is starting</h3>"


class Main:
    #globals
    r = None
    news_tick = None
    ticker_window = None
    root_frame = None
    config=None


    def __init__(self):
        pass

    def start(self):
        self.root_frame = Tk()
        self.root_frame.resizable(0, 0)
        self.ticker_window = Ticker(self.root_frame)  # create instance of ticker frame window and pass in Tk root window
        self.root_frame.mainloop()

    def start_ticking(self):
        self.root_frame.after(300, update_text)
        self.root_frame.after(MILLISECONDS_MIN, update_reddit)

    def open_reddit(self, reddit):
        self.r = reddit

    def setup_config(self):
        self.config = ConfigParser.ConfigParser()


class Ticker(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self._offsetx = 0
        self._offsety = 0
        self.parent = parent #sets parent frame, the default TK window.
        self.parent.title("TICKER WINDOW")
        #todo decide on proper font and color scheme
        font = tkFont.Font(family="Franklin Gothic Book", size=STR_SIZE)
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

    def on_dbl_click(self):
        pass

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
        thread.join()
        self.parent.quit()
        #exit(0)
        #sys.exit(0)

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
    global main

    #todo- filter sticked posts from subreddits when in public mode
    main.open_reddit(praw.Reddit("Reddit News Ticker"))

    posts = main.r.get_subreddit(SUBREDDIT).get_hot(limit=4)
    title_string = ""
    for post in posts: #burns top three posts to single string
        title_string += post.title.upper() +  " " + u"\u25BA" + " "

    main.start(TextObject(title_string))

def connect_to_reddit_personal():
    global main

    main.open_reddit(praw.Reddit("Personalized reddit news ticker with OAuth"))
    main.r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    auth_URL = main.r.get_authorize_url(UNAME, "identity read", True)

    print "starting web"
    webbrowser.open(auth_URL)

def update_reddit_refresh_key():
    global main

    print "updating reddit private mode"
    try:
        #re-connect to reddit and refresh
        posts = main.r.get_front_page(limit=4)
        title_string = ""
        for post in posts:  # burns top three posts to single string
            title_string += post.title.upper() + " " + u"\u25BA" + " "
        main.news_tick.string = title_string
    except:
        print "read time out or other error"
    main.root_frame.after(MILLISECONDS_MIN * 5, update_reddit)  # recurse after calls, update every 5 min

def login_reddit_refresh_key():
    global main

    main.open_reddit(praw.Reddit("Personalized reddit news ticker with OAuth"))
    main.r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    main.r.refresh_access_information(refresh_token=TOKEN, update_session=True)
    posts = main.r.get_front_page(limit=4)
    title_string = ""
    for post in posts:  # burns top three posts to single string
        title_string += post.title.upper() + " " + u"\u25BA" + " "

    main.start(TextObject(title_string))


def update_reddit():
    global main
    global PUBLIC_DATA

    print "updating reddit"
    if PUBLIC_DATA.lower() == "false":
        update_reddit_refresh_key()
    try:
        posts = main.r.get_subreddit(SUBREDDIT).get_hot(limit=4)
        title_string = ""
        for post in posts: #burns top three posts to single string
            title_string += post.title.upper() +  " " + u"\u25BA" + " "
        main.news_tick.string = title_string
    except:
        print "read time out or other error"
    main.root_frame.after(MILLISECONDS_MIN*5, update_reddit) #recurse after calls, update every 5 min

#called once every n milliseconds by the graphics thread, wakes this thread to start changing the text
def update_text():
    global main

    main.ticker_window.update_label(main.news_tick.get_next_fragment())
    main.ticker_window.after(300, update_text)


def config_to_dict(section): #taken from https://wiki.python.org/moin/ConfigParserExamples
    global main
    dict1 = {}
    options = main.config.options(section)
    for option in options:
        try:
            dict1[option] = main.config.get(section, option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def parse_options():
    global main
    main.config.read("settings.ini")
    settings = config_to_dict("main")

    #use global variables
    global PUBLIC_DATA
    global SUBREDDIT
    global NUM_POSTS
    global STR_SIZE
    global STR_LENGTH
    global TOKEN

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
    if settings.has_key('user'):
        UNAME = settings['user']
    if settings.has_key("token"):
        TOKEN = settings['token']

    print "data = %s, subreddit = %s, num posts = %s, text size= %s, text length= %s, token = %s" % (PUBLIC_DATA, SUBREDDIT, NUM_POSTS, STR_SIZE, STR_LENGTH, TOKEN)


def app_run():
    app.run(debug=False, port=65010)  # starts webserver for Reddit OAuth callback page

def main_func():
    global main
    global PUBLIC_DATA

    main =  Main()
    main.setup_config()
    parse_options()

    if PUBLIC_DATA.lower() == "false":
        if len(TOKEN) > 0:
            login_reddit_refresh_key()
        else:
            global thread
            thread = threading.Thread(target=app_run, args=[])
            thread.start()
            connect_to_reddit_personal()

        main.start()
        #thread.join()
    else:
        connect_to_reddit()
        main.start_ticking()

if __name__ == '__main__':
    main_func()


