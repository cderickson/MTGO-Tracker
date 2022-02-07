import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import modo
import os
import time
import io
import pandas as pd
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
pd.options.mode.chained_assignment = None
from tkcalendar import DateEntry
import datetime
import itertools
import pickle
import shutil

# Saved data:
ALL_DATA =          [[],[],[],{}]
ALL_DATA_INVERTED = [[],[],[],{}]
ALL_DECKS =         {}
DRAFTS_TABLE =      []
PICKS_TABLE =       []
PARSED_FILE_DICT =  {}
PARSED_DRAFT_DICT = {}

# Settings imported/saved in save folder:
FILEPATH_ROOT =          ""
FILEPATH_EXPORT =        ""
FILEPATH_LOGS =          ""
FILEPATH_LOGS_COPY =     ""
FILEPATH_DRAFTS =        ""
FILEPATH_DRAFTS_COPY =   ""
HERO =                   ""
INPUT_OPTIONS =          {}
MAIN_WINDOW_SIZE =  ("small",1000,490)

test_mode =         True
resize =            False
filter_dict =       {}
display =           ""
prev_display =      ""
uaw =               "NA"
field =             ""
new_import =        False
data_loaded =       False
filter_changed =    False
ask_to_save =       False
selected =          ()
display_index =     0
ln_per_page =       20
curr_data =         pd.DataFrame()

def save(exit):
    global ask_to_save
    ask_to_save = False

    save_settings()
    os.chdir(FILEPATH_ROOT + "\\" + "save")

    pickle.dump(ALL_DATA,open("ALL_DATA","wb"))
    pickle.dump(DRAFTS_TABLE,open("DRAFTS_TABLE","wb"))
    pickle.dump(PICKS_TABLE,open("PICKS_TABLE","wb"))
    pickle.dump(PARSED_FILE_DICT,open("PARSED_FILE_DICT","wb"))
    pickle.dump(PARSED_DRAFT_DICT,open("PARSED_DRAFT_DICT","wb"))

    update_status_bar(status="Save complete. Data will be loaded automatically on next startup.")
    os.chdir(FILEPATH_ROOT)

    if exit:
        close()
def save_window(exit):
    height = 100
    width =  300
    save_window = tk.Toplevel(window)
    save_window.title("Save Data")
    save_window.iconbitmap(save_window,"icon.ico")
    save_window.minsize(width,height)
    save_window.resizable(False,False)
    save_window.grab_set()
    save_window.focus()
    save_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def close_save_window():
        save_window.grab_release()
        save_window.destroy()

    mid_frame = tk.LabelFrame(save_window,text="")
    bot_frame = tk.Frame(save_window)

    mid_frame.grid(row=0,column=0,sticky="nsew")
    bot_frame.grid(row=1,column=0,sticky="")

    save_window.grid_columnconfigure(0,weight=1)
    save_window.rowconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1) 
    bot_frame.grid_columnconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(1,weight=1)

    if exit:
        t = "Save data before exiting?"
        button_nosave =  tk.Button(bot_frame,text="Don't Save",width=10,command=lambda : [close_save_window(),close()])
        button_save = tk.Button(bot_frame,text="Save",width=10,command=lambda : [close_save_window(),save(exit=True)])
        button_nosave.grid(row=0,column=1,padx=5,pady=5)
    else:
        t = "This will overwrite any previously saved data.\nAre you sure you want to save?"
        button_save = tk.Button(bot_frame,text="Save",width=10,command=lambda : [close_save_window(),save(exit=False)])
    label1 = tk.Label(mid_frame,text=t,wraplength=width)
    
    button_close = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_save_window())
    
    label1.grid(row=0,column=0,sticky="nsew")       
    button_save.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=2,padx=5,pady=5)
    
    save_window.protocol("WM_DELETE_WINDOW", lambda : close_save_window())
def set_default_window_size():
    height = 150
    width =  300
    popup = tk.Toplevel(window)
    popup.title("Default Window Size")
    popup.iconbitmap(popup,"icon.ico")
    popup.minsize(width,height)
    popup.resizable(False,False)
    popup.grab_set()
    popup.focus()
    popup.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def save_main_window_size():
        global MAIN_WINDOW_SIZE
        global ln_per_page

        if window_size.get() == "Small":
            MAIN_WINDOW_SIZE = ("small",1000,490)
            ln_per_page = 20
        elif window_size.get() == "Large":
            MAIN_WINDOW_SIZE = ("large",1723,780)
            ln_per_page = 35

        os.chdir(FILEPATH_ROOT + "\\" + "save")
        pickle.dump(MAIN_WINDOW_SIZE,open("MAIN_WINDOW_SIZE","wb"))
        window.geometry(str(MAIN_WINDOW_SIZE[1]) + "x" + str(MAIN_WINDOW_SIZE[2]))
        update_status_bar(status="Default Window Size saved.")
        os.chdir(FILEPATH_ROOT)
        set_display(display,update_status=False,start_index=0,reset=False)
        close_window()

    def close_window():
        popup.grab_release()
        popup.destroy()

    mid_frame = tk.LabelFrame(popup,text="")
    bot_frame = tk.Frame(popup)

    mid_frame.grid(row=0,column=0,sticky="nsew")
    bot_frame.grid(row=1,column=0,sticky="")

    popup.grid_columnconfigure(0,weight=1)
    popup.rowconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(1,weight=1)
    bot_frame.grid_columnconfigure(0,weight=1)

    options = ["Small","Large"]
    window_size = tk.StringVar()
    if MAIN_WINDOW_SIZE[0] == "small":
        window_size.set(options[0])
    elif MAIN_WINDOW_SIZE[0] == "large":
        window_size.set(options[1])

    menu_1 = tk.OptionMenu(mid_frame,window_size,*options)
    label1 = tk.Label(mid_frame,text="Default Main Window Size",wraplength=width)
    button_save = tk.Button(bot_frame,text="Save",width=10,command=lambda : save_main_window_size())
    button_close = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_window())
    
    menu_1.grid(row=0,column=0,sticky="s")
    menu_1.config(width=15)
    label1.grid(row=1,column=0,sticky="n",pady=10)       
    button_save.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=1,padx=5,pady=5)
    
    popup.protocol("WM_DELETE_WINDOW", lambda : close_window())
def clear_loaded():
    global ALL_DATA
    global ALL_DATA_INVERTED
    global DRAFTS_TABLE
    global PICKS_TABLE
    global PARSED_FILE_DICT
    global PARSED_DRAFT_DICT
    global HERO
    global filter_dict
    global display
    global data_loaded
    global filter_changed
    global prev_display
    global uaw
    global new_import
    global ask_to_save

    ALL_DATA =          [[],[],[],{}]
    ALL_DATA_INVERTED = [[],[],[],{}]
    DRAFTS_TABLE =      []
    PICKS_TABLE =       []
    PARSED_FILE_DICT.clear()
    PARSED_DRAFT_DICT.clear()
    HERO =              ""
    filter_dict.clear()
    display =           ""
    prev_display =      ""
    uaw =               "NA"
    data_loaded =       False
    filter_changed =    False
    new_import =        False
    ask_to_save =       False

    match_button["state"] = tk.DISABLED
    game_button["state"] = tk.DISABLED
    play_button["state"] = tk.DISABLED
    draft_button["state"] = tk.DISABLED
    pick_button["state"] = tk.DISABLED
    filter_button["state"] = tk.DISABLED
    clear_button["state"] = tk.DISABLED
    revise_button["state"] = tk.DISABLED
    remove_button["state"] = tk.DISABLED
    stats_button["state"] = tk.DISABLED
    next_button["state"] = tk.DISABLED
    back_button["state"] = tk.DISABLED
    
    text_frame.config(text="Dataframe")

    data_menu.entryconfig("Set Default Hero",state=tk.DISABLED)
    data_menu.entryconfig("Clear Loaded Data",state=tk.DISABLED)
    file_menu.entryconfig("Save Data",state=tk.DISABLED)
    data_menu.entryconfig("Input Missing Match Data",state=tk.DISABLED)
    data_menu.entryconfig("Input Missing Game_Winner Data",state=tk.DISABLED)
    data_menu.entryconfig("Apply Best Guess for Deck Names",state=tk.DISABLED)

    # Clear existing data in tree.
    tree1.delete(*tree1.get_children())
    tree1["show"] = "tree"
def clear_window():
    height = 100
    width =  300
    clear_window = tk.Toplevel(window)
    clear_window.title("Clear Loaded Data")
    clear_window.iconbitmap(clear_window,"icon.ico")
    clear_window.minsize(width,height)
    clear_window.resizable(False,False)
    clear_window.grab_set()
    clear_window.focus()
    clear_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def clear():
        clear_loaded()
        update_status_bar(status="Previously loaded data has been cleared.")
        close_clear_window()

    def close_clear_window():
        clear_window.grab_release()
        clear_window.destroy()

    mid_frame = tk.LabelFrame(clear_window,text="")
    bot_frame = tk.Frame(clear_window)

    mid_frame.grid(row=0,column=0,sticky="nsew")
    bot_frame.grid(row=1,column=0,sticky="")

    clear_window.grid_columnconfigure(0,weight=1)
    clear_window.rowconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1) 
    bot_frame.grid_columnconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(1,weight=1)

    label1 = tk.Label(mid_frame,text="This will clear loaded data without saving.\nAre you sure you want to continue?",wraplength=width)
    button_clear = tk.Button(bot_frame,text="Clear",width=10,command=lambda : clear())
    button_close = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_clear_window())
    
    label1.grid(row=0,column=0,sticky="nsew")       
    button_clear.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=1,padx=5,pady=5)
    
    clear_window.protocol("WM_DELETE_WINDOW", lambda : close_clear_window())
def load_saved_window():
    height = 100
    width =  300
    load_saved_window = tk.Toplevel(window)
    load_saved_window.title("Load Saved Data")
    load_saved_window.iconbitmap(load_saved_window,"icon.ico")
    load_saved_window.minsize(width,height)
    load_saved_window.resizable(False,False)
    load_saved_window.grab_set()
    load_saved_window.focus()

    load_saved_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def load():
        clear_filter(update_status=False,reload_display=True)
        startup()
        close_load_window()

    def close_load_window():
        load_saved_window.grab_release()
        load_saved_window.destroy()

    mid_frame = tk.LabelFrame(load_saved_window,text="")
    bot_frame = tk.Frame(load_saved_window)

    mid_frame.grid(row=0,column=0,sticky="nsew")
    bot_frame.grid(row=1,column=0,sticky="")

    load_saved_window.grid_columnconfigure(0,weight=1)
    load_saved_window.rowconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1) 
    bot_frame.grid_columnconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(1,weight=1)

    label1 = tk.Label(mid_frame,text="This will clear your current session.\nAre you sure you want to continue?",wraplength=width)
    button_load = tk.Button(bot_frame,text="Load",width=10,command=lambda : load())
    button_close = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_load_window())
    
    label1.grid(row=0,column=0,sticky="nsew")       
    button_load.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=1,padx=5,pady=5)
    
    load_saved_window.protocol("WM_DELETE_WINDOW", lambda : close_load_window())
def delete_session():
    height = 100
    width =  300
    del_window = tk.Toplevel(window)
    del_window.title("Delete Saved Session")
    del_window.iconbitmap(del_window,"icon.ico")
    del_window.minsize(width,height)
    del_window.resizable(False,False)
    del_window.grab_set()
    del_window.focus()

    del_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def del_session():
        global ALL_DECKS
        ALL_DECKS.clear()

        save_files = ["ALL_DATA","DRAFTS_TABLE","PICKS_TABLE","PARSED_FILE_DICT","PARSED_DRAFT_DICT","SETTINGS","MAIN_WINDOW_SIZE"]
        os.chdir(FILEPATH_ROOT + "\\" + "save")   

        session_exists = False
        for i in save_files:
            if os.path.exists(i):
                session_exists = True
                os.remove(i)

        os.chdir(FILEPATH_LOGS_COPY)
        for (root,dirs,files) in os.walk(os.getcwd()):
            for i in files:
                os.remove(i)
        
        os.chdir(FILEPATH_DRAFTS_COPY)
        for (root,dirs,files) in os.walk(os.getcwd()):
            for i in files:
                os.remove(i) 

        if session_exists == True:
            update_status_bar(status="Saved session data has been deleted.")
        else:
            update_status_bar(status="No saved session data was found.")

        os.chdir(FILEPATH_ROOT)
        close_del_window()

    def close_del_window():
        del_window.grab_release()
        del_window.destroy()

    mid_frame = tk.LabelFrame(del_window,text="")
    bot_frame = tk.Frame(del_window)

    mid_frame.grid(row=0,column=0,sticky="nsew")
    bot_frame.grid(row=1,column=0,sticky="")

    del_window.grid_columnconfigure(0,weight=1)
    del_window.rowconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1) 
    bot_frame.grid_columnconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(1,weight=1)

    label1 = tk.Label(mid_frame,text="This will delete your previous saved session.\nAre you sure you want to continue?",wraplength=width)
    button_del = tk.Button(bot_frame,text="Delete",width=10,command=lambda : del_session())
    button_close = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_del_window())
    
    label1.grid(row=0,column=0,sticky="nsew")       
    button_del.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=1,padx=5,pady=5)
    
    del_window.protocol("WM_DELETE_WINDOW", lambda : close_del_window())
def startup():
    global FILEPATH_ROOT
    global FILEPATH_EXPORT
    global FILEPATH_LOGS
    global FILEPATH_LOGS_COPY
    global FILEPATH_DRAFTS
    global FILEPATH_DRAFTS_COPY
    global HERO
    global ALL_DATA
    global ALL_DATA_INVERTED
    global ALL_DECKS
    global DRAFTS_TABLE
    global PICKS_TABLE
    global PARSED_FILE_DICT
    global PARSED_DRAFT_DICT
    global INPUT_OPTIONS
    global data_loaded
    global ask_to_save

    if os.path.isfile("INPUT_OPTIONS.txt"):
        in_header = False
        in_instr = True
        x = ""
        y = []
        with io.open("INPUT_OPTIONS.txt","r",encoding="ansi") as file:
            initial = file.read().split("\n")
            for i in initial:
                if i == "-----------------------------":
                    if in_instr:
                        in_instr = False
                    in_header = not in_header
                    if in_header == False:
                        x = last.split(":")[0].split("# ")[1]
                    elif x != "":
                        INPUT_OPTIONS[x] = y
                        y = []                        
                elif (in_header == False) and (i != "") and (in_instr == False):
                    y.append(i)
                last = i
    else:
        INPUT_OPTIONS["Constructed Match Types"] = modo.match_types(con=True)
        INPUT_OPTIONS["Booster Draft Match Types"] = modo.match_types(booster=True)
        INPUT_OPTIONS["Sealed Match Types"] = modo.match_types(sealed=True)
        INPUT_OPTIONS["Archetypes"] = modo.archetypes()
        INPUT_OPTIONS["Constructed Formats"] = modo.formats(con=True)
        INPUT_OPTIONS["Limited Formats"] = modo.formats(lim=True)
        INPUT_OPTIONS["Cube Formats"] = modo.formats(cube=True)
        INPUT_OPTIONS["Booster Draft Formats"] = modo.formats(booster=True)
        INPUT_OPTIONS["Sealed Formats"] = modo.formats(sealed=True)
    
    FILEPATH_ROOT = os.getcwd()
    if os.path.isdir("save") == False:
        os.mkdir(FILEPATH_ROOT + "\\" + "save")
    if os.path.isdir("export") == False:
        os.mkdir(FILEPATH_ROOT + "\\" + "export") 
    if os.path.isdir("gamelogs") == False:
        os.mkdir(FILEPATH_ROOT + "\\" + "gamelogs")
    if os.path.isdir("draftlogs") == False:
        os.mkdir(FILEPATH_ROOT + "\\" + "draftlogs")
    FILEPATH_EXPORT = FILEPATH_ROOT + "\\" + "export"
    FILEPATH_LOGS_COPY = FILEPATH_ROOT + "\\" + "gamelogs"
    FILEPATH_DRAFTS_COPY = FILEPATH_ROOT + "\\" + "draftlogs"
    os.chdir(FILEPATH_ROOT + "\\" + "save")

    if os.path.isfile("SETTINGS"):
        SETTINGS = pickle.load(open("SETTINGS","rb"))
        #FILEPATH_ROOT   =     SETTINGS[0]
        FILEPATH_EXPORT =      SETTINGS[1]
        FILEPATH_LOGS =        SETTINGS[2]
        #FILEPATH_LOGS_COPY =  SETTINGS[3]
        FILEPATH_DRAFTS =      SETTINGS[4]
        #FILEPATH_DRAFTS_COPY = SETTINGS[5]
        HERO =                 SETTINGS[6]

    if os.path.isfile("ALL_DECKS"):
        ALL_DECKS = pickle.load(open("ALL_DECKS","rb"))

    if (os.path.isfile("ALL_DATA") == False) & (os.path.isfile("DRAFTS_TABLE") == False):
        update_status_bar(status="No session data to load. Import your MTGO GameLog files to get started.")
        os.chdir(FILEPATH_ROOT)
        return
    ALL_DATA = pickle.load(open("ALL_DATA","rb"))
    DRAFTS_TABLE = pickle.load(open("DRAFTS_TABLE","rb"))
    PICKS_TABLE = pickle.load(open("PICKS_TABLE","rb"))
    PARSED_FILE_DICT = pickle.load(open("PARSED_FILE_DICT","rb"))
    PARSED_DRAFT_DICT = pickle.load(open("PARSED_DRAFT_DICT","rb"))

    ALL_DATA_INVERTED = modo.invert_join(ALL_DATA)

    filter_button["state"] = tk.NORMAL
    clear_button["state"] = tk.NORMAL
    if HERO != "":
        stats_button["state"] = tk.NORMAL
    data_loaded = True

    set_display("Matches",update_status=True,start_index=0,reset=True)
    data_menu.entryconfig("Set Default Hero",state=tk.NORMAL)
    data_menu.entryconfig("Clear Loaded Data",state=tk.NORMAL)
    file_menu.entryconfig("Save Data",state=tk.NORMAL)
    data_menu.entryconfig("Input Missing Match Data",state=tk.NORMAL)
    data_menu.entryconfig("Input Missing Game_Winner Data",state=tk.NORMAL)
    data_menu.entryconfig("Apply Best Guess for Deck Names",state=tk.NORMAL)
    ask_to_save = False
    os.chdir(FILEPATH_ROOT)
def save_settings():
    os.chdir(FILEPATH_ROOT + "\\" + "save")
    SETTINGS = [FILEPATH_ROOT,FILEPATH_EXPORT,FILEPATH_LOGS,FILEPATH_LOGS_COPY,FILEPATH_DRAFTS,FILEPATH_DRAFTS_COPY,HERO]
    pickle.dump(SETTINGS,open("SETTINGS","wb"))
    pickle.dump(MAIN_WINDOW_SIZE,open("MAIN_WINDOW_SIZE","wb"))
    os.chdir(FILEPATH_ROOT)
def set_display(d,update_status,start_index,reset):
    global display
    global prev_display
    global display_index

    if data_loaded == False:
        return

    if display != d:
        prev_display = display
        display = d
    
    if reset:
        display_index = 0

    text_frame.config(text=display)
    
    if len(ALL_DATA[0]) > 0:
        match_button["state"] = tk.NORMAL
        game_button["state"] = tk.NORMAL
        play_button["state"] = tk.NORMAL
    else:
        match_button["state"] = tk.DISABLED
        game_button["state"] = tk.DISABLED
        play_button["state"] = tk.DISABLED
    if len(DRAFTS_TABLE) > 0:
        draft_button["state"] = tk.NORMAL
        pick_button["state"] = tk.NORMAL
    else:
        draft_button["state"] = tk.DISABLED
        pick_button["state"] = tk.DISABLED

    if d == "Matches":
        if resize:
            if MAIN_WINDOW_SIZE[0] == "large":
                window.geometry("1740x" + str(MAIN_WINDOW_SIZE[2]))
        print_data(ALL_DATA[0],modo.header(display),update_status,start_index,apply_filter=True)
    elif d == "Games":
        if resize:
            if MAIN_WINDOW_SIZE[0] == "large":
                window.geometry("1315x" + str(MAIN_WINDOW_SIZE[2]))
        print_data(ALL_DATA[1],modo.header(display),update_status,start_index,apply_filter=True)
    elif d == "Plays":
        if resize:
            if MAIN_WINDOW_SIZE[0] == "large":
                window.geometry("1665x" + str(MAIN_WINDOW_SIZE[2]))
        print_data(ALL_DATA[2],modo.header(display),update_status,start_index,apply_filter=True)
    elif d == "Drafts":
        print_data(DRAFTS_TABLE,modo.header(display),update_status,start_index,apply_filter=True)
    elif d == "Picks":
        print_data(PICKS_TABLE,modo.header(display),update_status,start_index,apply_filter=True)
    revise_button["state"] = tk.DISABLED
    remove_button["state"] = tk.DISABLED
def get_all_data(fp_logs,fp_drafts,copy):
    global ALL_DATA
    global ALL_DATA_INVERTED
    global DRAFTS_TABLE
    global PICKS_TABLE
    global PARSED_FILE_DICT
    global PARSED_DRAFT_DICT
    global data_loaded
    global new_import
    global ask_to_save
    match_count = 0
    draft_count = 0
    if (fp_logs != "No Default GameLogs Folder"):
        new_data = [[],[],[],{}]
        os.chdir(fp_logs)
        for (root,dirs,files) in os.walk(fp_logs):
            for i in files:
                if ("Match_GameLog_" not in i) or (len(i) < 30):
                    pass
                elif (i in PARSED_FILE_DICT):
                    os.chdir(root)
                else:
                    os.chdir(root)
                    with io.open(i,"r",encoding="ansi") as gamelog:
                        initial = gamelog.read()
                        mtime = time.ctime(os.path.getmtime(i))
                    parsed_data = modo.get_all_data(initial,mtime)
                    PARSED_FILE_DICT[i] = (parsed_data[0][0],datetime.datetime.strptime(mtime,"%a %b %d %H:%M:%S %Y"))
                    if copy:
                        try:
                            shutil.copy(i,FILEPATH_LOGS_COPY)
                            os.chdir(FILEPATH_LOGS_COPY)
                            os.utime(i,(datetime.datetime.now().timestamp(),PARSED_FILE_DICT[i][1].timestamp()))
                            os.chdir(root)
                        except shutil.SameFileError:
                            pass
                    new_data[0].append(parsed_data[0])
                    for i in parsed_data[1]:
                        new_data[1].append(i)
                    for i in parsed_data[2]:
                        new_data[2].append(i)
                    for i in parsed_data[3]:
                        new_data[3] = new_data[3] | parsed_data[3]
                    match_count += 1
        new_data_inverted = modo.invert_join(new_data)
        for index in range(3):
            for j in new_data[index]:
                ALL_DATA[index].append(j)
            for j in new_data_inverted[index]:
                ALL_DATA_INVERTED[index].append(j)
        ALL_DATA[3] = ALL_DATA[3] | new_data[3]
        ALL_DATA_INVERTED[3] = ALL_DATA_INVERTED[3] | new_data_inverted[3]

    if (fp_drafts != "No Default DraftLogs Folder"):
        os.chdir(fp_drafts)
        for (root,dirs,files) in os.walk(fp_drafts):
            break
        for i in files:
            if (i.count(".") != 3) or (i.count("-") != 4) or (".txt" not in i):
                pass
            elif (i in PARSED_DRAFT_DICT):
                os.chdir(root)
            else:
                os.chdir(root)
                with io.open(i,"r",encoding="ansi") as gamelog:
                    initial = gamelog.read()   
                parsed_data = modo.parse_draft_log(i,initial) 
                DRAFTS_TABLE.extend(parsed_data[0])
                PICKS_TABLE.extend(parsed_data[1])
                PARSED_DRAFT_DICT[i] = parsed_data[2]
                if copy:
                    try:
                        shutil.copy(i,FILEPATH_DRAFTS_COPY)
                        os.chdir(FILEPATH_DRAFTS_COPY)
                        os.chdir(root)
                    except shutil.SameFileError:
                        pass
                draft_count += 1

    if (match_count == 1) & (draft_count == 1):
        update_status_bar(status=f"Imported {str(match_count)} new Match and {str(draft_count)} new Draft.")
    elif (match_count == 1):
        update_status_bar(status=f"Imported {str(match_count)} new Match and {str(draft_count)} new Drafts.")
    elif (draft_count == 1):
        update_status_bar(status=f"Imported {str(match_count)} new Matches and {str(draft_count)} new Draft.")
    else:
        update_status_bar(status=f"Imported {str(match_count)} new Matches and {str(draft_count)} new Drafts.")

    if (match_count > 0) or (draft_count > 0):
        ask_to_save = True
    new_import = True

    if (len(ALL_DATA[0]) != 0) or (len(DRAFTS_TABLE) != 0):
        filter_button["state"] = tk.NORMAL
        clear_button["state"] = tk.NORMAL
        data_loaded = True
    os.chdir(FILEPATH_ROOT)
def print_data(data,headers,update_status,start_index,apply_filter):
    global new_import
    global curr_data

    small_headers = ["P1_Roll","P2_Roll","P1_Wins","P2_Wins","Game_Num","Play_Num","Turn_Num","Pack_Num","Pick_Num","Pick_Ovr"]
    med_headers = ["Avail_1","Avail_2","Avail_3","Avail_4","Avail_5","Avail_6","Avail_7","Avail_8","Avail_9","Avail_10","Avail_11","Avail_12","Avail_13","Avail_14"]
    large_headers = ["Card"]

    # Clear existing data in tree
    tree1.delete(*tree1.get_children())

    tree1["column"] = headers
    tree1["show"] = "headings"

    # Insert column headers into tree
    for i in tree1["column"]:
        if i in small_headers:
            tree1.column(i,anchor="center",stretch=False,width=75)
        elif i in med_headers:
            tree1.column(i,anchor="center",stretch=False,width=80)
        elif i in large_headers:
            tree1.column(i,anchor="center",stretch=False,width=120)
        else:
            tree1.column(i,anchor="center",stretch=False,width=100)
        tree1.heading(i,text=i,command=lambda _col=i: sort_column2(_col,False,tree1))
    tree1.column(0,anchor="w")
    
    # Build dataframe being printed.
    if isinstance(data, pd.DataFrame):
        df = data
    elif data == None:
        df = df = pd.DataFrame([],columns=headers)
    elif (HERO != "") & (display == "Matches"):
        df = pd.DataFrame(ALL_DATA_INVERTED[0],columns=headers)
        df = df[(df.P1 == HERO)]
    elif (HERO != "") & (display == "Games"):
        df = pd.DataFrame(ALL_DATA_INVERTED[1],columns=headers)
        df = df[(df.P1 == HERO)]
    elif (display == "Drafts"):
        df = pd.DataFrame(DRAFTS_TABLE,columns=headers)
    elif (display == "Picks"):
        df = pd.DataFrame(PICKS_TABLE,columns=headers)
    else:
        df = pd.DataFrame(data,columns=headers)
    total = df.shape[0]
    curr_data = df

    if apply_filter:
        # Apply existing filters.
        filtered_list = []
        for key in filter_dict:
            print(key)
            if key not in headers:
                continue
            for i in filter_dict[key]:
                if i[2:].isnumeric():
                    value = int(i[2:])
                else:
                    value = i[2:]
                if i[0] == "=":
                    if key == "Date":
                        filtered_list.append(df[(df[key].str.contains(value[0:10]))])
                    else:
                        filtered_list.append(df[(df[key] == value)])
                elif i[0] == ">":
                    filtered_list.append(df[(df[key] > value)])
                elif i[0] == "<":
                    filtered_list.append(df[(df[key] < value)])
            if len(filtered_list) == 0:
                pass
            elif len(filtered_list) == 1:
                df = filtered_list[0]
            else:
                index = 1
                df = filtered_list[0]
                while index < (len(filtered_list)):
                    df = pd.merge(df,filtered_list[index],how="outer")
                    index += 1
            filtered_list.clear()
        # Apply Default Sorting.
        if display == "Matches":
            df = df.sort_values(by=["Match_ID"],ascending=False)
        elif display == "Games":
            df = df.sort_values(by=["Match_ID","Game_Num"],ascending=(False,True))
        elif display == "Plays":
            df = df.sort_values(by=["Match_ID","Game_Num","Play_Num"],ascending=(False,True,True))
        elif display == "Drafts":
            df = df.sort_values(by=["Draft_ID"],ascending=False)
        elif display == "Picks":
            df = df.sort_values(by=["Draft_ID","Pick_Ovr"],ascending=(False,True))
        curr_data = df

    df_rows = df.to_numpy().tolist()

    end_index = start_index + ln_per_page
    if len(df_rows) <= end_index:
        end_index = len(df_rows)
        next_button["state"] = tk.DISABLED
    else:
        next_button["state"] = tk.NORMAL

    if start_index == 0:
        back_button["state"] = tk.DISABLED
    else:
        back_button["state"] = tk.NORMAL

    for i in range(start_index,end_index):
        tree1.insert("","end",values=df_rows[i])

    if new_import == True:
        new_import = False
    elif update_status == True:
        update_status_bar(status=f"Displaying: {str(start_index + 1)}-{str(end_index)} of {str(len(df_rows))} total records.")
