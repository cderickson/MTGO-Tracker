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

# Saved data:
all_data =          [[],[],[],[]]
all_data_inverted = [[],[],[],[]]
all_headers =       [[],[],[]]
all_decks =         {}
parsed_file_list =  []

# Settings imported/saved in save folder:
filepath_root =     ""
filepath_export =   ""
filepath_decks =    ""
filepath_logs =     ""
hero =              ""
main_window_size =  ("small",1000,500)

input_options =     {}
filter_dict =       {}
display =           ""
data_loaded =       False
filter_changed =    False
prev_display =      ""
uaw =               "NA"
new_import =        False
field =             ""

def save_window():
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

    def save():
        save_settings()

        os.chdir(filepath_root + "\\" + "save")

        pickle.dump(all_data,open("all_data.p","wb"))
        pickle.dump(parsed_file_list,open("parsed_file_list.p","wb"))

        status_label.config(text="Save complete. Data will be loaded automatically on next startup.")
        os.chdir(filepath_root)
        close_save_window()

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

    label1 = tk.Label(mid_frame,text="This will overwrite any previously saved data.\nAre you sure you want to save?",wraplength=width)
    button_save = tk.Button(bot_frame,text="Save",command=lambda : save())
    button_close = tk.Button(bot_frame,text="Cancel",command=lambda : close_save_window())
    
    label1.grid(row=0,column=0,sticky="nsew")       
    button_save.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=1,padx=5,pady=5)
    
    save_window.protocol("WM_DELETE_WINDOW", lambda : close_save_window())
def choose_size_window():
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

    def save():
        global main_window_size

        if window_size.get() == "Small: 1000x500":
            main_window_size = ("small",1000,500)
        elif window_size.get() == "Large: 1750x750":
            main_window_size = ("large",1750,750)

        os.chdir(filepath_root + "\\" + "save")
        pickle.dump(main_window_size,open("main_window_size.p","wb"))
        status_label.config(text="Default Window Size saved. Change will take effect at next startup.")
        os.chdir(filepath_root)
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

    options = ["Small: 1000x500","Large: 1750x750"]
    window_size = tk.StringVar()
    if main_window_size[0] == "small":
        window_size.set(options[0])
    elif main_window_size[0] == "large":
        window_size.set(options[1])

    menu_1 = tk.OptionMenu(mid_frame,window_size,*options)
    label1 = tk.Label(mid_frame,text="Default Main Window Size",wraplength=width)
    button_save = tk.Button(bot_frame,text="Save",command=lambda : save())
    button_close = tk.Button(bot_frame,text="Cancel",command=lambda : close_window())
    
    menu_1.grid(row=0,column=0,sticky="s")
    label1.grid(row=1,column=0,sticky="n",pady=10)       
    button_save.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=1,padx=5,pady=5)
    
    popup.protocol("WM_DELETE_WINDOW", lambda : close_window())
def clear_loaded():
    global all_data
    global all_data_inverted
    global parsed_file_list
    global hero
    global filter_dict
    global display
    global data_loaded
    global filter_changed
    global prev_display
    global uaw
    global new_import

    all_data =          [[],[],[],[]]
    all_data_inverted = [[],[],[],[]]
    parsed_file_list =  []
    hero =              ""
    filter_dict.clear()
    display =           ""
    data_loaded =       False
    filter_changed =    False
    prev_display =      ""
    uaw =               "NA"
    new_import =        False

    match_button["state"] = tk.DISABLED
    game_button["state"] = tk.DISABLED
    play_button["state"] = tk.DISABLED
    filter_button["state"] = tk.DISABLED
    clear_button["state"] = tk.DISABLED
    revise_button["state"] = tk.DISABLED
    stats_button["state"] = tk.DISABLED
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
        status_label.config(text="Previously loaded data has been cleared.")
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
    button_clear = tk.Button(bot_frame,text="Clear",command=lambda : clear())
    button_close = tk.Button(bot_frame,text="Cancel",command=lambda : close_clear_window())
    
    label1.grid(row=0,column=0,sticky="nsew")       
    button_clear.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=1,padx=5,pady=5)
    
    clear_window.protocol("WM_DELETE_WINDOW", lambda : close_clear_window())
def load_saved_window():
    height = 100
    width =  300
    load_saved_window = tk.Toplevel(window)
    load_saved_window.title("Clear Saved Data")
    load_saved_window.iconbitmap(load_saved_window,"icon.ico")
    load_saved_window.minsize(width,height)
    load_saved_window.resizable(False,False)
    load_saved_window.grab_set()
    load_saved_window.focus()

    load_saved_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def load():
        clear_filter()
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
    button_load = tk.Button(bot_frame,text="Load",command=lambda : load())
    button_close = tk.Button(bot_frame,text="Cancel",command=lambda : close_load_window())
    
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
        global all_decks
        all_decks.clear()

        files = ["all_data.p","parsed_file_list.p","all_decks.p","settings.p","main_window_size.p"]
        os.chdir(filepath_root + "\\" + "save")   

        session_exists = False
        for i in files:
            if os.path.exists(i):
                session_exists = True
                os.remove(i)

        if session_exists == True:
            status_label.config(text="Saved session data has been deleted.")
        else:
            status_label.config(text="No saved session data was found.")

        os.chdir(filepath_root)
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
    button_del = tk.Button(bot_frame,text="Delete Saved Session",command=lambda : del_session())
    button_close = tk.Button(bot_frame,text="Cancel",command=lambda : close_del_window())
    
    label1.grid(row=0,column=0,sticky="nsew")       
    button_del.grid(row=0,column=0,padx=5,pady=5)
    button_close.grid(row=0,column=1,padx=5,pady=5)
    
    del_window.protocol("WM_DELETE_WINDOW", lambda : close_del_window())
def startup():
    global filepath_root
    global filepath_export
    global filepath_decks
    global filepath_logs
    global hero
    global all_data
    global all_data_inverted
    global all_decks
    global parsed_file_list
    global data_loaded
    global input_options

    if os.path.isfile("input_options.txt"):
        in_header = False
        in_instr = True
        x = ""
        y = []
        with io.open("input_options.txt","r",encoding="ansi") as file:
            initial = file.read().split("\n")
            for i in initial:
                if i == "-----------------------------":
                    if in_instr:
                        in_instr = False
                    in_header = not in_header
                    if in_header == False:
                        x = last.split(":")[0].split("# ")[1]
                    elif x != "":
                        input_options[x] = y
                        y = []                        
                elif (in_header == False) and (i != "") and (in_instr == False):
                    y.append(i)
                last = i
    else:
        input_options["Constructed Match Types"] = modo.match_types()
        input_options["Booster Draft Match Types"] = modo.match_type_booster()
        input_options["Sealed Match Types"] = modo.match_type_sealed()
        input_options["Archetypes"] = modo.archetypes()
        input_options["Constructed Formats"] = modo.con_formats()
        input_options["Limited Formats"] = modo.limited_formats()
        input_options["Cube Formats"] = modo.cube_formats()
        input_options["Booster Draft Formats"] = modo.draft_formats()
        input_options["Sealed Formats"] = modo.sealed_formats()
    
    filepath_root = os.getcwd()
    if os.path.isdir("lists") == False:
        os.mkdir(filepath_root + "\\" + "lists")
    filepath_decks = filepath_root + "\\" + "lists"

    if os.path.isdir("save") == False:
        os.mkdir(filepath_root + "\\" + "save")
    os.chdir(filepath_root + "\\" + "save")

    if os.path.isfile("settings.p"):
        settings = pickle.load(open("settings.p","rb"))
        #filepath_root =   settings[0]
        filepath_export = settings[1]
        #filepath_decks =  settings[2]
        filepath_logs =   settings[3]
        hero =            settings[4]

    all_headers[0] = modo.match_header()
    all_headers[1] = modo.game_header()
    all_headers[2] = modo.play_header()

    if (os.path.isfile("all_data.p") == False) or (os.path.isfile("parsed_file_list.p") == False) or (os.path.isfile("all_decks.p") == False):
        status_label.config(text="No session data to load. Import your MTGO GameLog files to get started.")
        os.chdir(filepath_root)
        return
    all_data = pickle.load(open("all_data.p","rb"))
    all_decks = pickle.load(open("all_decks.p","rb"))
    parsed_file_list = pickle.load(open("parsed_file_list.p","rb"))

    all_data_inverted = modo.invert_join(all_data)

    status_label.config(text="Imported " + str(len(all_data[0])) + " matches.")

    filter_button["state"] = tk.NORMAL
    clear_button["state"] = tk.NORMAL
    if hero != "":
        stats_button["state"] = tk.NORMAL
    data_loaded = True

    set_display("Matches")
    data_menu.entryconfig("Set Default Hero",state=tk.NORMAL)
    data_menu.entryconfig("Clear Loaded Data",state=tk.NORMAL)
    file_menu.entryconfig("Save Data",state=tk.NORMAL)
    data_menu.entryconfig("Input Missing Match Data",state=tk.NORMAL)
    data_menu.entryconfig("Input Missing Game_Winner Data",state=tk.NORMAL)
    data_menu.entryconfig("Apply Best Guess for Deck Names",state=tk.NORMAL)

    os.chdir(filepath_root)
def save_settings():
    os.chdir(filepath_root + "\\" + "save")
    settings = [filepath_root,filepath_export,filepath_decks,filepath_logs,hero]
    pickle.dump(settings,open("settings.p","wb"))
    pickle.dump(all_decks,open("all_decks.p","wb"))
    pickle.dump(main_window_size,open("main_window_size.p","wb"))
    os.chdir(filepath_root)
def set_display(d,*argv):
    global display
    global prev_display

    if data_loaded == False:
        return

    if display != d:
        prev_display = display
        display = d
        
    text_frame.config(text=display)

    if len(argv) > 0:
        if argv[0] == True:
            back_button["state"] = tk.NORMAL
        else:
            back_button["state"] = tk.DISABLED
    
    if match_button["state"] == tk.DISABLED:
        match_button["state"] = tk.NORMAL
    if game_button["state"] == tk.DISABLED:
        game_button["state"] = tk.NORMAL
    if play_button["state"] == tk.DISABLED:
        play_button["state"] = tk.NORMAL
    # if stats_button["state"] == tk.DISABLED:
    #     stats_button["state"] = tk.NORMAL
        
    if d == "Matches":
        back_button["state"] = tk.DISABLED
        print_data(all_data[0],all_headers[0])
    elif d == "Games":
        back_button["state"] = tk.NORMAL
        print_data(all_data[1],all_headers[1])
    elif d == "Plays":
        back_button["state"] = tk.NORMAL
        print_data(all_data[2],all_headers[2])