def get_lists():
    global ALL_DECKS
    global ask_to_save
    errors = []

    os.chdir(filepath_decks)
    folders = os.listdir()
    for i in folders:
        os.chdir(filepath_decks + "\\" + i)
        files = os.listdir()
        month_decks = []
        for j in files:
            with io.open(j,"r",encoding="ansi") as decklist:
                initial = decklist.read()
            deck = modo.parse_list(j,initial)
            if deck == None:
                errors.append((i,j))
            month_decks.append(deck)
        ALL_DECKS[i] = month_decks
    ask_to_save = True

    label = f"Imported Sample Decklists. {str(len(errors))} error(s) found"
    if len(errors) == 0:
        label += "."
    else:
        label += ": "
        for index,i in enumerate(errors):
            if index > 0:
                label += ", "
            label += i[0] + "/" + i[1]
    update_status_bar(status=label)
    
    os.chdir(FILEPATH_ROOT)
def input_missing_data():
    global ALL_DATA
    global ALL_DATA_INVERTED
  
    mformat_index = modo.header("Matches").index("Format")
    lformat_index = modo.header("Matches").index("Limited_Format")
    mtype_index =   modo.header("Matches").index("Match_Type")
    p1_arch_index = modo.header("Matches").index("P1_Arch")
    p1_sub_index =  modo.header("Matches").index("P1_Subarch")
    p2_arch_index = modo.header("Matches").index("P2_Arch")
    p2_sub_index =  modo.header("Matches").index("P2_Subarch")

    n = 0
    count = 0
    total = len(ALL_DATA[0])
    for i in ALL_DATA[0]:    # Iterate through matches.
        n += 1
        
        # Match record is missing some data.
        if (i[p1_arch_index] == "NA") or (i[p1_sub_index] == "NA") or \
            (i[p2_arch_index] == "NA") or (i[p2_sub_index] == "NA") or \
            (i[p1_sub_index] == "Unknown") or (i[p2_sub_index] == "Unknown") or \
            (i[mformat_index] == "NA") or (i[mtype_index] == "NA") or \
            ((i[mformat_index] in INPUT_OPTIONS["Limited Formats"]) & (i[lformat_index] == "NA")): 
            count += 1
            df = pd.DataFrame(ALL_DATA[2],columns=modo.header("Plays"))
            df = df[(df.Match_ID == i[0])]
            players = [i[modo.header("Matches").index("P1")],i[modo.header("Matches").index("P2")]]
            cards1 =  df[(df.Casting_Player == players[0]) & (df.Action == "Land Drop")].Primary_Card.value_counts().keys().tolist()
            cards2 =  df[(df.Casting_Player == players[0]) & (df.Action == "Casts")].Primary_Card.value_counts().keys().tolist()
            cards3 =  df[(df.Casting_Player == players[1]) & (df.Action == "Land Drop")].Primary_Card.value_counts().keys().tolist()
            cards4 =  df[(df.Casting_Player == players[1]) & (df.Action == "Casts")].Primary_Card.value_counts().keys().tolist()
            cards1 = sorted(cards1,key=str.casefold)
            cards2 = sorted(cards2,key=str.casefold)
            cards3 = sorted(cards3,key=str.casefold)
            cards4 = sorted(cards4,key=str.casefold)
            revise_entry_window(players,cards1,cards2,cards3,cards4,(n,total),i)
            if missing_data == "Exit":
                break
            elif missing_data == "Skip":
                continue
            else:
                i[p1_arch_index] = missing_data[0]
                i[p1_sub_index] =  missing_data[1]
                i[p2_arch_index] = missing_data[2]
                i[p2_sub_index] =  missing_data[3]
                i[mformat_index] = missing_data[4]
                i[lformat_index] = missing_data[5]
                i[mtype_index] =   missing_data[6]

    if count == 0:
        update_status_bar(status="No Matches with Missing Data.")
    else:
        ALL_DATA_INVERTED = modo.invert_join(ALL_DATA)
        set_display("Matches",update_status=True,start_index=0,reset=True)
def deck_data_guess(update_type):
    global ALL_DATA
    global ALL_DATA_INVERTED
    global ask_to_save

    date_index = modo.header("Matches").index("Date")
    p1_index = modo.header("Matches").index("P1")
    p2_index = modo.header("Matches").index("P2")
    p1_sa_index = modo.header("Matches").index("P1_Subarch")
    p2_sa_index = modo.header("Matches").index("P2_Subarch")
    format_index = modo.header("Matches").index("Format")
    df2 = pd.DataFrame(ALL_DATA[2],columns=modo.header("Plays"))

    for i in ALL_DATA[0]:
        yyyy_mm = i[date_index][0:4] + "-" + i[date_index][5:7]
        players = [i[p1_index],i[p2_index]]

        # Update P1_Subarch, P2_Subarch for all Limited Matches.
        if update_type == "Limited":
            if i[format_index] in INPUT_OPTIONS["Limited Formats"]:
                ask_to_save = True
                cards1 = df2[(df2.Casting_Player == players[0]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                cards2 = df2[(df2.Casting_Player == players[1]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                i[p1_sa_index] = modo.get_limited_subarch(cards1)
                i[p2_sa_index] = modo.get_limited_subarch(cards2)

        # Update P1_Subarch, P2_Subarch for all Constructed Matches.
        elif update_type == "Constructed":
            if i[format_index] in INPUT_OPTIONS["Constructed Formats"]:
                ask_to_save = True
                cards1 = df2[(df2.Casting_Player == players[0]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                cards2 = df2[(df2.Casting_Player == players[1]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                p1_data = modo.closest_list(set(cards1),ALL_DECKS,yyyy_mm)
                p2_data = modo.closest_list(set(cards2),ALL_DECKS,yyyy_mm)
                i[p1_sa_index] = p1_data[0]
                i[p2_sa_index] = p2_data[0]

        # Update P1_Subarch, P2_Subarch for all Matches.
        elif update_type == "All":
            ask_to_save = True
            cards1 = df2[(df2.Casting_Player == players[0]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
            cards2 = df2[(df2.Casting_Player == players[1]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
            if i[format_index] in INPUT_OPTIONS["Limited Formats"]:
                i[p1_sa_index] = modo.get_limited_subarch(cards1)
                i[p2_sa_index] = modo.get_limited_subarch(cards2)
            else: 
                p1_data = modo.closest_list(set(cards1),ALL_DECKS,yyyy_mm)
                p2_data = modo.closest_list(set(cards2),ALL_DECKS,yyyy_mm)
                i[p1_sa_index] = p1_data[0]
                i[p2_sa_index] = p2_data[0]

        # Update P1_Subarch, P2_Subarch only if equal to "Unknown" or "NA".
        elif update_type == "Unknowns":
            if (i[p1_sa_index] == "Unknown") or (i[p1_sa_index] == "NA"):
                ask_to_save = True
                cards1 = df2[(df2.Casting_Player == players[0]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                if i[format_index] in INPUT_OPTIONS["Limited Formats"]:
                    i[p1_sa_index] = modo.get_limited_subarch(cards1)
                else:
                    p1_data = modo.closest_list(set(cards1),ALL_DECKS,yyyy_mm)
                    i[p1_sa_index] = p1_data[0]
            if (i[p2_sa_index] == "Unknown") or (i[p2_sa_index] == "NA"):
                ask_to_save = True
                cards2 = df2[(df2.Casting_Player == players[1]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                if i[format_index] in INPUT_OPTIONS["Limited Formats"]:
                    i[p2_sa_index] = modo.get_limited_subarch(cards2)
                else:
                    p2_data = modo.closest_list(set(cards2),ALL_DECKS,yyyy_mm)
                    i[p2_sa_index] = p2_data[0]

    ALL_DATA_INVERTED = modo.invert_join(ALL_DATA)
def rerun_decks_window():
    height = 200
    width =  400
    rerun_decks_window = tk.Toplevel(window)
    rerun_decks_window.title("Best Guess Deck Names")
    rerun_decks_window.iconbitmap(rerun_decks_window,"icon.ico")
    rerun_decks_window.minsize(width,height)
    rerun_decks_window.resizable(False,False)
    rerun_decks_window.grab_set()
    rerun_decks_window.focus()
    rerun_decks_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def guess(mode):
        if mode == "NA/Unknown":
            t = "Updated the P1_Subarch, P2_Subarch columns for Unknown Decks in the Date Range: " + list(ALL_DECKS.keys())[0]
            deck_data_guess(update_type="Unknowns")
        elif mode == "Limited":
            t = "Updated the P1_Subarch, P2_Subarch columns for Limited Matches in the Date Range: " + list(ALL_DECKS.keys())[0]
            deck_data_guess(update_type="Limited")
        elif mode == "Constructed":
            t = "Updated the P1_Subarch, P2_Subarch columns for Constructed Matches in the Date Range: " + list(ALL_DECKS.keys())[0]
            deck_data_guess(update_type="Constructed")
        elif mode == "Overwrite All":
            t = "Updated the P1_Subarch, P2_Subarch columns for each Match in the Date Range: " + list(ALL_DECKS.keys())[0]
            deck_data_guess(update_type="All")

        set_display("Matches",update_status=False,start_index=0,reset=True)
        if len(ALL_DECKS) > 1:
            t += " to " + list(ALL_DECKS.keys())[-1]
        update_status_bar(status=t)
        close_window()

    def import_decks():
        global ALL_DECKS

        ALL_DECKS.clear()
        get_lists()
        if len(ALL_DECKS) == 0:
            label2["text"] = "Sample decklists loaded: NONE"
            button_apply["state"] = tk.DISABLED
        elif len(ALL_DECKS) == 1:
            label2["text"] = "Sample decklists loaded: " + list(ALL_DECKS.keys())[0]
            button_apply["state"] = tk.NORMAL
        else:
            label2["text"] = "Sample decklists loaded: " + list(ALL_DECKS.keys())[0] + " to " + list(ALL_DECKS.keys())[-1]
            button_apply["state"] = tk.NORMAL

        button2["state"] = tk.DISABLED

    def close_window():
        rerun_decks_window.grab_release()
        rerun_decks_window.destroy()

    mid_frame = tk.LabelFrame(rerun_decks_window)
    bot_frame = tk.Frame(rerun_decks_window)
    mid_frame.grid(row=0,column=0,sticky="nsew")
    bot_frame.grid(row=1,column=0,sticky="")

    rerun_decks_window.grid_columnconfigure(0,weight=1)
    rerun_decks_window.rowconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    bot_frame.grid_columnconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(1,weight=1)

    apply_options = ["NA/Unknown","Limited","Constructed","Overwrite All"]
    apply_mode = tk.StringVar()
    apply_mode.set(apply_options[0])

    button2 = tk.Button(mid_frame,text="Import Sample Decklists",width=20,command=lambda : import_decks())
    label2 = tk.Label(mid_frame,text="",wraplength=width)
    label3 = tk.Label(mid_frame,text="This will apply best guess deck names in the P1/P2_Subarch columns.\n\nChoose which rows to apply changes.",wraplength=width)
    apply_menu = tk.OptionMenu(bot_frame,apply_mode,*apply_options)
    button_apply = tk.Button(bot_frame,text="Apply",width=10,command=lambda : guess(apply_mode.get()))
    button_close = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_window())

    if len(ALL_DECKS) == 0:
        label2["text"] = "Sample decklists loaded: NONE"
    elif len(ALL_DECKS) == 1:
        label2["text"] = "Sample decklists loaded: " + list(ALL_DECKS.keys())[0]
    else:
        label2["text"] = "Sample decklists loaded: " + list(ALL_DECKS.keys())[0] + " to " + list(ALL_DECKS.keys())[-1]

    label2.grid(row=1,column=0,padx=10,pady=(20,0),sticky="nsew")
    button2.grid(row=2,column=0,padx=10,pady=5) 
    label3.grid(row=3,column=0,padx=10,pady=(10,5),sticky="nsew")       
    apply_menu.grid(row=0,column=0,padx=10,pady=10)
    apply_menu.config(width=15)
    button_apply.grid(row=0,column=1,padx=10,pady=10)
    button_close.grid(row=0,column=2,padx=10,pady=10)   

    if len(ALL_DECKS) == 0:
        button_apply["state"] = tk.DISABLED

    # Comment out if we want to add back ability to import sample decklists from .txt files.
    button2["state"] = tk.DISABLED
    rerun_decks_window.protocol("WM_DELETE_WINDOW", lambda : close_window())
def revise_entry_window(players,cards1,cards2,card3,cards4,progress,mdata):
    def close_format_window(*argv):
        global missing_data
        global ask_to_save

        if len(argv) > 0:
            missing_data = argv[0]
        else:
            missing_data = [p1_arch.get(),p1_sub.get().strip(),p2_arch.get(),p2_sub.get().strip(),mformat.get(),dformat.get(),mtype.get()]
            if missing_data[0] == "P1 Archetype":
                missing_data[0] = "NA"
            if missing_data[2] == "P2 Archetype":
                missing_data[2] = "NA"
            if missing_data[4] == "Select Format":
                missing_data[4] = "NA"
            if missing_data[5] == "Select Limited Format":
                missing_data[5] = "NA"
            if missing_data[6] == "Select Match Type":
                missing_data[6] = "NA"
            ask_to_save = True
        gf.grab_release()
        gf.destroy()
             
    height = 450
    width =  650                
    gf = tk.Toplevel(window)
    if progress == 0:
        gf.title("Revise Entry")
    else:
        gf.title("Input Missing Data - " + str(progress[0]) + "/" + str(progress[1]) + " Matches.")
    gf.iconbitmap(gf,"icon.ico")        
    gf.minsize(width,height)
    gf.resizable(False,False)
    gf.attributes("-topmost",True)
    gf.grab_set()
    gf.focus_force()

    gf.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))
    message = "Date Played: " + mdata[modo.header("Matches").index("Date")]
    str1 = str2 = str3 = str4 = ""
    for index,i in enumerate(cards1):
        if index > 0:
            str1 += "\n"
        str1 += i
    for index,i in enumerate(cards2):
        if index > 0:
            str2 += "\n"
        str2 += i
    for index,i in enumerate(card3):
        if index > 0:
            str3 += "\n"
        str3 += i
    for index,i in enumerate(cards4):
        if index > 0:
            str4 += "\n"
        str4 += i
    
    def update_arch(*argv):
        menu = match_type["menu"]
        menu.delete(0,"end")
        if mformat.get() == "NA":
            l = ["NA"] + INPUT_OPTIONS["Constructed Match Types"] + INPUT_OPTIONS["Booster Draft Match Types"] + INPUT_OPTIONS["Sealed Match Types"]
            for i in l:
                menu.add_command(label=i,command=lambda x=i: mtype.set(x))
        elif mformat.get() in INPUT_OPTIONS["Constructed Formats"]:
            l = ["NA"] + INPUT_OPTIONS["Constructed Match Types"]
            for i in l:
                menu.add_command(label=i,command=lambda x=i: mtype.set(x))
        elif (mformat.get() == "Cube") or (mformat.get() == "Booster Draft"):
            l = ["NA"] + INPUT_OPTIONS["Booster Draft Match Types"]
            for i in l:
                menu.add_command(label=i,command=lambda x=i: mtype.set(x))
        elif mformat.get() == "Sealed Deck":
            l = ["NA"] + INPUT_OPTIONS["Sealed Match Types"]
            for i in l:
                menu.add_command(label=i,command=lambda x=i: mtype.set(x))
        
        if mtype.get() not in l:
            mtype.set("Select Match Type")

        if mformat.get() in INPUT_OPTIONS["Limited Formats"]:
            draft_format["state"] = tk.NORMAL
            arch_options = ["Limited"]

            menu = p1_arch_menu["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p1_arch.set(x))

            menu = p2_arch_menu["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p2_arch.set(x))

            menu = draft_format["menu"]
            menu.delete(0,"end")
            if mformat.get() == "Cube":
                for i in INPUT_OPTIONS["Cube Formats"]:
                    menu.add_command(label=i,command=lambda x=i: dformat.set(x))
            elif mformat.get() == "Booster Draft":
                for i in INPUT_OPTIONS["Booster Draft Formats"]:
                    menu.add_command(label=i,command=lambda x=i: dformat.set(x))
            elif mformat.get() == "Sealed Deck":
                for i in INPUT_OPTIONS["Sealed Formats"]:
                    menu.add_command(label=i,command=lambda x=i: dformat.set(x))            

            p1_arch.set(arch_options[0])
            p2_arch.set(arch_options[0])
            dformat.set("Select Limited Format")
        elif (p1_arch.get() == "Limited"):
            draft_format["state"] = tk.DISABLED
            dformat.set("Select Limited Format")
            arch_options = ["NA"] + INPUT_OPTIONS["Archetypes"]

            menu = p1_arch_menu["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p1_arch.set(x))

            menu = p2_arch_menu["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p2_arch.set(x))

            if (mdata[modo.header("Matches").index("P1_Arch")] == "NA") or (mdata[modo.header("Matches").index("P1_Arch")] == "Limited"):
                p1_arch.set("P1 Archetype")
            else:
                p1_arch.set(mdata[modo.header("Matches").index("P1_Arch")])
            if (mdata[modo.header("Matches").index("P2_Arch")] == "NA") or (mdata[modo.header("Matches").index("P2_Arch")] == "Limited"):
                p2_arch.set("P2 Archetype")
            else:
                p2_arch.set(mdata[modo.header("Matches").index("P2_Arch")])

    top_frame = tk.Frame(gf)
    mid_frame = tk.Frame(gf)
    bot_frame1 = tk.Frame(gf)
    bot_frame2 = tk.Frame(gf)
    top_frame.grid(row=0,column=0,sticky="")
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame1.grid(row=2,column=0,sticky="")
    bot_frame2.grid(row=3,column=0,sticky="")
    
    mid_frame1 = tk.LabelFrame(mid_frame,text="P1: " + players[0])
    mid_frame2 = tk.LabelFrame(mid_frame,text="P2: " + players[1])
    mid_frame1.grid(row=0,column=0,sticky="nsew")
    mid_frame2.grid(row=0,column=1,sticky="nsew")
    
    gf.grid_columnconfigure(0,weight=1)
    gf.rowconfigure(1,minsize=0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(1,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1)
    mid_frame1.grid_columnconfigure(0,weight=1)
    mid_frame1.grid_columnconfigure(1,weight=1)
    mid_frame1.grid_rowconfigure(0,weight=1)
    mid_frame2.grid_columnconfigure(0,weight=1)
    mid_frame2.grid_columnconfigure(1,weight=1)
    mid_frame2.grid_rowconfigure(0,weight=1)

    label_message = tk.Label(top_frame,text=message)
    label1 = tk.Label(mid_frame1,text=str1,anchor="n",wraplength=width/2,justify="left")
    label2 = tk.Label(mid_frame1,text=str2,anchor="n",wraplength=width/2,justify="left")
    label3 = tk.Label(mid_frame2,text=str3,anchor="n",wraplength=width/2,justify="left")
    label4 = tk.Label(mid_frame2,text=str4,anchor="n",wraplength=width/2,justify="left")

    submit_button = tk.Button(bot_frame2,text="Apply",width=10,command=lambda : [close_format_window()])

    arch_options = ["NA"]
    p1_arch = tk.StringVar()
    p1_arch.set("P1 Archetype")
    p2_arch = tk.StringVar()
    p2_arch.set("P2 Archetype")

    format_options = ["NA"] + INPUT_OPTIONS["Constructed Formats"] + INPUT_OPTIONS["Limited Formats"]
    mformat = tk.StringVar()
    mformat.set("Select Format")

    type_options = ["NA"]
    mtype = tk.StringVar()
    mtype.set("Select Match Type")

    draft_format_options = ["NA"]
    dformat = tk.StringVar()
    dformat.set("Select Limited Format")

    if mdata[modo.header("Matches").index("Format")] in INPUT_OPTIONS["Limited Formats"]:
        arch_options = ["Limited"]
    else:
        arch_options += INPUT_OPTIONS["Archetypes"]

    if mdata[modo.header("Matches").index("P1_Arch")] != "NA":
        p1_arch.set(mdata[modo.header("Matches").index("P1_Arch")])
    if mdata[modo.header("Matches").index("P2_Arch")] != "NA":
        p2_arch.set(mdata[modo.header("Matches").index("P2_Arch")])
    if mdata[modo.header("Matches").index("Format")] != "NA": 
        mformat.set(mdata[modo.header("Matches").index("Format")])
    if mdata[modo.header("Matches").index("Limited_Format")] != "NA":
        dformat.set(mdata[modo.header("Matches").index("Limited_Format")])
    if mdata[modo.header("Matches").index("Match_Type")] != "NA":
        mtype.set(mdata[modo.header("Matches").index("Match_Type")])
    
    if mformat.get() == "Cube":
        draft_format_options += INPUT_OPTIONS["Cube Formats"]
        type_options += INPUT_OPTIONS["Booster Draft Match Types"]
    elif mformat.get() == "Booster Draft":
        draft_format_options += INPUT_OPTIONS["Booster Draft Formats"]
        type_options += INPUT_OPTIONS["Booster Draft Match Types"]
    elif mformat.get() == "Sealed Deck":
        draft_format_options += INPUT_OPTIONS["Sealed Formats"]
        type_options += INPUT_OPTIONS["Sealed Match Types"]
    elif mformat.get() in INPUT_OPTIONS["Constructed Formats"]:
        type_options += INPUT_OPTIONS["Constructed Match Types"]
    elif mformat.get() == "Select Format":
        type_options += INPUT_OPTIONS["Constructed Match Types"] + INPUT_OPTIONS["Booster Draft Match Types"] + INPUT_OPTIONS["Sealed Match Types"]

    p1_arch_menu = tk.OptionMenu(mid_frame1,p1_arch,*arch_options)
    p1_sub =  tk.Entry(mid_frame1)
    p2_arch_menu = tk.OptionMenu(mid_frame2,p2_arch,*arch_options)
    p2_sub =  tk.Entry(mid_frame2)

    match_format = tk.OptionMenu(bot_frame2,mformat,*format_options)
    match_type = tk.OptionMenu(bot_frame2,mtype,*type_options)
    draft_format = tk.OptionMenu(bot_frame2,dformat,*draft_format_options)
    p1_sub.insert(0,mdata[modo.header("Matches").index("P1_Subarch")])
    p2_sub.insert(0,mdata[modo.header("Matches").index("P2_Subarch")])

    button_skip = tk.Button(top_frame,text="Skip Match",width=10,command=lambda : [close_format_window("Skip")])
    button_exit = tk.Button(top_frame,text="Exit",width=10,command=lambda : [close_format_window("Exit")])
    
    label1.grid(row=0,column=0,sticky="nsew",padx=5,pady=5)
    label2.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
    label3.grid(row=0,column=0,sticky="nsew",padx=5,pady=5)
    label4.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
    p1_arch_menu.grid(row=1,column=0)
    p1_arch_menu.config(width=15)
    p1_sub.grid(row=1,column=1)
    p2_arch_menu.grid(row=1,column=0)
    p2_arch_menu.config(width=15)
    p2_sub.grid(row=1,column=1)
  
    button_skip.grid(row=0,column=0,padx=10,pady=10)
    label_message.grid(row=0,column=1,padx=10,pady=10)
    button_exit.grid(row=0,column=2,padx=10,pady=10)

    match_format.grid(row=0,column=0,padx=5,pady=5)
    match_format.config(width=20)
    draft_format.grid(row=0,column=1,padx=5,pady=5)
    draft_format.config(width=20)
    match_type.grid(row=0,column=2,padx=5,pady=5)
    match_type.config(width=25)
    submit_button.grid(row=0,column=3,padx=5,pady=5)

    if mformat.get() not in INPUT_OPTIONS["Limited Formats"]:
        draft_format["state"] = tk.DISABLED
    if progress == 0:
        button_skip["state"] = tk.DISABLED
    mformat.trace("w",update_arch)

    gf.protocol("WM_DELETE_WINDOW", lambda : close_format_window("Exit"))
    gf.wait_window()
def revise_draft_window(picks,progress,mdata):
    def close_format_window(*argv):
        global missing_data
        global ask_to_save

        if len(argv) > 0:
            missing_data = argv[0]
        else:
            missing_data = [wins.get(),losses.get()]
            if missing_data[0] == "Match Wins":
                missing_data[0] = "0"
            if missing_data[1] == "Match Losses":
                missing_data[1] = "0"
            ask_to_save = True
        gf.grab_release()
        gf.destroy()
             
    height = 450
    width =  650                
    gf = tk.Toplevel(window)
    if progress == 0:
        gf.title("Revise Entry")
    else:
        gf.title("Input Missing Data - " + str(progress[0]) + "/" + str(progress[1]) + " Matches.")
    gf.iconbitmap(gf,"icon.ico")        
    gf.minsize(width,height)
    gf.resizable(False,False)
    gf.attributes("-topmost",True)
    gf.grab_set()
    gf.focus_force()

    gf.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))
    message = "Date Drafted: " + mdata[modo.header("Drafts").index("Date")]

    string_list = []
    for i in picks:
        card_string = ""
        for index,card in enumerate(i):
            if index > 0:
                card_string += "\n"
            card_string += card
        string_list.append(card_string)

    top_frame = tk.Frame(gf)
    mid_frame = tk.Frame(gf)
    bot_frame2 = tk.Frame(gf)
    top_frame.grid(row=0,column=0,sticky="")
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame2.grid(row=3,column=0,sticky="")
    
    mid_frame1 = tk.LabelFrame(mid_frame,text="Mid Frame1")
    mid_frame1.grid(row=0,column=0,sticky="nsew")
    
    gf.grid_columnconfigure(0,weight=1)
    gf.rowconfigure(1,minsize=0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1)
    mid_frame1.grid_columnconfigure(0,weight=1)
    mid_frame1.grid_columnconfigure(1,weight=1)
    mid_frame1.grid_columnconfigure(2,weight=1)
    mid_frame1.grid_rowconfigure(0,weight=1)

    label_message = tk.Label(top_frame,text=message)
    label1 = tk.Label(mid_frame1,text=string_list[0],anchor="n",wraplength=width/2,justify="left")
    label2 = tk.Label(mid_frame1,text=string_list[1],anchor="n",wraplength=width/2,justify="left")
    label3 = tk.Label(mid_frame1,text=string_list[2],anchor="n",wraplength=width/2,justify="left")

    options_list = [0,1,2,3]

    wins = tk.StringVar()
    wins.set("Match Wins")
    losses = tk.StringVar()
    losses.set("Match Losses")

    wins_menu = tk.OptionMenu(bot_frame2,wins,*options_list)
    losses_menu = tk.OptionMenu(bot_frame2,losses,*options_list)

    button_skip = tk.Button(top_frame,text="Skip Match",width=10,command=lambda : [close_format_window("Skip")])
    button_exit = tk.Button(top_frame,text="Exit",width=10,command=lambda : [close_format_window("Exit")])
    submit_button = tk.Button(bot_frame2,text="Apply",width=10,command=lambda : [close_format_window()])
    
    label1.grid(row=0,column=0,sticky="nsew",padx=5,pady=5)
    label2.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
    label3.grid(row=0,column=2,sticky="nsew",padx=5,pady=5)
  
    button_skip.grid(row=0,column=0,padx=10,pady=10)
    label_message.grid(row=0,column=1,padx=10,pady=10)
    button_exit.grid(row=0,column=2,padx=10,pady=10)

    wins_menu.grid(row=0,column=0,padx=5,pady=5)
    wins_menu.config(width=15)
    losses_menu.grid(row=0,column=1,padx=5,pady=5)
    losses_menu.config(width=15)
    submit_button.grid(row=0,column=2,padx=5,pady=5)

    if progress == 0:
        button_skip["state"] = tk.DISABLED

    gf.protocol("WM_DELETE_WINDOW", lambda : close_format_window("Exit"))
    gf.wait_window()
def tree_double(event):
    global filter_dict  
    if tree1.focus() == "":
        return None
    if (display == "Plays") or (display == "Picks"):
        return None
    if tree1.identify_region(event.x,event.y) == "separator":
        return None
    if tree1.identify_region(event.x,event.y) == "heading":
        return None    
        
    clear_filter(update_status=False,reload_display=False)
    if (display == "Matches"):
        add_filter_setting("Match_ID",tree1.item(tree1.focus(),"values")[0],"=")
        set_display("Games",update_status=True,start_index=0,reset=True)
    elif (display == "Games"):
        add_filter_setting("Match_ID",tree1.item(tree1.focus(),"values")[0],"=")
        add_filter_setting("Game_Num",tree1.item(tree1.focus(),"values")[3],"=")
        set_display("Plays",update_status=True,start_index=0,reset=True)
    elif (display == "Drafts"):
        add_filter_setting("Draft_ID",tree1.item(tree1.focus(),"values")[0],"=")
        set_display("Picks",update_status=True,start_index=0,reset=True)
def back2():
    global filter_dict
    if "Match_ID" in filter_dict:
        match_id = filter_dict["Match_ID"][0][2:]
        clear_filter(update_status=False,reload_display=True)
        add_filter_setting("Match_ID",match_id,"=")
    else:
        clear_filter(update_status=False,reload_display=True)
    if display == "Games":
        set_display("Matches",update_status=True,start_index=0,reset=True)
    elif display == "Plays":
        set_display("Games",update_status=True,start_index=0,reset=True)
def back():
    global display_index
    display_index -= ln_per_page
    if (display == "Drafts") or (display == "Picks"):
        print_data(curr_data,headers=modo.header(display),update_status=True,start_index=display_index,apply_filter=False)
    else:
        print_data(curr_data,headers=modo.header(display),update_status=True,start_index=display_index,apply_filter=False)
    revise_button["state"] = tk.DISABLED
    remove_button["state"] = tk.DISABLED
def next_page():
    global display_index
    display_index += ln_per_page
    if (display == "Drafts") or (display == "Picks"):
        print_data(curr_data,headers=modo.header(display),update_status=True,start_index=display_index,apply_filter=False)
    else:
        print_data(curr_data,headers=modo.header(display),update_status=True,start_index=display_index,apply_filter=False)
    revise_button["state"] = tk.DISABLED
    remove_button["state"] = tk.DISABLED
def export2(current=False,matches=False,games=False,plays=False,drafts=False,picks=False,_csv=False,_excel=False,inverted=False,filtered=False):
    global FILEPATH_EXPORT
    fp = FILEPATH_EXPORT
    if (FILEPATH_EXPORT is None) or (FILEPATH_EXPORT == ""):
        FILEPATH_EXPORT = filedialog.askdirectory()
        FILEPATH_EXPORT = os.path.normpath(FILEPATH_EXPORT)
    if FILEPATH_EXPORT is None:
        return

    file_names = []
    header_list = []
    data_to_write = []

    if current:
        file_names.append("Current")
        if (display == "Drafts") or (display == "Picks"):
            header_list.append(modo.header(display))
        else:
            header_list.append(modo.header(display))
        if display == "Matches":
            if ((HERO != "") & (filtered)):
                df = pd.DataFrame(ALL_DATA_INVERTED[0],columns=modo.header(display))
                df = df[(df.P1 == HERO)]
            else:
                df = pd.DataFrame(ALL_DATA[0],columns=modo.header(display))
        elif display == "Games":
            if ((HERO != "") & (filtered)):
                df = pd.DataFrame(ALL_DATA_INVERTED[1],columns=modo.header(display))
                df = df[(df.P1 == HERO)]
            else:
                df = pd.DataFrame(ALL_DATA[1],columns=modo.header(display))            
        elif display == "Plays":
            df = pd.DataFrame(ALL_DATA[2],columns=modo.header(display))
        elif display == "Drafts":
            df = pd.DataFrame(DRAFTS_TABLE,columns=modo.header(display))
        elif display == "Picks":
            df = pd.DataFrame(PICKS_TABLE,columns=modo.header(display))
        data_to_write.append(df)
    if matches:
        file_names.append("Matches")
        header_list.append(modo.header("Matches"))
        if (inverted) or ((HERO != "") & (filtered)):
            df = pd.DataFrame(ALL_DATA_INVERTED[0],columns=modo.header("Matches"))
        else:
            df = pd.DataFrame(ALL_DATA[0],columns=modo.header("Matches"))
        if ((HERO != "") & (filtered)):
            df = df[(df.P1 == HERO)]
        data_to_write.append(df)
    if games:
        file_names.append("Games")
        header_list.append(modo.header("Games"))
        if (inverted) or ((HERO != "") & (filtered)):
            df = pd.DataFrame(ALL_DATA_INVERTED[1],columns=modo.header("Games"))
        else:
            df = pd.DataFrame(ALL_DATA[1],columns=modo.header("Games"))
        if ((HERO != "") & (filtered)):
            df = df[(df.P1 == HERO)]
        data_to_write.append(df)
    if plays:
        file_names.append("Plays")
        header_list.append(modo.header("Plays"))
        data_to_write.append(pd.DataFrame(ALL_DATA[2],columns=modo.header("Plays")))
    if drafts:
        file_names.append("Drafts")
        header_list.append(modo.header("Drafts"))
        data_to_write.append(pd.DataFrame(DRAFTS_TABLE,columns=modo.header("Drafts")))
    if picks:
        file_names.append("Picks")
        header_list.append(modo.header("Picks"))
        data_to_write.append(pd.DataFrame(PICKS_TABLE,columns=modo.header("Picks")))
    if filtered:
        for index,table in enumerate(data_to_write):
            for key in filter_dict:
                if key not in header_list[index]:
                    break
                for i in filter_dict[key]:
                    if i[2:].isnumeric():
                        value = int(i[2:])
                    else:
                        value = i[2:]
                    if i[0] == "=":
                        if key == "Date":
                            data_to_write[index] = i[(i[key].str.contains(value[0:10]))]
                        else:
                            data_to_write[index] = i[(i[key] == value)]
                    elif i[0] == ">":
                        data_to_write[index] = i[(i[key] > value)]
                    elif i[0] == "<":
                        data_to_write[index] = i[(i[key] < value)]
    if _csv:
        for index,i in enumerate(file_names):
            file_names[index] += ".csv"
        try:
            for index,i in enumerate(file_names):
                f = f"{FILEPATH_EXPORT}/{i}"
                with open(f,"w",encoding="UTF8",newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(header_list[index])
                    df_rows = data_to_write[index].to_numpy().tolist()
                    for row in df_rows:
                        writer.writerow(row)
            update_status_bar(status=f"Exported {len(file_names)} CSV file(s) to {FILEPATH_EXPORT}.")
        except PermissionError:
            update_status_bar(status="Permission Error: Common error cause is an open file that can not be overwritten.")
    elif _excel:
        for index,i in enumerate(file_names):
            file_names[index] += ".xlsx"
        try:
            for index,i in enumerate(file_names):
                f = f"{FILEPATH_EXPORT}/{i}"
                data_to_write[index].to_excel(f,index=False)
            update_status_bar(status=f"Exported {len(file_names)} Excel file(s) to {FILEPATH_EXPORT}.")
        except PermissionError:
            update_status_bar(status="Permission Error: Common error cause is an open file that can not be overwritten.")
    FILEPATH_EXPORT = fp
def set_default_hero():
    height = 100
    width =  275
    hero_window = tk.Toplevel(window)
    hero_window.title("Set Default Hero")
    hero_window.iconbitmap(hero_window,"icon.ico")
    hero_window.minsize(width,height)
    hero_window.resizable(False,False)
    hero_window.grab_set()
    hero_window.focus()
    hero_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def set_hero():
        global HERO
        entry_str = entry.get()
        entry_str = entry_str.strip()
        entry_str = entry_str.replace(".","*")
        entry_str = entry_str.replace(" ","+")
        if entry_str == "":
            HERO = ""
            save_settings()
            update_status_bar(status="Cleared Setting: Hero")
            if display != "Plays":
                set_display(display,update_status=False,start_index=0,reset=True)
            stats_button["state"] = tk.DISABLED
            close_hero_window()
        elif entry_str in hero_options:
            HERO = entry_str
            save_settings()
            update_status_bar(status="Updated Hero to " + HERO + ".")
            if display != "Plays":
                set_display(display,update_status=False,start_index=0,reset=True)
            stats_button["state"] = tk.NORMAL
            close_hero_window()
        else:
            label2["text"] = "Not found."

    def clear_hero():
        entry.delete(0,"end")

    def close_hero_window():
        hero_window.grab_release()
        hero_window.destroy()
    
    df0_i = pd.DataFrame(ALL_DATA_INVERTED[0],columns=modo.header("Matches"))
    hero_options = df0_i.P1.tolist()
    hero_options = sorted(list(set(hero_options)),key=str.casefold)

    mid_frame = tk.LabelFrame(hero_window,text="")
    bot_frame = tk.Frame(hero_window)

    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")

    hero_window.grid_columnconfigure(0,weight=1)
    hero_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(1,weight=1)

    label1 = tk.Label(mid_frame,text="Enter 'Hero' Username.",wraplength=width,justify="left")
    entry = tk.Entry(mid_frame)
    entry.insert(0,HERO)
    label2 = tk.Label(mid_frame,text="",wraplength=width,justify="left")
    button1 = tk.Button(bot_frame,text="Save",width=10,command=lambda : set_hero())
    button2 = tk.Button(bot_frame,text="Clear",width=10,command=lambda : clear_hero())
    button3 = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_hero_window())

    label1.grid(row=0,column=0,pady=(15,5))       
    entry.grid(row=1,column=0)    
    label2.grid(row=2,column=0,pady=(5,5))
    button1.grid(row=4,column=0,padx=5,pady=5)
    button2.grid(row=4,column=1,padx=5,pady=5)
    button3.grid(row=4,column=2,padx=5,pady=5)

    hero_window.protocol("WM_DELETE_WINDOW", lambda : close_hero_window())
def set_default_export():
    height = 150
    width =  350
    export_window = tk.Toplevel(window)
    export_window.title("Set Default Export Folder")
    export_window.iconbitmap(export_window,"icon.ico")
    export_window.minsize(width,height)
    export_window.resizable(False,False)
    export_window.grab_set()
    export_window.focus()
    export_window.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def get_export_path():
        fp = filedialog.askdirectory()
        fp = os.path.normpath(fp)
        if (fp is None) or (fp == "") or (fp == "."):
            label1.config(text="No Default Export Folder")
        else:
            label1.config(text=fp)

    def save_path():
        global FILEPATH_EXPORT
        if label1["text"] == "No Default Export Folder":
            FILEPATH_EXPORT = ""
        else:
            FILEPATH_EXPORT = label1["text"]
        save_settings()
        update_status_bar(status="Updated export folder location.")
        close_export_window()
        
    def close_export_window():
        export_window.grab_release()
        export_window.destroy()
   
    mid_frame = tk.LabelFrame(export_window,text="Export Folder Path")
    bot_frame = tk.Frame(export_window)
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    export_window.grid_columnconfigure(0,weight=1)
    export_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)

    if (FILEPATH_EXPORT is None) or (FILEPATH_EXPORT == "") or (FILEPATH_EXPORT == "."):
        label1 = tk.Label(mid_frame,text="No Default Export Folder",wraplength=width,justify="left")
    else:
        label1 = tk.Label(mid_frame,text=FILEPATH_EXPORT,wraplength=width,justify="left")
    button1 = tk.Button(mid_frame,text="Set Default Export Folder",width=20,command=lambda : get_export_path())
    button3 = tk.Button(bot_frame,text="Save",width=10,command=lambda : save_path())
    button4 = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_export_window())
    
    label1.grid(row=0,column=0,pady=(15,5))
    button1.grid(row=1,column=0,pady=0)
    button3.grid(row=4,column=0,padx=5,pady=5)
    button4.grid(row=4,column=1,padx=5,pady=5)
    
    export_window.protocol("WM_DELETE_WINDOW", lambda : close_export_window())
def set_default_import():
    height = 200
    width =  350
    import_window = tk.Toplevel(window)
    import_window.title("Set Default Import Folders")
    import_window.iconbitmap(import_window,"icon.ico")
    import_window.minsize(width,height)
    import_window.resizable(False,False)
    import_window.grab_set()
    import_window.focus()
    import_window.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def get_drafts_path():
        fp = filedialog.askdirectory()
        fp = os.path.normpath(fp)
        if (fp is None) or (fp == "") or (fp == "."):
            label1.config(text="No Default DraftLogs Folder")
        else:
            label1.config(text=fp)

    def get_logs_path():
        fp = filedialog.askdirectory() 
        fp = os.path.normpath(fp) 
        if (fp is None) or (fp == "") or (fp == "."):
            label2.config(text="No Default GameLogs Folder")
        else:
            label2.config(text=fp)

    def save_path():
        global FILEPATH_DRAFTS
        global FILEPATH_LOGS
        if label1["text"] == "No Default Decklists Folder":
            FILEPATH_DRAFTS = ""
        else:
            FILEPATH_DRAFTS = label1["text"]
        if label2["text"] == "No Default GameLogs Folder":
            FILEPATH_LOGS = ""
        else:
            FILEPATH_LOGS = label2["text"]
        save_settings()
        update_status_bar(status="Updated default import folder locations.")
        close_import_window()
        
    def close_import_window():
        import_window.grab_release()
        import_window.destroy()
   
    mid_frame = tk.LabelFrame(import_window,text="Import Folder Paths")
    bot_frame = tk.Frame(import_window)
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    import_window.grid_columnconfigure(0,weight=1)
    import_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)

    if (FILEPATH_DRAFTS is None) or (FILEPATH_DRAFTS == "") or (FILEPATH_DRAFTS == "."):
        label1 = tk.Label(mid_frame,text="No Default DraftLogs Folder",wraplength=width,justify="left")
    else:
        label1 = tk.Label(mid_frame,text=FILEPATH_DRAFTS,wraplength=width,justify="left")
    button1 = tk.Button(mid_frame,text="Get DraftLogs Folder",width=20,command=lambda : get_drafts_path())

    if (FILEPATH_LOGS is None) or (FILEPATH_LOGS == "") or (FILEPATH_LOGS == "."):
        label2 = tk.Label(mid_frame,text="No Default GameLogs Folder",wraplength=width,justify="left")
    else:
        label2 = tk.Label(mid_frame,text=FILEPATH_LOGS,wraplength=width,justify="left")
    button2 = tk.Button(mid_frame,text="Get GameLogs Folder",width=20,command=lambda : get_logs_path())
    button3 = tk.Button(bot_frame,text="Save",width=10,command=lambda : save_path())
    button4 = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_import_window())

    label1.grid(row=0,column=0,pady=(10,5))
    button1.grid(row=1,column=0,pady=0)
    label2.grid(row=2,column=0,pady=5)
    button2.grid(row=3,column=0,pady=0)
    button3.grid(row=4,column=0,padx=5,pady=5)
    button4.grid(row=4,column=1,padx=5,pady=5)

    import_window.protocol("WM_DELETE_WINDOW", lambda : close_import_window())   
def sort_column2(col,reverse,tree1):
    def sort_key(element):
        if element.dtype == np.int64:
            return element
        else:
            return element.str.casefold()
    global curr_data

    # Clear existing data in tree
    tree1.delete(*tree1.get_children())

    if display == "Matches":
        curr_data.sort_values(by=[col,"Match_ID"],inplace=True,ascending=(reverse,False),key=sort_key)
    elif display == "Games":
        curr_data.sort_values(by=[col,"Match_ID","Game_Num"],inplace=True,ascending=(reverse,False,True),key=sort_key)
    elif display == "Plays":
        curr_data.sort_values(by=[col,"Match_ID","Game_Num","Play_Num"],inplace=True,ascending=(reverse,False,True,True),key=sort_key)
    elif display == "Drafts":
        curr_data.sort_values(by=[col,"Draft_ID"],inplace=True,ascending=(reverse,False),key=sort_key)
    elif display == "Picks":
        curr_data.sort_values(by=[col,"Draft_ID","Pick_Ovr"],inplace=True,ascending=(reverse,False,True),key=sort_key)

    df_rows = curr_data.to_numpy().tolist()

    end_index = display_index + ln_per_page
    if len(df_rows) <= end_index:
        end_index = len(df_rows)
        next_button["state"] = tk.DISABLED
    else:
        next_button["state"] = tk.NORMAL

    if display_index == 0:
        back_button["state"] = tk.DISABLED
    else:
        back_button["state"] = tk.NORMAL

    for i in range(display_index,end_index):
        tree1.insert("","end",values=df_rows[i])

    # Reverse sort next time
    tree1.heading(col,text=col,command=lambda _col=col: sort_column2(_col,not reverse,tree1))
def sort_column(col,reverse,tree1):
    def tuple_casefold(t):
        return (t[0].casefold(),t[1])

    l = []
    for k in tree1.get_children(''):
        l.append((tree1.set(k, col), k))
    l.sort(reverse=reverse,key=tuple_casefold)

    # Rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tree1.move(k, '', index)

    # Reverse sort next time
    tree1.heading(col,text=col,command=lambda _col=col: sort_column(_col,not reverse,tree1))
def sort_column_int(col,reverse,tree1):
    def tree_tuple_to_int(t):
        return (int(t[0]),t[1])

    l = []
    for k in tree1.get_children(''):
        l.append((tree1.set(k, col), k))
    l.sort(reverse=reverse,key=tree_tuple_to_int)

    # Rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tree1.move(k, '', index)

    # Reverse sort next time
    tree1.heading(col,text=col,command=lambda _col=col: sort_column_int(_col,not reverse,tree1))
def add_filter_setting(index,key,op):
    global filter_dict
    global filter_changed
    if key == "None Selected":
        return None
    
    if index in filter_dict:
        l = filter_dict[index]
        if (op + " " + key) not in l:
            l.append(op + " " + key)
            filter_dict[index] = l
            filter_changed = True
    else:
        filter_dict[index] = [op + " " + key]
        filter_changed = True
def clear_filter(update_status,reload_display):
    global filter_changed
    filter_changed = True
    filter_dict.clear()
    if update_status:
        update_status_bar("Cleared All Filters.")
    if reload_display:
        set_display(display,update_status=False,start_index=0,reset=True)
def set_filter():
    height = 300
    width =  550

    if (display == "Drafts") or (display == "Picks"):
        print_data(data=None,headers=modo.header(display),update_status=False,start_index=0,apply_filter=False)
    else:
        print_data(data=None,headers=modo.header(display),update_status=False,start_index=0,apply_filter=False)
    update_status_bar(status=f"Applying Filters to {display} Table.")

    filter_window = tk.Toplevel(window)
    filter_window.title(f"Set Filters - {display}")
    filter_window.iconbitmap(filter_window,"icon.ico")
    filter_window.minsize(width,height)
    filter_window.resizable(False,False)
    filter_window.grab_set()
    filter_window.focus_force()
    filter_window.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))
    
    top_frame = tk.Frame(filter_window)
    mid_frame = tk.Frame(filter_window)
    bot_frame = tk.Frame(filter_window)

    top_frame.grid(row=0,column=0,sticky="")
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")

    mid_frame1 = tk.LabelFrame(mid_frame,text="")
    mid_frame2 = tk.LabelFrame(mid_frame,text="")
    mid_frame1.grid(row=0,column=0,sticky="nsew")
    mid_frame2.grid(row=0,column=1,sticky="nsew")
    mid_frame1.grid_propagate(0)
    mid_frame2.grid_propagate(0)

    filter_window.grid_columnconfigure(0,weight=1)
    filter_window.grid_rowconfigure(1,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(1,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1)

    def update_keys(*argv):
        op.set(operators[0])
        if col.get() == "Date":
            drop_key.grid_forget()
            date.grid(row=0,column=3,padx=10,pady=10)
        else:
            drop_key.grid(row=0,column=3,padx=10,pady=10)
            drop_key.set("None Selected.")
            date.grid_forget()

    def update_combobox():
        key_options = list(df[col.get()].unique())
        if isinstance(key_options[0],(int,np.integer)):
            key_options = sorted(list(set(key_options)),key=int)
        else:
            key_options = sorted(list(set(key_options)),key=str.casefold)
        drop_key["values"] = key_options       
    
    def add():
        o = op.get()
        c = col.get()
        k = key.get()
        if (k == "None Selected.") and (c != "Date"):
            return
        if c == "Date":
            if o == ">":
                k = date.get() + "-00:00"
            elif o == "<":
                k = date.get() + "-23:59"
            elif o == "=":
                k = date.get() + "-12:00"
        add_filter_setting(c,k,o)
        update_filter_text()
        if button2["state"] == tk.DISABLED:
            button2["state"] = tk.NORMAL
    
    def update_filter_text():
        tlabel1 = ""
        tlabel2 = ""
        for key_index,i in enumerate(filter_dict):
            if key_index < 9:
                tlabel1 += i + " : "
                for val_index,value in enumerate(filter_dict[i]):
                    if val_index > 0:
                        tlabel1 += ", "
                    tlabel1 += str(value)
                tlabel1 += "\n"
            else:
                tlabel2 += i + " : "
                for val_index,value in enumerate(filter_dict[i]):
                    if val_index > 0:
                        tlabel2 += ", "
                    tlabel2 += str(value)
                tlabel2 += "\n"
        label1.config(text=tlabel1)
        label2.config(text=tlabel2)
    
    def defocus(event):
        # Clear Auto-Highlight in Combobox menu.
        drop_key.selection_clear()
    
    def apply_filter():
        # Update table and close window.
        set_display(display,update_status=True,start_index=0,reset=True)
        filter_window.grab_release()
        filter_window.destroy()

    def clear_button():
        global filter_changed
        filter_changed = True
        filter_dict.clear()
        update_filter_text()
        button2["state"] = tk.DISABLED

    def close_filter_window():
        # Revert filter changes and close window.
        global filter_dict
        filter_dict = filter_init
        set_display(display,update_status=True,start_index=0,reset=True)
        text_frame.config(text=display)
        filter_window.grab_release()
        filter_window.destroy()

    global filter_changed
    filter_changed = False
    filter_init = filter_dict.copy()

    # Building dataframe (unfiltered) to give us our dropdown options.
    if HERO == "":
        if display == "Matches":
            df = pd.DataFrame(ALL_DATA[0],columns=modo.header(display))
        elif display == "Games":
            df = pd.DataFrame(ALL_DATA[1],columns=modo.header(display))
        elif display == "Plays":
            df = pd.DataFrame(ALL_DATA[2],columns=modo.header(display))
    else:
        if display == "Matches":
            df = pd.DataFrame(ALL_DATA_INVERTED[0],columns=modo.header(display))
            df = df[(df.P1 == HERO)]
        elif display == "Games":
            df = pd.DataFrame(ALL_DATA_INVERTED[1],columns=modo.header(display))
            df = df[(df.P1 == HERO)]
        elif display == "Plays":
            df = pd.DataFrame(ALL_DATA_INVERTED[2],columns=modo.header(display))
    if display == "Drafts":
        df = pd.DataFrame(DRAFTS_TABLE,columns=modo.header(display))
    elif display == "Picks":
        df = pd.DataFrame(PICKS_TABLE,columns=modo.header(display))

    if (display == "Drafts") or (display == "Picks"):
        col_options = modo.header(display).copy()
    else:
        col_options = modo.header(display).copy()
    col_options.pop(0)
    
    col = tk.StringVar()
    col.set(col_options[0])
    key = tk.StringVar()
    key.set("None Selected.")

    key_options = ["None Selected."]
    
    operators = ["=",">","<"]
    op = tk.StringVar()
    op.set(operators[0])

    today = datetime.date.today()

    drop_col = tk.OptionMenu(top_frame,col,*col_options)
    op_menu  = tk.OptionMenu(top_frame,op,*operators)
    drop_key = ttk.Combobox(top_frame,textvariable=key,width=15,
        state="readonly",font="Helvetica 14",justify=tk.CENTER,
        postcommand=update_combobox)
    drop_key.bind("<FocusIn>",defocus)
    date = DateEntry(top_frame,date_pattern="y-mm-dd",width=10,
        year=today.year,month=today.month,day=today.day,
        font="Helvetica 14",state="readonly")
 
    button1 = tk.Button(top_frame,text="Add",width=10,command=lambda : add())
    button2 = tk.Button(bot_frame,text="Clear",state=tk.DISABLED,width=10,command=lambda : clear_button())
    button3 = tk.Button(bot_frame,text="Apply Filter",width=10,command=lambda : apply_filter())
    button4 = tk.Button(bot_frame,text="Exit",width=10,command=lambda : close_filter_window())
    label1 = tk.Label(mid_frame1,text="",wraplength=width/2,justify="left")
    label2 = tk.Label(mid_frame2,text="",wraplength=width/2,justify="left")

    drop_col.grid(row=0,column=1,padx=10,pady=10)
    drop_col.config(width=15)
    op_menu.grid(row=0,column=2,padx=10,pady=10)
    op_menu.config(width=3)
    drop_key.grid(row=0,column=3,padx=10,pady=10)
    button1.grid(row=0,column=4,padx=10,pady=10)

    label1.grid(row=0,column=0,sticky="w")
    label2.grid(row=0,column=1,sticky="w")

    button2.grid(row=0,column=0,padx=10,pady=10)
    button3.grid(row=0,column=1,padx=10,pady=10)
    button4.grid(row=0,column=2,padx=10,pady=10)

    if len(filter_dict) > 0:
        button2["state"] = tk.NORMAL

    col.trace("w",update_keys)
    update_filter_text()
    filter_window.protocol("WM_DELETE_WINDOW", lambda : close_filter_window())
def revise_record2():
    global ALL_DATA
    global ALL_DATA_INVERTED
    global selected

    if tree1.focus() == "":
        return

    selected = tree1.focus()
    values = list(tree1.item(selected,"values"))
    sel_matchid = values[0]

    p1_index      = modo.header("Matches").index("P1")
    p2_index      = modo.header("Matches").index("P2")
    mformat_index = modo.header("Matches").index("Format")
    lformat_index = modo.header("Matches").index("Limited_Format")
    mtype_index =   modo.header("Matches").index("Match_Type")
    p1_arch_index = modo.header("Matches").index("P1_Arch")
    p1_sub_index =  modo.header("Matches").index("P1_Subarch")
    p2_arch_index = modo.header("Matches").index("P2_Arch")
    p2_sub_index =  modo.header("Matches").index("P2_Subarch")

    df = pd.DataFrame(ALL_DATA[2],columns=modo.header("Plays"))
    df = df[(df.Match_ID == values[0])]
    players = [values[p1_index],values[p2_index]]
    cards1 =  df[(df.Casting_Player == players[0]) & (df.Action == "Land Drop")].Primary_Card.value_counts().keys().tolist()
    cards2 =  df[(df.Casting_Player == players[0]) & (df.Action == "Casts")].Primary_Card.value_counts().keys().tolist()
    cards3 =  df[(df.Casting_Player == players[1]) & (df.Action == "Land Drop")].Primary_Card.value_counts().keys().tolist()
    cards4 =  df[(df.Casting_Player == players[1]) & (df.Action == "Casts")].Primary_Card.value_counts().keys().tolist()
    cards1 = sorted(cards1,key=str.casefold)
    cards2 = sorted(cards2,key=str.casefold)
    cards3 = sorted(cards3,key=str.casefold)
    cards4 = sorted(cards4,key=str.casefold)
    revise_entry_window(players,cards1,cards2,cards3,cards4,0,values)
    if (missing_data == "Exit") or (missing_data == "Skip"):
        return

    for i in ALL_DATA[0]:
        if i[0] == values[0]:
            if i[p1_index] == values[p1_index]:
                i[p1_arch_index] = missing_data[0]
                i[p1_sub_index] =  missing_data[1]
                i[p2_arch_index] = missing_data[2]
                i[p2_sub_index] =  missing_data[3]
            else:
                i[p1_arch_index] = missing_data[2]
                i[p1_sub_index] =  missing_data[3]
                i[p2_arch_index] = missing_data[0]
                i[p2_sub_index] =  missing_data[1]
            i[mformat_index] = missing_data[4]
            i[lformat_index] = missing_data[5]
            i[mtype_index] =   missing_data[6]  
            break

    ALL_DATA_INVERTED = modo.invert_join(ALL_DATA)
    set_display("Matches",update_status=True,start_index=display_index,reset=False)
    revise_button["state"] = tk.NORMAL
    remove_button["state"] = tk.NORMAL

    for i in tree1.get_children():
        if list(tree1.item(i,"values"))[0] == sel_matchid:
            tree1.selection_set(i)
            tree1.focus(i)
            selected = i
            break
def revise_record3():
    global ALL_DATA
    global ALL_DATA_INVERTED
    global selected
    if tree1.focus() == "":
        return

    if isinstance(tree1.focus(),str):
        selected = tree1.focus()
    else:
        selected = tree1.focus()[0]
    values = list(tree1.item(selected,"values"))
    sel_matchid = values[0]

    match_wins_index = modo.header(display).index("Match_Wins")
    match_losses_index = modo.header(display).index("Match_Losses")

    df = pd.DataFrame(PICKS_TABLE,columns=modo.header("Picks"))
    df = df[(df.Draft_ID == values[0])]
    pack_nums = df.Pack_Num.unique().tolist()
    pick_list = []
    for i in pack_nums:
        pick_list.append(df[(df.Pack_Num == i)].sort_values("Pick_Ovr",ascending=True).Card.tolist())
        
    revise_draft_window(pick_list,0,values)
    if (missing_data == "Exit") or (missing_data == "Skip"):
        return

    for i in DRAFTS_TABLE:
        if i[0] == values[0]:
            i[match_wins_index] = missing_data[0]
            i[match_losses_index] = missing_data[1]
            break

    set_display(display,update_status=True,start_index=display_index,reset=False)
    revise_button["state"] = tk.NORMAL
    # remove_button["state"] = tk.NORMAL

    for i in tree1.get_children():
        if list(tree1.item(i,"values"))[0] == sel_matchid:
            tree1.selection_set(i)
            tree1.focus(i)
            selected = i
            break
def revise_record():
    if tree1.focus() == "":
        return
    height = 300
    width =  700
    revise_window = tk.Toplevel(window)
    revise_window.title("Revise Record")
    revise_window.iconbitmap(revise_window,"icon.ico")
    revise_window.minsize(width,height)
    revise_window.resizable(False,False)
    revise_window.attributes("-topmost",True)
    revise_window.grab_set()
    revise_window.focus()

    revise_window.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))
    
    mid_frame = tk.LabelFrame(revise_window,text="Match_ID")
    bot_frame = tk.Frame(revise_window)
    mid_frame.grid(row=0,column=0,sticky="nsew")
    bot_frame.grid(row=1,column=0,sticky="")
    
    revise_window.grid_columnconfigure(0,weight=1)
    revise_window.rowconfigure(0,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(1,weight=1)
    mid_frame.grid_columnconfigure(2,weight=1)
    mid_frame.grid_columnconfigure(3,weight=1)
    mid_frame.grid_columnconfigure(4,weight=1)
    mid_frame.grid_columnconfigure(5,weight=1)

    def update_arch(*argv):
        menu = match_type_entry["menu"]
        menu.delete(0,"end")
        if match_format.get() == "NA":
            for i in ["NA"] + INPUT_OPTIONS["Constructed Match Types"] + INPUT_OPTIONS["Booster Draft Match Types"] + INPUT_OPTIONS["Sealed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: match_type.set(x))
        elif match_format.get() in INPUT_OPTIONS["Constructed Formats"]:
            for i in ["NA"] + INPUT_OPTIONS["Constructed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: match_type.set(x))
        elif (match_format.get() == "Cube") or (match_format.get() == "Booster Draft"):
            for i in ["NA"] + INPUT_OPTIONS["Booster Draft Match Types"]:
                menu.add_command(label=i,command=lambda x=i: match_type.set(x))
        elif match_format.get() == "Sealed Deck":
            for i in ["NA"] + INPUT_OPTIONS["Sealed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: match_type.set(x))

        if match_format.get() in INPUT_OPTIONS["Limited Formats"]:
            arch_options = ["Limited"]
            draft_type_entry["state"] = tk.NORMAL

            menu = p1_arch_entry["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p1_arch_type.set(x))

            menu = p2_arch_entry["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p2_arch_type.set(x))

            menu = draft_type_entry["menu"]
            menu.delete(0,"end")
            if match_format.get() == "Cube":
                for i in ["NA"] + INPUT_OPTIONS["Cube Formats"]:
                    menu.add_command(label=i,command=lambda x=i: limited_format.set(x))
            elif match_format.get() == "Booster Draft":
                for i in ["NA"] + INPUT_OPTIONS["Booster Draft Formats"]:
                    menu.add_command(label=i,command=lambda x=i: limited_format.set(x))
            elif match_format.get() == "Sealed Deck":
                for i in ["NA"] + INPUT_OPTIONS["Sealed Formats"]:
                    menu.add_command(label=i,command=lambda x=i: limited_format.set(x))

            p1_arch_type.set(arch_options[0])
            p2_arch_type.set(arch_options[0])
        elif (p1_arch_type.get() == "Limited"):
            arch_options = ["NA"] + INPUT_OPTIONS["Archetypes"]
            limited_format.set("NA")
            draft_type_entry["state"] = tk.DISABLED

            menu = p1_arch_entry["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p1_arch_type.set(x))

            menu = p2_arch_entry["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p2_arch_type.set(x))

            if values[modo.header("Matches").index("P1_Arch")] == "Limited":
                p1_arch_type.set(arch_options[0])
                p2_arch_type.set(arch_options[0])
            else:
                p1_arch_type.set(values[modo.header("Matches").index("P1_Arch")])
                p2_arch_type.set(values[modo.header("Matches").index("P2_Arch")])

    def close_revise_window():
        global ALL_DATA_INVERTED
        for count,i in enumerate(ALL_DATA[0]):
            if i[0] == values[0]:
                if i[modo.header("Matches").index("P1")] == values[modo.header("Matches").index("P1")]:
                    i[modo.header("Matches").index("P1_Arch")] = p1_arch_type.get()
                    i[modo.header("Matches").index("P1_Subarch")] = p1_subarch_entry.get()
                    i[modo.header("Matches").index("P2_Arch")] = p2_arch_type.get()
                    i[modo.header("Matches").index("P2_Subarch")] = p2_subarch_entry.get()
                else:
                    i[modo.header("Matches").index("P1_Arch")] = p2_arch_type.get()
                    i[modo.header("Matches").index("P1_Subarch")] = p2_subarch_entry.get()
                    i[modo.header("Matches").index("P2_Arch")] = p1_arch_type.get()
                    i[modo.header("Matches").index("P2_Subarch")] = p1_subarch_entry.get()
                i[modo.header("Matches").index("Format")] = match_format.get()
                i[modo.header("Matches").index("Limited_Format")] = limited_format.get()
                i[modo.header("Matches").index("Match_Type")] = match_type.get()                   
                ALL_DATA_INVERTED = modo.invert_join(ALL_DATA)
                set_display("Matches",update_status=True,start_index=0,reset=True)
                break
        revise_window.grab_release()
        revise_window.destroy()

    def close_without_saving():
        revise_window.grab_release()
        revise_window.destroy()       

    selected = tree1.focus()
    values = list(tree1.item(selected,"values"))

    format_options = ["NA"] + INPUT_OPTIONS["Constructed Formats"] + INPUT_OPTIONS["Limited Formats"]
    match_format = tk.StringVar()
    match_format.set(values[modo.header("Matches").index("Format")])

    if match_format.get() == "Cube":
        limited_options = INPUT_OPTIONS["Cube Formats"]
        match_options = ["NA"] + INPUT_OPTIONS["Booster Draft Match Types"]
    elif match_format.get() == "Booster Draft":
        limited_options = INPUT_OPTIONS["Booster Draft Formats"]
        match_options = ["NA"] + INPUT_OPTIONS["Booster Draft Match Types"]
    elif match_format.get() == "Sealed Deck":
        limited_options = INPUT_OPTIONS["Sealed Formats"]
        match_options = ["NA"] + INPUT_OPTIONS["Sealed Match Types"]
    elif match_format.get() in INPUT_OPTIONS["Constructed Formats"]:
        limited_options = ["NA"]
        match_options = ["NA"] + INPUT_OPTIONS["Constructed Match Types"]
    elif match_format.get() == "NA":
        limited_options = ["NA"]
        match_options = ["NA"] + INPUT_OPTIONS["Constructed Match Types"] + INPUT_OPTIONS["Booster Draft Match Types"] + INPUT_OPTIONS["Sealed Match Types"]

    limited_format = tk.StringVar()
    limited_format.set(values[modo.header("Matches").index("Limited_Format")])

    match_type = tk.StringVar()
    match_type.set(values[modo.header("Matches").index("Match_Type")])

    if values[modo.header("Matches").index("Format")] in INPUT_OPTIONS["Limited Formats"]:
        arch_options = ["Limited"]
    else:
        arch_options = INPUT_OPTIONS["Archetypes"]
    p1_arch_type = tk.StringVar()
    p1_arch_type.set(values[modo.header("Matches").index("P1_Arch")])

    p2_arch_type = tk.StringVar()
    p2_arch_type.set(values[modo.header("Matches").index("P2_Arch")])

    p1_label =           tk.Label(mid_frame,text="P1:")
    p1_entry =           tk.Label(mid_frame,text=values[modo.header("Matches").index("P1")])
    p1_arch_label =      tk.Label(mid_frame,text="P1_Arch:")
    p1_arch_entry =      tk.OptionMenu(mid_frame,p1_arch_type,*arch_options)
    p1_subarch_label =   tk.Label(mid_frame,text="P1_Subarch:")
    p1_subarch_entry =   tk.Entry(mid_frame)
    p2_label =           tk.Label(mid_frame,text="P2:")
    p2_entry =           tk.Label(mid_frame,text=values[modo.header("Matches").index("P2")])
    p2_arch_label =      tk.Label(mid_frame,text="P2_Arch:")
    p2_arch_entry =      tk.OptionMenu(mid_frame,p2_arch_type,*arch_options)
    p2_subarch_label =   tk.Label(mid_frame,text="P2_Subarch:")
    p2_subarch_entry =   tk.Entry(mid_frame)
    p1_roll_label =      tk.Label(mid_frame,text="P1_Roll:")
    p1_roll_entry =      tk.Label(mid_frame,text=values[modo.header("Matches").index("P1_Roll")])
    p2_roll_label =      tk.Label(mid_frame,text="P2_Roll:")
    p2_roll_entry =      tk.Label(mid_frame,text=values[modo.header("Matches").index("P2_Roll")])
    roll_winner_label =  tk.Label(mid_frame,text="Roll_Winner:")
    roll_winner_entry =  tk.Label(mid_frame,text=values[modo.header("Matches").index("Roll_Winner")])
    p1_wins_label =      tk.Label(mid_frame,text="P1_Wins:")
    p1_wins_entry =      tk.Label(mid_frame,text=values[modo.header("Matches").index("P1_Wins")])
    p2_wins_label =      tk.Label(mid_frame,text="P2_Wins:")
    p2_wins_entry =      tk.Label(mid_frame,text=values[modo.header("Matches").index("P2_Wins")])
    match_winner_label = tk.Label(mid_frame,text="Match_Winner:")
    match_winner_entry = tk.Label(mid_frame,text=values[modo.header("Matches").index("Match_Winner")])
    format_label =       tk.Label(mid_frame,text="Format:")
    format_entry =       tk.OptionMenu(mid_frame,match_format,*format_options)
    draft_type_label =   tk.Label(mid_frame,text="Limited_Format:")
    draft_type_entry =   tk.OptionMenu(mid_frame,limited_format,*limited_options)
    match_type_label =   tk.Label(mid_frame,text="Match_Type:")
    match_type_entry =   tk.OptionMenu(mid_frame,match_type,*match_options)
    date_label =         tk.Label(mid_frame,text="Date:")
    date_entry =         tk.Label(mid_frame,text=values[modo.header("Matches").index("Date")])

    p1_subarch_entry.insert(0,values[modo.header("Matches").index("P1_Subarch")])
    p2_subarch_entry.insert(0,values[modo.header("Matches").index("P2_Subarch")])

    button3 = tk.Button(bot_frame,text="Apply Changes",
                        command=lambda : close_revise_window())
    button4 = tk.Button(bot_frame,text="Cancel",
                        command=lambda : close_without_saving())

    p1_label.grid(row=1,column=0,padx=10,pady=10,sticky="w")
    p1_entry.grid(row=1,column=1,pady=10,sticky="w")
    p1_arch_label.grid(row=1,column=2,pady=10,sticky="w")
    p1_arch_entry.grid(row=1,column=3,pady=10,sticky="w")
    p1_subarch_label.grid(row=1,column=4,pady=10,sticky="w")
    p1_subarch_entry.grid(row=1,column=5,pady=10,sticky="w")
    p2_label.grid(row=2,column=0,padx=10,pady=10,sticky="w")
    p2_entry.grid(row=2,column=1,pady=10,sticky="w")
    p2_arch_label.grid(row=2,column=2,pady=10,sticky="w")
    p2_arch_entry.grid(row=2,column=3,pady=10,sticky="w")
    p2_subarch_label.grid(row=2,column=4,pady=10,sticky="w")
    p2_subarch_entry.grid(row=2,column=5,pady=10,sticky="w")
    p1_roll_label.grid(row=3,column=0,padx=10,pady=10,sticky="w")
    p1_roll_entry.grid(row=3,column=1,pady=10,sticky="w")
    p2_roll_label.grid(row=3,column=2,pady=10,sticky="w")
    p2_roll_entry.grid(row=3,column=3,pady=10,sticky="w")
    roll_winner_label.grid(row=3,column=4,pady=10,sticky="w")
    roll_winner_entry.grid(row=3,column=5,pady=10,sticky="w")
    p1_wins_label.grid(row=4,column=0,padx=10,pady=10,sticky="w")
    p1_wins_entry.grid(row=4,column=1,pady=10,sticky="w")
    p2_wins_label.grid(row=4,column=2,pady=10,sticky="w")
    p2_wins_entry.grid(row=4,column=3,pady=10,sticky="w")
    match_winner_label.grid(row=4,column=4,pady=10,sticky="w")
    match_winner_entry.grid(row=4,column=5,pady=10,sticky="w")
    format_label.grid(row=5,column=0,padx=10,pady=10,sticky="w")
    format_entry.grid(row=5,column=1,pady=10,sticky="w")
    draft_type_label.grid(row=5,column=2,pady=10,sticky="w")
    draft_type_entry.grid(row=5,column=3,pady=10,sticky="w")
    match_type_label.grid(row=5,column=4,pady=10,sticky="w")
    match_type_entry.grid(row=5,column=5,pady=10,sticky="w")
    date_label.grid(row=6,column=0,padx=10,pady=10,sticky="w")
    date_entry.grid(row=6,column=1,pady=10,sticky="w")

    button3.grid(row=0,column=0,padx=10,pady=10)
    button4.grid(row=0,column=1,padx=10,pady=10)

    mid_frame["text"] = "Match_ID: " + values[0]
    if match_format.get() not in INPUT_OPTIONS["Limited Formats"]:
        draft_type_entry["state"] = tk.DISABLED

    match_format.trace("w",update_arch)

    revise_window.protocol("WM_DELETE_WINDOW", lambda : close_without_saving())
def revise_record_multi():
    if tree1.focus() == "":
        return
    height = 180
    width =  300
    revise_window = tk.Toplevel(window)
    revise_window.title("Revise Multiple Records")
    revise_window.iconbitmap(revise_window,"icon.ico")
    revise_window.minsize(width,height)
    revise_window.resizable(False,False)
    revise_window.attributes("-topmost",True)
    revise_window.grab_set()
    revise_window.focus()
    revise_window.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))
    
    top_frame = tk.Frame(revise_window)
    mid_frame = tk.LabelFrame(revise_window)
    bot_frame = tk.Frame(revise_window)
    top_frame.grid(row=0,column=0,sticky="")
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    revise_window.grid_columnconfigure(0,weight=1)
    revise_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(1,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(1,weight=1)

    def field_updated(*argv):
        global field
        field = field_val.get()

        if field == "P1 Deck":
            mid_frame.grid_rowconfigure(1,weight=1)
            p1_arch_label.grid(row=0,column=0,sticky="e")
            p1_arch_entry.grid(row=0,column=1,sticky="")
            p1_arch_entry.config(width=20)
            p1_subarch_label.grid(row=1,column=0,sticky="e")
            p1_subarch_entry.grid(row=1,column=1,sticky="")
            p1_subarch_entry.config(width=26)
            p2_arch_label.grid_forget()
            p2_arch_entry.grid_forget()
            p2_subarch_label.grid_forget()
            p2_subarch_entry.grid_forget()
            format_label.grid_forget()
            format_entry.grid_forget()
            lim_format_label.grid_forget()
            lim_format_entry.grid_forget()
            match_type_label.grid_forget()
            match_type_entry.grid_forget()
        elif field == "P2 Deck":
            mid_frame.grid_rowconfigure(1,weight=1)
            p1_arch_label.grid_forget()
            p1_arch_entry.grid_forget()
            p1_subarch_label.grid_forget()
            p1_subarch_entry.grid_forget()
            p2_arch_label.grid(row=0,column=0,sticky="e")
            p2_arch_entry.grid(row=0,column=1,sticky="")
            p2_arch_entry.config(width=20)
            p2_subarch_label.grid(row=1,column=0,sticky="e")
            p2_subarch_entry.grid(row=1,column=1,sticky="")
            p2_subarch_entry.config(width=26)
            format_label.grid_forget()
            format_entry.grid_forget()
            lim_format_label.grid_forget()
            lim_format_entry.grid_forget()
            match_type_label.grid_forget()
            match_type_entry.grid_forget()
        elif field == "Format":
            mid_frame.grid_rowconfigure(1,weight=1)
            p1_arch_label.grid_forget()
            p1_arch_entry.grid_forget()
            p1_subarch_label.grid_forget()
            p1_subarch_entry.grid_forget()
            p2_arch_label.grid_forget()
            p2_arch_entry.grid_forget()
            p2_subarch_label.grid_forget()
            p2_subarch_entry.grid_forget()
            format_label.grid(row=0,column=0,sticky="e")
            format_entry.grid(row=0,column=1,sticky="")
            format_entry.config(width=20)
            lim_format_label.grid(row=1,column=0,sticky="e")
            lim_format_entry.grid(row=1,column=1,sticky="")
            lim_format_entry.config(width=20)
            match_type_label.grid_forget()
            match_type_entry.grid_forget()
        elif field == "Match Type":
            mid_frame.grid_rowconfigure(1,weight=0)
            p1_arch_label.grid_forget()
            p1_arch_entry.grid_forget()
            p1_subarch_label.grid_forget()
            p1_subarch_entry.grid_forget()
            p2_arch_label.grid_forget()
            p2_arch_entry.grid_forget()
            p2_subarch_label.grid_forget()
            p2_subarch_entry.grid_forget()
            format_label.grid_forget()
            format_entry.grid_forget()
            lim_format_label.grid_forget()
            lim_format_entry.grid_forget()
            match_type_label.grid(row=0,column=0,sticky="e")
            match_type_entry.grid(row=0,column=1,sticky="")
            match_type_entry.config(width=20)

    def format_updated(*argv):
        if match_format.get() in INPUT_OPTIONS["Limited Formats"]:
            lim_format_entry["state"] = tk.NORMAL
            lim_format.set("NA")

            menu = lim_format_entry["menu"]
            menu.delete(0,"end")
            if match_format.get() == "Cube":
                for i in INPUT_OPTIONS["Cube Formats"]:
                    menu.add_command(label=i,command=lambda x=i: lim_format.set(x))
            elif match_format.get() == "Booster Draft":
                for i in INPUT_OPTIONS["Booster Draft Formats"]:
                    menu.add_command(label=i,command=lambda x=i: lim_format.set(x))
            elif match_format.get() == "Sealed Deck":
                for i in INPUT_OPTIONS["Sealed Formats"]:
                    menu.add_command(label=i,command=lambda x=i: lim_format.set(x))    
        else:
            lim_format.set("NA")
            lim_format_entry["state"] = tk.DISABLED

    def close_revise_window():
        global ask_to_save
        global selected
        ask_to_save = True
        for i in selected:
            values = list(tree1.item(i,"values"))
            for index,j in enumerate(itertools.chain(*[ALL_DATA[0],ALL_DATA_INVERTED[0]])):
                if values[0] == j[0]:
                    if field == "P1 Deck":
                        if values[modo.header("Matches").index("P1")] == j[modo.header("Matches").index("P1")]:
                            j[modo.header("Matches").index("P1_Arch")] = p1_arch_type.get()
                            j[modo.header("Matches").index("P1_Subarch")] = p1_subarch_entry.get().strip()
                        else:
                            j[modo.header("Matches").index("P2_Arch")] = p1_arch_type.get()
                            j[modo.header("Matches").index("P2_Subarch")] = p1_subarch_entry.get().strip()                   
                    elif field == "P2 Deck":
                        if values[modo.header("Matches").index("P2")] == j[modo.header("Matches").index("P2")]:
                            j[modo.header("Matches").index("P2_Arch")] = p2_arch_type.get()
                            j[modo.header("Matches").index("P2_Subarch")] = p2_subarch_entry.get().strip()
                        else:
                            j[modo.header("Matches").index("P1_Arch")] = p2_arch_type.get()
                            j[modo.header("Matches").index("P1_Subarch")] = p2_subarch_entry.get().strip()
                    elif field == "Format":
                        j[modo.header("Matches").index("Format")] = match_format.get()
                        j[modo.header("Matches").index("Limited_Format")] = lim_format.get()
                        if match_format.get() in INPUT_OPTIONS["Limited Formats"]:
                            j[modo.header("Matches").index("P1_Arch")] = "Limited"
                            j[modo.header("Matches").index("P2_Arch")] = "Limited"
                        elif match_format.get() in INPUT_OPTIONS["Constructed Formats"]:
                            if j[modo.header("Matches").index("P1_Arch")] == "Limited":
                                j[modo.header("Matches").index("P1_Arch")] = "NA"
                            if j[modo.header("Matches").index("P2_Arch")] == "Limited":
                                j[modo.header("Matches").index("P2_Arch")] = "NA"
                    elif field == "Match Type":
                        j[modo.header("Matches").index("Match_Type")] = match_type.get() 
        set_display("Matches",update_status=True,start_index=display_index,reset=False)
        revise_button["state"] = tk.NORMAL
        remove_button["state"] = tk.NORMAL

        sel_tuple = ()
        for i in tree1.get_children():
            if list(tree1.item(i,"values"))[0] in sel_matchid:
                sel_tuple += (i,)
        tree1.selection_set(sel_tuple)
        tree1.focus(list(sel_tuple)[0])
        selected = sel_tuple

    def close_without_saving():
        revise_window.grab_release()
        revise_window.destroy()       

    global selected
    selected = tree1.selection()
    sel_matchid = []
    format_index = modo.header("Matches").index("Format")
    sel_formats = {"constructed":False,"booster":False,"sealed":False}
    for i in selected:
        format_i = list(tree1.item(i,"values"))[format_index]
        sel_matchid.append(list(tree1.item(i,"values"))[0])
        if format_i in INPUT_OPTIONS["Constructed Formats"]:
            sel_formats["constructed"] = True
        elif (format_i == "Booster Draft") or (format_i == "Cube"):
            sel_formats["booster"] = True
        elif format_i == "Sealed Deck":
            sel_formats["sealed"] = True

    format_options = ["NA"] + INPUT_OPTIONS["Constructed Formats"] + INPUT_OPTIONS["Limited Formats"]
    match_format = tk.StringVar()
    match_format.set(format_options[0])

    limited_options = ["NA"]
    lim_format = tk.StringVar()
    lim_format.set(limited_options[0])

    match_options = ["NA"]
    if (sel_formats["constructed"] == True) and (sel_formats["booster"] == False) and (sel_formats["sealed"] == False):
        match_options += INPUT_OPTIONS["Constructed Match Types"]
    elif (sel_formats["constructed"] == False) and (sel_formats["booster"] == True) and (sel_formats["sealed"] == False):
        match_options += INPUT_OPTIONS["Booster Draft Match Types"]
    elif (sel_formats["constructed"] == False) and (sel_formats["booster"] == False) and (sel_formats["sealed"] == True):
        match_options += INPUT_OPTIONS["Sealed Match Types"]
    elif (sel_formats["constructed"] == False) and (sel_formats["booster"] == False) and (sel_formats["sealed"] == False):
        match_options += INPUT_OPTIONS["Constructed Match Types"] + INPUT_OPTIONS["Booster Draft Match Types"] + INPUT_OPTIONS["Sealed Match Types"]
    match_type = tk.StringVar()
    match_type.set(match_options[0])

    field_options = ["P1 Deck","P2 Deck","Format","Match Type"]
    field_val = tk.StringVar()
    if field == "":
        field_val.set(field_options[0])
    else:
        field_val.set(field)

    field_menu = tk.OptionMenu(top_frame,field_val,*field_options)
    field_menu.grid(row=0,column=0,pady=10,sticky="")
    field_menu.config(width=15)

    arch_options = ["NA"] + ["Limited"] + INPUT_OPTIONS["Archetypes"]

    p1_arch_type = tk.StringVar()
    p1_arch_type.set(arch_options[0])

    p2_arch_type = tk.StringVar()
    p2_arch_type.set(arch_options[0])

    p1_arch_label =      tk.Label(mid_frame,text="P1_Arch:")
    p1_arch_entry =      tk.OptionMenu(mid_frame,p1_arch_type,*arch_options)
    p1_subarch_label =   tk.Label(mid_frame,text="P1_Subarch:")
    p1_subarch_entry =   tk.Entry(mid_frame)
    p2_arch_label =      tk.Label(mid_frame,text="P2_Arch:")
    p2_arch_entry =      tk.OptionMenu(mid_frame,p2_arch_type,*arch_options)
    p2_subarch_label =   tk.Label(mid_frame,text="P2_Subarch:")
    p2_subarch_entry =   tk.Entry(mid_frame)
    format_label =       tk.Label(mid_frame,text="Format:")
    format_entry =       tk.OptionMenu(mid_frame,match_format,*format_options)
    lim_format_label =   tk.Label(mid_frame,text="Limited_Format:")
    lim_format_entry =   tk.OptionMenu(mid_frame,lim_format,*limited_options)
    match_type_label =   tk.Label(mid_frame,text="Match_Type:")
    match_type_entry =   tk.OptionMenu(mid_frame,match_type,*match_options)

    button3 = tk.Button(bot_frame,text="Apply to All",width=10,command=lambda : close_revise_window())
    button4 = tk.Button(bot_frame,text="Close",width=10,command=lambda : close_without_saving())

    lim_format_entry["state"] = tk.DISABLED
    button3.grid(row=0,column=0,padx=10,pady=10)
    button4.grid(row=0,column=1,padx=10,pady=10)

    p1_subarch_entry.insert(0,"NA")
    p2_subarch_entry.insert(0,"NA")

    field_val.trace("w",field_updated)
    match_format.trace("w",format_updated)

    field_updated()
    revise_window.protocol("WM_DELETE_WINDOW", lambda : close_without_saving())
def activate_revise(event):
    if tree1.identify_region(event.x,event.y) == "heading":
        return
    if data_loaded == False:
        return
    if (display == "Matches") or (display == "Drafts"):
        revise_button["state"] = tk.NORMAL
        remove_button["state"] = tk.NORMAL
def revise_method_select():
    if (len(tree1.selection()) > 1) & (display == "Matches"):
        revise_record_multi()
    elif (display == "Matches"):
        revise_record2()
    elif (display == "Drafts"):
        revise_record3()
def import_window():
    height = 200
    width =  350
    import_window = tk.Toplevel(window)
    import_window.title("Import Data")
    import_window.iconbitmap(import_window,"icon.ico")
    import_window.minsize(width,height)
    import_window.resizable(False,False)
    import_window.grab_set()
    import_window.focus()

    import_window.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def get_drafts_path():
        fp = filedialog.askdirectory()
        fp = os.path.normpath(fp) 
        if (fp is None) or (fp == "") or (fp == "."):
            label1.config(text="No Default DraftLogs Folder")
        else:
            label1.config(text=fp)
        if (label1["text"]  == "No Default DraftLogs Folder") & (label2["text"]  == "No Default GameLogs Folder"):
            button3["state"] = tk.DISABLED
        else:
            button3["state"] = tk.NORMAL

    def get_logs_path():
        fp = filedialog.askdirectory()
        fp = os.path.normpath(fp) 
        if (fp is None) or (fp == "") or (fp == "."):
            label2.config(text="No Default GameLogs Folder")
        else:
            label2.config(text=fp)
        if (label1["text"]  == "No Default DraftLogs Folder") & (label2["text"]  == "No Default GameLogs Folder"):
            button3["state"] = tk.DISABLED
        else:
            button3["state"] = tk.NORMAL

    def import_data(overwrite):
        global ALL_DATA
        global ALL_DATA_INVERTED
        global FILEPATH_LOGS
        global FILEPATH_DRAFTS
        global HERO

        FILEPATH_DRAFTS = label1["text"]
        FILEPATH_LOGS = label2["text"]

        if overwrite:
            h = HERO
            match_dict = user_inputs(type="Matches")
            game_dict = user_inputs(type="Games")
            clear_loaded()
            get_all_data(fp_logs=FILEPATH_LOGS_COPY,fp_drafts=FILEPATH_DRAFTS_COPY,copy=False)
            for i in ALL_DATA[0]:
                try:
                    i[modo.header("Matches").index("P1_Arch")] = match_dict[i[0]][0][i[modo.header("Matches").index("P1")]][0]
                    i[modo.header("Matches").index("P1_Subarch")] = match_dict[i[0]][0][i[modo.header("Matches").index("P1")]][1]
                    i[modo.header("Matches").index("P2_Arch")] = match_dict[i[0]][0][i[modo.header("Matches").index("P2")]][0]
                    i[modo.header("Matches").index("P2_Subarch")] = match_dict[i[0]][0][i[modo.header("Matches").index("P2")]][1]
                    i[modo.header("Matches").index("Format")] = match_dict[i[0]][1]
                    i[modo.header("Matches").index("Limited_Format")] = match_dict[i[0]][2]
                    i[modo.header("Matches").index("Match_Type")] = match_dict[i[0]][3]
                # Found new Match for which we don't have user inputs.
                except KeyError:
                    pass
            for i in ALL_DATA[1]:
                key = i[0] + "-" + str(i[modo.header("Games").index("Game_Num")])
                try:
                    if (i[modo.header("Games").index("P1")] == game_dict[key][0]):
                        i[modo.header("Games").index("Game_Winner")] = game_dict[key][2]
                # Found new Game for which we don't have user inputs.
                except KeyError:
                    pass
                # Delete RawData for Games that have a manually entered Game_Winner.
                if key in ALL_DATA[3]:
                    if i[modo.header("Games").index("Game_Winner")] != "NA":
                        ALL_DATA[3].pop(key)
            HERO = h
            if HERO != "":
                stats_button["state"] = tk.NORMAL
            modo.update_game_wins(ALL_DATA)
            ALL_DATA_INVERTED = modo.invert_join(ALL_DATA)
        else:
            get_all_data(fp_logs=FILEPATH_LOGS,fp_drafts=FILEPATH_DRAFTS,copy=True)
        clear_filter(update_status=False,reload_display=False)
        if data_loaded != False:
            data_menu.entryconfig("Set Default Hero",state=tk.NORMAL)
            file_menu.entryconfig("Save Data",state=tk.NORMAL)
            data_menu.entryconfig("Clear Loaded Data",state=tk.NORMAL)
            data_menu.entryconfig("Input Missing Match Data",state=tk.NORMAL)
            data_menu.entryconfig("Input Missing Game_Winner Data",state=tk.NORMAL)
            data_menu.entryconfig("Apply Best Guess for Deck Names",state=tk.NORMAL)
        #save_settings()
        set_display("Matches",update_status=False,start_index=0,reset=True)
        close_import_window()

    def close_import_window():
        import_window.grab_release()
        import_window.destroy()
    
    mid_frame = tk.LabelFrame(import_window,text="Import Folder Paths")
    bot_frame = tk.Frame(import_window)
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    import_window.grid_columnconfigure(0,weight=1)
    import_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)

    button1 = tk.Button(mid_frame,text="Get DraftLogs Folder",width=20,command=lambda : get_drafts_path())
    button2 = tk.Button(mid_frame,text="Get GameLogs Folder",width=20,command=lambda : get_logs_path())
    button3 = tk.Button(bot_frame,text="Scan for New Files",width=15,command=lambda : import_data(overwrite=False))
    button4 = tk.Button(bot_frame,text="Re-Import Copies",width=15,command=lambda : import_data(overwrite=True))
    button5 = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_import_window())
    if (FILEPATH_DRAFTS is None) or (FILEPATH_DRAFTS == "") or (FILEPATH_DRAFTS == "."):
        label1 = tk.Label(mid_frame,text="No Default DraftLogs Folder",wraplength=width,justify="left")
    else:
        label1 = tk.Label(mid_frame,text=FILEPATH_DRAFTS,wraplength=width,justify="left")
    if (FILEPATH_LOGS is None) or (FILEPATH_LOGS == "") or (FILEPATH_LOGS == "."):
        label2 = tk.Label(mid_frame,text="No Default GameLogs Folder",wraplength=width,justify="left")
    else:
        label2 = tk.Label(mid_frame,text=FILEPATH_LOGS,wraplength=width,justify="left")
    if (label1["text"]  == "No Default DraftLogs Folder") & (label2["text"]  == "No Default GameLogs Folder"):
        button3["state"] = tk.DISABLED
    else:
        button3["state"] = tk.NORMAL   

    label1.grid(row=0,column=0,pady=(10,5))
    button1.grid(row=1,column=0,pady=0)
    label2.grid(row=2,column=0,pady=5)
    button2.grid(row=3,column=0,pady=0)
    button3.grid(row=0,column=0,padx=5,pady=5)
    button4.grid(row=0,column=1,padx=5,pady=5)
    button5.grid(row=0,column=2,padx=5,pady=5)

    import_window.protocol("WM_DELETE_WINDOW", lambda : close_import_window())
def get_winners():
    global ALL_DATA
    global ALL_DATA_INVERTED
    global uaw
    global ask_to_save

    gw_index = modo.header("Games").index("Game_Winner")
    p1_index = modo.header("Games").index("P1")
    p2_index = modo.header("Games").index("P2")
    gn_index = modo.header("Games").index("Game_Num")
  
    exit = False
    raw_dict_new = {}
    for count,key in enumerate(ALL_DATA[3]):
        match_id = key.split("-")[0]
        game_num = key.split("-")[1]
        if exit == False:
            for i in ALL_DATA[1]:
                if (i[0] == match_id) & (str(i[gn_index]) == game_num) & (i[gw_index] == "NA"):
                    ask_for_winner(ALL_DATA[3][key],i[p1_index],i[p2_index],count+1,len(ALL_DATA[3]))
                    if uaw == "Exit.":
                        exit = True
                        raw_dict_new[key] = ALL_DATA[3][key]
                    elif uaw == "NA":
                        raw_dict_new[key] = ALL_DATA[3][key]
                    else:
                        i[gw_index] = uaw
                    break
        if exit:
            raw_dict_new[key] = ALL_DATA[3][key]

    if len(ALL_DATA[3]) > len(raw_dict_new):
        ALL_DATA[3] = raw_dict_new
        modo.update_game_wins(ALL_DATA)
        ALL_DATA_INVERTED = modo.invert_join(ALL_DATA)
        ask_to_save = True

    update_status_bar(status=f"{len(ALL_DATA[3])} Game(s) with missing Game_Winner.")
    set_display("Matches",update_status=False,start_index=0,reset=True)
def ask_for_winner(ga_list,p1,p2,n,total):
    # List of game actions (Strings)
    # String = P1
    # String = P2
    # Int = Count in cycle
    # Int = Total number of games missing Game_Winner

    def close_gw_window(winner):
        global uaw
        uaw = winner
        gw.grab_release()
        gw.destroy()
        
    gw = tk.Toplevel()
    gw.title("Select Game Winner - " + str(n) + "/" + str(total) + " Games")
    gw.iconbitmap(gw,"icon.ico")
    height = 400
    width = 700
    gw.minsize(width,height)
    gw.resizable(False,False)
    gw.attributes("-topmost",True)
    gw.grab_set()
    gw.focus_force()

    gw.geometry("+%d+%d" %
                (window.winfo_x()+(window.winfo_width()/2)-(width/2),
                 window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    message = "Winner could not be determined.\nPlease select Game Winner."
    all_ga =  ""
    for i in ga_list[-15:]:
        all_ga += i + "\n"
        
    top_frame = tk.Frame(gw)
    mid_frame = tk.LabelFrame(gw,text="Game Actions")
    bot_frame = tk.Frame(gw)

    top_frame.grid(row=0,column=0,sticky="")
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    gw.grid_columnconfigure(0,weight=1)
    gw.rowconfigure(1,minsize=0,weight=1)
    mid_frame.rowconfigure(0,minsize=0,weight=1)
    mid_frame.columnconfigure(0,minsize=0,weight=1)
    
    label1 = tk.Label(top_frame,text=message,anchor="center",wraplength=width)
    label2 = tk.Label(mid_frame,text=all_ga,anchor="center",wraplength=width,justify="left")

    button_skip = tk.Button(top_frame,text="Skip Game",width=10,command=lambda : close_gw_window("NA"))
    button_exit = tk.Button(top_frame,text="Exit",width=10,command=lambda : close_gw_window("Exit."))    
    button1 = tk.Button(bot_frame,text=p1,width=20,command=lambda : close_gw_window("P1"))
    button2 = tk.Button(bot_frame,text=p2,width=20,command=lambda : close_gw_window("P2"))

    button_skip.grid(row=0,column=0,padx=10,pady=10)
    label1.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
    button_exit.grid(row=0,column=2,padx=10,pady=10)    
    label2.grid(row=0,column=0,sticky="nsew",padx=5,pady=5)
    button1.grid(row=0,column=0,padx=10,pady=10)
    button2.grid(row=0,column=1,padx=10,pady=10)
    
    gw.protocol("WM_DELETE_WINDOW", lambda : close_gw_window("Exit."))    
    gw.wait_window()  
def get_stats():
    width =  1350
    height = 750
    stats_window = tk.Toplevel(window)
    stats_window.title("Statistics - Match Data: ")
    stats_window.iconbitmap(stats_window,"icon.ico")
    stats_window.minsize(width,height)
    stats_window.resizable(False,False)
    window.withdraw()
    stats_window.focus_force()

    stats_window.geometry("+%d+%d" %
        (window.winfo_x(),
         window.winfo_y()))

    top_frame = tk.Frame(stats_window)
    mid_frame = tk.Frame(stats_window)

    top_frame.grid(row=0,column=0,sticky="nsew")
    mid_frame.grid(row=1,column=0,sticky="nsew")

    mid_frame1 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame2 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame3 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame4 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame5 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame6 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame7 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame8 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)  
    mid_frame9 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame10 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)  

    mid_frame1.grid(row=0,column=0,sticky="nsew")
    mid_frame2.grid(row=0,column=1,sticky="nsew")
    mid_frame3.grid(row=1,column=0,sticky="nsew")
    mid_frame4.grid(row=1,column=1,sticky="nsew")

    stats_window.grid_columnconfigure(0,weight=1)
    stats_window.rowconfigure(1,minsize=0,weight=1)  
    top_frame.grid_columnconfigure(0,weight=1)
    top_frame.grid_columnconfigure(1,weight=0)
    top_frame.grid_columnconfigure(2,weight=0)
    top_frame.grid_columnconfigure(3,weight=0)
    top_frame.grid_columnconfigure(4,weight=0)
    top_frame.grid_columnconfigure(5,weight=0)
    top_frame.grid_columnconfigure(6,weight=1)
    top_frame.grid_columnconfigure(7,weight=0)
    top_frame.grid_columnconfigure(8,weight=0)
    mid_frame.grid_rowconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(1,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(1,weight=1)
    
    df0 = pd.DataFrame(ALL_DATA[0],columns=modo.header("Matches"))
    df1 = pd.DataFrame(ALL_DATA[1],columns=modo.header("Games"))
    df2 = pd.DataFrame(ALL_DATA[2],columns=modo.header("Plays"))
    df0_i = pd.DataFrame(ALL_DATA_INVERTED[0],columns=modo.header("Matches"))
    df1_i = pd.DataFrame(ALL_DATA_INVERTED[1],columns=modo.header("Games"))
    df2_i = pd.DataFrame(ALL_DATA_INVERTED[2],columns=modo.header("Plays"))
 
    def clear_frames():
        for widget in mid_frame1.winfo_children():
            widget.destroy()
        for widget in mid_frame2.winfo_children():
            widget.destroy()
        for widget in mid_frame3.winfo_children():
            widget.destroy()
        for widget in mid_frame4.winfo_children():
            widget.destroy()
        for widget in mid_frame5.winfo_children():
            widget.destroy()  
        for widget in mid_frame6.winfo_children():
            widget.destroy()
        for widget in mid_frame7.winfo_children():
            widget.destroy()  
        for widget in mid_frame8.winfo_children():
            widget.destroy()
        for widget in mid_frame9.winfo_children():
            widget.destroy()  
        for widget in mid_frame10.winfo_children():
            widget.destroy()  
        mid_frame1.grid_remove()
        mid_frame2.grid_remove()
        mid_frame3.grid_remove()
        mid_frame4.grid_remove()
        mid_frame5.grid_remove()
        mid_frame6.grid_remove()
        mid_frame7.grid_remove()
        mid_frame8.grid_remove()
        mid_frame9.grid_remove()
        mid_frame10.grid_remove()

    def defocus(event):
        # Clear Auto-Highlight in Combobox menu.
        menu_1.selection_clear()
        menu_2.selection_clear()
        menu_3.selection_clear()
        menu_4.selection_clear()
        menu_5.selection_clear()

    def match_history(hero,opp,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Card Data: " + hero)
        clear_frames()
        def tree1_skip(event):
            if tree1.identify_region(event.x,event.y) == "separator":
                return "break"
            if tree1.identify_region(event.x,event.y) == "heading":
                return "break"
        def tree1_unselect(event):
            if tree1.identify_region(event.x,event.y) != "cell":
                tree1.selection_set(())  
            if tree1.identify_region(event.x,event.y) == "separator":
                return "break"
            if tree1.identify_region(event.x,event.y) == "heading":
                return "break"
        def tree2_skip(event):
            if tree2.identify_region(event.x,event.y) == "separator":
                return "break"
            if tree2.identify_region(event.x,event.y) == "heading":
                return "break"
        def tree2_unselect(event):
            if tree2.identify_region(event.x,event.y) != "cell":
                tree2.selection_set(())  
            if tree2.identify_region(event.x,event.y) == "separator":
                return "break"
            if tree2.identify_region(event.x,event.y) == "heading":
                return "break"
        def tree1_setup(tree):
            tree.place(relheight=1, relwidth=1)
            tree.bind("<Button-1>",tree1_unselect)
            tree.bind("<Enter>",tree1_skip)
            tree.bind("<ButtonRelease-1>",tree1_unselect)
            tree.bind("<Motion>",tree1_skip)
        def tree2_setup(tree):
            tree.place(relheight=1, relwidth=1)
            tree.bind("<Button-1>",tree2_unselect)
            tree.bind("<Enter>",tree2_skip)
            tree.bind("<ButtonRelease-1>",tree2_unselect)
            tree.bind("<Motion>",tree2_skip)   

        tree1 = ttk.Treeview(mid_frame9,show="headings",padding=10)
        tree2 = ttk.Treeview(mid_frame10,show="headings",padding=10)
        tree1_setup(tree1)
        tree2_setup(tree2)
        mid_frame.grid_rowconfigure(0,weight=1)
        mid_frame.grid_rowconfigure(1,weight=0)
        mid_frame.grid_columnconfigure(0,weight=1)
        mid_frame.grid_columnconfigure(1,weight=1)
        mid_frame9.grid_rowconfigure(0,weight=1)
        mid_frame9.grid_columnconfigure(0,weight=1)
        mid_frame10.grid_rowconfigure(0,weight=1)
        mid_frame10.grid_columnconfigure(0,weight=1)
        mid_frame9.grid(row=0,column=0,sticky="nsew")
        mid_frame10.grid(row=0,column=1,sticky="nsew")

        mid_frame9.grid_propagate(0)
        mid_frame10.grid_propagate(0)

        df0_i_f        = df0_i[(df0_i.P1 == hero)]
        df0_i_f.sort_values(by="Date",ascending=False,inplace=True)
        tree1_dates    = df0_i_f.Date.tolist()
        tree1_decks    = df0_i_f.P1_Subarch.tolist()
        tree1_opp      = df0_i_f.P2.tolist()
        tree1_oppdecks = df0_i_f.P2_Subarch.tolist()
        tree1_wins     = df0_i_f.P1_Wins.tolist()
        tree1_losses   = df0_i_f.P2_Wins.tolist()
        tree1_result   = df0_i_f.Match_Winner.tolist()
        tree1_format   = df0_i_f.Format.tolist()
        tree1_lformat  = df0_i_f.Limited_Format.tolist()
        tree1_count = 30
        if len(tree1_dates) < 30:
            tree1_count = len(tree1_dates)
        for index,i in enumerate(tree1_format):
            if i in modo.formats(lim=True):
                tree1_format[index] += ": " + tree1_lformat[index]
        for index,i in enumerate(tree1_result):
            if i == "P1":
                tree1_result[index] = "Win "
            elif i == "P2":
                tree1_result[index] = "Loss "
            elif i == "NA":
                tree1_result[index] = "NA "
            tree1_result[index] += str(tree1_wins[index]) + "-" + str(tree1_losses[index])

        df0_i_f = df0_i_f[(df0_i_f.Format == mformat)]
        if lformat != "All Limited Formats":
            df0_i_f = df0_i_f[(df0_i_f.Limited_Format == lformat)]
        tree2_dates    = df0_i_f.Date.tolist()
        tree2_decks    = df0_i_f.P1_Subarch.tolist()
        tree2_opp      = df0_i_f.P2.tolist()
        tree2_oppdecks = df0_i_f.P2_Subarch.tolist()
        tree2_wins     = df0_i_f.P1_Wins.tolist()
        tree2_losses   = df0_i_f.P2_Wins.tolist()
        tree2_result   = df0_i_f.Match_Winner.tolist()
        tree2_format   = df0_i_f.Format.tolist()
        tree2_lformat  = df0_i_f.Limited_Format.tolist()
        tree2_count = 30
        if len(tree2_dates) < 30:
            tree2_count = len(tree2_dates)
        for index,i in enumerate(tree2_format):
            if i in modo.formats(lim=True):
                tree2_format[index] += ": " + tree2_lformat[index]
        for index,i in enumerate(tree2_result):
            if i == "P1":
                tree2_result[index] = "Win "
            elif i == "P2":
                tree2_result[index] = "Loss "
            elif i == "NA":
                tree2_result[index] = "NA "
            tree2_result[index] += str(tree2_wins[index]) + "-" + str(tree2_losses[index])

        mid_frame9["text"] = "Match History: " + hero
        tree1.tag_configure("win",background="#a3ffb1")
        tree1.tag_configure("lose",background="#ffa3a3")
        tree1.delete(*tree1.get_children())
        tree1["column"] = ["Date","Opponent","Deck","Opp. Deck","Match Result","Format"]
        for i in tree1["column"]:
            tree1.column(i,minwidth=20,stretch=True,width=20,anchor="center")
            tree1.heading(i,text=i)
        tagged = False
        for i in range(tree1_count):
            if "Win" in tree1_result[i]:
                tree1.insert("","end",values=[tree1_dates[i],
                                              tree1_opp[i],
                                              tree1_decks[i],
                                              tree1_oppdecks[i],
                                              tree1_result[i],
                                              tree1_format[i]],tags=("win",))
            else:
                tree1.insert("","end",values=[tree1_dates[i],
                                              tree1_opp[i],
                                              tree1_decks[i],
                                              tree1_oppdecks[i],
                                              tree1_result[i],
                                              tree1_format[i]],tags=("lose",))

        if mformat == "All Formats":
            mid_frame10["text"] = "Choose a Format"
        elif (mformat in modo.formats(lim=True)) & (lformat != "All Limited Formats"):
            mid_frame10["text"] = "Match History: " + hero + " - " + mformat + ", " + lformat
        else:
            mid_frame10["text"] = "Match History: " + hero + " - " + mformat
        tree2.tag_configure("win",background="#a3ffb1")
        tree2.tag_configure("lose",background="#ffa3a3")
        tree2.delete(*tree2.get_children())
        tree2["column"] = ["Date","Opponent","Deck","Opp. Deck","Match Result","Format"]
        for i in tree2["column"]:
            tree2.column(i,minwidth=20,stretch=True,width=20,anchor="center")
            tree2.heading(i,text=i)
        tagged = False
        for i in range(tree2_count):
            if "Win" in tree2_result[i]:
                tree2.insert("","end",values=[tree2_dates[i],
                                              tree2_opp[i],
                                              tree2_decks[i],
                                              tree2_oppdecks[i],
                                              tree2_result[i],
                                              tree2_format[i]],tags=("win",))
            else:
                tree2.insert("","end",values=[tree2_dates[i],
                                              tree2_opp[i],
                                              tree2_decks[i],
                                              tree2_oppdecks[i],
                                              tree2_result[i],
                                              tree2_format[i]],tags=("lose",))

    def match_stats(hero,opp,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Match Data: " + hero)
        clear_frames()
        def tree_skip(event):
            if tree1.identify_region(event.x,event.y) == "separator":
                return "break"
            if tree1.identify_region(event.x,event.y) == "heading":
                return "break"
        def tree_setup(*argv):
            for i in argv:
                i.place(relheight=1, relwidth=1)
                i.bind("<Button-1>",tree_skip)
                i.bind("<Enter>",tree_skip)
                i.bind("<ButtonRelease-1>",tree_skip)
                i.bind("<Motion>",tree_skip)          
        tree1 = ttk.Treeview(mid_frame1,show="headings",selectmode="none",padding=10)
        tree2 = ttk.Treeview(mid_frame2,show="headings",selectmode="none",padding=10)
        tree3 = ttk.Treeview(mid_frame3,show="headings",selectmode="none",padding=10)       
        tree4 = ttk.Treeview(mid_frame4,show="headings",selectmode="none",padding=10)
        tree_setup(tree1,tree2,tree3,tree4)
        mid_frame.grid_rowconfigure(0,weight=1)
        mid_frame.grid_rowconfigure(1,weight=1)
        mid_frame.grid_columnconfigure(0,weight=1)
        mid_frame.grid_columnconfigure(1,weight=1)
        mid_frame1.grid(row=0,column=0,sticky="nsew")
        mid_frame2.grid(row=0,column=1,sticky="nsew")
        mid_frame3.grid(row=1,column=0,sticky="nsew")
        mid_frame4.grid(row=1,column=1,sticky="nsew")

        df0_i_f = df0_i[(df0_i.P1 == hero)]
        hero_n =  df0_i_f.shape[0] # Matches played by hero
        df0_i_f = df0_i_f[(df0_i_f.Date > date_range[0]) & (df0_i_f.Date < date_range[1])]

        if mformat in INPUT_OPTIONS["Limited Formats"]:
            formats_played = df0_i_f[(df0_i_f.Format == mformat)].Limited_Format.value_counts().keys().tolist()
        elif mformat != "All Formats":
            formats_played = [mformat]
        else:
            formats_played = df0_i_f.Format.value_counts().keys().tolist()
        format_wins =    [df0_i_f[(df0_i_f.Match_Winner == "P1")].shape[0]] #adding overall in L[0]
        format_losses =  [df0_i_f[(df0_i_f.Match_Winner == "P2")].shape[0]] #adding overall in L[0]
        if (format_wins[0] + format_losses[0]) == 0:
            format_wr = ["0.0%"]
        else:
            format_wr = [to_percent(format_wins[0]/(format_wins[0]+format_losses[0]),1) + "%"]    #adding overall in L[0]

        for i in formats_played:
            if mformat in INPUT_OPTIONS["Limited Formats"]:
                wins  =  df0_i_f[(df0_i_f.Limited_Format == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
                losses = df0_i_f[(df0_i_f.Limited_Format == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            else:
                wins  =  df0_i_f[(df0_i_f.Format == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
                losses = df0_i_f[(df0_i_f.Format == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            format_wins.append(str(wins))
            format_losses.append(str(losses))
            format_wr.append(to_percent(wins/(wins+losses),1) + "%")
        formats_played.insert(0,"Match Format")

        formats_played.extend(["","Match Type"])
        format_wins.extend(["",format_wins[0]])
        format_losses.extend(["",format_losses[0]])
        format_wr.extend(["",format_wr[0]])

        if mformat != "All Formats":
            matchtypes_played = df0_i_f[(df0_i_f.Format == mformat)].Match_Type.value_counts().keys().tolist()
        else:
            matchtypes_played = df0_i_f.Match_Type.value_counts().keys().tolist()
        for i in matchtypes_played:
            if mformat != "All Formats":
                mt_wins  =  df0_i_f[(df0_i_f.Format == mformat) & (df0_i_f.Match_Type == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
                mt_losses = df0_i_f[(df0_i_f.Format == mformat) & (df0_i_f.Match_Type == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            else:
                mt_wins  =  df0_i_f[(df0_i_f.Match_Type == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
                mt_losses = df0_i_f[(df0_i_f.Match_Type == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            formats_played.append(i)
            format_wins.append(mt_wins)
            format_losses.append(mt_losses)
            format_wr.append(to_percent(mt_wins/(mt_wins+mt_losses),1) + "%")

        roll_1_mean = round(df0["P1_Roll"].mean(),2)
        roll_2_mean = round(df0["P2_Roll"].mean(),2)
        p1_roll_wr =  to_percent((df0[df0.Roll_Winner == "P1"].shape[0])/df0.shape[0],1)
        p2_roll_wr =  to_percent((df0[df0.Roll_Winner == "P2"].shape[0])/df0.shape[0],1)
        rolls_won =   df0_i[(df0_i.P1 == hero) & (df0_i.Roll_Winner == "P1")].shape[0] 
        roll_labels = ["Roll 1 Mean","Roll 2 Mean","Roll 1 Win%","Roll 2 Win%","","Hero Roll Win%"]
        roll_values = [roll_1_mean,roll_2_mean,p1_roll_wr+"%",p2_roll_wr+"%","",to_percent(rolls_won/hero_n,1)+"%"]

        if mformat != "All Formats":
            df0_i_f = df0_i_f[(df0_i_f.Format == mformat)]
        if lformat != "All Limited Formats":
            df0_i_f = df0_i_f[(df0_i_f.Limited_Format == lformat)]
        if deck != "All Decks":
            df0_i_f = df0_i_f[(df0_i_f.P1_Subarch == deck)]
        if opp_deck != "All Opp. Decks":
            df0_i_f = df0_i_f[(df0_i_f.P2_Subarch == opp_deck)]

        filtered_n =        df0_i_f.shape[0] 
        meta_deck_wr =      []
        meta_decks =        df0_i_f.P2_Subarch.value_counts().keys().tolist()
        meta_deck_counts =  df0_i_f.P2_Subarch.value_counts().tolist()
        for i in meta_decks:
            wins  = df0_i_f[(df0_i_f.P2_Subarch == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
            losses= df0_i_f[(df0_i_f.P2_Subarch == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            total = df0_i_f[(df0_i_f.P2_Subarch == i)].shape[0]
            if total == 0:
                meta_deck_wr.append([wins,losses,"0"])
            else:
                meta_deck_wr.append([wins,losses,to_percent(wins/total,1)])
                
        hero_deck_wr = []
        hero_decks =        df0_i_f.P1_Subarch.value_counts().keys().tolist()
        hero_deck_counts =  df0_i_f.P1_Subarch.value_counts().tolist()
        for i in hero_decks:
            wins  = df0_i_f[(df0_i_f.P1_Subarch == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
            losses= df0_i_f[(df0_i_f.P1_Subarch == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            total = df0_i_f[(df0_i_f.P1_Subarch == i)].shape[0]
            if total == 0:
                hero_deck_wr.append([wins,losses,"0"])
            else:
                hero_deck_wr.append([wins,losses,to_percent(wins/total,1)])        

        mid_frame1["text"] = "Die Rolls"
        tree1.tag_configure("colored",background="#cccccc")
        tree1.delete(*tree1.get_children())
        tree1["column"] = ["",""]
        for i in tree1["column"]:
            tree1.column(i,minwidth=20,stretch=True,width=20)
            tree1.heading(i,text=i)
        tree1.column(1,anchor="center")
        tagged = False
        for i in range(len(roll_values)):
            tagged = not tagged
            if tagged == True:
                tree1.insert("","end",values=[roll_labels[i],roll_values[i]],tags=("colored",))
            else:
                tree1.insert("","end",values=[roll_labels[i],roll_values[i]])

        mid_frame2["text"] = "Overall Performance: " + mformat
        tree2.tag_configure("colored",background="#cccccc")
        tree2.delete(*tree2.get_children())
        tree2["column"] = ["Description","Wins","Losses","Match Win%"]
        for i in tree2["column"]:
            tree2.column(i,minwidth=20,stretch=True,width=20)
            tree2.heading(i,text=i)
        tree2.column("Wins",anchor="center")
        tree2.column("Losses",anchor="center")
        tree2.column("Match Win%",anchor="center")
        for i in range(len(formats_played)):
            if (formats_played[i] == "Match Format") or (formats_played[i] == "Match Type"):
                tagged = True
            else:
                tagged = False
            if tagged == True:
                tree2.insert("","end",values=[formats_played[i],
                                              format_wins[i],
                                              format_losses[i],
                                              format_wr[i]],tags=("colored",))
            else:
                tree2.insert("","end",values=[formats_played[i],
                                              format_wins[i],
                                              format_losses[i],
                                              format_wr[i]])

        if (deck != "All Decks") or (opp_deck != "All Opp. Decks"):
            if lformat != "All Limited Formats":
                mid_frame3["text"] = mformat + " - " + lformat + ": " + deck + " vs. " + opp_deck
            else:
                if mformat in INPUT_OPTIONS["Constructed Formats"]:
                    mid_frame3["text"] = mformat + ": " + deck + " vs. " + opp_deck               
        elif lformat != "All Limited Formats":
            mid_frame3["text"] = "Decks Played: " + mformat + " - " + lformat
        else:
            mid_frame3["text"] = "Decks Played: " + mformat
        tree3.tag_configure("colored",background="#cccccc")
        tree3.delete(*tree3.get_children())
        tree3["column"] = ["Decks","Share","Wins","Losses","Win%"]
        for i in tree3["column"]:
            tree3.column(i,minwidth=20,stretch=True,width=20)
            tree3.heading(i,text=i)
        for i in range(1,len(tree3["column"])):
            tree3.column(i,anchor="center")
        tagged = False
        if len(hero_decks) == 0:
            tree3.insert("","end",values=["No Games Found."],tags=('colored',))
        for i in range(10):
            if i >= len(hero_decks):
                break
            tagged = not tagged
            if tagged == True:
                tree3.insert("","end",values=[hero_decks[i],
                                              (str(hero_deck_counts[i])+" - ("+to_percent(hero_deck_counts[i]/filtered_n,0)+"%)"),
                                              hero_deck_wr[i][0],
                                              hero_deck_wr[i][1],
                                              (hero_deck_wr[i][2]+"%")],tags=("colored",))
            else:
                tree3.insert("","end",values=[hero_decks[i],
                                              (str(hero_deck_counts[i])+" - ("+to_percent(hero_deck_counts[i]/filtered_n,0)+"%)"),
                                              hero_deck_wr[i][0],
                                              hero_deck_wr[i][1],
                                              (hero_deck_wr[i][2]+"%")])
        
        if (deck != "All Decks") or (opp_deck != "All Opp. Decks"):
            if lformat != "All Limited Formats":
                mid_frame4["text"] = mformat + " - " + lformat + ": " + deck + " vs. " + opp_deck
            else:
                if mformat in INPUT_OPTIONS["Constructed Formats"]:
                    mid_frame4["text"] = mformat + ": " + deck + " vs. " + opp_deck  
        elif lformat != "All Limited Formats":
            mid_frame4["text"] = "Observed Metagame: " + mformat + " - " + lformat
        else:
            mid_frame4["text"] = "Observed Metagame: " + mformat
        tree4.tag_configure("colored",background="#cccccc")
        tree4.delete(*tree4.get_children())
        tree4["column"] = ["Decks","Share","Wins","Losses","Win% Against"]
        for i in tree4["column"]:
            tree4.column(i,minwidth=20,stretch=True,width=20)
            tree4.heading(i,text=i)
        for i in range(1,len(tree4["column"])):
            tree4.column(i,anchor="center")
        tagged = False
        if len(meta_decks) == 0:
            tree4.insert("","end",values=["No Games Found."],tags=('colored',))
        for i in range(10):
            if i >= len(meta_decks):
                break
            tagged = not tagged
            if tagged == True:
                tree4.insert("","end",values=[meta_decks[i],
                                              (str(meta_deck_counts[i])+" - ("+to_percent(meta_deck_counts[i]/filtered_n,0)+"%)"),
                                              meta_deck_wr[i][0],
                                              meta_deck_wr[i][1],
                                              (meta_deck_wr[i][2]+"%")],tags=("colored",))
            else:
                tree4.insert("","end",values=[meta_decks[i],
                                              (str(meta_deck_counts[i])+" - ("+to_percent(meta_deck_counts[i]/filtered_n,0)+"%)"),
                                              meta_deck_wr[i][0],
                                              meta_deck_wr[i][1],
                                              (meta_deck_wr[i][2]+"%")])

    def game_stats(hero,opp,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Game Data: " + hero)
        clear_frames()
        def tree_skip(event):
            if tree1.identify_region(event.x,event.y) == "separator":
                return "break"
            if tree1.identify_region(event.x,event.y) == "heading":
                return "break"
        def tree_setup(*argv):
            for i in argv:
                i.place(relheight=1, relwidth=1)
                i.bind("<Button-1>",tree_skip)
                i.bind("<Enter>",tree_skip)
                i.bind("<ButtonRelease-1>",tree_skip)
                i.bind("<Motion>",tree_skip)            
        tree1 = ttk.Treeview(mid_frame1,show="headings",selectmode="none",padding=10)
        tree2 = ttk.Treeview(mid_frame2,show="headings",selectmode="none",padding=10)
        tree3 = ttk.Treeview(mid_frame3,show="headings",selectmode="none",padding=10)
        tree4 = ttk.Treeview(mid_frame4,show="headings",selectmode="none",padding=10)
        tree_setup(tree1,tree2,tree3,tree4)
        mid_frame.grid_rowconfigure(0,weight=1)
        mid_frame.grid_rowconfigure(1,weight=1)
        mid_frame.grid_columnconfigure(0,weight=1)
        mid_frame.grid_columnconfigure(1,weight=1)
        mid_frame1.grid(row=0,column=0,sticky="nsew")
        mid_frame2.grid(row=0,column=1,sticky="nsew")
        mid_frame3.grid(row=1,column=0,sticky="nsew")
        mid_frame4.grid(row=1,column=1,sticky="nsew")

        df1_i_merge     = pd.merge(df0_i,
                                   df1_i,
                                   how="inner",
                                   left_on=["Match_ID","P1","P2"],
                                   right_on=["Match_ID","P1","P2"])
        if mformat != "All Formats":
            df1_i_merge = df1_i_merge[(df1_i_merge.Format == mformat)]
        if lformat != "All Limited Formats":
            df1_i_merge = df1_i_merge[(df1_i_merge.Limited_Format == lformat)]
        df1_i_merge     = df1_i_merge[(df1_i_merge.Date > date_range[0]) & (df1_i_merge.Date < date_range[1])]
        df1_i_hero      = df1_i_merge[df1_i_merge.P1 == hero]
        df1_i_hero_p    = df1_i_hero[df1_i_hero.On_Play == "P1"]
        df1_i_hero_d    = df1_i_hero[df1_i_hero.On_Play == "P2"]
        
        df1_i_hero_g1   = df1_i_hero[df1_i_hero.Game_Num == 1]
        df1_i_hero_g1_p = df1_i_hero_g1[df1_i_hero_g1.On_Play == "P1"]
        df1_i_hero_g1_d = df1_i_hero_g1[df1_i_hero_g1.On_Play == "P2"]
        
        df1_i_hero_g2   = df1_i_hero[df1_i_hero.Game_Num == 2]
        df1_i_hero_g2_p = df1_i_hero_g2[df1_i_hero_g2.On_Play == "P1"]
        df1_i_hero_g2_d = df1_i_hero_g2[df1_i_hero_g2.On_Play == "P2"]
        
        df1_i_hero_g3   = df1_i_hero[df1_i_hero.Game_Num == 3]
        df1_i_hero_g3_p = df1_i_hero_g3[df1_i_hero_g3.On_Play == "P1"]
        df1_i_hero_g3_d = df1_i_hero_g3[df1_i_hero_g3.On_Play == "P2"]

        df_list = [df1_i_hero,
                   df1_i_hero_p,
                   df1_i_hero_d,
                   df1_i_hero_g1,
                   df1_i_hero_g1_p,
                   df1_i_hero_g1_d,
                   df1_i_hero_g2,
                   df1_i_hero_g2_p,
                   df1_i_hero_g2_d,
                   df1_i_hero_g3,
                   df1_i_hero_g3_p,
                   df1_i_hero_g3_d]

        frame_labels = ["Game Data: " + mformat,
                        "Matchup Data",
                        "Choose a Deck",
                        "Choose an Opposing Deck"]
        if lformat != "All Limited Formats":
            frame_labels[0] += " - " + lformat
        tree1data =    []
        for i in df_list:
            total_n = i.shape[0]
            wins =    i[(i.Game_Winner == "P1")].shape[0]
            losses =  i[(i.Game_Winner == "P2")].shape[0]
            if (wins+losses) == 0:
                win_rate = "0.0"
            else:
                win_rate = to_percent(wins/(wins+losses),1)
            if total_n == 0:
                hero_mull_rate =0.0
                opp_mull_rate = 0.0
                turn_rate =     0.0
            else:
                hero_mull_rate =round((i.P1_Mulls.sum()/total_n),2)
                opp_mull_rate = round((i.P2_Mulls.sum()/total_n),2)
                turn_rate =     round((i.Turns.sum()/total_n),2)     
            tree1data.append([wins,
                              losses,
                              win_rate,
                              hero_mull_rate,
                              opp_mull_rate,
                              turn_rate])
        
        tree2data = []
        if (deck != "All Decks") & (opp_deck != "All Opp. Decks"):
            if lformat != "All Limited Formats":
                frame_labels[1] = ("Matchup Data: " + mformat + " - " + lformat + ", " + deck + " vs. " + opp_deck)
            else:
                frame_labels[1] = ("Matchup Data: " + mformat + ", " + deck + " vs. " + opp_deck)
            for i in df_list:
                total_n = i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck)].shape[0]
                wins =    i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck) & (i.Game_Winner == "P1")].shape[0]
                losses =  i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck) & (i.Game_Winner == "P2")].shape[0]
                if (wins+losses) == 0:
                    win_rate = "0.0"
                else:
                    win_rate = to_percent(wins/(wins+losses),1)
                if total_n == 0:
                    hero_mull_rate =0.0
                    opp_mull_rate = 0.0
                    turn_rate =     0.0
                else:
                    hero_mull_rate =round((i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck)].P1_Mulls.sum()/total_n),2)
                    opp_mull_rate = round((i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck)].P2_Mulls.sum()/total_n),2)
                    turn_rate =     round((i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck)].Turns.sum()/total_n),2)     
                tree2data.append([wins,
                                  losses,
                                  win_rate,
                                  hero_mull_rate,
                                  opp_mull_rate,
                                  turn_rate])
        
        tree3data = []
        if deck != "All Decks":
            if lformat != "All Limited Formats":
                frame_labels[2] = (mformat + " - " + lformat + ": " + deck + " vs. All Opp. Decks")
            else:
                frame_labels[2] = (mformat + ": " + deck + " vs. All Opp. Decks")
            for i in df_list:
                total_n = i[(i.P1_Subarch == deck)].shape[0]
                wins =    i[(i.P1_Subarch == deck) & (i.Game_Winner == "P1")].shape[0]
                losses =  i[(i.P1_Subarch == deck) & (i.Game_Winner == "P2")].shape[0]
                if (wins+losses) == 0:
                    win_rate = "0.0"
                else:
                    win_rate = to_percent(wins/(wins+losses),1)
                if total_n == 0:
                    hero_mull_rate =0.0
                    opp_mull_rate = 0.0
                    turn_rate =     0.0
                else:
                    hero_mull_rate =round((i[(i.P1_Subarch == deck)].P1_Mulls.sum()/total_n),2)
                    opp_mull_rate = round((i[(i.P1_Subarch == deck)].P2_Mulls.sum()/total_n),2)
                    turn_rate =     round((i[(i.P1_Subarch == deck)].Turns.sum()/total_n),2)     
                tree3data.append([wins,
                                  losses,
                                  win_rate,
                                  hero_mull_rate,
                                  opp_mull_rate,
                                  turn_rate])
            
        tree4data = []
        if opp_deck != "All Opp. Decks":
            if lformat != "All Limited Formats":
                frame_labels[3] = (mformat + " - " + lformat + ": All Decks vs. " + opp_deck)
            else:
                frame_labels[3] = (mformat + ": All Decks vs. " + opp_deck)
            for i in df_list:
                total_n = i[(i.P2_Subarch == opp_deck)].shape[0]
                wins =    i[(i.P2_Subarch == opp_deck) & (i.Game_Winner == "P1")].shape[0]
                losses =  i[(i.P2_Subarch == opp_deck) & (i.Game_Winner == "P2")].shape[0]
                if (wins+losses) == 0:
                    win_rate = "0.0"
                else:
                    win_rate = to_percent(wins/(wins+losses),1)
                if total_n == 0:
                    hero_mull_rate =0.0
                    opp_mull_rate = 0.0
                    turn_rate =     0.0
                else:
                    hero_mull_rate =round((i[(i.P2_Subarch == opp_deck)].P1_Mulls.sum()/total_n),2)
                    opp_mull_rate = round((i[(i.P2_Subarch == opp_deck)].P2_Mulls.sum()/total_n),2)
                    turn_rate =     round((i[(i.P2_Subarch == opp_deck)].Turns.sum()/total_n),2)     
                tree4data.append([wins,
                                  losses,
                                  win_rate,
                                  hero_mull_rate,
                                  opp_mull_rate,
                                  turn_rate])
        
        tree_data =     [tree1data,tree2data,tree3data,tree4data]
        frames =        [mid_frame1,mid_frame2,mid_frame3,mid_frame4]
        for index,tree in enumerate([tree1,tree2,tree3,tree4]):
            frames[index]["text"] = frame_labels[index]
            tree.tag_configure("colored",background="#cccccc")
            if tree_data[index]:
                tree.delete(*tree.get_children())
                tree["column"] = ["","","Wins","Losses","Win%","Mulls/G","Opp Mulls/G","Turns/G"]
                for i in tree["column"]:
                    tree.column(i,minwidth=25,stretch=True,width=25)
                    tree.heading(i,text=i)
                tree.column(0,minwidth=110,stretch=False,width=110)
                for i in range(2,len(tree["column"])):
                    tree.column(i,anchor="center")
                index_list = [["All Games","Overall"],["","Play"],["","Draw"],
                              ["Game 1","Overall"],["","Play"],["","Draw"],
                              ["Game 2","Overall"],["","Play"],["","Draw"],
                              ["Game 3","Overall"],["","Play"],["","Draw"]]
                tagged = True
                count = 0
                for i in range(len(index_list)):
                    if tagged == True:
                        tree.insert("","end",values=index_list[i]+tree_data[index][i],tags=("colored",))
                    else:
                        tree.insert("","end",values=index_list[i]+tree_data[index][i])
                    count += 1
                    if count == 3:
                        tagged = not tagged
                        count = 0

    def play_stats(hero,opp,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Play Data: " + hero)
        clear_frames()
        def tree_skip(event):
            if tree1.identify_region(event.x,event.y) == "separator":
                return "break"
            if tree1.identify_region(event.x,event.y) == "heading":
                return "break"
        def tree_setup(*argv):
            for i in argv:
                i.place(relheight=1, relwidth=1)
                i.bind("<Button-1>",tree_skip)
                i.bind("<Enter>",tree_skip)
                i.bind("<ButtonRelease-1>",tree_skip)
                i.bind("<Motion>",tree_skip)            
        tree1 = ttk.Treeview(mid_frame1,show="headings",selectmode="none",padding=10)
        tree2 = ttk.Treeview(mid_frame2,show="headings",selectmode="none",padding=10)
        tree3 = ttk.Treeview(mid_frame3,show="headings",selectmode="none",padding=10)       
        tree4 = ttk.Treeview(mid_frame4,show="headings",selectmode="none",padding=10)
        tree_setup(tree1,tree2,tree3,tree4)
        mid_frame.grid_rowconfigure(0,weight=1)
        mid_frame.grid_rowconfigure(1,weight=1)
        mid_frame.grid_columnconfigure(0,weight=1)
        mid_frame.grid_columnconfigure(1,weight=1)
        mid_frame1.grid(row=0,column=0,sticky="nsew")
        mid_frame2.grid(row=0,column=1,sticky="nsew")
        mid_frame3.grid(row=1,column=0,sticky="nsew")
        mid_frame4.grid(row=1,column=1,sticky="nsew")

        df1_i_merge =   pd.merge(df0_i,
                                 df1_i,
                                 how="inner",
                                 left_on=["Match_ID","P1","P2"],
                                 right_on=["Match_ID","P1","P2"])       
        df2_merge   =   pd.merge(df0,
                                 df2,
                                 how="inner",
                                 left_on=["Match_ID"],
                                 right_on=["Match_ID"])
        df1_i_merge   = df1_i_merge[(df1_i_merge.Date > date_range[0]) & (df1_i_merge.Date < date_range[1])]
        df2_merge     = df2_merge[(df2_merge.Date > date_range[0]) & (df2_merge.Date < date_range[1])]
        if mformat != "All Formats":
            df1_i_merge = df1_i_merge[(df1_i_merge.Format == mformat)]
            df2_merge = df2_merge[(df2_merge.Format == mformat)]
        if lformat != "All Limited Formats":
            df1_i_merge = df1_i_merge[(df1_i_merge.Limited_Format == lformat)]
            df2_merge = df2_merge[(df2_merge.Limited_Format == lformat)]
        df2_hero      = df2_merge[(df2_merge.Casting_Player == hero)]
        
        formats_played = df2_hero.Format.value_counts().keys().tolist()
        formats =    []
        index_list = []
        for i in formats_played:
            hero_n_format = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.Format == i)].shape[0]
            formats.append(i)
            formats.append(str(hero_n_format) + " Games")
            index_list.append("Total")
            index_list.append("Per Game")
        tree1_data = []
        for i in formats_played:
            hero_n_format = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.Format == i)].shape[0]
            play_count =    df2_hero[(df2_hero.Format == i) & (df2_hero.Action == "Land Drop")].shape[0]
            cast_count =    df2_hero[(df2_hero.Format == i) & (df2_hero.Action == "Casts")].shape[0]
            act_count =     df2_hero[(df2_hero.Format == i) & (df2_hero.Action == "Activated Ability")].shape[0]
            trig_count =    df2_hero[(df2_hero.Format == i) & (df2_hero.Action == "Triggers")].shape[0]
            attack_count =  df2_hero[(df2_hero.Format == i) & (df2_hero.Action == "Attacks")].Attackers.sum()
            draw_count =    df2_hero[(df2_hero.Format == i) & (df2_hero.Action == "Draws")].Cards_Drawn.sum()
            tree1_data.append([play_count,
                               cast_count,
                               act_count,
                               trig_count,
                               attack_count,
                               draw_count])
            tree1_data.append([round(play_count/hero_n_format,1),
                               round(cast_count/hero_n_format,1),
                               round(act_count/hero_n_format,1),
                               round(trig_count/hero_n_format,1),
                               round(attack_count/hero_n_format,1),
                               round(draw_count/hero_n_format,1)])

        df_tree2 = df2_hero
        turn_list = df_tree2.Turn_Num.value_counts().keys().tolist()
        turn_list = sorted(turn_list)
        tree2_data =  []
        index_list2 = []
        for i in turn_list:
            play_count =    df_tree2[(df_tree2.Turn_Num == i) & (df_tree2.Action == "Land Drop")].shape[0]
            cast_count =    df_tree2[(df_tree2.Turn_Num == i) & (df_tree2.Action == "Casts")].shape[0]
            act_count =     df_tree2[(df_tree2.Turn_Num == i) & (df_tree2.Action == "Activated Ability")].shape[0]
            trig_count =    df_tree2[(df_tree2.Turn_Num == i) & (df_tree2.Action == "Triggers")].shape[0]
            attack_count =  df_tree2[(df_tree2.Turn_Num == i) & (df_tree2.Action == "Attacks")].Attackers.sum()
            draw_count =    df_tree2[(df_tree2.Turn_Num == i) & (df_tree2.Action == "Draws")].Cards_Drawn.sum()
            total_actions = play_count + cast_count + act_count + trig_count + attack_count
            tree2_data.append([play_count,
                               cast_count,
                               act_count,
                               trig_count,
                               attack_count,
                               draw_count,
                               total_actions])
            index_list2.append(["Turn "+str(i)])

        df2_i_merge = pd.merge(df0_i,
                               df2,
                               how="inner",
                               left_on=["Match_ID"],
                               right_on=["Match_ID"])
        df2_i_merge =  df2_i_merge[(df2_i_merge.Date > date_range[0]) & (df2_i_merge.Date < date_range[1])]
        if mformat != "All Formats":
            df2_i_merge = df2_i_merge[(df2_i_merge.Format == mformat)]
        if lformat != "All Limited Formats":
            df2_i_merge = df2_i_merge[(df2_i_merge.Limited_Format == lformat)]
        df2_i_m_hero = df2_i_merge[(df2_i_merge.P1 == hero)]
   
        decks3 =        []
        index_list3 =   []
        tree3_data =    []
        df_tree3 = df2_i_m_hero[(df2_i_m_hero.Casting_Player == hero)]
        if deck != "All Decks":
            df_tree3 = df_tree3[(df_tree3.P1_Subarch == deck)]
        hero_decks =    df_tree3.P1_Subarch.value_counts().keys().tolist()
        hero_decks_n =  []
        for i in hero_decks:
            games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P1_Subarch == i)].shape[0]
            hero_decks_n.append(games_played)
            index_list3.append("Total")
            index_list3.append("Per Game")
        tuples = zip(*sorted(zip(hero_decks_n,hero_decks),reverse=True))
        if len(hero_decks_n) > 1:
            hero_decks_n, hero_decks = [list(tuple) for tuple in tuples]
        for i in range(len(hero_decks)):
            decks3.append(hero_decks[i])
            decks3.append(str(hero_decks_n[i])+" Games")
        for i in hero_decks:
            if mformat != "All Formats":
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.Format == mformat) & (df1_i_merge.P1_Subarch == i)].shape[0]
            else:
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P1_Subarch == i)].shape[0]
            play_count = df_tree3[(df_tree3.P1_Subarch == i) & (df_tree3.Action == "Land Drop")].shape[0]
            cast_count = df_tree3[(df_tree3.P1_Subarch == i) & (df_tree3.Action == "Casts")].shape[0]
            act_count = df_tree3[(df_tree3.P1_Subarch == i) & (df_tree3.Action == "Activated Ability")].shape[0]
            trig_count = df_tree3[(df_tree3.P1_Subarch == i) & (df_tree3.Action == "Triggers")].shape[0]
            attack_count = df_tree3[(df_tree3.P1_Subarch == i) & (df_tree3.Action == "Attacks")].Attackers.sum()
            draw_count = df_tree3[(df_tree3.P1_Subarch == i) & (df_tree3.Action == "Draws")].Cards_Drawn.sum()
            tree3_data.append([play_count,
                               cast_count,
                               act_count,
                               trig_count,
                               attack_count,
                               draw_count])
            if games_played == 0:
                tree3_data.append([0.0,0.0,0.0,0.0,0.0,0.0])
            else:
                tree3_data.append([round(play_count/games_played,1),
                                   round(cast_count/games_played,1),
                                   round(act_count/games_played,1),
                                   round(trig_count/games_played,1),
                                   round(attack_count/games_played,1),
                                   round(draw_count/games_played,1)])
        
        decks4 = []
        index_list4 = []
        tree4_data = []
        df_tree4 = df2_i_m_hero[(df2_i_m_hero.Casting_Player != hero)]
        if opp_deck != "All Opp. Decks":
            df_tree4 = df_tree4[(df_tree4.P2_Subarch == opp_deck)]
        opp_decks = df_tree4.P2_Subarch.value_counts().keys().tolist()
        opp_decks_n = []
        for i in opp_decks:
            games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P2_Subarch == i)].shape[0]
            opp_decks_n.append(games_played)
            index_list4.append("Total")
            index_list4.append("Per Game")
        tuples = zip(*sorted(zip(opp_decks_n,opp_decks),reverse=True))
        if len(opp_decks_n) > 1:
            opp_decks_n, opp_decks = [list(tuple) for tuple in tuples]        
        for i in range(len(opp_decks)):
            decks4.append(opp_decks[i])
            decks4.append(str(opp_decks_n[i])+" Games")
        for i in opp_decks:
            if mformat != "All Formats":
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.Format == mformat) & (df1_i_merge.P2_Subarch == i)].shape[0]
            else:
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P2_Subarch == i)].shape[0]
            play_count = df_tree4[(df_tree4.P2_Subarch == i) & (df_tree4.Action == "Land Drop")].shape[0]
            cast_count = df_tree4[(df_tree4.P2_Subarch == i) & (df_tree4.Action == "Casts")].shape[0]
            act_count = df_tree4[(df_tree4.P2_Subarch == i) & (df_tree4.Action == "Activated Ability")].shape[0]
            trig_count = df_tree4[(df_tree4.P2_Subarch == i) & (df_tree4.Action == "Triggers")].shape[0]
            attack_count = df_tree4[(df_tree4.P2_Subarch == i) & (df_tree4.Action == "Attacks")].Attackers.sum()
            draw_count = df_tree4[(df_tree4.P2_Subarch == i) & (df_tree4.Action == "Draws")].Cards_Drawn.sum()
            tree4_data.append([play_count,
                               cast_count,
                               act_count,
                               trig_count,
                               attack_count,
                               draw_count])
            if games_played == 0:
                tree4_data.append([0.0,0.0,0.0,0.0,0.0,0.0])
            else:
                tree4_data.append([round(play_count/games_played,1),
                                   round(cast_count/games_played,1),
                                   round(act_count/games_played,1),
                                   round(trig_count/games_played,1),
                                   round(attack_count/games_played,1),
                                   round(draw_count/games_played,1)])

        frame_labels = ["Play Data By Format",
                        "Play Data By Turn: " + hero + ", " + mformat,
                        "Play Data: " + mformat + ", " + deck,
                        "Opposing Play Data: " + mformat + ", " + opp_deck]
        
        if lformat != "All Limited Formats":
            frame_labels[1] += " - " + lformat
            frame_labels[2] = "Play Data: " + mformat + " - " + lformat + ", " + deck
            frame_labels[3] = "Opposing Play Data: " + mformat + " - " + lformat + ", " + deck

        mid_frame1["text"] = frame_labels[0]
        tree1.tag_configure("colored",background="#cccccc")   
        tree1.delete(*tree1.get_children())
        tree1["column"] = ["","","Land Drop","Casts","Activates","Triggers","Attacks","Draws"]
        for i in tree1["column"]:
            tree1.column(i,minwidth=25,stretch=True,width=25)
            tree1.heading(i,text=i)
        tree1.column(0,minwidth=110,stretch=False,width=110)
        for i in range(len(tree1["column"])):
            tree1.column(i,anchor="center")
        tagged = True
        count = 0
        if len(formats) == 0:
            tree1.insert("","end",values=["No Games Found."],tags=('colored',))
        for i in range(len(formats)):
            if tagged == True:
                tree1.insert("","end",values=[formats[i]]+[index_list[i]]+tree1_data[i],tags=('colored',))
            else:
                tree1.insert("","end",values=[formats[i]]+[index_list[i]]+tree1_data[i])
            count += 1
            if count == 2:
                tagged = not tagged
                count = 0
                
        mid_frame2["text"] = frame_labels[1]
        tree2.tag_configure("colored",background="#cccccc")   
        tree2.delete(*tree2.get_children())
        tree2["column"] = ["","Land Drop","Casts","Activates","Triggers","Attacks","Draws","Total GA"]
        for i in tree2["column"]:
            tree2.column(i,minwidth=25,stretch=True,width=25)
            tree2.heading(i,text=i)
        tree2.column(0,minwidth=110,stretch=False,width=110)
        for i in range(len(tree2["column"])):
            tree2.column(i,anchor="center")
        tagged = True
        if len(turn_list) == 0:
            tree2.insert("","end",values=["No Games Found."],tags=('colored',))
        for i in range(len(turn_list)):
            if tagged == True:
                tree2.insert("","end",values=index_list2[i]+tree2_data[i],tags=('colored',))
            else:
                tree2.insert("","end",values=index_list2[i]+tree2_data[i])
            tagged = not tagged

        mid_frame3["text"] = frame_labels[2]               
        tree3.tag_configure("colored",background="#cccccc")
        tree3.delete(*tree3.get_children())
        tree3["column"] = ["","","Land Drop","Casts","Activates","Triggers","Attacks","Draws"]
        for i in tree3["column"]:
            tree3.column(i,minwidth=25,stretch=True,width=25)
            tree3.heading(i,text=i)
        tree3.column(0,minwidth=110,stretch=False,width=110)
        for i in range(len(tree3["column"])):
            tree3.column(i,anchor="center")
        tagged = True
        count = 0
        if len(decks3) == 0:
            tree3.insert("","end",values=["No Games Found."],tags=('colored',))
        for i in range(len(decks3)):
            if i > 13:
                break
            if tagged == True:
                tree3.insert("","end",values=[decks3[i]]+[index_list3[i]]+tree3_data[i],tags=('colored',))
            else:
                tree3.insert("","end",values=[decks3[i]]+[index_list3[i]]+tree3_data[i])
            count += 1
            if count == 2:
                tagged = not tagged
                count = 0

        mid_frame4["text"] = frame_labels[3]                
        tree4.tag_configure("colored",background="#cccccc")
        tree4.delete(*tree4.get_children())
        tree4["column"] = ["","","Land Drop","Casts","Activates","Triggers","Attacks","Draws"]
        for i in tree4["column"]:
            tree4.column(i,minwidth=25,stretch=True,width=25)
            tree4.heading(i,text=i)
        tree4.column(0,minwidth=110,stretch=False,width=110)
        for i in range(len(tree4["column"])):
            tree4.column(i,anchor="center")
        tagged = True
        count = 0
        if len(decks4) == 0:
            tree4.insert("","end",values=["No Games Found."],tags=('colored',))
        for i in range(len(decks4)):
            if i > 13:
                break
            if tagged == True:
                tree4.insert("","end",values=[decks4[i]]+[index_list4[i]]+tree4_data[i],tags=('colored',))
            else:
                tree4.insert("","end",values=[decks4[i]]+[index_list4[i]]+tree4_data[i])
            count += 1
            if count == 2:
                tagged = not tagged
                count = 0
    
    def opp_stats(hero,opp,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Opponent Data: " + hero + " vs. " + opp)
        clear_frames()
        def tree_skip(event):
            if tree1.identify_region(event.x,event.y) == "separator":
                return "break"
            if tree1.identify_region(event.x,event.y) == "heading":
                return "break"
        def tree_setup(*argv):
            for i in argv:
                i.place(relheight=1, relwidth=1)
                i.bind("<Button-1>",tree_skip)
                i.bind("<Enter>",tree_skip)
                i.bind("<ButtonRelease-1>",tree_skip)
                i.bind("<Motion>",tree_skip)          
        tree1 = ttk.Treeview(mid_frame1,show="headings",selectmode="none",padding=10)
        tree2 = ttk.Treeview(mid_frame2,show="headings",selectmode="none",padding=10)
        tree3 = ttk.Treeview(mid_frame3,show="headings",selectmode="none",padding=10)       
        tree4 = ttk.Treeview(mid_frame4,show="headings",selectmode="none",padding=10)
        tree_setup(tree1,tree2,tree3,tree4)
        mid_frame.grid_rowconfigure(0,weight=1)
        mid_frame.grid_rowconfigure(1,weight=1)
        mid_frame.grid_columnconfigure(0,weight=1)
        mid_frame.grid_columnconfigure(1,weight=1)
        mid_frame1.grid(row=0,column=0,sticky="nsew")
        mid_frame2.grid(row=0,column=1,sticky="nsew")
        mid_frame3.grid(row=1,column=0,sticky="nsew")
        mid_frame4.grid(row=1,column=1,sticky="nsew")

        df0_i_f        = df0_i[(df0_i.P1 == hero) & (df0_i.P2 == opp)]
        df0_i_f.sort_values(by="Date",ascending=False,inplace=True)
        tree1_dates    = df0_i_f.Date.tolist()
        tree1_decks    = df0_i_f.P1_Subarch.tolist()
        tree1_oppdecks = df0_i_f.P2_Subarch.tolist()
        tree1_wins     = df0_i_f.P1_Wins.tolist()
        tree1_losses   = df0_i_f.P2_Wins.tolist()
        tree1_result   = df0_i_f.Match_Winner.tolist()
        for index,i in enumerate(tree1_result):
            if i == "P1":
                tree1_result[index] = "Win "
            elif i == "P2":
                tree1_result[index] = "Loss "
            elif i == "NA":
                tree1_result[index] = "NA "
            tree1_result[index] += str(tree1_wins[index]) + "-" + str(tree1_losses[index])

        df1_i_merge     = pd.merge(df0_i,
                                   df1_i,
                                   how="inner",
                                   left_on=["Match_ID","P1","P2"],
                                   right_on=["Match_ID","P1","P2"])
        df1_i_hero      = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P2 == opp)]
        df1_i_hero_p    = df1_i_hero[df1_i_hero.On_Play == "P1"]
        df1_i_hero_d    = df1_i_hero[df1_i_hero.On_Play == "P2"]
        
        df1_i_hero_g1   = df1_i_hero[df1_i_hero.Game_Num == 1]
        df1_i_hero_g1_p = df1_i_hero_g1[df1_i_hero_g1.On_Play == "P1"]
        df1_i_hero_g1_d = df1_i_hero_g1[df1_i_hero_g1.On_Play == "P2"]
        
        df1_i_hero_g2   = df1_i_hero[df1_i_hero.Game_Num == 2]
        df1_i_hero_g2_p = df1_i_hero_g2[df1_i_hero_g2.On_Play == "P1"]
        df1_i_hero_g2_d = df1_i_hero_g2[df1_i_hero_g2.On_Play == "P2"]
        
        df1_i_hero_g3   = df1_i_hero[df1_i_hero.Game_Num == 3]
        df1_i_hero_g3_p = df1_i_hero_g3[df1_i_hero_g3.On_Play == "P1"]
        df1_i_hero_g3_d = df1_i_hero_g3[df1_i_hero_g3.On_Play == "P2"]

        df_list = [df1_i_hero,
                   df1_i_hero_p,
                   df1_i_hero_d,
                   df1_i_hero_g1,
                   df1_i_hero_g1_p,
                   df1_i_hero_g1_d,
                   df1_i_hero_g2,
                   df1_i_hero_g2_p,
                   df1_i_hero_g2_d,
                   df1_i_hero_g3,
                   df1_i_hero_g3_p,
                   df1_i_hero_g3_d]

        tree3data =    []
        for i in df_list:
            total_n = i.shape[0]
            wins =    i[(i.Game_Winner == "P1")].shape[0]
            losses =  i[(i.Game_Winner == "P2")].shape[0]
            if (wins+losses) == 0:
                win_rate = "0.0"
            else:
                win_rate = to_percent(wins/(wins+losses),1)
            if total_n == 0:
                hero_mull_rate =0.0
                opp_mull_rate = 0.0
                turn_rate =     0.0
            else:
                hero_mull_rate =round((i.P1_Mulls.sum()/total_n),2)
                opp_mull_rate = round((i.P2_Mulls.sum()/total_n),2)
                turn_rate =     round((i.Turns.sum()/total_n),2)     
            tree3data.append([wins,
                              losses,
                              win_rate,
                              hero_mull_rate,
                              opp_mull_rate,
                              turn_rate])

        formats_played = df0_i_f.Format.value_counts().keys().tolist()
        format_wins =    [df0_i_f[(df0_i_f.Match_Winner == "P1")].shape[0]] #adding overall in L[0]
        format_losses =  [df0_i_f[(df0_i_f.Match_Winner == "P2")].shape[0]] #adding overall in L[0]
        if (format_wins[0] + format_losses[0]) == 0:
            format_wr = ["0.0%"]
        else:
            format_wr = [to_percent(format_wins[0]/(format_wins[0]+format_losses[0]),1) + "%"]    #adding overall in L[0]

        for i in formats_played:
            wins  =  df0_i_f[(df0_i_f.Format == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
            losses = df0_i_f[(df0_i_f.Format == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            format_wins.append(str(wins))
            format_losses.append(str(losses))
            format_wr.append(to_percent(wins/(wins+losses),1) + "%")
        formats_played.insert(0,"Match Format")

        formats_played.extend(["","Match Type"])
        format_wins.extend(["",format_wins[0]])
        format_losses.extend(["",format_losses[0]])
        format_wr.extend(["",format_wr[0]])

        matchtypes_played = df0_i_f.Match_Type.value_counts().keys().tolist()
        for i in matchtypes_played:
            mt_wins  =  df0_i_f[(df0_i_f.Match_Type == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
            mt_losses = df0_i_f[(df0_i_f.Match_Type == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            formats_played.append(i)
            format_wins.append(mt_wins)
            format_losses.append(mt_losses)
            format_wr.append(to_percent(mt_wins/(mt_wins+mt_losses),1) + "%")

        filtered_n =        df0_i_f.shape[0] 
        meta_deck_wr =      []
        meta_decks =        df0_i_f.P2_Subarch.value_counts().keys().tolist()
        meta_deck_counts =  df0_i_f.P2_Subarch.value_counts().tolist()
        for i in meta_decks:
            wins  = df0_i_f[(df0_i_f.P2_Subarch == i) & (df0_i_f.Match_Winner == "P1")].shape[0]
            losses= df0_i_f[(df0_i_f.P2_Subarch == i) & (df0_i_f.Match_Winner == "P2")].shape[0]
            total = df0_i_f[(df0_i_f.P2_Subarch == i)].shape[0]
            if total == 0:
                meta_deck_wr.append([wins,losses,"0"])
            else:
                meta_deck_wr.append([wins,losses,to_percent(wins/total,1)])

        mid_frame1["text"] = "Match History: vs. " + opp
        tree1.tag_configure("win",background="#a3ffb1")
        tree1.tag_configure("lose",background="#ffa3a3")
        tree1.delete(*tree1.get_children())
        tree1["column"] = ["Date","Deck","Opp. Deck","Match Result"]
        for i in tree1["column"]:
            tree1.column(i,minwidth=20,stretch=True,width=20)
            tree1.heading(i,text=i)
        tree1.column("Deck",anchor="center")
        tree1.column("Opp. Deck",anchor="center")
        tree1.column("Match Result",anchor="center")
        for i in range(len(tree1_dates)):
            if "Win" in tree1_result[i]:
                tree1.insert("","end",values=[tree1_dates[i],
                                              tree1_decks[i],
                                              tree1_oppdecks[i],
                                              tree1_result[i]],tags=("win",))
            else:
                tree1.insert("","end",values=[tree1_dates[i],
                                              tree1_decks[i],
                                              tree1_oppdecks[i],
                                              tree1_result[i]],tags=("lose",))

        mid_frame2["text"] = "Overall Performance: vs. " + opp
        tree2.tag_configure("colored",background="#cccccc")
        tree2.delete(*tree2.get_children())
        tree2["column"] = ["Description","Wins","Losses","Match Win% Against"]
        for i in tree2["column"]:
            tree2.column(i,minwidth=20,stretch=True,width=20)
            tree2.heading(i,text=i)
        tree2.column("Wins",anchor="center")
        tree2.column("Losses",anchor="center")
        tree2.column("Match Win% Against",anchor="center")
        for i in range(len(formats_played)):
            if (formats_played[i] == "Match Format") or (formats_played[i] == "Match Type"):
                tagged = True
            else:
                tagged = False
            if tagged == True:
                tree2.insert("","end",values=[formats_played[i],
                                              format_wins[i],
                                              format_losses[i],
                                              format_wr[i]],tags=("colored",))
            else:
                tree2.insert("","end",values=[formats_played[i],
                                              format_wins[i],
                                              format_losses[i],
                                              format_wr[i]])

        mid_frame3["text"] = "Game Stats: vs. " + opp
        tree3.tag_configure("colored",background="#cccccc")
        tree3.delete(*tree3.get_children())
        tree3["column"] = ["","","Wins","Losses","Win%","Mulls/G","Opp Mulls/G","Turns/G"]
        for i in tree3["column"]:
            tree3.column(i,minwidth=25,stretch=True,width=25)
            tree3.heading(i,text=i)
        tree3.column(0,minwidth=110,stretch=False,width=110)
        for i in range(2,len(tree3["column"])):
            tree3.column(i,anchor="center")
        index_list = [["All Games","Overall"],["","Play"],["","Draw"],
                      ["Game 1","Overall"],["","Play"],["","Draw"],
                      ["Game 2","Overall"],["","Play"],["","Draw"],
                      ["Game 3","Overall"],["","Play"],["","Draw"]]
        tagged = True
        count = 0
        for i in range(len(index_list)):
            if tagged == True:
                tree3.insert("","end",values=index_list[i]+tree3data[i],tags=("colored",))
            else:
                tree3.insert("","end",values=index_list[i]+tree3data[i])
            count += 1
            if count == 3:
                tagged = not tagged
                count = 0

        mid_frame4["text"] = "Decks Played: " + opp
        tree4.tag_configure("colored",background="#cccccc")
        tree4.delete(*tree4.get_children())
        tree4["column"] = ["Decks","Share","Wins","Losses","Win% Against"]
        for i in tree4["column"]:
            tree4.column(i,minwidth=20,stretch=True,width=20)
            tree4.heading(i,text=i)
        for i in range(1,len(tree4["column"])):
            tree4.column(i,anchor="center")
        tagged = False
        for i in range(10):
            if i >= len(meta_decks):
                break
            tagged = not tagged
            if tagged == True:
                tree4.insert("","end",values=[meta_decks[i],
                                              (str(meta_deck_counts[i])+" - ("+to_percent(meta_deck_counts[i]/filtered_n,0)+"%)"),
                                              meta_deck_wr[i][0],
                                              meta_deck_wr[i][1],
                                              (meta_deck_wr[i][2]+"%")],tags=("colored",))
            else:
                tree4.insert("","end",values=[meta_decks[i],
                                              (str(meta_deck_counts[i])+" - ("+to_percent(meta_deck_counts[i]/filtered_n,0)+"%)"),
                                              meta_deck_wr[i][0],
                                              meta_deck_wr[i][1],
                                              (meta_deck_wr[i][2]+"%")])

    def time_stats(hero,opp,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Time Data: " + hero)
        clear_frames()
        mid_frame.grid_rowconfigure(0,weight=1)
        mid_frame.grid_rowconfigure(1,weight=0)
        mid_frame.grid_columnconfigure(0,weight=1)
        mid_frame.grid_columnconfigure(1,weight=1)
        mid_frame5.grid_rowconfigure(0,weight=1)
        mid_frame5.grid_columnconfigure(0,weight=1)
        mid_frame6.grid_rowconfigure(0,weight=1)
        mid_frame6.grid_columnconfigure(0,weight=1)
        mid_frame5.grid(row=0,column=0,sticky="nsew")
        mid_frame6.grid(row=0,column=1,sticky="nsew")

        mid_frame5.grid_propagate(0)
        mid_frame6.grid_propagate(0)

        def get_wr_over_time(df,start_index):
            match_winners = df.Match_Winner.tolist()
            x = []
            wr_over_time = []
            p1_count = 0
            for index,i in enumerate(match_winners,1):
                if i == "P1":
                    p1_count += 1
                wr_over_time.append(round(p1_count/index,3)*100)
                x.append(index)
            if start_index < len(wr_over_time):
                x = x[start_index:]
                wr_over_time = wr_over_time[start_index:]
            return [x,wr_over_time]

        def get_pm_over_time(df,start_index):
            match_winners = df.Match_Winner.tolist()
            x = []
            last = 0
            pm_over_time = []
            for index,i in enumerate(match_winners):
                if i == "P1":
                    pm_over_time.append(last + 1)
                    x.append(index)
                elif i == "P2":
                    pm_over_time.append(last - 1)
                    x.append(index)
                last = pm_over_time[-1]
            if start_index < len(pm_over_time):
                x = x[start_index:]
                pm_over_time = pm_over_time[start_index:]
            return [x,pm_over_time]

        chart_type = "plusminus"

        df_time = df0_i[(df0_i.P1 == hero)]
        if mformat != "All Formats":
            df_time = df_time[(df_time.Format == mformat)]
        if lformat != "All Limited Formats":
            df_time = df_time[(df_time.Limited_Format == lformat)]
        df_time = df_time.sort_values(by=["Date"])
        df_time = df_time[(df_time.Date.between(date_range[0],date_range[1]))]
        
        if chart_type == "winrate":
            g1_list = get_wr_over_time(df_time,0)
        elif chart_type == "plusminus":
            g1_list = get_pm_over_time(df_time,0)

        fig = plt.figure(figsize=(7,5),dpi=100)
        plt.plot(g1_list[0],g1_list[1])
        plt.xlabel("Matches Played")

        if chart_type == "winrate":
            if lformat == "All Limited Formats":
                plt.title("Win Rate Over Time:\n" + mformat)
            else:
                plt.title("Win Rate Over Time:\n" + mformat + " - " + lformat)
            plt.ylabel("Winning Percentage")
        elif chart_type == "plusminus":
            if lformat == "All Limited Formats":
                plt.title("Match Wins Over .500:\n" + mformat)
            else:
                plt.title("Match Wins Over .500:\n" + mformat + " - " + lformat)
            plt.ylabel("Match Wins Over .500")

        canvas = FigureCanvasTkAgg(fig,mid_frame5)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0,column=0,sticky="")

        if deck != "All Decks":
            df_time_d = df_time[(df_time.P1_Subarch == deck)]
            df_time_d = df_time_d.sort_values(by=["Date"])     
            
            if chart_type == "winrate":
                g2_list = get_wr_over_time(df_time_d,0)
            elif chart_type == "plusminus":
                g2_list = get_pm_over_time(df_time_d,0)

            fig = plt.figure(figsize=(7,5),dpi=100)
            plt.plot(g2_list[0],g2_list[1])
            plt.xlabel("Matches Played")

            if chart_type == "winrate":
                if lformat == "All Limited Formats":
                    plt.title("Win Rate Over Time:\n" + mformat + ": " + deck)
                else:
                    plt.title("Win Rate Over Time:\n" + mformat + " - " + lformat + ": " + deck)
                plt.ylabel("Winning Percentage")
            elif chart_type == "plusminus":
                if lformat == "All Limited Formats":
                    plt.title("Match Wins Over .500:\n" + mformat + ": " + deck)
                else:
                    plt.title("Match Wins Over .500:\n" + mformat + " - " + lformat + ": " + deck)
                plt.ylabel("Match Wins Over .500")

            canvas2 = FigureCanvasTkAgg(fig,mid_frame6)
            canvas2.draw()
            canvas2.get_tk_widget().grid(row=0,column=0,sticky="")

    def card_stats(hero,opp,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Card Data: " + hero)
        clear_frames()
        def tree_setup(*argv):
            for i in argv:
                i.place(relheight=1, relwidth=1)
        def sort_column(col,reverse,tree1):
            l = []
            for k in tree1.get_children(''):
                l.append((tree1.set(k, col), k))
            l.sort(reverse=reverse)
            # Re-arrange items in sorted positions.
            for index, (val, k) in enumerate(l):
                tree1.move(k, '', index)
            # Reverse sort next time.
            tree1.heading(col,text=col,command=lambda _col=col: sort_column(_col,not reverse,tree1))
        def sort_column_float(col,reverse,tree1):
            def tree_tuple_to_float(tuple):
                if tuple[0] == "":
                    return ""
                return float(tuple[0])

            l = []
            for k in tree1.get_children(''):
                l.append((tree1.set(k, col), k))
            l.sort(reverse=reverse,key=tree_tuple_to_float)
            # Re-arrange items in sorted positions.
            for index, (val, k) in enumerate(l):
                tree1.move(k, '', index)
            # Reverse sort next time.
            tree1.heading(col,text=col,command=lambda _col=col: sort_column_float(_col,not reverse,tree1))
        def sort_column_mixed(col,reverse,tree1):
            def tree_tuple_to_mixed(tuple):
                if tuple[0] == "":
                    return ""
                return int(tuple[0].split(" - ")[0])

            l = []
            for k in tree1.get_children(''):
                l.append((tree1.set(k, col), k))
            l.sort(reverse=reverse,key=tree_tuple_to_mixed)
            # Re-arrange items in sorted positions.
            for index, (val, k) in enumerate(l):
                tree1.move(k, '', index)
            # Reverse sort next time.
            tree1.heading(col,text=col,command=lambda _col=col: sort_column_mixed(_col,not reverse,tree1))

        tree1 = ttk.Treeview(mid_frame7,show="headings",padding=10)
        tree2 = ttk.Treeview(mid_frame8,show="headings",padding=10)
        tree_setup(tree1,tree2)
        mid_frame.grid_rowconfigure(0,weight=1)
        mid_frame.grid_rowconfigure(1,weight=0)
        mid_frame.grid_columnconfigure(0,weight=1)
        mid_frame.grid_columnconfigure(1,weight=1)
        mid_frame7.grid_rowconfigure(0,weight=1)
        mid_frame7.grid_columnconfigure(0,weight=1)
        mid_frame8.grid_rowconfigure(0,weight=1)
        mid_frame8.grid_columnconfigure(0,weight=1)
        mid_frame7.grid(row=0,column=0,sticky="nsew")
        mid_frame8.grid(row=0,column=1,sticky="nsew")

        mid_frame7.grid_propagate(0)
        mid_frame8.grid_propagate(0)

        # Use Left Join because we want to keep Games where 0 Plays occurred.
        df_merge = pd.merge(df1_i,
                            df2_i,
                            how="left",
                            left_on=["Match_ID","Game_Num"],
                            right_on=["Match_ID","Game_Num"])
        df_merge = pd.merge(df0_i,
                            df_merge,
                            how="inner",
                            left_on=["Match_ID","P1","P2"],
                            right_on=["Match_ID","P1","P2"])
        df_merge = df_merge[(df_merge.Game_Winner != "NA") & (df_merge.Date > date_range[0]) & (df_merge.Date < date_range[1])]
        if mformat != "All Formats":
            df_merge = df_merge[(df_merge.Format == mformat)]
        if lformat != "All Limited Formats":
            df_merge = df_merge[(df_merge.Limited_Format == lformat)]
        if deck != "All Decks":
            df_merge = df_merge[(df_merge.P1_Subarch == deck)]
        if opp_deck != "All Opp. Decks":
            df_merge = df_merge[(df_merge.P2_Subarch == opp_deck)]
        if hero != "All Players":
            df_merge = df_merge[(df_merge.P1 == hero)]
        df_merge["Game_ID"]  = df_merge.Match_ID + "_G" + df_merge.Game_Num.astype(str)
        df_merge["Won_Game"] = np.where(df_merge["Game_Winner"] == "P1",1,0)

        df_merge_pre  = df_merge[(df_merge.Game_Num == 1)]
        df_merge_post = df_merge[(df_merge.Game_Num != 1)]

        n_pre  = len(list(df_merge_pre.Game_ID.value_counts()))
        n_post = len(list(df_merge_post.Game_ID.value_counts()))
        wins_pre =  df_merge_pre.drop_duplicates("Game_ID").Won_Game.sum()
        wins_post = df_merge_post.drop_duplicates("Game_ID").Won_Game.sum()
        if n_pre == 0:
            wr_pre = 0.0
        else:
            wr_pre = round((wins_pre/n_pre)*100,1).item()
        if n_post == 0:
            wr_post = 0.0
        else:
            wr_post = round((wins_post/n_post)*100,1).item()

        df_merge_pre = df_merge_pre[(df_merge_pre.Casting_Player == hero) & (df_merge_pre.Action.isin(["Plays","Casts"]))]
        df_merge_pre.drop(df_merge_pre.columns.difference(["Game_ID","Game_Num","P1_Subarch","P2_Subarch","Primary_Card","Won_Game"]),axis=1,inplace=True)
        df_merge_pre.drop_duplicates(inplace=True)

        df_merge_post = df_merge_post[(df_merge_post.Casting_Player == hero) & (df_merge_post.Action.isin(["Plays","Casts"]))]
        df_merge_post.drop(df_merge_post.columns.difference(["Game_ID","Game_Num","P1_Subarch","P2_Subarch","Primary_Card","Won_Game"]),axis=1,inplace=True)
        df_merge_post.drop_duplicates(inplace=True)

        cards_played_pre = list(df_merge_pre.groupby(["Primary_Card"]).groups.keys())
        games_played_pre = df_merge_pre.groupby(["Primary_Card"]).Game_ID.size().tolist()
        games_won_pre =    df_merge_pre.groupby(["Primary_Card"]).Won_Game.sum().tolist()
        games_wr_pre = []
        for i in range(len(games_played_pre)):
            games_wr_pre.append(round((int(games_won_pre[i])/int(games_played_pre[i]))*100,1))

        cards_played_post = list(df_merge_post.groupby(["Primary_Card"]).groups.keys())
        games_played_post = df_merge_post.groupby(["Primary_Card"]).Game_ID.size().tolist()
        games_won_post =    df_merge_post.groupby(["Primary_Card"]).Won_Game.sum().tolist()
        games_wr_post = []
        for i in range(len(games_played_post)):
            games_wr_post.append(round((int(games_won_post[i])/int(games_played_post[i]))*100,1))

        # Create lists of data to be inserted into trees.
        list_pre =  np.array([cards_played_pre,games_played_pre,games_won_pre,games_wr_pre]).T.tolist()
        list_post = np.array([cards_played_post,games_played_post,games_won_post,games_wr_post]).T.tolist()

        list_pre =  sorted(list_pre,key=lambda x: -int(x[1]))
        list_post = sorted(list_post,key=lambda x: -int(x[1]))

        mid_frame7["text"] = "Pre-Sideboard - " + str(n_pre) + " Games: " + mformat
        tree1.tag_configure("colored",background="#cccccc")
        tree1.delete(*tree1.get_children())
        tree1["column"] = ["Card","Games Cast","Game Win%","Delta"]
        for i in tree1["column"]:
            tree1.column(i,minwidth=20,stretch=True,width=20)
            if (i == "Game Win%") or (i == "Delta"):
                tree1.heading(i,text=i,command=lambda _col=i: sort_column_float(_col,False,tree1))
            elif (i == "Games Cast"):
                tree1.heading(i,text=i,command=lambda _col=i: sort_column_mixed(_col,False,tree1))
            else:
                tree1.heading(i,text=i,command=lambda _col=i: sort_column(_col,False,tree1))
        for i in range(1,len(tree1["column"])):
            tree1.column(i,anchor="center")
        tagged = False
        if len(list_pre) == 0:
            tree1.insert("","end",values=["No Games Found."],tags=('colored',))
        for i in list_pre:
            tree1.insert("","end",values=[i[0],
                                          i[1]+" - ("+to_percent(int(i[1])/n_pre,0)+"%)",
                                          i[3],
                                          round(float(i[3])-wr_pre,1)])

        mid_frame8["text"] = "Post-Sideboard - " + str(n_post) + " Games: " + mformat
        if lformat != "All Limited Formats":
            mid_frame7["text"] += " - " + lformat
            mid_frame8["text"] += " - " + lformat
        if deck != "All Decks":
            mid_frame7["text"] += ": " + deck
            mid_frame8["text"] += ": " + deck
        if opp_deck != "All Opp. Decks":
            if deck == "All Decks":
                mid_frame7["text"] += ": " + deck + " vs. " + opp_deck
                mid_frame8["text"] += ": " + deck + " vs. " + opp_deck
            else:
                mid_frame7["text"] += " vs. " + opp_deck
                mid_frame8["text"] += " vs. " + opp_deck 
        tree2.tag_configure("colored",background="#cccccc")
        tree2.delete(*tree2.get_children())
        tree2["column"] = ["Card","Games Cast","Game Win%","Delta"]
        for i in tree2["column"]:
            tree2.column(i,minwidth=20,stretch=True,width=20)
            if (i == "Game Win%") or (i == "Delta"):
                tree2.heading(i,text=i,command=lambda _col=i: sort_column_float(_col,False,tree2))
            elif (i == "Games Cast"):
                tree2.heading(i,text=i,command=lambda _col=i: sort_column_mixed(_col,False,tree2))
            else:
                tree2.heading(i,text=i,command=lambda _col=i: sort_column(_col,False,tree2))
        for i in range(1,len(tree2["column"])):
            tree2.column(i,anchor="center")
        if len(list_post) == 0:
            tree2.insert("","end",values=["No Games Found."],tags=('colored',))
        for i in list_post:
            tree2.insert("","end",values=[i[0],
                                          i[1]+" - ("+to_percent(int(i[1])/n_post,0)+"%)",
                                          i[3],
                                          round(float(i[3])-wr_post,1)])
                                                
    def to_percent(fl,n):
        if fl == 0:
            return "0.0"
        if n == 0:
            return str(int(fl*100))
        else:
            return str(round(fl*100,n))

    def update_format_menu(*argv):
        format_options = df0_i[(df0_i.P1 == player.get())].Format.value_counts().keys().tolist()
        format_options.insert(0,"All Formats")

        menu_2["values"] = format_options
        mformat.set(format_options[0]) 

    def update_hero(*argv):
        HERO = player.get()
        update_format_menu()
        update_deck_menu()
        update_opp_deck_menu()
        update_opp_menu()
       
        menu_2["state"]   = "readonly"
        menu_4["state"]   = "readonly"
        menu_5["state"]   = "readonly"
        menu_6["state"]   = tk.NORMAL

    def update_opp_menu(*argv):
        df = df0_i[(df0_i.P1 == player.get())]

        opponents = df.P2.value_counts().keys().tolist()
        opponents.sort(reverse=False,key=str.casefold)
        if s_type.get() != "Opponent Stats":
            opponents.insert(0,"Opponent")

        menu_1["values"] = opponents
        opponent.set(opponents[0])

    def update_format(*argv):
        if mformat.get() in INPUT_OPTIONS["Limited Formats"]:
            lim_format.set("All Limited Formats")
            menu_3["state"] = "readonly"
            menu_3.grid(row=0,column=2,padx=5,pady=10)
            update_lim_menu()
        else:
            lim_format.set("All Limited Formats")
            menu_3["state"] = tk.DISABLED
            menu_3.grid_forget()
        update_deck_menu()
        update_opp_deck_menu()

    def update_lim_format(*argv):
        update_deck_menu()
        update_opp_deck_menu()

    def update_lim_menu(*argv):
        lim_formats_played = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())].Limited_Format.value_counts().keys().tolist()
        lim_formats_played.insert(0,"All Limited Formats")

        menu_3["values"] = lim_formats_played
        lim_format.set(lim_formats_played[0])

    def update_deck_menu(*argv):
        if mformat.get() == "All Formats":
            df = df0_i[(df0_i.P1 == player.get())]
        elif mformat.get() in INPUT_OPTIONS["Constructed Formats"]:
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        elif (mformat.get() in INPUT_OPTIONS["Limited Formats"]) & (lim_format.get() == "All Limited Formats"):
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        elif (mformat.get() in INPUT_OPTIONS["Limited Formats"]) & (lim_format.get() != "All Limited Formats"):
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get()) & (df0_i.Limited_Format == lim_format.get())]
        else:
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        
        decks_played = df.P1_Subarch.value_counts().keys().tolist()
        if s_type.get() == "Time Data":
            deck_counts  = df0_i[(df0_i.P1 == player.get())].P1_Subarch.value_counts().tolist()
            for index,i in enumerate(deck_counts):
                if i < 20:
                    del decks_played[index:]
                    del deck_counts[index:]
                    break
        decks_played.insert(0,"All Decks")

        menu_4["values"] = decks_played
        deck.set(decks_played[0])

    def update_opp_deck_menu(*argv):
        if mformat.get() == "All Formats":
            df = df0_i[(df0_i.P1 == player.get())]
        elif mformat.get() in INPUT_OPTIONS["Constructed Formats"]:
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        elif (mformat.get() in INPUT_OPTIONS["Limited Formats"]) & (lim_format.get() == "All Limited Formats"):
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        elif (mformat.get() in INPUT_OPTIONS["Limited Formats"]) & (lim_format.get() != "All Limited Formats"):
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get()) & (df0_i.Limited_Format == lim_format.get())]
        else:
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]

        opp_decks_played = df.P2_Subarch.value_counts().keys().tolist()
        opp_decks_played.insert(0,"All Opp. Decks")

        menu_5["values"] = opp_decks_played
        opp_deck.set(opp_decks_played[0])

    def update_s_type(*argv):
        update_opp_menu()
        update_format_menu()
        update_deck_menu()
        update_opp_deck_menu()
        if s_type.get() == "Match History":
            menu_1["state"] = tk.DISABLED
            menu_2["state"] = "readonly"
            menu_4["state"] = tk.DISABLED
            menu_5["state"] = tk.DISABLED
            date_entry_1["state"] = tk.DISABLED
            date_entry_2["state"] = tk.DISABLED
        elif s_type.get() == "Time Data":
            menu_1["state"] = tk.DISABLED
            menu_2["state"] = "readonly"
            menu_4["state"] = "readonly"
            menu_5["state"] = tk.DISABLED
            date_entry_1["state"] = "readonly"
            date_entry_2["state"] = "readonly"
        elif s_type.get() == "Opponent Stats":
            menu_1["state"] = "readonly"
            menu_2["state"] = tk.DISABLED
            menu_4["state"] = tk.DISABLED
            menu_5["state"] = tk.DISABLED
            date_entry_1["state"] = tk.DISABLED
            date_entry_2["state"] = tk.DISABLED
        else:
            menu_1["state"] = tk.DISABLED
            menu_2["state"] = "readonly"
            menu_4["state"] = "readonly"
            menu_5["state"] = "readonly"
            date_entry_1["state"] = "readonly"
            date_entry_2["state"] = "readonly"
        load_data()

    def load_data(*argv):
        if date_entry_1.get() < date_entry_2.get():
            dr = [date_entry_1.get() + "-00:00",date_entry_2.get() + "-23:59"]
        else:
            dr = [date_entry_1.get() + "-00:00",date_entry_2.get() + "-23:59"]
        if s_type.get() == "Match History":
            match_history(player.get(),opponent.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Match Stats":
            match_stats(player.get(),opponent.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Game Stats":
            game_stats(player.get(),opponent.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Play Stats":
            play_stats(player.get(),opponent.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Opponent Stats":
            opp_stats(player.get(),opponent.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Time Data":
            time_stats(player.get(),opponent.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Card Data":
            card_stats(player.get(),opponent.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())      
        print("Loaded Data:"+player.get()+","+opponent.get()+","+mformat.get()+","+lim_format.get()+","+deck.get()+","+opp_deck.get()+","+dr[0]+","+dr[1]+","+s_type.get())

    def close_stats_window():
        window.deiconify()
        stats_window.destroy()
        
    p1_options = df0_i.P1.tolist()
    p1_options = sorted(list(set(p1_options)),key=str.casefold)
    
    date_min = df0.Date.min()
    today = datetime.date.today()

    format_options = [""]
    limited_options = [""]
    decks_played = [""]
    opp_decks_played = [""]
    # stat_types = ["Match History","Match Stats","Game Stats","Play Stats","Opponent Stats","Time Data","Card Data"]
    stat_types = ["Match History","Match Stats","Game Stats","Play Stats","Opponent Stats","Card Data"]
    
    player = tk.StringVar()
    player.set(HERO)
    opponent = tk.StringVar()
    opponent.set("Opponent")
    mformat = tk.StringVar()
    mformat.set("Format")
    lim_format = tk.StringVar()
    lim_format.set("All Limited Formats")
    deck = tk.StringVar()
    deck.set("Decks Played")
    opp_deck = tk.StringVar()
    opp_deck.set("All Opp. Decks")
    s_type = tk.StringVar()
    s_type.set(stat_types[0])
    
    menu_1 = ttk.Combobox(top_frame,textvariable=opponent,width=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER)
    menu_2 = ttk.Combobox(top_frame,textvariable=mformat,width=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER)
    menu_3 = ttk.Combobox(top_frame,textvariable=lim_format,width=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER)
    menu_4 = ttk.Combobox(top_frame,textvariable=deck,width=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER)
    menu_5 = ttk.Combobox(top_frame,textvariable=opp_deck,width=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER)
    date_entry_1 = DateEntry(top_frame,date_pattern="y-mm-dd",width=10,
        year=int(date_min[0:4]),month=int(date_min[5:7]),day=int(date_min[8:10]),
        font="Helvetica 14",state="readonly")
    date_entry_2 = DateEntry(top_frame,date_pattern="y-mm-dd",width=10,
        year=today.year,month=today.month,day=today.day,
        font="Helvetica 14",state="readonly")
    menu_6 = tk.OptionMenu(top_frame,s_type,*stat_types)
    
    menu_1["state"] = tk.DISABLED
    menu_2["state"] = tk.DISABLED
    menu_3["state"] = tk.DISABLED
    menu_4["state"] = tk.DISABLED
    menu_5["state"] = tk.DISABLED
    menu_6["state"] = tk.DISABLED

    menu_1.bind("<FocusIn>",defocus)
    menu_2.bind("<FocusIn>",defocus)
    menu_3.bind("<FocusIn>",defocus)
    menu_4.bind("<FocusIn>",defocus)
    menu_5.bind("<FocusIn>",defocus)

    menu_1.grid(row=0,column=0,padx=5,pady=10,sticky="e")
    menu_2.grid(row=0,column=1,padx=5,pady=10)
    menu_4.grid(row=0,column=3,padx=5,pady=10)
    menu_5.grid(row=0,column=4,padx=5,pady=10)
    date_entry_1.grid(row=0,column=5,padx=5,pady=10)
    date_entry_2.grid(row=0,column=6,padx=5,pady=10,sticky="w")
    menu_6.grid(row=0,column=7,padx=(5,10),pady=10)
    menu_6.config(width=15)
    
    menu_6.config(bg="black",fg="white",activebackground="black",activeforeground="white")
    menu_6["menu"].config(bg="black",fg="white",borderwidth=0)

    player.trace("w",update_hero)
    mformat.trace("w",update_format)
    lim_format.trace("w",update_lim_format)
    s_type.trace("w",update_s_type)

    menu_1.bind("<<ComboboxSelected>>",load_data)
    menu_2.bind("<<ComboboxSelected>>",load_data)
    menu_3.bind("<<ComboboxSelected>>",load_data)
    menu_4.bind("<<ComboboxSelected>>",load_data)
    menu_5.bind("<<ComboboxSelected>>",load_data)
    date_entry_1.bind("<<DateEntrySelected>>",load_data)
    date_entry_2.bind("<<DateEntrySelected>>",load_data)

    player.set(HERO)
    update_s_type(s_type.get())

    stats_window.title("Statistics - Match Data: " + player.get())
    stats_window.protocol("WM_DELETE_WINDOW", lambda : close_stats_window())
def close():
    # Close window and exit program.
    window.destroy()
def exit_select():
    if ask_to_save:
        save_window(exit=True)
    else:
        close()
def load_window_size_setting():
    global MAIN_WINDOW_SIZE
    global ln_per_page

    cwd = os.getcwd()
    if os.path.isdir("save") == True:
        os.chdir(cwd + "\\" + "save")
        if os.path.isfile("MAIN_WINDOW_SIZE"):
            MAIN_WINDOW_SIZE = pickle.load(open("MAIN_WINDOW_SIZE","rb"))
            if MAIN_WINDOW_SIZE[0] == "small":
                ln_per_page = 20
            elif MAIN_WINDOW_SIZE[0] == "large":
                ln_per_page = 35
        os.chdir(cwd)
def update_status_bar(status):
    status_label.config(text=status)
    print(status)
def remove_record(ignore):
    global ALL_DATA
    global ALL_DATA_INVERTED
    global DRAFTS_TABLE
    global PICKS_TABLE
    global PARSED_FILE_DICT
    global PARSED_DRAFT_DICT
    global ask_to_save
    global selected

    # Return if nothing is selected.
    selected = tree1.selection()
    if len(selected) == 0:
        return

    # Get Match/Draft_IDs of selected records.
    sel_matchid = []
    for i in selected:
        sel_matchid.append(list(tree1.item(i,"values"))[0])

    # Remove records from our table data and get table size differences.
    if display == "Matches":
        precounts = [len(ALL_DATA[0]),len(ALL_DATA[1]),len(ALL_DATA[2])]
        ALL_DATA[0] = [i for i in ALL_DATA[0] if i[0] not in sel_matchid]
        ALL_DATA[1] = [i for i in ALL_DATA[1] if i[0] not in sel_matchid]
        ALL_DATA[2] = [i for i in ALL_DATA[2] if i[0] not in sel_matchid]
        ALL_DATA_INVERTED[0] = [i for i in ALL_DATA_INVERTED[0] if i[0] not in sel_matchid]
        ALL_DATA_INVERTED[1] = [i for i in ALL_DATA_INVERTED[1] if i[0] not in sel_matchid]
        ALL_DATA_INVERTED[2] = [i for i in ALL_DATA_INVERTED[2] if i[0] not in sel_matchid]
        counts = [precounts[0]-len(ALL_DATA[0]),precounts[1]-len(ALL_DATA[1]),precounts[2]-len(ALL_DATA[2])]
    elif display == "Drafts":
        precounts = [len(DRAFTS_TABLE),len(PICKS_TABLE)]
        DRAFTS_TABLE = [i for i in DRAFTS_TABLE if i[0] not in sel_matchid]
        PICKS_TABLE = [i for i in PICKS_TABLE if i[0] not in sel_matchid]
        counts = [precounts[0]-len(DRAFTS_TABLE),precounts[1]-len(PICKS_TABLE)]

    # Remove GameLog filename from our list of previously parsed files.
    if ignore == False:
        if display == "Matches":
            for i in sel_matchid:
                for j in PARSED_FILE_DICT:
                    if PARSED_FILE_DICT[j][0] in sel_matchid:
                        PARSED_FILE_DICT.pop(j)
                        break
        elif display == "Drafts":
            for i in sel_matchid:
                for j in PARSED_DRAFT_DICT:
                    if PARSED_DRAFT_DICT[j] in sel_matchid:
                        PARSED_DRAFT_DICT.pop(j)
                        break          

    ask_to_save = True
    set_display(display,update_status=False,start_index=0,reset=True)
    if display == "Matches":
        if len(selected) == 1:
            update_status_bar(f"Removed {counts[0]} Match, {counts[1]} Games, and {counts[2]} Plays from Database.")
        else:
            update_status_bar(f"Removed {counts[0]} Matches, {counts[1]} Games, and {counts[2]} Plays from Database.")
    elif display == "Drafts":
        if len(selected) == 1:
            update_status_bar(f"Removed {counts[0]} Draft and {counts[1]} Draft Picks from Database.")
        else:
            update_status_bar(f"Removed {counts[0]} Drafts and {counts[1]} Draft Picks from Database.")
def remove_select():
    height = 150
    width =  350
    remove_select = tk.Toplevel(window)
    remove_select.title("Remove Record(s)")
    remove_select.iconbitmap(remove_select,"icon.ico")
    remove_select.minsize(width,height)
    remove_select.resizable(False,False)
    remove_select.grab_set()
    remove_select.focus()
    remove_select.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def close_window():
        remove_select.grab_release()
        remove_select.destroy()

    mid_frame = tk.LabelFrame(remove_select,text="")
    bot_frame = tk.Frame(remove_select)

    mid_frame.grid(row=0,column=0,sticky="nsew")
    bot_frame.grid(row=1,column=0,sticky="")

    remove_select.grid_columnconfigure(0,weight=1)
    remove_select.rowconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(1,weight=1)
    bot_frame.grid_columnconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(0,weight=1)
    bot_frame.grid_rowconfigure(1,weight=1)

    if len(tree1.selection()) == 1:
        t1 = "This will delete the selected Match and associated Games and Plays from your Database."
        t2 = "Would you like to ignore this Match in future imports?"
    else:
        t1 = "This will delete the selected Matches and associated Games and Plays from your Database."
        t2 = "Would you like to ignore these Matches in future imports?"

    label1 = tk.Label(mid_frame,text=t1,wraplength=width,anchor="s",justify="left")
    label2 = tk.Label(mid_frame,text=t2,wraplength=width,anchor="n")
    button_delete =  tk.Button(bot_frame,text="Remove",width=10,command=lambda : [close_window(),remove_record(ignore=False)])
    button_ignore = tk.Button(bot_frame,text="Remove and Ignore",width=15,command=lambda : [close_window(),remove_record(ignore=True)])
    button_close = tk.Button(bot_frame,text="Cancel",width=10,command=lambda : close_window())
    
    label1.grid(row=0,column=0,sticky="nsew",padx=20,pady=(0,5))
    label2.grid(row=1,column=0,sticky="nsew",padx=20,pady=(5,0))
    button_delete.grid(row=0,column=0,padx=5,pady=5)
    button_ignore.grid(row=0,column=1,padx=5,pady=5)
    button_close.grid(row=0,column=2,padx=5,pady=5)
    
    remove_select.protocol("WM_DELETE_WINDOW", lambda : close_window())
def user_inputs(type):
    match_dict = {}
    game_dict = {}
    player_dict = {}

    p1_index = modo.header("Matches").index("P1")
    p2_index = modo.header("Matches").index("P2")
    p1_arch_index = modo.header("Matches").index("P1_Arch")
    p2_arch_index = modo.header("Matches").index("P2_Arch")
    p1_sub_index = modo.header("Matches").index("P1_Subarch")
    p2_sub_index = modo.header("Matches").index("P2_Subarch")
    format_index = modo.header("Matches").index("Format")
    lformat_index = modo.header("Matches").index("Limited_Format")
    match_type_index = modo.header("Matches").index("Match_Type")

    gn_index = modo.header("Games").index("Game_Num")
    gw_index = modo.header("Games").index("Game_Winner")

    if type == "Matches":
        for i in ALL_DATA[0]:
            player_dict = {}
            player_dict[i[p1_index]] = [i[p1_arch_index],i[p1_sub_index]]
            player_dict[i[p2_index]] = [i[p2_arch_index],i[p2_sub_index]]
            match_dict[i[0]] = [player_dict,i[format_index],i[lformat_index],i[match_type_index]]
        return match_dict
    elif type == "Games":
        for i in ALL_DATA[1]:
            key = f"{i[0]}-{i[gn_index]}"
            game_dict[key] = [i[modo.header("Games").index("P1")],i[modo.header("Games").index("P2")],i[gw_index]]
        return game_dict
def debug():
    os.chdir(FILEPATH_ROOT)
    with open("DEBUG.txt","w",encoding="utf-8") as txt:
        txt.write("SETTINGS:\n")
        txt.write(f"FILEPATH_ROOT: {FILEPATH_ROOT}\n")
        txt.write(f"FILEPATH_EXPORT: {FILEPATH_EXPORT}\n")
        txt.write(f"FILEPATH_LOGS: {FILEPATH_LOGS}\n")
        txt.write(f"FILEPATH_LOGS_COPY: {FILEPATH_LOGS_COPY}\n")
        txt.write(f"FILEPATH_DRAFTS: {FILEPATH_DRAFTS}\n")
        txt.write(f"FILEPATH_DRAFTS_COPY: {FILEPATH_DRAFTS_COPY}\n")
        txt.write(f"HERO: {HERO}\n")
        txt.write(f"MAIN_WINDOW_SIZE: {MAIN_WINDOW_SIZE}\n")
        txt.write("\n")

        txt.write("INPUT_OPTIONS:\n")
        for i in INPUT_OPTIONS:
            txt.write(f"{i}: {INPUT_OPTIONS[i]}\n")
        txt.write("\n")
        txt.write(f"PARSED_FILE_DICT ({str(len(PARSED_FILE_DICT))} files):\n")
        for i in PARSED_FILE_DICT:
            txt.write(f"{i}: {PARSED_FILE_DICT[i]}\n")
        txt.write("\n")
        txt.write(f"PARSED_DRAFT_DICT ({str(len(PARSED_DRAFT_DICT))} files):\n")
        for i in PARSED_DRAFT_DICT:
            txt.write(f"{i}: {PARSED_DRAFT_DICT[i]}\n")
        txt.write("\n")

        txt.write(f"Matches: {str(len(ALL_DATA[0]))}\n")
        txt.write(f"Games: {str(len(ALL_DATA[1]))}\n")
        txt.write(f"Plays: {str(len(ALL_DATA[2]))}\n")
        txt.write(f"Drafts: {str(len(DRAFTS_TABLE))}\n")
        txt.write(f"Picks: {str(len(PICKS_TABLE))}\n")
        txt.write(f"Raw: {str(len(ALL_DATA[3]))}\n")
        txt.write(f"Matches (Inverse): {str(len(ALL_DATA_INVERTED[0]))} (should be {str(len(ALL_DATA[0])*2)})\n")
        txt.write(f"Games (Inverse): {str(len(ALL_DATA_INVERTED[1]))} (should be {str(len(ALL_DATA[1])*2)})\n")
        txt.write(f"Plays (Inverse): {str(len(ALL_DATA_INVERTED[2]))} (should be {str(len(ALL_DATA[2]))})\n")
        txt.write(f"Raw (Inverse): {str(len(ALL_DATA_INVERTED[3]))}\n")
        txt.write("\n")

        txt.write("ALL_DECKS:\n")
        txt.write(f"{list(ALL_DECKS.keys())[0]} to {list(ALL_DECKS.keys())[-1]}\n")
        for i in ALL_DECKS:
            txt.write(f"{i}: {str(len(ALL_DECKS[i]))}\n")
        txt.write("\n")

        txt.write("Other Variables:\n")
        txt.write(f"Display: {display}\n")
        txt.write(f"Previous Display: {prev_display}\n")
        txt.write(f"UAW: {uaw}\n")
        txt.write(f"Field: {field}\n")
        txt.write(f"New_Import: {new_import}\n")
        txt.write(f"Data_Loaded: {data_loaded}\n")
        txt.write(f"Filter_Changed: {filter_changed}\n")
        txt.write(f"Ask_To_Save: {ask_to_save}\n")
        txt.write(f"Selected: {selected}\n")
def test():
    # Test function
    pass

window = tk.Tk() 
window.title("MTGO-Tracker")
window.iconbitmap(window,"icon.ico")

load_window_size_setting()
window.geometry(str(MAIN_WINDOW_SIZE[1]) + "x" + str(MAIN_WINDOW_SIZE[2]))
window.resizable(False,False)

window.rowconfigure(0,weight=1)
window.columnconfigure(1,weight=1)

bottom_frame = tk.LabelFrame(window)
left_frame = tk.Frame(window)
text_frame = tk.LabelFrame(window,text="Dataframe")
bottom_frame.grid(row=1,column=1,sticky="ew")
left_frame.grid(row=0,column=0,sticky="ns")
text_frame.grid(row=0,column=1,sticky="nsew")

text_frame.grid_columnconfigure(0,weight=1)
text_frame.grid_columnconfigure(1,weight=0)
text_frame.grid_rowconfigure(0,weight=1)
text_frame.grid_rowconfigure(1,weight=0)
bottom_frame.grid_columnconfigure(0,weight=1)

match_button = tk.Button(left_frame,text="Matches",state=tk.DISABLED,\
    command=lambda : set_display("Matches",update_status=True,start_index=0,reset=True))
game_button = tk.Button(left_frame,text="Games",state=tk.DISABLED,\
    command=lambda : set_display("Games",update_status=True,start_index=0,reset=True))
play_button = tk.Button(left_frame,text="Plays",state=tk.DISABLED,\
    command=lambda : set_display("Plays",update_status=True,start_index=0,reset=True))
draft_button = tk.Button(left_frame,text="Drafts",state=tk.DISABLED,\
    command=lambda : set_display("Drafts",update_status=True,start_index=0,reset=True))
pick_button = tk.Button(left_frame,text="Draft Picks",state=tk.DISABLED,\
    command=lambda : set_display("Picks",update_status=True,start_index=0,reset=True))
stats_button = tk.Button(left_frame,text="Statistics",state=tk.DISABLED,command=lambda : get_stats())
filter_button = tk.Button(left_frame,text="Filter",state=tk.DISABLED,command=lambda : set_filter())
clear_button = tk.Button(left_frame,text="Clear Filter",state=tk.DISABLED,command=lambda : clear_filter(update_status=True,reload_display=True))
revise_button = tk.Button(left_frame,text="Revise Record(s)",state=tk.DISABLED,command=lambda : revise_method_select())
remove_button = tk.Button(left_frame,text="Remove Record(s)",state=tk.DISABLED,command=lambda : remove_select())
next_button = tk.Button(left_frame,text="Next",command=lambda : next_page())
back_button = tk.Button(left_frame,text="Back",state=tk.DISABLED,command=lambda : back())

status_label = tk.Label(bottom_frame,text="")
status_label.grid(row=0,column=0)

menu_bar = tk.Menu(window)

file_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="File",menu=file_menu)

file_menu.add_command(label="Import MTGO GameLogs",command=lambda : import_window())
file_menu.add_separator()
file_menu.add_command(label="Load Saved Data",command=lambda : load_saved_window())
file_menu.add_command(label="Save Data",command=lambda : save_window(exit=False),state=tk.DISABLED)
file_menu.add_separator()
file_menu.add_command(label="Set Main Window Size",command=lambda : set_default_window_size())
file_menu.add_separator()
file_menu.add_command(label="Exit",command=lambda : exit_select())

export_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="Export",menu=export_menu)

export_csv = tk.Menu(export_menu,tearoff=False)
export_csv.add_command(label="Match History",command=lambda : export2(matches=True,_csv=True))
export_csv.add_command(label="Game History",command=lambda : export2(games=True,_csv=True))
export_csv.add_command(label="Play History",command=lambda : export2(plays=True,_csv=True))
export_csv.add_command(label="Draft History",command=lambda : export2(drafts=True,_csv=True))
export_csv.add_command(label="Draft Pick History",command=lambda : export2(picks=True,_csv=True))
export_csv.add_command(label="All Data (5 Files)",\
    command=lambda : export2(matches=True,games=True,plays=True,drafts=True,picks=True,_csv=True))
export_csv.add_separator()
export_csv.add_command(label="Match History (Inverse Join)",command=lambda : export2(matches=True,_csv=True,inverted=True))
export_csv.add_command(label="Game History (Inverse Join)",command=lambda : export2(games=True,_csv=True,inverted=True))
export_csv.add_command(label="All Data (Inverse Join, 5 Files)",\
    command=lambda : export2(matches=True,games=True,plays=True,drafts=True,picks=True,_csv=True,inverted=True))
export_csv.add_separator()
export_csv.add_command(label="Currently Displayed Data (with Filters)",command=lambda : export2(current=True,_csv=True,filtered=True))

export_excel = tk.Menu(export_menu,tearoff=False)
export_excel.add_command(label="Match History",command=lambda : export2(matches=True,_excel=True))
export_excel.add_command(label="Game History",command=lambda : export2(games=True,_excel=True))
export_excel.add_command(label="Play History",command=lambda : export2(plays=True,_excel=True))
export_excel.add_command(label="Draft History",command=lambda : export2(drafts=True,_excel=True))
export_excel.add_command(label="Draft Pick History",command=lambda : export2(picks=True,_excel=True))
export_excel.add_command(label="All Data (5 Files)",\
    command=lambda : export2(matches=True,games=True,plays=True,drafts=True,picks=True,_excel=True))
export_excel.add_separator()
export_excel.add_command(label="Match History (Inverse Join)",command=lambda : export2(matches=True,_excel=True,inverted=True))
export_excel.add_command(label="Game History (Inverse Join)",command=lambda : export2(games=True,_excel=True,inverted=True))
export_excel.add_command(label="All Data (Inverse Join, 5 Files)",\
    command=lambda : export2(matches=True,games=True,plays=True,drafts=True,picks=True,_excel=True,inverted=True))
export_excel.add_separator()
export_excel.add_command(label="Currently Displayed Table (with Filters)",command=lambda : export2(current=True,_excel=True,filtered=True))

export_menu.add_cascade(label="Export to CSV",menu=export_csv)
export_menu.add_cascade(label="Export to Excel",menu=export_excel)
export_menu.add_separator()
export_menu.add_command(label="Set Default Export Folder",command=lambda : set_default_export())

data_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="Data",menu=data_menu)

data_menu.add_command(label="Input Missing Match Data",command=lambda : input_missing_data(),state=tk.DISABLED)
data_menu.add_command(label="Input Missing Game_Winner Data",command=lambda : get_winners(),state=tk.DISABLED)
data_menu.add_command(label="Apply Best Guess for Deck Names",command=lambda : rerun_decks_window(),state=tk.DISABLED)
data_menu.add_separator()
data_menu.add_command(label="Set Default Hero",command=lambda : set_default_hero(),state=tk.DISABLED)
data_menu.add_command(label="Set Default Import Folders",command=lambda : set_default_import())
data_menu.add_separator()
data_menu.add_command(label="Clear Loaded Data",command=lambda : clear_window(),state=tk.DISABLED)
data_menu.add_command(label="Delete Saved Session",command=lambda : delete_session())

if test_mode:
    test_menu = tk.Menu(menu_bar,tearoff=False)
    menu_bar.add_cascade(label="Test",menu=test_menu)
    test_menu.add_command(label="Create Debug Log",command=lambda : debug())
    test_menu.add_command(label="Test Function",command=lambda : test())

window.config(menu=menu_bar)

match_button.grid(row=1,column=0,sticky="ew",padx=5,pady=(15,5))
game_button.grid(row=2,column=0,sticky="ew",padx=5,pady=(0,5))
play_button.grid(row=3,column=0,sticky="ew",padx=5,pady=(0,5))
draft_button.grid(row=4,column=0,sticky="ew",padx=5,pady=(0,5))
pick_button.grid(row=5,column=0,sticky="ew",padx=5,pady=(0,5))
stats_button.grid(row=6,column=0,sticky="ew",padx=5,pady=(0,5))
filter_button.grid(row=7,column=0,sticky="ew",padx=5,pady=(25,5))
clear_button.grid(row=8,column=0,sticky="ew",padx=5,pady=(0,5))
revise_button.grid(row=9,column=0,sticky="ew",padx=5,pady=(25,5))
remove_button.grid(row=10,column=0,sticky="ew",padx=5,pady=(0,5))
next_button.grid(row=11,column=0,sticky="ew",padx=5,pady=(25,5))
back_button.grid(row=12,column=0,sticky="ew",padx=5,pady=(0,5))

tree1 = ttk.Treeview(text_frame,show="tree")
tree1.grid(row=0,column=0,sticky="nsew")
tree1.bind("<Double-1>",tree_double)
tree1.bind("<ButtonRelease-1>",activate_revise)

# tree_scrolly = tk.Scrollbar(text_frame,command=tree1.yview)
# tree1.configure(yscrollcommand=tree_scrolly.set)
# tree_scrolly.grid(row=0,column=1,sticky="ns")

tree_scrollx = tk.Scrollbar(text_frame,orient="horizontal",command=tree1.xview)
tree1.configure(xscrollcommand=tree_scrollx.set)
tree_scrollx.grid(row=1,column=0,sticky="ew")

s = ttk.Style()
s.theme_use("default")
s.configure("Treeview",
            background='white',
            fieldbackground='white')
s.map("Treeview",
      background=[("selected","#4a6984")],
      foreground=[("selected","#ffffff")])

startup()
window.protocol("WM_DELETE_WINDOW", lambda : exit_select())

# Event loop: listens for events (keypress, etc.)
# Blocks code after from running until window is closed.
window.mainloop()