def get_all_data():
    global all_data
    global all_data_inverted
    global all_headers
    global data_loaded
    global parsed_file_list
    global new_import
    count = 0

    new_data = [[],[],[],[]]
    os.chdir(filepath_logs)
    n = 0
    for (root,dirs,files) in os.walk(filepath_logs):
        for i in files:
            if ("Match_GameLog_" not in i) or (len(i) < 30):
                pass
            elif (i in parsed_file_list):
                pass
            else:
                os.chdir(root)
                with io.open(i,"r",encoding="ansi") as gamelog:
                    initial = gamelog.read()
                    mtime = time.ctime(os.path.getmtime(i))
                parsed_data = modo.get_all_data(initial,mtime)
                parsed_file_list.append(i)
                count += 1

                new_data[0].append(parsed_data[0])
                for i in parsed_data[1]:
                    new_data[1].append(i)
                for i in parsed_data[2]:
                    new_data[2].append(i)
                for i in parsed_data[3]:
                    new_data[3].append(i)

    new_data_inverted = modo.invert_join(new_data)
    for index,i in enumerate(new_data):
        for j in new_data[index]:
            all_data[index].append(j)
    for index,i in enumerate(new_data_inverted):
        for j in new_data_inverted[index]:
            all_data_inverted[index].append(j)

    status_label.config(text="Imported " + str(count) + " new matches.")
    new_import = True

    if len(all_data[0]) != 0:
        filter_button["state"] = tk.NORMAL
        clear_button["state"] = tk.NORMAL
        data_loaded = True
    os.chdir(filepath_root)
def print_data(data,header):
    global new_import
    small_headers = ["P1_Roll","P2_Roll","P1_Wins","P2_Wins","Game_Num","Play_Num","Turn_Num"]

        # Clear existing data in tree
    tree1.delete(*tree1.get_children())

    tree1["column"] = header
    tree1["show"] = "headings"

        # Insert column headers into tree
    for i in tree1["column"]:
        if i in small_headers:
            tree1.column(i,anchor="center",stretch=False,width=75)
        else:
            tree1.column(i,anchor="center",stretch=False,width=100)
        if (i == "Turns") or (i == "Play_Num") or (i == "Turn_Num") or (i == "Cards_Drawn") or (i == "Attackers"):
            tree1.heading(i,text=i,command=lambda _col=i: sort_column_int(_col,False,tree1))
        else:
            tree1.heading(i,text=i,command=lambda _col=i: sort_column(_col,False,tree1))
    tree1.column("Match_ID",anchor="w")
    
    if (hero != "") & (display == "Matches"):
        df = modo.to_dataframe(all_data_inverted[0],all_headers[0])
        df = df[(df.P1 == hero)]
    elif (hero != "") & (display == "Games"):
        df = modo.to_dataframe(all_data_inverted[1],all_headers[1])
        df = df[(df.P1 == hero)]
    else:
        df = modo.to_dataframe(data,header)
    total = df.shape[0]
    for key in filter_dict:
        if key not in header:
            break
        for i in filter_dict[key]:
            if i[2:].isnumeric():
                value = int(i[2:])
            else:
                value = i[2:]
            if i[0] == "=":
                if key == "Date":
                    print(value[0:10])
                    df = df[(df[key].str.contains(value[0:10]))]
                else:
                    df = df[(df[key] == value)]
            elif i[0] == ">":
                df = df[(df[key] > value)]
            elif i[0] == "<":
                df = df[(df[key] < value)]
    if (display == "Matches") or (display == "Games"):
        df = df.sort_values(by=["Match_ID"],ascending=False)
    elif display == "Plays":
        df = df.sort_values(by=["Match_ID","Game_Num","Play_Num"],ascending=(False,True,True))
    df_rows = df.to_numpy().tolist()
    for i in df_rows:
        tree1.insert("","end",values=i)

    if new_import == True:
        new_import = False
    else:
        status_label.config(text="Displaying: " + str(len(df_rows)) + " of " + str(total) + " records.")
    revise_button["state"] = tk.DISABLED
def get_lists():
    global all_decks
    
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
            month_decks.append(deck)
        all_decks[i] = month_decks
    os.chdir(filepath_root)
def input_missing_data():
    global all_data
    global all_data_inverted
  
    mformat_index = modo.match_header().index("Format")
    lformat_index = modo.match_header().index("Limited_Format")
    mtype_index =   modo.match_header().index("Match_Type")
    p1_arch_index = modo.match_header().index("P1_Arch")
    p1_sub_index =  modo.match_header().index("P1_Subarch")
    p2_arch_index = modo.match_header().index("P2_Arch")
    p2_sub_index =  modo.match_header().index("P2_Subarch")

    n = 0
    count = 0
    total = len(all_data[0])
    for i in all_data[0]:    # Iterate through matches.
        n += 1
        
        # Match record is missing some data.
        if (i[p1_arch_index] == "NA") or (i[p1_sub_index] == "NA") or \
            (i[p2_arch_index] == "NA") or (i[p2_sub_index] == "NA") or \
            (i[p1_sub_index] == "Unknown") or (i[p2_sub_index] == "Unknown") or \
            (i[mformat_index] == "NA") or (i[mtype_index] == "NA") or \
            ((i[mformat_index] in input_options["Limited Formats"]) & (i[lformat_index] == "NA")): 
            count += 1
            df = modo.to_dataframe(all_data[2],modo.play_header())
            df = df[(df.Match_ID == i[0])]
            players = [i[modo.match_header().index("P1")],i[modo.match_header().index("P2")]]
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
        status_label.config(text="No Matches with Missing Data.")
    else:
        all_data_inverted = modo.invert_join(all_data)
        set_display("Matches")
def deck_data_guess(update_type):
    global all_data
    global all_data_inverted

    date_index = modo.match_header().index("Date")
    p1_index = modo.match_header().index("P1")
    p2_index = modo.match_header().index("P2")
    p1_sa_index = modo.match_header().index("P1_Subarch")
    p2_sa_index = modo.match_header().index("P2_Subarch")
    format_index = modo.match_header().index("Format")
    df2 = modo.to_dataframe(all_data[2],modo.play_header())

    for i in all_data[0]:
        yyyy_mm = i[date_index][0:4] + "-" + i[date_index][5:7]
        players = [i[p1_index],i[p2_index]]
        
        # Skip Limited Matches.
        # if i[format_index] in input_options["Limited Formats"]:
        #     continue

        if update_type == "Limited":
            if i[format_index] in input_options["Limited Formats"]:
                cards1 = df2[(df2.Casting_Player == players[0]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                cards2 = df2[(df2.Casting_Player == players[1]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                i[p1_sa_index] = modo.get_limited_subarch(cards1)
                i[p2_sa_index] = modo.get_limited_subarch(cards2)

        # Update P1_Subarch, P2_Subarch for all Matches.
        elif update_type == "All":
            cards1 = df2[(df2.Casting_Player == players[0]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
            cards2 = df2[(df2.Casting_Player == players[1]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
            if i[format_index] in input_options["Limited Formats"]:
                i[p1_sa_index] = modo.get_limited_subarch(cards1)
                i[p2_sa_index] = modo.get_limited_subarch(cards2)
            else: 
                p1_data = modo.closest_list(set(cards1),all_decks,yyyy_mm)
                p2_data = modo.closest_list(set(cards2),all_decks,yyyy_mm)
                i[p1_sa_index] = p1_data[0]
                i[p2_sa_index] = p2_data[0]

            # if p1_data[1] == p2_data[1]:
            #     i[format_index] = p1_data[1]
            # Uncomment if we want to update Format column if Best Guesses have matching Format.

        # Update P1_Subarch, P2_Subarch only if equal to "Unknown" or "NA".
        elif update_type == "Unknowns":
            if (i[p1_sa_index] == "Unknown") or (i[p1_sa_index] == "NA"):
                cards1 = df2[(df2.Casting_Player == players[0]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                if i[format_index] in input_options["Limited Formats"]:
                    i[p1_sa_index] = modo.get_limited_subarch(cards1)
                else:
                    p1_data = modo.closest_list(set(cards1),all_decks,yyyy_mm)
                    i[p1_sa_index] = p1_data[0]
            if (i[p2_sa_index] == "Unknown") or (i[p2_sa_index] == "NA"):
                cards2 = df2[(df2.Casting_Player == players[1]) & (df2.Match_ID == i[0])].Primary_Card.value_counts().keys().tolist()
                if i[format_index] in input_options["Limited Formats"]:
                    i[p2_sa_index] = modo.get_limited_subarch(cards2)
                else:
                    p2_data = modo.closest_list(set(cards2),all_decks,yyyy_mm)
                    i[p2_sa_index] = p2_data[0]

    all_data_inverted = modo.invert_join(all_data)
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

    def apply_to_all():
        deck_data_guess(update_type="All")
        set_display("Matches")
        t = "Updated the P1_Subarch, P2_Subarch columns for each Match in the Date Range: " + list(all_decks.keys())[0]
        if len(all_decks) > 1:
            t += " to " + list(all_decks.keys())[-1]
        status_label.config(text=t)
        close()

    def apply_to_unknowns():
        deck_data_guess(update_type="Unknowns")
        set_display("Matches")
        t = "Updated the P1_Subarch, P2_Subarch columns for Unknown Decks in the Date Range: " + list(all_decks.keys())[0]
        if len(all_decks) > 1:
            t += " to " + list(all_decks.keys())[-1]
        status_label.config(text=t)
        close()

    def apply_to_limited():
        deck_data_guess(update_type="Limited")
        set_display("Matches")
        t = "Updated the P1_Subarch, P2_Subarch columns for Limited Matches in the Date Range: " + list(all_decks.keys())[0]
        if len(all_decks) > 1:
            t += " to " + list(all_decks.keys())[-1]
        status_label.config(text=t)
        close()

    def guess(mode):
        if mode == "Overwrite All":
            apply_to_all()
        elif mode == "Unknown Decks Only":
            apply_to_unknowns()
        elif mode == "Limited (Non-Cube) Decks Only":
            apply_to_limited()

    def get_decks_path():
        fp_decks = filedialog.askdirectory()  
        fp_decks = os.path.normpath(fp_decks)
        if (fp_decks is None) or (fp_decks == "") or (fp_decks == "."):
            label1.config(text="No Default Decklists Folder")
            #button_apply_all["state"] = tk.DISABLED
            #button_apply_unknown["state"] = tk.DISABLED
            button_apply["state"] = tk.DISABLED
        else:
            label1.config(text=fp_decks)
            #button_apply_all["state"] = tk.NORMAL
            #button_apply_unknown["state"] = tk.NORMAL
            button_apply["state"] = tk.NORMAL
        button2["state"] = tk.NORMAL

    def import_decks():
        global all_decks
        global filepath_decks
        
        if (label1["text"] == "No Default Decklists Folder"):
            label3["text"] = "Decks and/or Game Logs Folder Location not set."
            return
        filepath_decks = label1["text"]

        all_decks.clear()

        get_lists()
        if len(all_decks) == 0:
            label2["text"] = "Sample decklists loaded: NONE"
            #button_apply_all["state"] = tk.DISABLED
            #button_apply_unknown["state"] = tk.DISABLED
            button_apply["state"] = tk.DISABLED
        elif len(all_decks) == 1:
            label2["text"] = "Sample decklists loaded: " + list(all_decks.keys())[0]
            #button_apply_all["state"] = tk.NORMAL
            #button_apply_unknown["state"] = tk.NORMAL
            button_apply["state"] = tk.NORMAL
        else:
            label2["text"] = "Sample decklists loaded: " + list(all_decks.keys())[0] + " to " + list(all_decks.keys())[-1]
            #button_apply_all["state"] = tk.NORMAL
            #button_apply_unknown["state"] = tk.NORMAL
            button_apply["state"] = tk.NORMAL

        button2["state"] = tk.DISABLED

    def close():
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

    apply_options = ["Overwrite All","Unknown Decks Only","Limited (Non-Cube) Decks Only"]
    apply_mode = tk.StringVar()
    apply_mode.set(apply_options[0])

    button2 = tk.Button(mid_frame,text="Import Sample Decklists",command=lambda : import_decks())
    label2 = tk.Label(mid_frame,text="",wraplength=width)
    label3 = tk.Label(mid_frame,text="This will apply best guess deck names in the P1/P2_Subarch columns.\n\nChoose which rows to apply changes.",wraplength=width)
    #button_apply_all = tk.Button(bot_frame,text="Apply to All",command=lambda : apply_to_all())
    #button_apply_unknown = tk.Button(bot_frame,text="Apply to Unknowns",command=lambda : apply_to_unknowns())
    apply_menu = tk.OptionMenu(bot_frame,apply_mode,*apply_options)
    button_apply = tk.Button(bot_frame,text="Apply",command=lambda : guess(apply_mode.get()))
    button_close = tk.Button(bot_frame,text="Cancel",command=lambda : close())

    if len(all_decks) == 0:
        label2["text"] = "Sample decklists loaded: NONE"
    elif len(all_decks) == 1:
        label2["text"] = "Sample decklists loaded: " + list(all_decks.keys())[0]
    else:
        label2["text"] = "Sample decklists loaded: " + list(all_decks.keys())[0] + " to " + list(all_decks.keys())[-1]

    fp_decks = filepath_decks
    if (filepath_decks is None) or (filepath_decks == "") or (filepath_decks == "."):
        label1 = tk.Label(mid_frame,text="No Default Decklists Folder",wraplength=width,justify="left")
        #button_apply_all["state"] = tk.DISABLED
        #button_apply_unknown["state"] = tk.DISABLED
        button_apply["state"] = tk.DISABLED
    else:
        label1 = tk.Label(mid_frame,text=filepath_decks,wraplength=width,justify="left")

    label2.grid(row=1,column=0,padx=10,pady=(20,0),sticky="nsew")
    button2.grid(row=2,column=0,padx=10,pady=5) 
    label3.grid(row=3,column=0,padx=10,pady=(10,5),sticky="nsew")       
    #button_apply_all.grid(row=0,column=0,padx=10,pady=10)
    #button_apply_unknown.grid(row=0,column=1,padx=10,pady=10)
    apply_menu.grid(row=0,column=0,padx=10,pady=10)
    button_apply.grid(row=0,column=1,padx=10,pady=10)
    button_close.grid(row=0,column=2,padx=10,pady=10)   

    if len(all_decks) == 0:
        #button_apply_all["state"] = tk.DISABLED
        #button_apply_unknown["state"] = tk.DISABLED
        button_apply["state"] = tk.DISABLED

    rerun_decks_window.protocol("WM_DELETE_WINDOW", lambda : close())
def revise_entry_window(players,cards1,cards2,card3,cards4,progress,mdata):
    def close_format_window(*argv):
        global missing_data
        missing_data = [p1_arch.get(),p1_sub.get(),p2_arch.get(),p2_sub.get(),mformat.get(),dformat.get(),mtype.get()]
        if missing_data[0] == "Select P1 Archetype":
            missing_data[0] = "NA"
        if missing_data[2] == "Select P2 Archetype":
            missing_data[2] = "NA"
        if missing_data[4] == "Select Format":
            missing_data[4] = "NA"
        if missing_data[5] == "Select Limited Format":
            missing_data[5] = "NA"
        if missing_data[6] == "Select Match Type":
            missing_data[6] = "NA"         
        for i in argv:
            missing_data = i
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
    gf.focus()

    gf.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))
    message = "Date Played: " + mdata[modo.match_header().index("Date")]
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
            for i in ["NA"] + input_options["Constructed Match Types"] + input_options["Booster Draft Match Types"] + input_options["Sealed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: mtype.set(x))
        elif mformat.get() in input_options["Constructed Formats"]:
            for i in ["NA"] + input_options["Constructed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: mtype.set(x))
        elif (mformat.get() == "Cube") or (mformat.get() == "Booster Draft"):
            for i in ["NA"] + input_options["Booster Draft Match Types"]:
                menu.add_command(label=i,command=lambda x=i: mtype.set(x))
        elif mformat.get() == "Sealed Deck":
            for i in ["NA"] + input_options["Sealed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: mtype.set(x))

        if mformat.get() in input_options["Limited Formats"]:
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
                for i in input_options["Cube Formats"]:
                    menu.add_command(label=i,command=lambda x=i: dformat.set(x))
            elif mformat.get() == "Booster Draft":
                for i in input_options["Booster Draft Formats"]:
                    menu.add_command(label=i,command=lambda x=i: dformat.set(x))
            elif mformat.get() == "Sealed Deck":
                for i in input_options["Sealed Formats"]:
                    menu.add_command(label=i,command=lambda x=i: dformat.set(x))            

            p1_arch.set(arch_options[0])
            p2_arch.set(arch_options[0])
            dformat.set("Select Limited Format")
        elif (p1_arch.get() == "Limited"):
            draft_format["state"] = tk.DISABLED
            dformat.set("Select Limited Format")
            arch_options = ["NA"] + input_options["Archetypes"]

            menu = p1_arch_menu["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p1_arch.set(x))

            menu = p2_arch_menu["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p2_arch.set(x))

            if mdata[modo.match_header().index("P1_Arch")] == "NA":
                p1_arch.set("Select P1 Archetype")
            else:
                p1_arch.set(mdata[modo.match_header().index("P1_Arch")])

            if mdata[modo.match_header().index("P2_Arch")] == "NA":
                p2_arch.set("Select P2 Archetype")
            else:
                p2_arch.set(mdata[modo.match_header().index("P2_Arch")])

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

    submit_button = tk.Button(bot_frame2,text="Apply Changes",command=lambda : [close_format_window()])

    arch_options = ["NA"] + input_options["Archetypes"]
    p1_arch = tk.StringVar()
    p1_arch.set("Select P1 Archetype")
    p2_arch = tk.StringVar()
    p2_arch.set("Select P2 Archetype")

    format_options = ["NA"] + input_options["Constructed Formats"] + input_options["Limited Formats"]
    mformat = tk.StringVar()
    mformat.set("Select Format")

    type_options = ["NA"]
    mtype = tk.StringVar()
    mtype.set("Select Match Type")

    draft_format_options = ["NA"]
    dformat = tk.StringVar()
    dformat.set("Select Limited Format")

    if mdata[modo.match_header().index("P1_Arch")] != "NA":
        p1_arch.set(mdata[modo.match_header().index("P1_Arch")])
    if mdata[modo.match_header().index("P2_Arch")] != "NA":
        p2_arch.set(mdata[modo.match_header().index("P2_Arch")])
    if mdata[modo.match_header().index("Format")] != "NA": 
        mformat.set(mdata[modo.match_header().index("Format")])
    if mdata[modo.match_header().index("Limited_Format")] != "NA":
        dformat.set(mdata[modo.match_header().index("Limited_Format")])
    if mdata[modo.match_header().index("Match_Type")] != "NA":
        mtype.set(mdata[modo.match_header().index("Match_Type")])
    
    if mformat.get() == "Cube":
        draft_format_options += input_options["Cube Formats"]
        type_options += input_options["Booster Draft Match Types"]
    elif mformat.get() == "Booster Draft":
        draft_format_options += input_options["Booster Draft Formats"]
        type_options += input_options["Booster Draft Match Types"]
    elif mformat.get() == "Sealed Deck":
        draft_format_options += input_options["Sealed Formats"]
        type_options += input_options["Sealed Match Types"]
    elif mformat.get() in input_options["Constructed Formats"]:
        type_options += input_options["Constructed Match Types"]
    elif mformat.get() == "Select Format":
        type_options += input_options["Constructed Match Types"] + input_options["Booster Draft Match Types"] + input_options["Sealed Match Types"]

    p1_arch_menu = tk.OptionMenu(mid_frame1,p1_arch,*arch_options)
    p1_sub =  tk.Entry(mid_frame1)
    p2_arch_menu = tk.OptionMenu(mid_frame2,p2_arch,*arch_options)
    p2_sub =  tk.Entry(mid_frame2)

    match_format = tk.OptionMenu(bot_frame2,mformat,*format_options)
    match_type = tk.OptionMenu(bot_frame2,mtype,*type_options)
    draft_format = tk.OptionMenu(bot_frame2,dformat,*draft_format_options)
    p1_sub.insert(0,mdata[modo.match_header().index("P1_Subarch")])
    p2_sub.insert(0,mdata[modo.match_header().index("P2_Subarch")])

    button_skip = tk.Button(top_frame,text="Skip Match",command=lambda : [close_format_window("Skip")])
    button_exit = tk.Button(top_frame,text="Exit",command=lambda : [close_format_window("Exit")])
    
    label1.grid(row=0,column=0,sticky="nsew",padx=5,pady=5)
    label2.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
    label3.grid(row=0,column=0,sticky="nsew",padx=5,pady=5)
    label4.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
    p1_arch_menu.grid(row=1,column=0)
    p1_sub.grid(row=1,column=1)
    p2_arch_menu.grid(row=1,column=0)
    p2_sub.grid(row=1,column=1)
  
    button_skip.grid(row=0,column=0,padx=10,pady=10)
    label_message.grid(row=0,column=1,padx=10,pady=10)
    button_exit.grid(row=0,column=2,padx=10,pady=10)

    match_format.grid(row=0,column=0,padx=10,pady=10)
    draft_format.grid(row=0,column=1,padx=10,pady=10)
    match_type.grid(row=0,column=2,padx=10,pady=10)
    submit_button.grid(row=0,column=3,padx=10,pady=10)

    if mformat.get() not in input_options["Limited Formats"]:
        draft_format["state"] = tk.DISABLED

    mformat.trace("w",update_arch)

    gf.protocol("WM_DELETE_WINDOW", lambda : close_format_window("Exit"))
    gf.wait_window()
def tree_double(event):
    global filter_dict
    
    if tree1.focus() == "":
        return None
    if display == "Plays":
        return None
    if tree1.identify_region(event.x,event.y) == "separator":
        return None
    if tree1.identify_region(event.x,event.y) == "heading":
        return None    
        
    clear_filter()
    add_filter_setting("Match_ID",tree1.item(tree1.focus(),"values")[0],"=")
    if display == "Matches":
        set_display("Games",True)
    elif display == "Games":
        add_filter_setting("Game_Num",tree1.item(tree1.focus(),"values")[3],"=")
        set_display("Plays",True)
def bb_clicked():
    global filter_dict
    
    if "Match_ID" in filter_dict:
        match_id = filter_dict["Match_ID"][0][2:]
        clear_filter()
        add_filter_setting("Match_ID",match_id,"=")
    else:
        clear_filter()
    if display == "Games":
        set_display("Matches")
    elif display == "Plays":
        set_display("Games")
def export(file_type,data_type,inverted):
    # File_Type: String, "CSV" or "Excel"
    # Data_Type: Int, 0=Match,1=Game,2=Play,3=All,4=Filtered
    # Inverted:  Bool

    global filepath_export
    fp = filepath_export
    if (filepath_export is None) or (filepath_export == ""):
        filepath_export = filedialog.askdirectory()
        filepath_export = os.path.normpath(filepath_export)
    if filepath_export is None:
        return

    if (hero != "") or (inverted == True):
        data_to_write = all_data_inverted
    else:
        data_to_write = all_data

    # Outputting filtered data.
    # Create Dataframe and apply filters.
    if data_type == 4:
        if display == "Matches":
            df_filtered = modo.to_dataframe(data_to_write[0],all_headers[0])
            headers = all_headers[0]
            file_names = ["matches"]
        elif display == "Games":
            df_filtered = modo.to_dataframe(data_to_write[1],all_headers[1])
            headers = all_headers[1]
            file_names = ["games"]
        elif display == "Plays":
            df_filtered = modo.to_dataframe(data_to_write[2],all_headers[2])
            headers = all_headers[2]
            file_names = ["plays"]
        if hero != "":
            df_filtered = df_filtered[(df_filtered.P1 == hero)]
        for key in filter_dict:
            if key not in headers:
                break
            for i in filter_dict[key]:
                if i[2:].isnumeric():
                    value = int(i[2:])
                else:
                    value = i[2:]
                if i[0] == "=":
                    if key == "Date":
                        df_filtered = df_filtered[(df_filtered[key].str.contains(value[0:10]))]
                    else:
                        df_filtered = df_filtered[(df_filtered[key] == value)]
                elif i[0] == ">":
                    df_filtered = df_filtered[(df_filtered[key] > value)]
                elif i[0] == "<":
                    df_filtered = df_filtered[(df_filtered[key] < value)]
    elif data_type == 3:
        df_filtered_0 = modo.to_dataframe(data_to_write[0],all_headers[0])
        df_filtered_1 = modo.to_dataframe(data_to_write[1],all_headers[1])
        df_filtered_2 = modo.to_dataframe(data_to_write[2],all_headers[2])
        if (hero != "") & (inverted == False):
            df_filtered_0 = df_filtered_0[(df_filtered_0.P1 == hero)]
            df_filtered_1 = df_filtered_1[(df_filtered_1.P1 == hero)]
        df_list = [df_filtered_0,df_filtered_1,df_filtered_2]
    elif data_type == 2:
        df_filtered = modo.to_dataframe(data_to_write[data_type],all_headers[data_type])     
    elif data_type < 2:
        df_filtered = modo.to_dataframe(data_to_write[data_type],all_headers[data_type])
        if (hero != "") & (inverted == False):
            df_filtered = df_filtered[(df_filtered.P1 == hero)]

    # Create List of applicable file names.
    all_file_names = ["matches","games","plays"]
    if data_type == 3:
        headers = all_headers
        file_names = all_file_names
    elif data_type < 3:
        headers = [all_headers[data_type]]
        file_names = [all_file_names[data_type]]
    for index,i in enumerate(file_names):
        if file_type == "CSV":
            file_names[index] = i + ".csv"
        else:
            file_names[index] = i + ".xlsx"

    if file_type == "CSV":
        for i in range(len(file_names)):
            with open(filepath_export+"/"+file_names[i],"w",encoding="UTF8",newline="") as file:
                writer = csv.writer(file)
                if data_type == 3:
                    writer.writerow(headers[i])
                    df_rows = df_list[i].to_numpy().tolist()
                    for row in df_rows:
                        writer.writerow(row)
                elif data_type == 4:
                    writer.writerow(headers)
                    df_rows = df_filtered.to_numpy().tolist()
                    for row in df_rows:
                        writer.writerow(row)
                else:
                    writer.writerow(headers[i])
                    df_rows = df_filtered.to_numpy().tolist()
                    for row in df_rows:
                        writer.writerow(row)
    elif file_type == "Excel":
        for i in range(len(file_names)):
            f = filepath_export+"/"+file_names[i]
            if data_type == 3:
                df = df_list[i]
            elif data_type == 4:
                df = df_filtered
            else:
                df = df_filtered
            df.to_excel(f,index=False)
    filepath_export = fp
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
        global hero
        if entry.get() == "":
            hero = ""
            save_settings()
            status_label.config(text="Cleared Setting: Hero")
            if display != "Plays":
                set_display(display)
            stats_button["state"] = tk.DISABLED
            close_hero_window()
        elif entry.get() in hero_options:
            hero = entry.get()
            save_settings()
            status_label.config(text="Updated Hero to " + hero + ".")
            if display != "Plays":
                set_display(display)
            stats_button["state"] = tk.NORMAL
            close_hero_window()
        else:
            label2["text"] = "Not found."

    def clear_hero():
        entry.delete(0,"end")

    def close_hero_window():
        hero_window.grab_release()
        hero_window.destroy()
    
    df0_i = modo.to_dataframe(all_data_inverted[0],all_headers[0])
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

    label1 = tk.Label(mid_frame,text="Enter 'Hero' Name.",wraplength=width,justify="left")
    entry = tk.Entry(mid_frame)
    entry.insert(0,hero)
    label2 = tk.Label(mid_frame,text="",wraplength=width,justify="left")
    button1 = tk.Button(bot_frame,text="Save",command=lambda : set_hero())
    button2 = tk.Button(bot_frame,text="Clear",command=lambda : clear_hero())
    button3 = tk.Button(bot_frame,text="Cancel",command=lambda : close_hero_window())

    label1.grid(row=0,column=0,pady=(15,5))       
    entry.grid(row=1,column=0)    
    label2.grid(row=2,column=0,pady=(5,5))
    button1.grid(row=4,column=0,padx=10,pady=10)
    button2.grid(row=4,column=1,padx=10,pady=10)
    button3.grid(row=4,column=2,padx=10,pady=10)

    hero_window.protocol("WM_DELETE_WINDOW", lambda : close_hero_window())
def set_default_export():
    height = 150
    width =  300
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
        global filepath_export
        if label1["text"] == "No Default Export Folder":
            filepath_export = ""
        else:
            filepath_export = label1["text"]
        save_settings()
        status_label.config(text="Updated export folder location.")
        close_export_window()
        
    def close_export_window():
        export_window.grab_release()
        export_window.destroy()
   
    mid_frame = tk.LabelFrame(export_window,text="Folder Paths")
    bot_frame = tk.Frame(export_window)
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    export_window.grid_columnconfigure(0,weight=1)
    export_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)

    if (filepath_export is None) or (filepath_export == ""):
        label1 = tk.Label(mid_frame,text="No Default Export Folder",wraplength=width,justify="left")
    else:
        label1 = tk.Label(mid_frame,text=filepath_export,wraplength=width,justify="left")
    button1 = tk.Button(mid_frame,text="Set Default Export Folder",command=lambda : get_export_path())
    button3 = tk.Button(bot_frame,text="Save",command=lambda : save_path())
    button4 = tk.Button(bot_frame,text="Cancel",command=lambda : close_export_window())
    
    label1.grid(row=0,column=0,pady=(10,5))
    button1.grid(row=1,column=0,pady=0)
    button3.grid(row=4,column=0,padx=10,pady=10)
    button4.grid(row=4,column=1,padx=10,pady=10)
    
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

    def get_decks_path():
        fp = filedialog.askdirectory()
        fp = os.path.normpath(fp)
        if (fp is None) or (fp == "") or (fp == "."):
            label1.config(text="No Default Decklists Folder")
        else:
            label1.config(text=fp)

    def get_logs_path():
        fp = filedialog.askdirectory() 
        fp = os.path.normpath(fp) 
        if (fp is None) or (fp == "") or (fp == "."):
            label2.config(text="No Default Game Logs Folder")
        else:
            label2.config(text=fp)

    def save_path():
        global filepath_decks
        global filepath_logs
        if label1["text"] == "No Default Decklists Folder":
            filepath_decks = ""
        else:
            filepath_decks = label1["text"]
        if label2["text"] == "No Default Game Logs Folder":
            filepath_logs = ""
        else:
            filepath_logs = label2["text"]
        save_settings()
        status_label.config(text="Updated default import folder location.")
        close_import_window()
        
    def close_import_window():
        import_window.grab_release()
        import_window.destroy()
   
    mid_frame = tk.LabelFrame(import_window,text="Folder Paths")
    bot_frame = tk.Frame(import_window)
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    import_window.grid_columnconfigure(0,weight=1)
    import_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)

    if (filepath_decks is None) or (filepath_decks == "") or (filepath_decks == "."):
        label1 = tk.Label(mid_frame,text="No Default Decklists Folder",wraplength=width,justify="left")
    else:
        label1 = tk.Label(mid_frame,text=filepath_decks,wraplength=width,justify="left")
    button1 = tk.Button(mid_frame,text="Set Default Decklists Folder",command=lambda : get_decks_path())

    if (filepath_logs is None) or (filepath_logs == "") or (filepath_decks == "."):
        label2 = tk.Label(mid_frame,text="No Default Game Logs Folder",wraplength=width,justify="left")
    else:
        label2 = tk.Label(mid_frame,text=filepath_logs,wraplength=width,justify="left")
    button2 = tk.Button(mid_frame,text="Get Game Logs Folder",command=lambda : get_logs_path())
    button3 = tk.Button(bot_frame,text="Save",command=lambda : save_path())
    button4 = tk.Button(bot_frame,text="Cancel",command=lambda : close_import_window())

    label1.grid(row=0,column=0,pady=(5,5))
    button1.grid(row=1,column=0,pady=0)
    label2.grid(row=2,column=0,pady=5)
    button2.grid(row=3,column=0,pady=0)
    button3.grid(row=4,column=0,padx=10,pady=10)
    button4.grid(row=4,column=1,padx=10,pady=10)
    
    button1["state"] = tk.DISABLED

    import_window.protocol("WM_DELETE_WINDOW", lambda : close_import_window())   
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
def clear_filter():
    global filter_changed
    filter_changed = True
    filter_dict.clear()
def set_filter():
    height = 300
    width =  550
    filter_window = tk.Toplevel(window)
    filter_window.title("Set Filters")
    filter_window.iconbitmap(filter_window,"icon.ico")
    filter_window.minsize(width,height)
    filter_window.resizable(False,False)
    filter_window.grab_set()
    filter_window.focus()

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
        if col.get() == "Date":
            drop_key.grid_forget()
            date.grid(row=0,column=3,padx=10,pady=10)
        else:
            drop_key.grid(row=0,column=3,padx=10,pady=10)
            drop_key.set("None Selected.")
            date.grid_forget()

    def update_combobox():
        index = col_dict[col.get()]
        key_options = []
        for i in tree1.get_children():
            key_options.append(tree1.set(i,index))
        if key_options[0].isnumeric():
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
        set_display(display)
        filter_window.grab_release()
        filter_window.destroy()
    
    def close_filter_window():
        # Revert filter changes and close window.
        global filter_dict
        filter_dict = filter_init
        filter_window.grab_release()
        filter_window.destroy()

    global filter_changed
    filter_changed = False
    filter_init = filter_dict.copy()

    col_dict = {}
    if display == "Matches":
        for index, i in enumerate(all_headers[0]):
            col_dict[i] = index
    elif display == "Games":
        for index, i in enumerate(all_headers[1]):
            col_dict[i] = index
    elif display == "Plays":
        for index, i in enumerate(all_headers[2]):
            col_dict[i] = index
    col_dict.pop("Match_ID")
    
    col_options = list(col_dict.keys())
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
 
    button1 = tk.Button(top_frame,text="Add",command=lambda : add())
    button2 = tk.Button(bot_frame,text="Clear",command=lambda : [clear_filter(),update_filter_text()])
    button3 = tk.Button(bot_frame,text="Apply Filter",command=lambda : apply_filter())
    button4 = tk.Button(bot_frame,text="Exit",command=lambda : close_filter_window())
    label1 = tk.Label(mid_frame1,text="",wraplength=width/2,justify="left")
    label2 = tk.Label(mid_frame2,text="",wraplength=width/2,justify="left")

    col.trace("w",update_keys)

    drop_col.grid(row=0,column=1,padx=10,pady=10)
    op_menu.grid(row=0,column=2,padx=10,pady=10)
    button1.grid(row=0,column=4,padx=10,pady=10)
    label1.grid(row=0,column=0,sticky="w",rowspan=11)
    label2.grid(row=0,column=1,sticky="w")
    button2.grid(row=0,column=0,padx=10,pady=10)
    button3.grid(row=0,column=1,padx=10,pady=10)
    button4.grid(row=0,column=2,padx=10,pady=10)

    update_keys()
    update_filter_text()
    filter_window.protocol("WM_DELETE_WINDOW", lambda : close_filter_window())
def revise_record2():
    global all_data
    global all_data_inverted

    if tree1.focus() == "":
        return

    selected = tree1.focus()
    values = list(tree1.item(selected,"values"))

    p1_index      = modo.match_header().index("P1")
    p2_index      = modo.match_header().index("P2")
    mformat_index = modo.match_header().index("Format")
    lformat_index = modo.match_header().index("Limited_Format")
    mtype_index =   modo.match_header().index("Match_Type")
    p1_arch_index = modo.match_header().index("P1_Arch")
    p1_sub_index =  modo.match_header().index("P1_Subarch")
    p2_arch_index = modo.match_header().index("P2_Arch")
    p2_sub_index =  modo.match_header().index("P2_Subarch")

    df = modo.to_dataframe(all_data[2],modo.play_header())
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

    for i in all_data[0]:
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

    all_data_inverted = modo.invert_join(all_data)
    set_display("Matches")
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
            for i in ["NA"] + input_options["Constructed Match Types"] + input_options["Booster Draft Match Types"] + input_options["Sealed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: match_type.set(x))
        elif match_format.get() in input_options["Constructed Formats"]:
            for i in ["NA"] + input_options["Constructed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: match_type.set(x))
        elif (match_format.get() == "Cube") or (match_format.get() == "Booster Draft"):
            for i in ["NA"] + input_options["Booster Draft Match Types"]:
                menu.add_command(label=i,command=lambda x=i: match_type.set(x))
        elif match_format.get() == "Sealed Deck":
            for i in ["NA"] + input_options["Sealed Match Types"]:
                menu.add_command(label=i,command=lambda x=i: match_type.set(x))

        if match_format.get() in input_options["Limited Formats"]:
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
                for i in ["NA"] + input_options["Cube Formats"]:
                    menu.add_command(label=i,command=lambda x=i: limited_format.set(x))
            elif match_format.get() == "Booster Draft":
                for i in ["NA"] + input_options["Booster Draft Formats"]:
                    menu.add_command(label=i,command=lambda x=i: limited_format.set(x))
            elif match_format.get() == "Sealed Deck":
                for i in ["NA"] + input_options["Sealed Formats"]:
                    menu.add_command(label=i,command=lambda x=i: limited_format.set(x))

            p1_arch_type.set(arch_options[0])
            p2_arch_type.set(arch_options[0])
        elif (p1_arch_type.get() == "Limited"):
            arch_options = ["NA"] + input_options["Archetypes"]
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

            if values[modo.match_header().index("P1_Arch")] == "Limited":
                p1_arch_type.set(arch_options[0])
                p2_arch_type.set(arch_options[0])
            else:
                p1_arch_type.set(values[modo.match_header().index("P1_Arch")])
                p2_arch_type.set(values[modo.match_header().index("P2_Arch")])

    def close_revise_window():
        global all_data_inverted
        for count,i in enumerate(all_data[0]):
            if i[0] == values[0]:
                if i[modo.match_header().index("P1")] == values[modo.match_header().index("P1")]:
                    i[modo.match_header().index("P1_Arch")] = p1_arch_type.get()
                    i[modo.match_header().index("P1_Subarch")] = p1_subarch_entry.get()
                    i[modo.match_header().index("P2_Arch")] = p2_arch_type.get()
                    i[modo.match_header().index("P2_Subarch")] = p2_subarch_entry.get()
                else:
                    i[modo.match_header().index("P1_Arch")] = p2_arch_type.get()
                    i[modo.match_header().index("P1_Subarch")] = p2_subarch_entry.get()
                    i[modo.match_header().index("P2_Arch")] = p1_arch_type.get()
                    i[modo.match_header().index("P2_Subarch")] = p1_subarch_entry.get()
                i[modo.match_header().index("Format")] = match_format.get()
                i[modo.match_header().index("Limited_Format")] = limited_format.get()
                i[modo.match_header().index("Match_Type")] = match_type.get()                   
                all_data_inverted = modo.invert_join(all_data)
                set_display("Matches")
                break
        revise_window.grab_release()
        revise_window.destroy()

    def close_without_saving():
        revise_window.grab_release()
        revise_window.destroy()       

    selected = tree1.focus()
    values = list(tree1.item(selected,"values"))

    format_options = ["NA"] + input_options["Constructed Formats"] + input_options["Limited Formats"]
    match_format = tk.StringVar()
    match_format.set(values[modo.match_header().index("Format")])

    if match_format.get() == "Cube":
        limited_options = input_options["Cube Formats"]
        match_options = ["NA"] + input_options["Booster Draft Match Types"]
    elif match_format.get() == "Booster Draft":
        limited_options = input_options["Booster Draft Formats"]
        match_options = ["NA"] + input_options["Booster Draft Match Types"]
    elif match_format.get() == "Sealed Deck":
        limited_options = input_options["Sealed Formats"]
        match_options = ["NA"] + input_options["Sealed Match Types"]
    elif match_format.get() in input_options["Constructed Formats"]:
        limited_options = ["NA"]
        match_options = ["NA"] + input_options["Constructed Match Types"]
    elif match_format.get() == "NA":
        limited_options = ["NA"]
        match_options = ["NA"] + input_options["Constructed Match Types"] + input_options["Booster Draft Match Types"] + input_options["Sealed Match Types"]

    limited_format = tk.StringVar()
    limited_format.set(values[modo.match_header().index("Limited_Format")])

    match_type = tk.StringVar()
    match_type.set(values[modo.match_header().index("Match_Type")])

    if values[modo.match_header().index("Format")] in input_options["Limited Formats"]:
        arch_options = ["Limited"]
    else:
        arch_options = input_options["Archetypes"]
    p1_arch_type = tk.StringVar()
    p1_arch_type.set(values[modo.match_header().index("P1_Arch")])

    p2_arch_type = tk.StringVar()
    p2_arch_type.set(values[modo.match_header().index("P2_Arch")])

    p1_label =           tk.Label(mid_frame,text="P1:")
    p1_entry =           tk.Label(mid_frame,text=values[modo.match_header().index("P1")])
    p1_arch_label =      tk.Label(mid_frame,text="P1_Arch:")
    p1_arch_entry =      tk.OptionMenu(mid_frame,p1_arch_type,*arch_options)
    p1_subarch_label =   tk.Label(mid_frame,text="P1_Subarch:")
    p1_subarch_entry =   tk.Entry(mid_frame)
    p2_label =           tk.Label(mid_frame,text="P2:")
    p2_entry =           tk.Label(mid_frame,text=values[modo.match_header().index("P2")])
    p2_arch_label =      tk.Label(mid_frame,text="P2_Arch:")
    p2_arch_entry =      tk.OptionMenu(mid_frame,p2_arch_type,*arch_options)
    p2_subarch_label =   tk.Label(mid_frame,text="P2_Subarch:")
    p2_subarch_entry =   tk.Entry(mid_frame)
    p1_roll_label =      tk.Label(mid_frame,text="P1_Roll:")
    p1_roll_entry =      tk.Label(mid_frame,text=values[modo.match_header().index("P1_Roll")])
    p2_roll_label =      tk.Label(mid_frame,text="P2_Roll:")
    p2_roll_entry =      tk.Label(mid_frame,text=values[modo.match_header().index("P2_Roll")])
    roll_winner_label =  tk.Label(mid_frame,text="Roll_Winner:")
    roll_winner_entry =  tk.Label(mid_frame,text=values[modo.match_header().index("Roll_Winner")])
    p1_wins_label =      tk.Label(mid_frame,text="P1_Wins:")
    p1_wins_entry =      tk.Label(mid_frame,text=values[modo.match_header().index("P1_Wins")])
    p2_wins_label =      tk.Label(mid_frame,text="P2_Wins:")
    p2_wins_entry =      tk.Label(mid_frame,text=values[modo.match_header().index("P2_Wins")])
    match_winner_label = tk.Label(mid_frame,text="Match_Winner:")
    match_winner_entry = tk.Label(mid_frame,text=values[modo.match_header().index("Match_Winner")])
    format_label =       tk.Label(mid_frame,text="Format:")
    format_entry =       tk.OptionMenu(mid_frame,match_format,*format_options)
    draft_type_label =   tk.Label(mid_frame,text="Limited_Format:")
    draft_type_entry =   tk.OptionMenu(mid_frame,limited_format,*limited_options)
    match_type_label =   tk.Label(mid_frame,text="Match_Type:")
    match_type_entry =   tk.OptionMenu(mid_frame,match_type,*match_options)
    date_label =         tk.Label(mid_frame,text="Date:")
    date_entry =         tk.Label(mid_frame,text=values[modo.match_header().index("Date")])

    p1_subarch_entry.insert(0,values[modo.match_header().index("P1_Subarch")])
    p2_subarch_entry.insert(0,values[modo.match_header().index("P2_Subarch")])

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
    if match_format.get() not in input_options["Limited Formats"]:
        draft_type_entry["state"] = tk.DISABLED

    match_format.trace("w",update_arch)

    revise_window.protocol("WM_DELETE_WINDOW", lambda : close_without_saving())
def revise_record_multi():
    if tree1.focus() == "":
        return

    height = 175
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

    def field_updated(*argv):
        global field
        field = field_val.get()

        if field == "P1 Deck":
            p1_arch_label.grid(row=1,column=0,padx=(25,0),pady=10,sticky="e")
            p1_arch_entry.grid(row=1,column=1,padx=(25,50),pady=5,sticky="ew")
            p1_subarch_label.grid(row=2,column=0,padx=(25,0),pady=5,sticky="e")
            p1_subarch_entry.grid(row=2,column=1,padx=(25,50),pady=5,sticky="ew")
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
            p1_arch_label.grid_forget()
            p1_arch_entry.grid_forget()
            p1_subarch_label.grid_forget()
            p1_subarch_entry.grid_forget()
            p2_arch_label.grid(row=1,column=0,padx=(25,0),pady=10,sticky="e")
            p2_arch_entry.grid(row=1,column=1,padx=(25,50),pady=5,sticky="ew")
            p2_subarch_label.grid(row=2,column=0,padx=(25,0),pady=5,sticky="e")
            p2_subarch_entry.grid(row=2,column=1,padx=(25,50),pady=5,sticky="ew")
            format_label.grid_forget()
            format_entry.grid_forget()
            lim_format_label.grid_forget()
            lim_format_entry.grid_forget()
            match_type_label.grid_forget()
            match_type_entry.grid_forget()
        elif field == "Format":
            p1_arch_label.grid_forget()
            p1_arch_entry.grid_forget()
            p1_subarch_label.grid_forget()
            p1_subarch_entry.grid_forget()
            p2_arch_label.grid_forget()
            p2_arch_entry.grid_forget()
            p2_subarch_label.grid_forget()
            p2_subarch_entry.grid_forget()
            format_label.grid(row=1,column=0,padx=(25,0),pady=10,sticky="e")
            format_entry.grid(row=1,column=1,padx=(25,50),pady=5,sticky="ew")
            lim_format_label.grid(row=2,column=0,padx=(25,0),pady=5,sticky="e")
            lim_format_entry.grid(row=2,column=1,padx=(25,50),pady=5,sticky="ew")
            match_type_label.grid_forget()
            match_type_entry.grid_forget()
        elif field == "Match Type":
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
            match_type_label.grid(row=1,column=0,padx=(25,0),pady=(25,),sticky="e")
            match_type_entry.grid(row=1,column=1,padx=(25,50),pady=(20,),sticky="ew")

    def format_updated(*argv):
        if match_format.get() in input_options["Limited Formats"]:
            lim_format_entry["state"] = tk.NORMAL
            lim_format.set("NA")

            menu = lim_format_entry["menu"]
            menu.delete(0,"end")
            if match_format.get() == "Cube":
                for i in input_options["Cube Formats"]:
                    menu.add_command(label=i,command=lambda x=i: lim_format.set(x))
            elif match_format.get() == "Booster Draft":
                for i in input_options["Booster Draft Formats"]:
                    menu.add_command(label=i,command=lambda x=i: lim_format.set(x))
            elif match_format.get() == "Sealed Deck":
                for i in input_options["Sealed Formats"]:
                    menu.add_command(label=i,command=lambda x=i: lim_format.set(x))    
        else:
            lim_format.set("NA")
            lim_format_entry["state"] = tk.DISABLED

    def close_revise_window():
        for i in selected:
            values = list(tree1.item(i,"values"))
            for index,j in enumerate(itertools.chain(*[all_data[0],all_data_inverted[0]])):
                if values[0] == j[0]:
                    if field == "P1 Deck":
                        if values[modo.match_header().index("P1")] == j[modo.match_header().index("P1")]:
                            j[modo.match_header().index("P1_Arch")] = p1_arch_type.get()
                            j[modo.match_header().index("P1_Subarch")] = p1_subarch_entry.get()
                        else:
                            j[modo.match_header().index("P2_Arch")] = p1_arch_type.get()
                            j[modo.match_header().index("P2_Subarch")] = p1_subarch_entry.get()                          
                    elif field == "P2 Deck":
                        if values[modo.match_header().index("P2")] == j[modo.match_header().index("P2")]:
                            j[modo.match_header().index("P2_Arch")] = p2_arch_type.get()
                            j[modo.match_header().index("P2_Subarch")] = p2_subarch_entry.get()
                        else:
                            j[modo.match_header().index("P1_Arch")] = p2_arch_type.get()
                            j[modo.match_header().index("P1_Subarch")] = p2_subarch_entry.get()
                    elif field == "Format":
                        j[modo.match_header().index("Format")] = match_format.get()
                        j[modo.match_header().index("Limited_Format")] = lim_format.get()
                    elif field == "Match Type":
                        j[modo.match_header().index("Match_Type")] = match_type.get() 
        set_display("Matches")
        revise_window.grab_release()
        revise_window.destroy()

    def close_without_saving():
        revise_window.grab_release()
        revise_window.destroy()       

    selected = tree1.selection()
    format_index = modo.match_header().index("Format")
    sel_formats = {"constructed":False,"booster":False,"sealed":False}
    for i in selected:
        format_i = list(tree1.item(i,"values"))[format_index]
        if format_i in input_options["Constructed Formats"]:
            sel_formats["constructed"] = True
        elif (format_i == "Booster Draft") or (format_i == "Cube"):
            sel_formats["booster"] = True
        elif format_i == "Sealed Deck":
            sel_formats["sealed"] = True

    format_options = ["NA"] + input_options["Constructed Formats"] + input_options["Limited Formats"]
    match_format = tk.StringVar()
    match_format.set(format_options[0])

    limited_options = ["NA"]
    lim_format = tk.StringVar()
    lim_format.set(limited_options[0])

    match_options = ["NA"]
    if (sel_formats["constructed"] == True) and (sel_formats["booster"] == False) and (sel_formats["sealed"] == False):
        match_options += input_options["Constructed Match Types"]
    elif (sel_formats["constructed"] == False) and (sel_formats["booster"] == True) and (sel_formats["sealed"] == False):
        match_options += input_options["Booster Draft Match Types"]
    elif (sel_formats["constructed"] == False) and (sel_formats["booster"] == False) and (sel_formats["sealed"] == True):
        match_options += input_options["Sealed Match Types"]
    elif (sel_formats["constructed"] == False) and (sel_formats["booster"] == False) and (sel_formats["sealed"] == False):
        match_options += input_options["Constructed Match Types"] + input_options["Booster Draft Match Types"] + input_options["Sealed Match Types"]
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

    arch_options = ["NA"] + input_options["Archetypes"]

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

    button3 = tk.Button(bot_frame,text="Apply to All",
                        command=lambda : close_revise_window())
    button4 = tk.Button(bot_frame,text="Cancel",
                        command=lambda : close_without_saving())

    lim_format_entry["state"] = tk.DISABLED
    button3.grid(row=0,column=0,padx=10,pady=10)
    button4.grid(row=0,column=1,padx=10,pady=10)

    field_val.trace("w",field_updated)
    match_format.trace("w",format_updated)

    field_updated()
    revise_window.protocol("WM_DELETE_WINDOW", lambda : close_without_saving())
def activate_revise(event):
    if tree1.identify_region(event.x,event.y) == "heading":
        return
    if display != "Matches":
        return
    if data_loaded == False:
        return
    revise_button["state"] = tk.NORMAL
def revise_method_select():
    if len(tree1.selection()) > 1:
        revise_record_multi()
    else:
        revise_record2()
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

    def get_logs_path():
        fp_logs = filedialog.askdirectory()
        fp_logs = os.path.normpath(fp_logs) 
        if (fp_logs is None) or (fp_logs == "") or (fp_logs == "."):
            label2.config(text="No Default Game Logs Folder")
            button3["state"] = tk.DISABLED
        else:
            label2.config(text=fp_logs)
            button3["state"] = tk.NORMAL

    def import_data():
        global filepath_logs

        if (label2["text"]  == "No Default Game Logs Folder"):
            label3["text"] = "Decks and/or Game Logs Folder Location not set."
            return
        filepath_logs = label2["text"]
        get_all_data()
        clear_filter()
        set_display("Matches")
        if data_loaded != False:
            data_menu.entryconfig("Set Default Hero",state=tk.NORMAL)
            file_menu.entryconfig("Save Data",state=tk.NORMAL)
            data_menu.entryconfig("Clear Loaded Data",state=tk.NORMAL)
            data_menu.entryconfig("Input Missing Match Data",state=tk.NORMAL)
            data_menu.entryconfig("Input Missing Game_Winner Data",state=tk.NORMAL)
            data_menu.entryconfig("Apply Best Guess for Deck Names",state=tk.NORMAL)
        #filepath_logs = fp_logs
            # Uncomment to revert filepath_logs to original setting.
        close_import_window()

    def close_import_window():
        import_window.grab_release()
        import_window.destroy()
    
    fp_logs = filepath_logs

    mid_frame = tk.LabelFrame(import_window,text="Folder Path")
    bot_frame = tk.Frame(import_window)
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    import_window.grid_columnconfigure(0,weight=1)
    import_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)

    button2 = tk.Button(mid_frame,text="Get Logs Folder",command=lambda : get_logs_path())
    button3 = tk.Button(bot_frame,text="Import", command=lambda : import_data())
    button4 = tk.Button(bot_frame,text="Cancel", command=lambda : close_import_window())
    if (filepath_logs is None) or (filepath_logs == ""):
        label2 = tk.Label(mid_frame,text="No Default Game Logs Folder",wraplength=width,justify="left")
        button3["state"] = tk.DISABLED
    else:
        label2 = tk.Label(mid_frame,text=filepath_logs,wraplength=width,justify="left")
    label3 = tk.Label(mid_frame,text="Select folder containing your MTGO GameLog files.",wraplength=width,pady=(20,),justify="left")

    label2.grid(row=0,column=0,pady=(20,5))
    button2.grid(row=1,column=0,pady=0)
    label3.grid(row=2,column=0,pady=5)
    button3.grid(row=0,column=0,padx=10,pady=10)
    button4.grid(row=0,column=1,padx=10,pady=10)

    import_window.protocol("WM_DELETE_WINDOW", lambda : close_import_window())
def get_winners():
    global all_data
    global all_data_inverted
    global uaw

    gw_index = modo.game_header().index("Game_Winner")
    p1_index = modo.game_header().index("P1")
    p2_index = modo.game_header().index("P2")
    gn_index = modo.game_header().index("Game_Num")

    n = 0
    data_index = 0
    df1 =   modo.to_dataframe(all_data[1],modo.game_header())
    total = df1[(df1.Game_Winner == "NA")].shape[0]
    for count,i in enumerate(all_data[1]):    # Iterate through games.
        if i[gw_index] == "NA": # Game record does not have a winner.
            empty = False
            n += 1
            p1 = i[p1_index]
            p2 = i[p2_index]
            ask_for_winner(all_data[3][data_index],p1,p2,n,total)
            if uaw == "Exit.":
                break
            if uaw == "NA":
                data_index += 1
            else:
                all_data[3].pop(data_index)
            i[gw_index] = uaw
    if n == 0:
        status_label.config(text="No Games with missing Game_Winner.")
    else:
        modo.update_game_wins(all_data,all_headers)
        all_data_inverted = modo.invert_join(all_data)
        set_display("Matches")
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
    gw.title("Select Game Winner")
    gw.iconbitmap(gw,"icon.ico")
    height = 400
    width = 700
    gw.minsize(width,height)
    gw.resizable(False,False)
    gw.attributes("-topmost",True)
    gw.grab_set()
    gw.focus()

    gw.geometry("+%d+%d" %
                (window.winfo_x()+(window.winfo_width()/2)-(width/2),
                 window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    message = "Winner could not be determined. Please determine Game Winner.\n" + str(n) + "/" + str(total) + " Games"
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

    button_skip = tk.Button(top_frame,text="Skip Game",
                            command=lambda : close_gw_window("NA"))
    button_exit = tk.Button(top_frame,text="Exit",
                            command=lambda : close_gw_window("Exit."))    
    button1 = tk.Button(bot_frame,text=p1,
                        command=lambda : close_gw_window("P1"))
    button2 = tk.Button(bot_frame,text=p2,
                        command=lambda : close_gw_window("P2"))

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
    stats_window.title("Statistics - Match Data")
    stats_window.iconbitmap(stats_window,"icon.ico")
    stats_window.minsize(width,height)
    stats_window.resizable(False,False)
    window.withdraw()
    stats_window.focus()

    stats_window.geometry("+%d+%d" %
        (window.winfo_x(),
         window.winfo_y()))

    top_frame = tk.Frame(stats_window)
    mid_frame = tk.Frame(stats_window)

    top_frame.grid(row=0,column=0,sticky="")
    mid_frame.grid(row=1,column=0,sticky="nsew")

    mid_frame1 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame2 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame3 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame4 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame5 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame6 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame7 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)
    mid_frame8 = tk.LabelFrame(mid_frame,font=14,labelanchor="n",width=100,height=100)  

    mid_frame1.grid(row=0,column=0,sticky="nsew")
    mid_frame2.grid(row=0,column=1,sticky="nsew")
    mid_frame3.grid(row=1,column=0,sticky="nsew")
    mid_frame4.grid(row=1,column=1,sticky="nsew")

    stats_window.grid_columnconfigure(0,weight=1)
    stats_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_rowconfigure(0,weight=1)
    mid_frame.grid_rowconfigure(1,weight=1)
    mid_frame.grid_columnconfigure(0,weight=1)
    mid_frame.grid_columnconfigure(1,weight=1)
    
    df0 = modo.to_dataframe(all_data[0],all_headers[0])
    df1 = modo.to_dataframe(all_data[1],all_headers[1])
    df2 = modo.to_dataframe(all_data[2],all_headers[2])
    df0_i = modo.to_dataframe(all_data_inverted[0],all_headers[0])
    df1_i = modo.to_dataframe(all_data_inverted[1],all_headers[1])
    df2_i = modo.to_dataframe(all_data_inverted[2],all_headers[2])
 
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
        mid_frame1.grid_remove()
        mid_frame2.grid_remove()
        mid_frame3.grid_remove()
        mid_frame4.grid_remove()
        mid_frame5.grid_remove()
        mid_frame6.grid_remove()
        mid_frame7.grid_remove()
        mid_frame8.grid_remove()

    def defocus(event):
        # Clear Auto-Highlight in Combobox menu.
        menu_2.selection_clear()
        menu_3.selection_clear()
        menu_4.selection_clear()
        menu_5.selection_clear()

    def match_stats(hero,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Match Data")
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

        df0_i_f =        df0_i[(df0_i.P1 == hero)]
        hero_n =         df0_i_f.shape[0] # Matches played by hero
        df0_i_f =        df0_i_f[(df0_i_f.Date > date_range[0]) & (df0_i_f.Date < date_range[1])]

        if mformat in input_options["Limited Formats"]:
            formats_played = df0_i_f[(df0_i_f.Format == mformat)].Limited_Format.value_counts().keys().tolist()
        else:
            formats_played = df0_i_f.Format.value_counts().keys().tolist()
        format_wins =    [df0_i_f[(df0_i_f.Match_Winner == "P1")].shape[0]] #adding overall in L[0]
        format_losses =  [df0_i_f[(df0_i_f.Match_Winner == "P2")].shape[0]] #adding overall in L[0]
        if (format_wins[0] + format_losses[0]) == 0:
            format_wr = ["0.0%"]
        else:
            format_wr = [to_percent(format_wins[0]/(format_wins[0]+format_losses[0]),1) + "%"]    #adding overall in L[0]

        for i in formats_played:
            if mformat in input_options["Limited Formats"]:
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

        matchtypes_played = df0_i_f.Match_Type.value_counts().keys().tolist()
        matchtypes_counts = df0_i_f.Format.value_counts().tolist()
        for index,i in enumerate(matchtypes_played):
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

        mid_frame2["text"] = "Overall Performance"
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
                if mformat in input_options["Constructed Formats"]:
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
                if mformat in input_options["Constructed Formats"]:
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

    def game_stats(hero,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Game Data")
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

        play_choice_n = df1_i_hero[df1_i_hero.PD_Choice == "Play"]        
        draw_choice_n = df1_i_hero[df1_i_hero.PD_Choice == "Draw"]
        
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

    def play_stats(hero,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Play Data")
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
    
    def time_stats(hero,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Time Data")
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

        df_time = df0_i[(df0_i.P1 == hero)]
        if mformat != "All Formats":
            df_time =   df_time[(df_time.Format == mformat)]
        df_time = df_time.sort_values(by=["Date"])
        df_time = df_time[(df_time.Date.between(date_range[0],date_range[1]))]
        
        g1_list = get_wr_over_time(df_time,0)
        # g1_list = get_pm_over_time(df_time,0)

        fig = plt.figure(figsize=(7,5),dpi=100)
        plt.plot(g1_list[0],g1_list[1])
        plt.xlabel("Matches Played")

        # plt.title("Match Wins Over .500:\n" + mformat)
        # plt.ylabel("Match Wins Over .500")
        plt.title("Win Rate Over Time:\n" + mformat)
        plt.ylabel("Winning Percentage")

        canvas = FigureCanvasTkAgg(fig,mid_frame5)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0,column=0,sticky="")

        if deck != "All Decks":
            # Filtered by P1=hero,Format=mformat,P1_Subarch=deck
            df_time_d = df_time[(df_time.P1_Subarch == deck)]
            df_time_d = df_time_d.sort_values(by=["Date"])     
            
            g2_list = get_wr_over_time(df_time_d,0)
            # g2_list = get_pm_over_time(df_time_d,0)

            fig = plt.figure(figsize=(7,5),dpi=100)
            plt.plot(g2_list[0],g2_list[1])
            plt.xlabel("Matches Played")

            # plt.title("Match Wins Over .500:\n" + mformat + ": " + deck)
            # plt.ylabel("Match Wins Over .500")
            plt.title("Win Rate Over Time:\n" + mformat + ": " + deck)
            plt.ylabel("Winning Percentage")

            canvas2 = FigureCanvasTkAgg(fig,mid_frame6)
            canvas2.draw()
            canvas2.get_tk_widget().grid(row=0,column=0,sticky="")

    def card_stats(hero,mformat,lformat,deck,opp_deck,date_range,s_type):
        stats_window.title("Statistics - Card Data")
        clear_frames()
        def tree_setup(*argv):
            for i in argv:
                i.place(relheight=1, relwidth=1)
        def sort_column(col,reverse,tree1):
            l = []
            for k in tree1.get_children(''):
                l.append((tree1.set(k, col), k))
            l.sort(reverse=reverse)
            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l):
                tree1.move(k, '', index)
            # reverse sort next time
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
            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l):
                tree1.move(k, '', index)
            # reverse sort next time
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
            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l):
                tree1.move(k, '', index)
            # reverse sort next time
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
    
    def update_hero(*argv):
        hero = player.get()

        format_options = df0_i[(df0_i.P1 == player.get())].Format.value_counts().keys().tolist()
        format_options.insert(0,"All Formats")
        # menu = menu_2["menu"]
        # menu.delete(0,"end")
        # for i in format_options:
        #     menu.add_command(label=i,command=lambda x=i: mformat.set(x))
        menu_2["values"] = format_options # Comment out to switch to OptionMenu.
        mformat.set(format_options[0])

        update_deck_menu()
        update_opp_deck_menu()
       
        #menu_2["state"]   = tk.NORMAL
        #menu_4["state"]   = tk.NORMAL
        #menu_5["state"]   = tk.NORMAL
        menu_6["state"]   = tk.NORMAL
        menu_2["state"]   = "readonly"
        menu_4["state"]   = "readonly"
        menu_5["state"]   = "readonly"
        button_1["state"] = tk.NORMAL
        
    def update_format(*argv):
        if mformat.get() in input_options["Limited Formats"]:
            lim_format.set("All Limited Formats")
            #menu_3["state"] = tk.NORMAL
            menu_3["state"] = "readonly"
            update_lim_menu()
        else:
            lim_format.set("All Limited Formats")
            menu_3["state"] = tk.DISABLED
        update_deck_menu()
        update_opp_deck_menu()

    def update_lim_format(*argv):
        update_deck_menu()
        update_opp_deck_menu()

    def update_lim_menu(*argv):
        lim_formats_played = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())].Limited_Format.value_counts().keys().tolist()
        lim_formats_played.insert(0,"All Limited Formats")

        # menu = menu_3["menu"]
        # menu.delete(0,"end")
        # for i in lim_formats_played:
        #     menu.add_command(label=i,command=lambda x=i: lim_format.set(x))
        menu_3["values"] = lim_formats_played # Comment out to switch to OptionMenu.
        lim_format.set(lim_formats_played[0])

    def update_deck_menu(*argv):
        if mformat.get() == "All Formats":
            df = df0_i[(df0_i.P1 == player.get())]
        elif mformat.get() in input_options["Constructed Formats"]:
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        elif (mformat.get() in input_options["Limited Formats"]) & (lim_format.get() == "All Limited Formats"):
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        elif (mformat.get() in input_options["Limited Formats"]) & (lim_format.get() != "All Limited Formats"):
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

        # menu = menu_4["menu"]
        # menu.delete(0,"end")
        # for i in decks_played:
        #     menu.add_command(label=i,command=lambda x=i: deck.set(x))
        menu_4["values"] = decks_played # Comment out to switch to OptionMenu.
        deck.set(decks_played[0])

    def update_opp_deck_menu(*argv):
        if mformat.get() == "All Formats":
            df = df0_i[(df0_i.P1 == player.get())]
        elif mformat.get() in input_options["Constructed Formats"]:
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        elif (mformat.get() in input_options["Limited Formats"]) & (lim_format.get() == "All Limited Formats"):
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]
        elif (mformat.get() in input_options["Limited Formats"]) & (lim_format.get() != "All Limited Formats"):
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get()) & (df0_i.Limited_Format == lim_format.get())]
        else:
            df = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())]

        opp_decks_played = df.P2_Subarch.value_counts().keys().tolist()
        opp_decks_played.insert(0,"All Opp. Decks")

        # menu = menu_5["menu"]
        # menu.delete(0,"end")
        # for i in opp_decks_played:
        #     menu.add_command(label=i,command=lambda x=i: opp_deck.set(x))
        menu_5["values"] = opp_decks_played # Comment out to switch to OptionMenu.
        opp_deck.set(opp_decks_played[0])

    def update_s_type(*argv):
        update_deck_menu()
        update_opp_deck_menu()
        if s_type.get() == "Time Data":
            menu_5["state"]   = tk.DISABLED
        else:
            #menu_5["state"]   = tk.NORMAL
            menu_5["state"]   = "readonly"

    def update_combobox():
        pass

    def load_data():
        if date_entry_1.get() < date_entry_2.get():
            dr = [date_entry_1.get() + "-00:00",date_entry_2.get() + "-23:59"]
        else:
            dr = [date_entry_1.get() + "-00:00",date_entry_2.get() + "-23:59"]

        if s_type.get() == "Match Stats":
            match_stats(player.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Game Stats":
            game_stats(player.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Play Stats":
            play_stats(player.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Time Data":
            time_stats(player.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())
        elif s_type.get() == "Card Data":
            card_stats(player.get(),mformat.get(),lim_format.get(),deck.get(),opp_deck.get(),dr,s_type.get())      
        
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
    stat_types = ["Match Stats","Game Stats","Play Stats","Time Data","Card Data"]
    
    player = tk.StringVar()
    player.set("Select a Player")
    mformat = tk.StringVar()
    mformat.set("Format")
    lim_format = tk.StringVar()
    lim_format.set("All Limited Formats")
    deck = tk.StringVar()
    deck.set("Decks Played")
    opp_deck = tk.StringVar()
    opp_deck.set("Opp. Decks")
    s_type = tk.StringVar()
    s_type.set(stat_types[0])
    
    menu_1 = tk.OptionMenu(top_frame,player,*p1_options)
    # menu_2 = tk.OptionMenu(top_frame,mformat,*format_options)
    # menu_3 = tk.OptionMenu(top_frame,lim_format,*limited_options)
    # menu_4 = tk.OptionMenu(top_frame,deck,*decks_played)
    # menu_5 = tk.OptionMenu(top_frame,opp_deck,*opp_decks_played)
    menu_2 = ttk.Combobox(top_frame,textvariable=mformat,width=14,height=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER,
        postcommand=update_combobox)
    menu_3 = ttk.Combobox(top_frame,textvariable=lim_format,width=14,height=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER,
        postcommand=update_combobox)
    menu_4 = ttk.Combobox(top_frame,textvariable=deck,width=14,height=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER,
        postcommand=update_combobox)
    menu_5 = ttk.Combobox(top_frame,textvariable=opp_deck,width=14,height=12,
        state="readonly",font="Helvetica 14",justify=tk.CENTER,
        postcommand=update_combobox)
    menu_6 = tk.OptionMenu(top_frame,s_type,*stat_types)
    date_entry_1 = DateEntry(top_frame,date_pattern="y-mm-dd",width=10,
        year=int(date_min[0:4]),month=int(date_min[5:7]),day=int(date_min[8:10]),
        font="Helvetica 14",state="readonly")
    date_entry_2 = DateEntry(top_frame,date_pattern="y-mm-dd",width=10,
        year=today.year,month=today.month,day=today.day,
        font="Helvetica 14",state="readonly")
    button_1 = tk.Button(top_frame,text="GO",state=tk.DISABLED,width=12,bg="black",fg="white",command=lambda : load_data())
    
    menu_1["state"] = tk.DISABLED
    menu_2["state"] = tk.DISABLED
    menu_3["state"] = tk.DISABLED
    menu_4["state"] = tk.DISABLED
    menu_5["state"] = tk.DISABLED
    menu_6["state"] = tk.DISABLED

    menu_2.bind("<FocusIn>",defocus)
    menu_3.bind("<FocusIn>",defocus)
    menu_4.bind("<FocusIn>",defocus)
    menu_5.bind("<FocusIn>",defocus)

    menu_1.grid(row=0,column=0,padx=5,pady=10)
    menu_2.grid(row=0,column=1,padx=5,pady=10)
    menu_3.grid(row=0,column=2,padx=5,pady=10)
    menu_4.grid(row=0,column=3,padx=5,pady=10)
    menu_5.grid(row=0,column=4,padx=5,pady=10)
    date_entry_1.grid(row=0,column=5,padx=5,pady=10)
    date_entry_2.grid(row=0,column=6,padx=5,pady=10)
    menu_6.grid(row=0,column=7,padx=5,pady=10)
    button_1.grid(row=0,column=8,padx=5,pady=10)
    
    menu_1.config(bg="black",disabledforeground="white")
    menu_6.config(bg="black",fg="white",activebackground="black",activeforeground="white")
    menu_6["menu"].config(bg="black",fg="white",borderwidth=0)

    player.trace("w",update_hero)
    mformat.trace("w",update_format)
    lim_format.trace("w",update_lim_format)
    s_type.trace("w",update_s_type)

    if hero != "":
        player.set(hero)
        load_data()
    else:
        menu_1["state"] = tk.NORMAL

    stats_window.protocol("WM_DELETE_WINDOW", lambda : close_stats_window())
def exit():
    #save_settings()
    window.destroy()
def test():
    # Test method
    pass

window = tk.Tk() 
window.title("MTGO-Tracker")
window.iconbitmap(window,"icon.ico")

cwd = os.getcwd()
if os.path.isdir("save") == True:
    os.chdir(cwd + "\\" + "save")
    if os.path.isfile("main_window_size.p"):
        main_window_size = pickle.load(open("main_window_size.p","rb"))
    os.chdir(cwd)
window.geometry(str(main_window_size[1]) + "x" + str(main_window_size[2]))
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

match_button = tk.Button(left_frame,text="Match Data",state=tk.DISABLED,
                        command=lambda : set_display("Matches"))
game_button = tk.Button(left_frame,text="Game Data",state=tk.DISABLED,
                        command=lambda : set_display("Games"))
play_button = tk.Button(left_frame,text="Play Data",state=tk.DISABLED,
                        command=lambda : set_display("Plays"))
filter_button = tk.Button(left_frame,text="Filter",state=tk.DISABLED,
                        command=lambda : set_filter())
clear_button = tk.Button(left_frame,text="Clear Filter",state=tk.DISABLED,
                        command=lambda : [clear_filter(),set_display(display)])
revise_button = tk.Button(left_frame,text="Revise Record(s)",state=tk.DISABLED,
                        command=lambda : revise_method_select())
stats_button = tk.Button(left_frame,text="Statistics",state=tk.DISABLED,
                        command=lambda : get_stats())
back_button = tk.Button(left_frame,text="Back",state=tk.DISABLED,
                        command=lambda :bb_clicked())
test_button = tk.Button(left_frame,text="TEST BUTTON",
                        command=lambda : choose_size_window())

status_label = tk.Label(bottom_frame,text="")
status_label.grid(row=0,column=0)

menu_bar = tk.Menu(window)

file_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="File",menu=file_menu)

file_menu.add_command(label="Load MTGO GameLogs",command=lambda : import_window())
file_menu.add_separator()
file_menu.add_command(label="Load Saved Data",command=lambda : load_saved_window())
file_menu.add_command(label="Save Data",command=lambda : save_window(),state=tk.DISABLED)
file_menu.add_separator()
file_menu.add_command(label="Set Default Window Size",command=lambda : choose_size_window())
file_menu.add_separator()
file_menu.add_command(label="Exit",command=lambda : exit())

export_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="Export",menu=export_menu)

export_csv = tk.Menu(export_menu,tearoff=False)
export_csv.add_command(label="Match History",command=lambda : export("CSV",0,False))
export_csv.add_command(label="Game History",command=lambda : export("CSV",1,False))
export_csv.add_command(label="Play History",command=lambda : export("CSV",2,False))
export_csv.add_command(label="All Data (3 Files)",command=lambda : export("CSV",3,False))
export_csv.add_separator()
export_csv.add_command(label="Match History (Inverse Join)",command=lambda : export("CSV",0,True))
export_csv.add_command(label="Game History (Inverse Join)",command=lambda : export("CSV",1,True))
export_csv.add_command(label="All Data (Inverse Join, 3 Files)",command=lambda : export("CSV",3,True))
export_csv.add_separator()
export_csv.add_command(label="Currently Displayed Data (with Filters)",command=lambda : export("CSV",4,False))

export_excel = tk.Menu(export_menu,tearoff=False)
export_excel.add_command(label="Match History",command=lambda : export("Excel",0,False))
export_excel.add_command(label="Game History",command=lambda : export("Excel",1,False))
export_excel.add_command(label="Play History",command=lambda : export("Excel",2,False))
export_excel.add_command(label="All Data (3 Files)",command=lambda : export("Excel",3,False))
export_excel.add_separator()
export_excel.add_command(label="Match History (Inverse Join)",command=lambda : export("Excel",0,True))
export_excel.add_command(label="Game History (Inverse Join)",command=lambda : export("Excel",1,True))
export_excel.add_command(label="All Data (Inverse Join, 3 Files)",command=lambda : export("Excel",3,True))
export_excel.add_separator()
export_excel.add_command(label="Currently Displayed Table (with Filters)",command=lambda : export("Excel",4,False))

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

window.config(menu=menu_bar)

match_button.grid(row=0,column=0,sticky="ew",padx=5,pady=(20,5))
game_button.grid(row=1,column=0,sticky="ew",padx=5,pady=5)
play_button.grid(row=2,column=0,sticky="ew",padx=5,pady=5)
filter_button.grid(row=3,column=0,sticky="ew",padx=5,pady=(50,5))
clear_button.grid(row=4,column=0,sticky="ew",padx=5,pady=5)
revise_button.grid(row=5,column=0,sticky="ew",padx=5,pady=5)
stats_button.grid(row=6,column=0,sticky="ew",padx=5,pady=50)
back_button.grid(row=7,column=0,sticky="ew",padx=5,pady=5)
#test_button.grid(row=13,column=0,sticky="ew",padx=5,pady=5)

tree1 = ttk.Treeview(text_frame,show="tree")
tree1.grid(row=0,column=0,sticky="nsew")
tree1.bind("<Double-1>",tree_double)
tree1.bind("<ButtonRelease-1>",activate_revise)

tree_scrolly = tk.Scrollbar(text_frame,command=tree1.yview)
tree1.configure(yscrollcommand=tree_scrolly.set)
tree_scrolly.grid(row=0,column=1,sticky="ns")

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
window.protocol("WM_DELETE_WINDOW", lambda : exit())

# Event loop: listens for events (keypress, etc.)
# Blocks code after from running until window is closed.
window.mainloop()