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

all_data =          [[],[],[],[]]
all_data_inverted = [[],[],[],[]]
all_headers =       [[],[],[]]
all_decks =         []
display =           ""
filter_dict =       {}
filepath_root =     ""
filepath_export =   ""
filepath_decks =    ""
filepath_logs =     ""
data_loaded =       False
filter_changed =    False
prev_display =      ""
uaw =               "NA"
main_window_width = 1725
main_window_height= 750
hero =              ""
parsed_file_list =  []
new_import =        False

def save_window():
    height = 100
    width =  300
    save_window = tk.Toplevel(window)
    save_window.title("Save Data")
    save_window.minsize(width,height)
    save_window.resizable(False,False)
    save_window.grab_set()
    save_window.focus()

    save_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def save():
        save_settings()

        os.chdir(filepath_root + r"\save")
        files = ["matches.csv","games.csv","plays.csv","rawdata.csv","parsedfiles.csv"]

        for index,i in enumerate(files):
            if index == 3:
                df = pd.DataFrame(all_data[index])
                df.to_csv(i,header=False,index=False)
            elif index == 4:
                df = pd.DataFrame(parsed_file_list)
                df.to_csv(i,header=False,index=False)
            else:
                df = modo.to_dataframe(all_data[index],all_headers[index])
                df.to_csv(i,header=True,index=False)

        status_label.config(text="Save complete. Data will be loaded automatically on next startup.")
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

def clear_window():
    height = 100
    width =  300
    clear_window = tk.Toplevel(window)
    clear_window.title("Clear Saved Data")
    clear_window.minsize(width,height)
    clear_window.resizable(False,False)
    clear_window.grab_set()
    clear_window.focus()

    clear_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def clear():
        global all_data
        global all_data_inverted
        global all_decks
        global display
        global filter_dict
        global data_loaded
        global filter_changed
        global prev_display
        global uaw
        global parsed_file_list
        global new_import

        all_data =          [[],[],[],[]]
        all_data_inverted = [[],[],[],[]]
        all_decks =         []
        display =           ""
        filter_dict =       {}
        data_loaded =       False
        filter_changed =    False
        prev_display =      ""
        uaw =               "NA"
        parsed_file_list =  []
        new_import =        False

        button1["state"] = tk.DISABLED
        button2["state"] = tk.DISABLED
        button3["state"] = tk.DISABLED
        button7["state"] = tk.DISABLED
        button8["state"] = tk.DISABLED
        button4["state"] = tk.DISABLED
        button9["state"] = tk.DISABLED
        back_button["state"] = tk.DISABLED
        
        text_frame.config(text="Dataframe")

        data_menu.entryconfig("Set Default 'Hero'",state=tk.DISABLED)
        file_menu.entryconfig("Clear Loaded Data",state=tk.DISABLED)
        file_menu.entryconfig("Save Data",state=tk.DISABLED)

        #clear existing data in tree
        tree1.delete(*tree1.get_children())
        tree1["show"] = "tree"

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

def startup():
    global filepath_root
    global filepath_export
    global filepath_decks
    global filepath_logs
    global hero
    global all_data
    global all_data_inverted
    global parsed_file_list
    global data_loaded

    with io.open("modo-config.txt","r",encoding="ansi") as config:
        initial = config.read()

        settings =       initial.split("\n")
        filepath_root =  os.getcwd()
        filepath_export =settings[1].split("=>")[1]
        filepath_decks = settings[2].split("=>")[1]
        filepath_logs =  settings[3].split("=>")[1]
        hero =           settings[4].split("=>")[1]

    os.chdir(filepath_root + r"\save")
    files = ["matches.csv","games.csv","plays.csv","rawdata.csv","parsedfiles.csv"]

    all_headers[0] = modo.match_header()
    all_headers[1] = modo.game_header()
    all_headers[2] = modo.play_header()

    for index,i in enumerate(files):
        if os.path.isfile(i) == False:
            return
        if index == 3:
            try:
                df = pd.read_csv(i,header=None,na_filter=False)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame()
            df_rows = df.to_numpy().tolist()
            for i in df_rows:
                while "" in i:
                    i.remove("")
        elif index == 4:
            try:
                df = pd.read_csv(i,header=None,na_filter=False)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame()   
        else:
            df = pd.read_csv(i,header=0,na_filter=False)
            df_rows = df.to_numpy().tolist()
        if index == 4:
            parsed_file_list = df[0].tolist()
        else:
            all_data[index] = df_rows

    all_data_inverted = modo.invert_join(all_data)

    status_label.config(text="Imported " + str(len(all_data[0])) + " matches.")

    button7["state"] = tk.NORMAL
    button8["state"] = tk.NORMAL
    data_loaded = True

    set_display("Matches")
    data_menu.entryconfig("Set Default 'Hero'",state=tk.NORMAL)
    file_menu.entryconfig("Clear Loaded Data",state=tk.NORMAL)
    file_menu.entryconfig("Save Data",state=tk.NORMAL)

def save_settings():
    os.chdir(filepath_root)
    with io.open("modo-config.txt","w",encoding="ansi") as config:
        config.write("filepath_root=>" + filepath_root + "\n")
        config.write("filepath_export=>" + filepath_export + "\n")
        config.write("filepath_decks=>" + filepath_decks + "\n")
        config.write("filepath_logs=>" + filepath_logs + "\n")
        config.write("hero=>" + hero)

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
        set_bb_state(argv[0])
    
    if button1["state"] == tk.DISABLED:
        button1["state"] = tk.NORMAL
    if button2["state"] == tk.DISABLED:
        button2["state"] = tk.NORMAL
    if button3["state"] == tk.DISABLED:
        button3["state"] = tk.NORMAL
    if button9["state"] == tk.DISABLED:
        button9["state"] = tk.NORMAL
        
    if d == "Matches":
        set_bb_state(False)
        print_data(all_data[0],all_headers[0])
    elif d == "Games":
        set_bb_state(True)
        #button4["state"] = tk.DISABLED
        print_data(all_data[1],all_headers[1])
    elif d == "Plays":
        set_bb_state(True)
        #button4["state"] = tk.DISABLED
        print_data(all_data[2],all_headers[2])
    print(filter_dict)
    
def set_bb_state(state):
    if state:
        back_button["state"] = tk.NORMAL
    else:
        back_button["state"] = tk.DISABLED
        
def get_all_data():
    global all_data
    global all_data_inverted
    global all_headers
    global data_loaded
    global parsed_file_list
    global new_import
    w = [window.winfo_x(),window.winfo_y(),window.winfo_width(),window.winfo_height()]
    count = 0
    
    for (root,dirs,files) in os.walk(filepath_logs):
        None
        
    os.chdir(filepath_logs)
    for i in files:
        if ("Match_GameLog_" not in i) or (len(i) < 30):
            pass
        elif (i in parsed_file_list):
            pass
        else:
            with io.open(i,"r",encoding="ansi") as gamelog:
                initial = gamelog.read()
                mtime = time.ctime(os.path.getmtime(i))

            parsed_data = modo.get_all_data(initial,mtime,all_decks,w)
            parsed_file_list.append(i)
            count += 1

            all_data[0].append(parsed_data[0])
            for i in parsed_data[1]:
                all_data[1].append(i)
            for i in parsed_data[2]:
                all_data[2].append(i)
            for i in parsed_data[3]:
                all_data[3].append(i)

    all_data_inverted = modo.invert_join(all_data)

    status_label.config(text="Imported " + str(count) + " new matches.")

    new_import = True

    if len(all_data[0]) != 0:
        button7["state"] = tk.NORMAL
        button8["state"] = tk.NORMAL
        data_loaded = True
    print(len(all_data[0]))

def print_data(data,header):
    global new_import

    #clear existing data in tree
    tree1.delete(*tree1.get_children())

    tree1["column"] = header
    tree1["show"] = "headings"

    #insert column headers into tree
    for i in tree1["column"]:
        tree1.column(i,anchor="center",stretch=False,width=100)
        tree1.heading(i,text=i, command=lambda _col=i:
                      sort_column(_col,False))
    tree1.column("Match_ID",anchor="w")
        
    df = modo.to_dataframe(data,header)
    total = df.shape[0]
    for key in filter_dict:
        if key not in header:
            break
        for i in filter_dict[key]:
            df = df[(df[key].isin(filter_dict[key]))]
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
    button4["state"] = tk.DISABLED

def get_lists():
    global all_decks
    
    for (root,dirs,files) in os.walk(filepath_decks):
        None

    os.chdir(filepath_decks)
    for i in files:
        with io.open(i,"r",encoding="ansi") as decklist:
            initial = decklist.read()

        deck = modo.parse_list(i,initial)
        all_decks.append(deck)

def get_formats():
    global all_data
    global all_data_inverted
  
    # for count,i in enumerate(modo.match_header()):
    #     if i == "Format":
    #         index = count
    #         break
    mformat_index = modo.match_header().index("Format")
    mtype_index =   modo.match_header().index("Match_Type")
    p1_arch_index = modo.match_header().index("P1_Arch")
    p1_sub_index =  modo.match_header().index("P1_Subarch")
    p2_arch_index = modo.match_header().index("P2_Arch")
    p2_sub_index =  modo.match_header().index("P2_Subarch")

    n =     0
    df0 =   modo.to_dataframe(all_data[0],modo.match_header())
    total = df0[(df0.Format == "NA")].shape[0]  
    for i in all_data[0]:    # Iterate through matches.
        # Match record is missing some data.
        if (i[p1_arch_index] == "NA") or (i[p2_arch_index] == "NA") or (i[mformat_index] == "NA") or (i[mtype_index] == "NA"):
            n += 1
            plays = []
            for j in all_data[2]: # Iterate through plays.
                if i[0] == j[0]:  # Add Play to our List if it has a matching Match_ID
                    plays.append(j)
            df =      modo.to_dataframe(plays,modo.play_header())
            #players = df.Casting_Player.value_counts().keys().tolist()
            players = [i[modo.match_header().index("P1")],i[modo.match_header().index("P2")]]
            cards1 =  df[(df.Casting_Player == players[0]) & (df.Action == "Plays")].Primary_Card.value_counts().keys().tolist()
            cards2 =  df[(df.Casting_Player == players[0]) & (df.Action == "Casts")].Primary_Card.value_counts().keys().tolist()
            cards3 =  df[(df.Casting_Player == players[1]) & (df.Action == "Plays")].Primary_Card.value_counts().keys().tolist()
            cards4 =  df[(df.Casting_Player == players[1]) & (df.Action == "Casts")].Primary_Card.value_counts().keys().tolist()
            cards1 = sorted(cards1,key=str.casefold)
            cards2 = sorted(cards2,key=str.casefold)
            cards3 = sorted(cards3,key=str.casefold)
            cards4 = sorted(cards4,key=str.casefold)
            ask_for_format(players,cards1,cards2,cards3,cards4,n,total,i)
            if match_format == "Exit":
                break
            if match_format != "Skip":
                i[p1_arch_index] = match_format[0]
                i[p1_sub_index] =  match_format[1]
                i[p2_arch_index] = match_format[2]
                i[p2_sub_index] =  match_format[3]
                i[mformat_index] = match_format[4]
                i[mtype_index] =   match_format[5]

            # if (match_format == "Draft - Sealed") or (match_format == "Draft - Booster") or (match_format == "Cube"):
            #     i[p1_arch_index] = "Limited"
            #     i[p2_arch_index] = "Limited"
    if n == 0:
        status_label.config(text="No Matches with missing Format.")
    else:
        all_data_inverted = modo.invert_join(all_data)
        set_display("Matches")

def ask_for_format(players,cards1,cards2,card3,cards4,n,total,mdata):
    def close_format_window(*argv):
        global match_format

        match_format = [p1_arch.get(),p1_sub.get(),p2_arch.get(),p2_sub.get(),mformat.get(),mtype.get()]
        for i in argv:
            match_format = i

        print(match_format)
        gf.grab_release()
        gf.destroy()
             
    height = 450
    width =  650                
    gf = tk.Toplevel(window)
    gf.title("Input Missing Data - " + str(n) + "/" + str(total) + " Matches.")           
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
            #str1 += ", "
            str1 += "\n"
        str1 += i
    for index,i in enumerate(cards2):
        if index > 0:
            #str2 += ", "
            str2 += "\n"
        str2 += i
    for index,i in enumerate(card3):
        if index > 0:
            #str3 += ", "
            str3 += "\n"
        str3 += i
    for index,i in enumerate(cards4):
        if index > 0:
            #str4 += ", "
            str4 += "\n"
        str4 += i
    
    def update_arch(*argv):
        if (mformat.get() == "Draft - Sealed") or (mformat.get() == "Draft - Booster") or (mformat.get() == "Cube"):
            arch_options = ["Limited"]

            menu = p1_arch_menu["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p1_arch.set(x))

            menu = p2_arch_menu["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p2_arch.set(x))
            
            p1_arch.set(arch_options[0])
            p2_arch.set(arch_options[0])
        elif (p1_arch.get() == "Limited"):
            arch_options = ["NA","Aggro","Midrange","Control","Combo","Prison","Tempo"]

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
    #id_message = tk.Label(bot_frame1,text="Date Played: " + mdata[modo.match_header().index("Date")])

    # button1 = tk.Button(bot_frame1,text="Vintage",
    #                      command=lambda :
    #                      [close_format_window("Vintage")])
    # button2 = tk.Button(bot_frame1,text="Legacy",
    #                      command=lambda :
    #                      [close_format_window("Legacy")])
    # button3 = tk.Button(bot_frame1,text="Modern",
    #                      command=lambda :
    #                      [close_format_window("Modern")])
    # button4 = tk.Button(bot_frame1,text="Standard",
    #                      command=lambda :
    #                      [close_format_window("Standard")])
    # button5 = tk.Button(bot_frame1,text="Pioneer",
    #                      command=lambda :
    #                      [close_format_window("Pioneer")])
    # button6 = tk.Button(bot_frame2,text="Pauper",
    #                      command=lambda :
    #                      [close_format_window("Pauper")])
    # button7 = tk.Button(bot_frame2,text="Draft - Booster",
    #                      command=lambda :
    #                      [close_format_window("Draft - Booster")])
    # button8 = tk.Button(bot_frame2,text="Draft - Sealed",
    #                      command=lambda :
    #                      [close_format_window("Draft - Sealed")])
    # button9 = tk.Button(bot_frame2,text="Cube",
    #                      command=lambda :
    #                      [close_format_window("Cube")])
    submit_button = tk.Button(bot_frame2,text="Save Changes",command=lambda : [close_format_window()])

    arch_options = ["NA","Aggro","Midrange","Control","Combo","Prison","Tempo"]
    p1_arch = tk.StringVar()
    p1_arch.set("Select P1 Archetype")
    p2_arch = tk.StringVar()
    p2_arch.set("Select P2 Archetype")

    format_options = ["NA","Vintage","Legacy","Modern","Standard","Pioneer","Pauper","Draft - Booster","Draft - Sealed","Cube"]
    mformat = tk.StringVar()
    mformat.set("Select Format")

    type_options = ["NA","League","Preliminary","Challenge"]
    mtype = tk.StringVar()
    mtype.set("Select Match Type")

    p1_arch_menu = tk.OptionMenu(mid_frame1,p1_arch,*arch_options)
    p1_sub =  tk.Entry(mid_frame1)
    p2_arch_menu = tk.OptionMenu(mid_frame2,p2_arch,*arch_options)
    p2_sub =  tk.Entry(mid_frame2)

    match_format = tk.OptionMenu(bot_frame2,mformat,*format_options)
    match_type = tk.OptionMenu(bot_frame2,mtype,*type_options)

    p1_sub.insert(0,mdata[modo.match_header().index("P1_Subarch")])
    p2_sub.insert(0,mdata[modo.match_header().index("P2_Subarch")])

    if mdata[modo.match_header().index("P1_Arch")] != "NA":
        p1_arch.set(mdata[modo.match_header().index("P1_Arch")])
    if mdata[modo.match_header().index("P2_Arch")] != "NA":
        p2_arch.set(mdata[modo.match_header().index("P2_Arch")])
    if mdata[modo.match_header().index("Format")] != "NA": 
        mformat.set(mdata[modo.match_header().index("Format")])
    if mdata[modo.match_header().index("Match_Type")] != "NA":
        mtype.set(mdata[modo.match_header().index("Match_Type")])

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

    match_format.grid(row=0,column=0)
    match_type.grid(row=0,column=1)
    submit_button.grid(row=0,column=2)
    # button1.grid(row=0,column=0,padx=5,pady=5,sticky="nsew")
    # button2.grid(row=0,column=1,padx=5,pady=5,sticky="nsew")
    # button3.grid(row=0,column=2,padx=5,pady=5,sticky="nsew")
    # button4.grid(row=0,column=3,padx=5,pady=5,sticky="nsew")
    # button5.grid(row=0,column=4,padx=5,pady=5,sticky="nsew")
    # button6.grid(row=0,column=0,padx=5,pady=5,sticky="nsew")
    # button7.grid(row=0,column=1,padx=5,pady=5,sticky="nsew")
    # button8.grid(row=0,column=2,padx=5,pady=5,sticky="nsew")
    # button9.grid(row=0,column=3,padx=5,pady=5,sticky="nsew")
    
    button_skip.grid(row=0,column=0,padx=10,pady=10)
    label_message.grid(row=0,column=1,padx=10,pady=10)
    button_exit.grid(row=0,column=2,padx=10,pady=10)
    #id_message.grid(row=0,column=0)

    mformat.trace("w",update_arch)

    gf.protocol("WM_DELETE_WINDOW", lambda : close_format_window("Exit"))
    gf.wait_window()
    
def tree_double(event):
    global filter_dict
    
    if tree1.focus() == "":
        return None
    if display == "Plays":
        return None
    
    clear_filter()
    add_filter_setting("Match_ID",tree1.item(tree1.focus(),"values")[0])
    if display == "Matches":
        set_display("Games",True)
    elif display == "Games":
        add_filter_setting("Game_Num",tree1.item(tree1.focus(),"values")[3])
        set_display("Plays",True)

def bb_clicked():
    global filter_dict
    
    if "Match_ID" in filter_dict:
        match_id = filter_dict["Match_ID"][0]
        clear_filter()
        add_filter_setting("Match_ID",match_id)
    else:
        clear_filter()
    if display == "Games":
        set_display("Matches")
    elif display == "Plays":
        set_display("Games")

def get_decks_path():
    global filepath_decks
    filepath_decks = filedialog.askdirectory()
    save_settings()
    status_label.config(text="Updated folder location. Click 'Import' to update data.")
    
def get_logs_path():
    global filepath_logs
    filepath_logs = filedialog.askdirectory()
    save_settings()
    status_label.config(text="Updated folder location. Click 'Import' to update data.")

def export(file_type,data_type,inverted):
    #file_type: string, "CSV" or "Excel"
    #data_type: int, 0=Match,1=Game,2=Play,3=All,4=Filtered
    #inverted:  bool
    global filepath_export
    fp = filepath_export
    if (filepath_export is None) or (filepath_export == ""):
        filepath_export = filedialog.askdirectory()
    if filepath_export is None:
        return

    if inverted:
        data_to_write = all_data_inverted
    else:
        data_to_write = all_data

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
        for key in filter_dict:
            for value in filter_dict[key]:
                df_filtered = df_filtered[df_filtered[key] == value]

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
            print(file_names)
            with open(filepath_export+"/"+file_names[i],"w",encoding="UTF8",newline="") as file:
                print(file)
                writer = csv.writer(file)
                if data_type == 3:
                    writer.writerow(headers[i])
                    for row in data_to_write[i]:
                        writer.writerow(row)
                elif data_type == 4:
                    writer.writerow(headers)
                    df_rows = df_filtered.to_numpy().tolist()
                    for row in df_rows:
                        writer.writerow(row)
                else:
                    writer.writerow(headers[i])
                    for row in data_to_write[data_type]:
                        writer.writerow(row)
    elif file_type == "Excel":
        for i in range(len(file_names)):
            f = filepath_export+"/"+file_names[i]
            if data_type == 3:
                df = modo.to_dataframe(data_to_write[i],headers[i])
            elif data_type == 4:
                df = df_filtered
            else:
                df = modo.to_dataframe(data_to_write[data_type],headers[i])
            df.to_excel(f,index=False)
    filepath_export = fp

def set_default_hero():
    height = 100
    width =  200
    hero_window = tk.Toplevel(window)
    hero_window.title("Set Default 'Hero'")
    hero_window.minsize(width,height)
    hero_window.resizable(False,False)
    hero_window.grab_set()
    hero_window.focus()

    hero_window.geometry("+%d+%d" % 
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def set_hero():
        global hero
        if entry.get() in hero_options:
            hero = entry.get()
            save_settings()
            status_label.config(text="Updated Hero to " + hero + ".")
            close_hero_window()
        else:
            label2["text"] = "Not found."
        
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
    
    label1.grid(row=0,column=0,pady=(10,5))       
    entry.grid(row=1,column=0)    
    label2.grid(row=2,column=0,pady=(10,5))
    button1.grid(row=4,column=0,pady=5)
    
    hero_window.protocol("WM_DELETE_WINDOW", lambda : close_hero_window())

def set_default_export():
    height = 300
    width =  400
    export_window = tk.Toplevel(window)
    export_window.title("Set Default Export Folder")
    export_window.minsize(width,height)
    export_window.resizable(False,False)
    export_window.grab_set()
    export_window.focus()

    export_window.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def get_export_path():
        fp = filedialog.askdirectory()  
        if (fp is None) or (fp == ""):
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
    #label2 = tk.Label(mid_frame,text=filepath_logs,wraplength=width,justify="left")
    #button2 = tk.Button(mid_frame,text="Get Logs Folder",command=lambda : [get_logs_path(),update_path_labels()])
    button3 = tk.Button(bot_frame,text="Save",command=lambda : save_path())
    
    label1.grid(row=0,column=0,pady=(40,5))
    button1.grid(row=1,column=0,pady=0)
    #label2.grid(row=2,column=0,pady=5)
    #button2.grid(row=3,column=0,pady=0)
    button3.grid(row=4,column=0,pady=5)
    
    export_window.protocol("WM_DELETE_WINDOW", lambda : close_export_window())

def set_default_import():
    height = 300
    width =  400
    import_window = tk.Toplevel(window)
    import_window.title("Set Default Export Folder")
    import_window.minsize(width,height)
    import_window.resizable(False,False)
    import_window.grab_set()
    import_window.focus()

    import_window.geometry("+%d+%d" %
        (window.winfo_x()+(window.winfo_width()/2)-(width/2),
        window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def get_decks_path():
        fp = filedialog.askdirectory()  
        if (fp is None) or (fp == ""):
            label1.config(text="No Default Decklists Folder")
        else:
            label1.config(text=fp)

    def get_logs_path():
        fp = filedialog.askdirectory()  
        if (fp is None) or (fp == ""):
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

    if (filepath_decks is None) or (filepath_decks == ""):
        label1 = tk.Label(mid_frame,text="No Default Decklists Folder",wraplength=width,justify="left")
    else:
        label1 = tk.Label(mid_frame,text=filepath_decks,wraplength=width,justify="left")
    button1 = tk.Button(mid_frame,text="Set Default Decklists Folder",command=lambda : get_decks_path())

    if (filepath_logs is None) or (filepath_logs == ""):
        label2 = tk.Label(mid_frame,text="No Default Game Logs Folder",wraplength=width,justify="left")
    else:
        label2 = tk.Label(mid_frame,text=filepath_logs,wraplength=width,justify="left")
    button2 = tk.Button(mid_frame,text="Get Game Logs Folder",command=lambda : get_logs_path())
    button3 = tk.Button(bot_frame,text="Save",command=lambda : save_path())
    
    label1.grid(row=0,column=0,pady=(40,5))
    button1.grid(row=1,column=0,pady=0)
    label2.grid(row=2,column=0,pady=5)
    button2.grid(row=3,column=0,pady=0)
    button3.grid(row=4,column=0,pady=5)
    
    import_window.protocol("WM_DELETE_WINDOW", lambda : close_import_window())   

def sort_column(col, reverse):
    l = []
    for k in tree1.get_children(''):
        l.append((tree1.set(k, col), k))
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tree1.move(k, '', index)

    # reverse sort next time
    tree1.heading(col, text=col, command=lambda _col=col: 
                 sort_column(_col, not reverse))
    
def add_filter_setting(index, key):
    global filter_dict
    global filter_changed
    
    if key == "None Selected":
        return None
    
    if index in filter_dict:
        l = filter_dict[index]
        if key not in l:
            if key.isnumeric():
                l.append(int(key))
            else:
                l.append(key)
            filter_dict[index] = l
            filter_changed = True
    else:
        if key.isnumeric():
            filter_dict[index] = [int(key)]
        else:
            filter_dict[index] = [key]
        filter_changed = True
    print(filter_dict)
    
def clear_filter():
    global filter_changed
    filter_changed = True
    filter_dict.clear()
    
def set_filter():
    height = 300
    width =  400
    filter_window = tk.Toplevel(window)
    filter_window.title("Set Filters")
    filter_window.minsize(width,height)
    filter_window.resizable(False,False)
    filter_window.attributes("-topmost",True)
    filter_window.grab_set()
    filter_window.focus()

    filter_window.geometry("+%d+%d" %
                           (window.winfo_x()+(window.winfo_width()/2)-(width/2),
                            window.winfo_y()+(window.winfo_height()/2)-(height/2)))
    
    top_frame = tk.Frame(filter_window)
    mid_frame = tk.LabelFrame(filter_window,text="Filters")
    bot_frame = tk.Frame(filter_window)
    top_frame.grid(row=0,column=0,sticky="")
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    filter_window.grid_columnconfigure(0,weight=1)
    filter_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)
    
    def update_keys(*argv):
        index = col_dict[col.get()]
        
        key_options = []
        for i in tree1.get_children():
            key_options.append(tree1.set(i,index))
        key_options = sorted(list(set(key_options)))

        key.set("None Selected")       
        menu = drop_key["menu"]
        menu.delete(0,"end")
        for i in key_options:
            menu.add_command(label=i,command=lambda x=i: key.set(x))

    def apply_filter():
        set_display(display)

    def update_filter_text():
        tlabel = ""
        for index in filter_dict:
            tlabel += index + " : "
            for index,value in enumerate(filter_dict[index]):
                if index > 0:
                    tlabel += ", "
                tlabel += str(value)
            tlabel += "\n"
        label1.config(text=tlabel)

    def close_filter_window():
        apply_filter()
        filter_window.grab_release()
        filter_window.destroy()

    global filter_changed
    filter_changed = False
    
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
    print(col_dict)
    col_dict.pop("Match_ID")
    
    col_options = list(col_dict.keys())
    col = tk.StringVar()
    col.set(col_options[0])
    key = tk.StringVar()
    key.set("None Selected")

    index = col_dict[col.get()]
    key_options = []
    for i in tree1.get_children():
        key_options.append(tree1.set(i,index))
    key_options = sorted(list(set(key_options)),key=str.casefold)
    if len(key_options) == 0:
        key_options = ["None Selected"]
    
    drop_col = tk.OptionMenu(top_frame,col,*col_options)
    drop_key = tk.OptionMenu(top_frame,key,*key_options)

    button1 = tk.Button(top_frame,text="Clear",
                        command=lambda : [clear_filter(),update_filter_text()])
    button2 = tk.Button(top_frame,text="Add",
                        command=lambda : [add_filter_setting(col.get(),key.get()),
                                           update_filter_text()])
    button3 = tk.Button(bot_frame,text="Apply Filter",
                        command=lambda : close_filter_window())
    label1 = tk.Label(mid_frame,text="",wraplength=width,justify="left")
    
    col.trace("w",update_keys)

    button1.grid(row=0,column=0,padx=10,pady=10)
    drop_col.grid(row=0,column=1,padx=10,pady=10)
    drop_key.grid(row=0,column=2,padx=10,pady=10)
    button2.grid(row=0,column=3,padx=10,pady=10)
    label1.grid(row=0,column=0,sticky="w")
    button3.grid(row=0,column=0,padx=10,pady=10)
    
    update_filter_text()
    filter_window.protocol("WM_DELETE_WINDOW", lambda : close_filter_window())

def revise_record():
    if tree1.focus() == "":
        return

    height = 300
    width =  700
    revise_window = tk.Toplevel(window)
    revise_window.title("Revise Record")
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
        if (match_format.get() == "Draft - Sealed") or (match_format.get() == "Draft - Booster") or (match_format.get() == "Cube"):
            arch_options = ["Limited"]

            menu = p1_arch_entry["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p1_arch_type.set(x))

            menu = p2_arch_entry["menu"]
            menu.delete(0,"end")
            for i in arch_options:
                menu.add_command(label=i,command=lambda x=i: p2_arch_type.set(x))
            p1_arch_type.set(arch_options[0])
            p2_arch_type.set(arch_options[0])
        elif (p1_arch_type.get() == "Limited"):
            arch_options = ["NA","Aggro","Midrange","Control","Combo","Prison","Tempo"]

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
        values[2] = p1_arch_type.get()
        values[3] = p1_subarch_entry.get()
        values[5] = p2_arch_type.get()
        values[6] = p2_subarch_entry.get()
        values[13] = match_format.get()
        values[14] = match_type.get()

        for count,i in enumerate(all_data[0]):
            if i[0] == values[0]:
                i[2] = values[2]
                i[3] = values[3]
                i[5] = values[5]
                i[6] = values[6]
                i[13] = values[13]
                i[14] = values[14]
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

    format_options = ["NA","Vintage","Legacy","Modern","Standard","Pioneer","Pauper","Draft - Booster","Draft - Sealed","Cube"]
    match_format = tk.StringVar()
    match_format.set(values[13])

    match_options = ["NA","League","Preliminary","Challenge"]
    match_type = tk.StringVar()
    match_type.set(values[14])

    if (values[13] == "Draft - Booster") or (values[13] == "Draft - Sealed") or (values[13] == "Cube"):
        arch_options = ["Limited"]
    else:
        arch_options = ["NA","Aggro","Midrange","Control","Combo","Prison","Tempo"]
    p1_arch_type = tk.StringVar()
    p1_arch_type.set(values[2])

    p2_arch_type = tk.StringVar()
    p2_arch_type.set(values[5])

    p1_label =           tk.Label(mid_frame,text="P1:")
    p1_entry =           tk.Label(mid_frame,text=values[1])
    p1_arch_label =      tk.Label(mid_frame,text="P1_Arch:")
    p1_arch_entry =      tk.OptionMenu(mid_frame,p1_arch_type,*arch_options)
    p1_subarch_label =   tk.Label(mid_frame,text="P1_Subarch:")
    p1_subarch_entry =   tk.Entry(mid_frame)
    p2_label =           tk.Label(mid_frame,text="P2:")
    p2_entry =           tk.Label(mid_frame,text=values[4])
    p2_arch_label =      tk.Label(mid_frame,text="P2_Arch:")
    p2_arch_entry =      tk.OptionMenu(mid_frame,p2_arch_type,*arch_options)
    p2_subarch_label =   tk.Label(mid_frame,text="P2_Subarch:")
    p2_subarch_entry =   tk.Entry(mid_frame)
    p1_roll_label =      tk.Label(mid_frame,text="P1_Roll:")
    p1_roll_entry =      tk.Label(mid_frame,text=values[7])
    p2_roll_label =      tk.Label(mid_frame,text="P2_Roll:")
    p2_roll_entry =      tk.Label(mid_frame,text=values[8])
    roll_winner_label =  tk.Label(mid_frame,text="Roll_Winner:")
    roll_winner_entry =  tk.Label(mid_frame,text=values[9])
    p1_wins_label =      tk.Label(mid_frame,text="P1_Wins:")
    p1_wins_entry =      tk.Label(mid_frame,text=values[10])
    p2_wins_label =      tk.Label(mid_frame,text="P2_Wins:")
    p2_wins_entry =      tk.Label(mid_frame,text=values[11])
    match_winner_label = tk.Label(mid_frame,text="Match_Winner:")
    match_winner_entry = tk.Label(mid_frame,text=values[12])
    format_label =       tk.Label(mid_frame,text="Format:")
    format_entry =       tk.OptionMenu(mid_frame,match_format,*format_options)
    match_type_label =   tk.Label(mid_frame,text="Match_Type:")
    match_type_entry =   tk.OptionMenu(mid_frame,match_type,*match_options)
    date_label =         tk.Label(mid_frame,text="Date:")
    date_entry =         tk.Label(mid_frame,text=values[15])

    p1_subarch_entry.insert(0,values[3])
    p2_subarch_entry.insert(0,values[6])

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
    match_type_label.grid(row=5,column=2,pady=10,sticky="w")
    match_type_entry.grid(row=5,column=3,pady=10,sticky="w")
    date_label.grid(row=6,column=0,padx=10,pady=10,sticky="w")
    date_entry.grid(row=6,column=1,pady=10,sticky="w")

    button3.grid(row=0,column=0,padx=10,pady=10)
    button4.grid(row=0,column=1,padx=10,pady=10)

    mid_frame["text"] = "Match_ID: " + values[0]

    match_format.trace("w",update_arch)

    revise_window.protocol("WM_DELETE_WINDOW", lambda : close_without_saving())

def activate_revise(event):
    if tree1.identify_region(event.x,event.y) == "heading":
        return
    if display != "Matches":
        return
    if data_loaded == False:
        return
    button4["state"] = tk.NORMAL

def import_window():
    height = 300
    width =  400
    import_window = tk.Toplevel(window)
    import_window.title("Import Data")
    import_window.minsize(width,height)
    import_window.resizable(False,False)
    import_window.grab_set()
    import_window.focus()

    import_window.geometry("+%d+%d" %
                           (window.winfo_x()+(window.winfo_width()/2)-(width/2),
                            window.winfo_y()+(window.winfo_height()/2)-(height/2)))

    def get_decks_path():
        fp_decks = filedialog.askdirectory()  
        if (fp_decks is None) or (fp_decks == ""):
            label1.config(text="No Default Decklists Folder")
        else:
            label1.config(text=fp_decks)
        label3["text"] = ""

    def get_logs_path():
        fp_logs = filedialog.askdirectory()  
        if (fp_logs is None) or (fp_logs == ""):
            label2.config(text="No Default Game Logs Folder")
        else:
            label2.config(text=fp_logs)
        label3["text"] = ""

    def import_data():
        global filepath_decks
        global filepath_logs
        if (label1["text"] == "No Default Decklists Folder") or (label2["text"]  == "No Default Game Logs Folder"):
            label3["text"] = "Decks and/or Game Logs Folder Location not set."
            return
        filepath_decks = label1["text"]
        filepath_logs = label2["text"]
        get_lists()
        get_all_data()
        clear_filter()
        set_display("Matches")
        if data_loaded != False:
            data_menu.entryconfig("Set Default 'Hero'",state=tk.NORMAL)
            file_menu.entryconfig("Save Data",state=tk.NORMAL)
            file_menu.entryconfig("Clear Loaded Data",state=tk.NORMAL)
        filepath_decks = fp_decks
        filepath_logs = fp_logs
        close_import_window()

    def close_import_window():
        import_window.grab_release()
        import_window.destroy()
    
    fp_decks = filepath_decks
    fp_logs = filepath_logs

    mid_frame = tk.LabelFrame(import_window,text="Folder Paths")
    bot_frame = tk.Frame(import_window)
    mid_frame.grid(row=1,column=0,sticky="nsew")
    bot_frame.grid(row=2,column=0,sticky="")
    
    import_window.grid_columnconfigure(0,weight=1)
    import_window.rowconfigure(1,minsize=0,weight=1)  
    mid_frame.grid_columnconfigure(0,weight=1)

    button1 = tk.Button(mid_frame,text="Get Decks Folder",command=lambda : get_decks_path())
    button2 = tk.Button(mid_frame,text="Get Logs Folder",command=lambda : get_logs_path())
    button3 = tk.Button(bot_frame,text="Import", command=lambda : import_data())
    if (filepath_decks is None) or (filepath_decks == ""):
        label1 = tk.Label(mid_frame,text="No Default Decklists Folder",wraplength=width,justify="left")
    else:
        label1 = tk.Label(mid_frame,text=filepath_decks,wraplength=width,justify="left")
    if (filepath_logs is None) or (filepath_logs == ""):
        label2 = tk.Label(mid_frame,text="No Default Game Logs Folder",wraplength=width,justify="left")
    else:
        label2 = tk.Label(mid_frame,text=filepath_logs,wraplength=width,justify="left")
    label3 = tk.Label(mid_frame,text="",wraplength=width,justify="left")

    label1.grid(row=0,column=0,pady=(40,5))
    button1.grid(row=1,column=0,pady=0)
    label2.grid(row=2,column=0,pady=5)
    button2.grid(row=3,column=0,pady=0)
    label3.grid(row=4,column=0,pady=5)
    button3.grid(row=5,column=0,pady=5)
    
    import_window.protocol("WM_DELETE_WINDOW", lambda : close_import_window())

def get_winners():
    global all_data
    global all_data_inverted
    global uaw

    # def build_ga_list(match_id,game_num):
    #     df = modo.to_dataframe(all_data[2],all_headers[2])
    #     df = df[(df.Match_ID == match_id) & (df.Game_Num == game_num)].tail(15)
    #     for i in df.iterrows():
    #         if row["Action"] == "Play":
    #             action = "plays"
    #         elif row["Action"] == "Casts":
    #             action = "casts"
    #         elif row["Action"] == "Draws":
    #             action = "draws"
    #         elif row["Action"] == "Discards":
    #             action = "discards"
    #         elif row["Action"] == "Activated Ability":
    #             action = "activates"
    #         elif row["Action"] == "Triggers":
    #             action = "triggers"
    #         ga = "Turn "+row["Turn_Num"]+": "+row["Casting_Player"]+" "+row["Action"]

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
    # list of game actions (strings)
    # string = player1
    # string = player2
    # int = number in cycle
    # int = total number of games missing winner

    def close_gw_window(winner):
        global uaw
        uaw = winner
        gw.grab_release()
        gw.destroy()
        
    gw = tk.Toplevel()
    gw.title("Select Game Winner")
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
                            command=lambda :
                            [close_gw_window("NA")])
    button_exit = tk.Button(top_frame,text="Exit",
                            command=lambda :
                            [close_gw_window("Exit.")])    
    button1 = tk.Button(bot_frame,text=p1,
                         command=lambda :
                         [close_gw_window("P1")])
    button2 = tk.Button(bot_frame,text=p2,
                         command=lambda :
                         [close_gw_window("P2")])

    button_skip.grid(row=0,column=0,padx=10,pady=10)
    label1.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
    button_exit.grid(row=0,column=2,padx=10,pady=10)    
    label2.grid(row=0,column=0,sticky="nsew",padx=5,pady=5)
    button1.grid(row=0,column=0,padx=10,pady=10)
    button2.grid(row=0,column=1,padx=10,pady=10)
    
    gw.protocol("WM_DELETE_WINDOW", lambda : close_gw_window("Exit."))    
    gw.wait_window()  

def get_stats():
    width =  main_window_width -400
    height = main_window_height
    stats_window = tk.Toplevel(window)
    stats_window.title("Statistics - Match Data")
    stats_window.minsize(width,height)
    stats_window.resizable(False,False)
    #stats_window.attributes("-topmost",True)
    window.withdraw()
    stats_window.focus()

    stats_window.geometry("+%d+%d" %
                           (window.winfo_x()+(window.winfo_width()/2)-(width/2),
                            window.winfo_y()+(window.winfo_height()/2)-(height/2)))

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

    def match_stats(hero,mformat,deck,opp_deck,s_type):
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

        hero_n =            df0_i[df0_i.P1 == hero].shape[0] # Matches played by hero
        
        formats_played =    df0_i[df0_i.P1 == hero].Format.value_counts().keys().tolist()
        format_counts =     df0_i[df0_i.P1 == hero].Format.value_counts().tolist()
        format_wins =       [df0_i[(df0_i.P1 == hero) & (df0_i.Match_Winner == "P1")].shape[0]] #adding overall in L[0]
        format_losses =     [df0_i[(df0_i.P1 == hero) & (df0_i.Match_Winner == "P2")].shape[0]] #adding overall in L[0]
        format_wr =         [to_percent( format_wins[0]/(format_wins[0]+format_losses[0]) )]    #adding overall in L[0]
        format_counts.insert(0,hero_n)
                         
        for i in formats_played:
            wins  =  df0_i[(df0_i.P1 == hero) & (df0_i.Format == i) & (df0_i.Match_Winner == "P1")].shape[0]
            losses = df0_i[(df0_i.P1 == hero) & (df0_i.Format == i) & (df0_i.Match_Winner == "P2")].shape[0]
            format_wins.append(str(wins))
            format_losses.append(str(losses))
            format_wr.append(to_percent(wins/(wins+losses)))
        formats_played.insert(0,"Overall")
        
        roll_1_mean =       round(df0["P1_Roll"].mean(),2)
        roll_2_mean =       round(df0["P2_Roll"].mean(),2)
        p1_roll_wr =        to_percent((df0[df0.Roll_Winner == "P1"].shape[0])/df0.shape[0])
        p2_roll_wr =        to_percent((df0[df0.Roll_Winner == "P2"].shape[0])/df0.shape[0])
        rolls_won =         df0_i[(df0_i.P1 == hero) & (df0_i.Roll_Winner == "P1")].shape[0] 
        roll_labels =       ["Roll 1 Mean","Roll 2 Mean","Roll 1 Win%","Roll 2 Win%","","Hero Roll Win%"]
        roll_values =       [roll_1_mean,roll_2_mean,p1_roll_wr+"%",p2_roll_wr+"%","",to_percent(rolls_won/hero_n)+"%"]

        df0_i_f = df0_i[(df0_i.P1 == hero)]
        if mformat != "All Formats":
            df0_i_f = df0_i_f[(df0_i_f.Format == mformat)]
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
                meta_deck_wr.append([wins,losses,to_percent(wins/total)])
                
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
                hero_deck_wr.append([wins,losses,to_percent(wins/total)])        

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

        mid_frame2["text"] = "Format Performance"
        tree2.tag_configure("colored",background="#cccccc")
        tree2.delete(*tree2.get_children())
        tree2["column"] = ["Format","Wins","Losses","Match Win%"]
        for i in tree2["column"]:
            tree2.column(i,minwidth=20,stretch=True,width=20)
            tree2.heading(i,text=i)
        tree2.column("Wins",anchor="center")
        tree2.column("Losses",anchor="center")
        tree2.column("Match Win%",anchor="center")
        tagged = False
        for i in range(len(formats_played)):
            tagged = not tagged
            if tagged == True:
                tree2.insert("","end",values=[formats_played[i],
                                              format_wins[i],
                                              format_losses[i],
                                              format_wr[i]+"%"],tags=("colored",))
            else:
                tree2.insert("","end",values=[formats_played[i],
                                              format_wins[i],
                                              format_losses[i],
                                              format_wr[i]+"%"])

        if (deck != "All Decks") or (opp_deck != "All Opp. Decks"):
            mid_frame3["text"] = deck + " vs. " + opp_deck + " - " + mformat
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
        for i in range(10):
            if i >= len(hero_decks):
                break
            tagged = not tagged
            if tagged == True:
                tree3.insert("","end",values=[hero_decks[i],
                                              (str(hero_deck_counts[i])+" - ("+to_percent(hero_deck_counts[i]/filtered_n)+"%)"),
                                              hero_deck_wr[i][0],
                                              hero_deck_wr[i][1],
                                              (hero_deck_wr[i][2]+"%")],tags=("colored",))
            else:
                tree3.insert("","end",values=[hero_decks[i],
                                              (str(hero_deck_counts[i])+" - ("+to_percent(hero_deck_counts[i]/filtered_n)+"%)"),
                                              hero_deck_wr[i][0],
                                              hero_deck_wr[i][1],
                                              (hero_deck_wr[i][2]+"%")])
        if (deck != "All Decks") or (opp_deck != "All Opp. Decks"):
            mid_frame4["text"] = deck + " vs. " + opp_deck + " - "+ mformat
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
        for i in range(10):
            if i >= len(meta_decks):
                break
            tagged = not tagged
            if tagged == True:
                tree4.insert("","end",values=[meta_decks[i],
                                              (str(meta_deck_counts[i])+" - ("+to_percent(meta_deck_counts[i]/filtered_n)+"%)"),
                                              meta_deck_wr[i][0],
                                              meta_deck_wr[i][1],
                                              (meta_deck_wr[i][2]+"%")],tags=("colored",))
            else:
                tree4.insert("","end",values=[meta_decks[i],
                                              (str(meta_deck_counts[i])+" - ("+to_percent(meta_deck_counts[i]/filtered_n)+"%)"),
                                              meta_deck_wr[i][0],
                                              meta_deck_wr[i][1],
                                              (meta_deck_wr[i][2]+"%")])

    def game_stats(hero,mformat,deck,opp_deck,s_type):
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

        frame_labels = [("Overall Data: " + mformat),"Matchup Data","Choose a Deck","Choose an Opposing Deck"]

        tree1data =    []
        frame_labels[0] = (mformat)
        for i in df_list:
            j = i
            if mformat != "All Formats":
                j = i[(i.Format == mformat)]
            total_n = j.shape[0]
            wins =    j[(j.Game_Winner == "P1")].shape[0]
            losses =  j[(j.Game_Winner == "P2")].shape[0]
            if (wins+losses) == 0:
                win_rate = "0"
            else:
                win_rate = to_percent(wins/(wins+losses))
            if total_n == 0:
                hero_mull_rate =0.0
                opp_mull_rate = 0.0
                turn_rate =     0.0
            else:
                hero_mull_rate =round((j.P1_Mulls.sum()/total_n),2)
                opp_mull_rate = round((j.P2_Mulls.sum()/total_n),2)
                turn_rate =     round((j.Turns.sum()/total_n),2)     
            tree1data.append([wins,
                              losses,
                              win_rate,
                              hero_mull_rate,
                              opp_mull_rate,
                              turn_rate])
        
        tree2data = []
        if (deck != "All Decks") & (opp_deck != "All Opp. Decks"):
            frame_labels[1] = ("Matchup Data: " + deck + " vs. " + opp_deck)
            for i in df_list:
                total_n = i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck)].shape[0]
                wins =    i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck) & (i.Game_Winner == "P1")].shape[0]
                losses =  i[(i.P1_Subarch == deck) & (i.P2_Subarch == opp_deck) & (i.Game_Winner == "P2")].shape[0]
                if (wins+losses) == 0:
                    win_rate = "0"
                else:
                    win_rate = to_percent(wins/(wins+losses))
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
            frame_labels[2] = (mformat + ": " + deck + " vs. All Opp. Decks")
            for i in df_list:
                total_n = i[(i.P1_Subarch == deck)].shape[0]
                wins =    i[(i.P1_Subarch == deck) & (i.Game_Winner == "P1")].shape[0]
                losses =  i[(i.P1_Subarch == deck) & (i.Game_Winner == "P2")].shape[0]
                if (wins+losses) == 0:
                    win_rate = "0"
                else:
                    win_rate = to_percent(wins/(wins+losses))
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
            frame_labels[3] = (mformat + ": All Decks vs. " + opp_deck)
            for i in df_list:
                total_n = i[(i.P2_Subarch == opp_deck)].shape[0]
                wins =    i[(i.P2_Subarch == opp_deck) & (i.Game_Winner == "P1")].shape[0]
                losses =  i[(i.P2_Subarch == opp_deck) & (i.Game_Winner == "P2")].shape[0]
                if (wins+losses) == 0:
                    win_rate = "0"
                else:
                    win_rate = to_percent(wins/(wins+losses))
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
                tree.column(0,minwidth=int(main_window_width/16),stretch=False,width=int(main_window_width/16))
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

    def play_stats(hero,mformat,deck,opp_deck,s_type):
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
        df2_merge =     pd.merge(df0,
                                 df2,
                                 how="inner",
                                 left_on=["Match_ID"],
                                 right_on=["Match_ID"])
        df2_hero =      df2_merge[(df2_merge.Casting_Player == hero)]
        
        formats_played = df2_hero.Format.value_counts().keys().tolist()
        format_counts =  df2_hero.Format.value_counts().tolist()
        hero_n = df1_i[(df1_i.P1 == hero)].shape[0]
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
            play_count =    df2_hero[(df2_hero.Format == i) & (df2_hero.Action == "Plays")].shape[0]
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
        if mformat != "All Formats":
            df_tree2 = df2_hero[(df2_hero.Format == mformat)]
        turn_list = df_tree2.Turn_Num.value_counts().keys().tolist()
        turn_list = sorted(turn_list)
        tree2_data =  []
        index_list2 = []
        for i in turn_list:
            play_count =    df_tree2[(df_tree2.Turn_Num == i) & (df_tree2.Action == "Plays")].shape[0]
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

        df2_i_merge =     pd.merge(df0_i,
                                   df2,
                                   how="inner",
                                   left_on=["Match_ID"],
                                   right_on=["Match_ID"])
        df2_i_m_hero = df2_i_merge[(df2_i_merge.P1 == hero)]
   
        decks3 =        []
        index_list3 =   []
        tree3_data =    []
        df_tree3 = df2_i_m_hero[(df2_i_m_hero.Casting_Player == hero)]
        if mformat != "All Formats":
            df_tree3 = df_tree3[(df_tree3.Format == mformat)]
        if deck != "All Decks":
            df_tree3 = df_tree3[(df_tree3.P1_Subarch == deck)]
        hero_decks =    df_tree3.P1_Subarch.value_counts().keys().tolist()
        hero_decks_n =  []
        for i in hero_decks:
            if mformat != "All Formats":
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.Format == mformat) & (df1_i_merge.P1_Subarch == i)].shape[0]
            else:
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P1_Subarch == i)].shape[0]
            hero_decks_n.append(games_played)
            index_list3.append("Total")
            index_list3.append("Per Game")
        tuples = zip(*sorted(zip(hero_decks_n,hero_decks),reverse=True))
        hero_decks_n, hero_decks = [list(tuple) for tuple in tuples]
        for i in range(len(hero_decks)):
            decks3.append(hero_decks[i])
            decks3.append(str(hero_decks_n[i])+" Games")
        for i in hero_decks:
            if mformat != "All Formats":
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.Format == mformat) & (df1_i_merge.P1_Subarch == i)].shape[0]
            else:
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P1_Subarch == i)].shape[0]
            play_count = df_tree3[(df_tree3.P1_Subarch == i) & (df_tree3.Action == "Plays")].shape[0]
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
        if mformat != "All Formats":
            df_tree4 = df_tree4[(df_tree4.Format == mformat)]
        if opp_deck != "All Opp. Decks":
            df_tree4 = df_tree4[(df_tree4.P2_Subarch == opp_deck)]
        opp_decks = df_tree4.P2_Subarch.value_counts().keys().tolist()
        opp_decks_n = []
        for i in opp_decks:
            if mformat != "All Formats":
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.Format == mformat) & (df1_i_merge.P2_Subarch == i)].shape[0]
            else:
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P2_Subarch == i)].shape[0]
            opp_decks_n.append(games_played)
            index_list4.append("Total")
            index_list4.append("Per Game")
        tuples = zip(*sorted(zip(opp_decks_n,opp_decks),reverse=True))
        opp_decks_n, opp_decks = [list(tuple) for tuple in tuples]        
        for i in range(len(opp_decks)):
            decks4.append(opp_decks[i])
            decks4.append(str(opp_decks_n[i])+" Games")
        for i in opp_decks:
            if mformat != "All Formats":
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.Format == mformat) & (df1_i_merge.P2_Subarch == i)].shape[0]
            else:
                games_played = df1_i_merge[(df1_i_merge.P1 == hero) & (df1_i_merge.P2_Subarch == i)].shape[0]
            play_count = df_tree4[(df_tree4.P2_Subarch == i) & (df_tree4.Action == "Plays")].shape[0]
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
            tree4_data.append([round(play_count/games_played,1),
                               round(cast_count/games_played,1),
                               round(act_count/games_played,1),
                               round(trig_count/games_played,1),
                               round(attack_count/games_played,1),
                               round(draw_count/games_played,1)])

        frame_labels = ["Play Data By Format",
                        "Play Data By Turn: " + hero + ", " + mformat,
                        "Play Data: " + deck,
                        "Opposing Play Data: " + opp_deck]

        mid_frame1["text"] = frame_labels[0]
        tree1.tag_configure("colored",background="#cccccc")   
        tree1.delete(*tree1.get_children())
        tree1["column"] = ["","","Plays","Casts","Activates","Triggers","Attacks","Draws"]
        for i in tree1["column"]:
            tree1.column(i,minwidth=25,stretch=True,width=25)
            tree1.heading(i,text=i)
        tree1.column(0,minwidth=int(main_window_width/16),stretch=False,width=int(main_window_width/16))
        for i in range(len(tree1["column"])):
            tree1.column(i,anchor="center")
        tagged = True
        count = 0
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
        tree2["column"] = ["","Plays","Casts","Activates","Triggers","Attacks","Draws","Total GA"]
        for i in tree2["column"]:
            tree2.column(i,minwidth=25,stretch=True,width=25)
            tree2.heading(i,text=i)
        tree2.column(0,minwidth=int(main_window_width/16),stretch=False,width=int(main_window_width/16))
        for i in range(len(tree2["column"])):
            tree2.column(i,anchor="center")
        tagged = True
        for i in range(len(turn_list)):
            if tagged == True:
                tree2.insert("","end",values=index_list2[i]+tree2_data[i],tags=('colored',))
            else:
                tree2.insert("","end",values=index_list2[i]+tree2_data[i])
            tagged = not tagged

        mid_frame3["text"] = frame_labels[2]               
        tree3.tag_configure("colored",background="#cccccc")
        tree3.delete(*tree3.get_children())
        tree3["column"] = ["","","Plays","Casts","Activates","Triggers","Attacks","Draws"]
        for i in tree3["column"]:
            tree3.column(i,minwidth=25,stretch=True,width=25)
            tree3.heading(i,text=i)
        tree3.column(0,minwidth=int(main_window_width/16),stretch=False,width=int(main_window_width/16))
        for i in range(len(tree3["column"])):
            tree3.column(i,anchor="center")
        tagged = True
        count = 0
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
        tree4["column"] = ["","","Plays","Casts","Activates","Triggers","Attacks","Draws"]
        for i in tree4["column"]:
            tree4.column(i,minwidth=25,stretch=True,width=25)
            tree4.heading(i,text=i)
        tree4.column(0,minwidth=int(main_window_width/16),stretch=False,width=int(main_window_width/16))
        for i in range(len(tree4["column"])):
            tree4.column(i,anchor="center")
        tagged = True
        count = 0
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
    
    def time_stats(hero,mformat,deck,opp_deck,s_type):
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
                elif i == "P2":
                    pm_over_time.append(last - 1)
                x.append(index)
                last = pm_over_time[-1]
            if start_index < len(pm_over_time):
                x = x[start_index:]
                pm_over_time = pm_over_time[start_index:]
            return [x,pm_over_time]

        #mid_frame5["text"] = "Win Rate Over Time: " + mformat
        #mid_frame6["text"] = "Win Rate Over Time: "+ mformat + " - " + deck

        df_time = df0_i[(df0_i.P1 == hero)]
        if mformat != "All Formats":
            df_time =   df_time[(df_time.Format == mformat)]
        df_time = df_time.sort_values(by=["Date"])
        #g1_list = get_wr_over_time(df_time,20)
        g1_list = get_pm_over_time(df_time,0)

        fig = plt.figure(figsize=(5,4),dpi=100)
        plt.plot(g1_list[0],g1_list[1])
        plt.title("Match Wins Over .500:\n"+mformat)
        plt.xlabel("Matches Played")
        plt.ylabel("Match Wins Over .500")

        canvas = FigureCanvasTkAgg(fig,mid_frame5)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0,column=0,sticky="")

        if deck != "All Decks":
            df_time_d =  df_time[(df_time.P1_Subarch == deck)] # Filtered by P1=hero,Format=mformat,P1_Subarch=deck
            df_time_d = df_time_d.sort_values(by=["Date"])     
            #g2_list = get_wr_over_time(df_time_d,20)
            g2_list = get_pm_over_time(df_time_d,0)

            fig = plt.figure(figsize=(5,4),dpi=100)
            plt.plot(g2_list[0],g2_list[1])
            plt.title("Match Wins Over .500:\n"+mformat+": "+deck)
            plt.xlabel("Matches Played")
            plt.ylabel("Match Wins Over .500")

            canvas2 = FigureCanvasTkAgg(fig,mid_frame6)
            canvas2.draw()
            canvas2.get_tk_widget().grid(row=0,column=0,sticky="")
    
    def card_stats(hero,mformat,deck,opp_deck,s_type):
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
        tree1 = ttk.Treeview(mid_frame7,show="headings",selectmode="none",padding=10)
        tree2 = ttk.Treeview(mid_frame8,show="headings",selectmode="none",padding=10)
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
        df_merge = df_merge[(df_merge.Game_Winner != "NA")]
        if mformat != "All Formats":
            df_merge = df_merge[(df_merge.Format == mformat)]
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
        wr_pre = round((wins_pre/n_pre)*100,2).item()
        wr_post = round((wins_post/n_post)*100,2).item()
        print(wr_pre)
        print(wr_post)

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
            games_wr_pre.append(round((int(games_won_pre[i])/int(games_played_pre[i]))*100,2))

        cards_played_post = list(df_merge_post.groupby(["Primary_Card"]).groups.keys())
        games_played_post = df_merge_post.groupby(["Primary_Card"]).Game_ID.size().tolist()
        games_won_post =    df_merge_post.groupby(["Primary_Card"]).Won_Game.sum().tolist()
        games_wr_post = []
        for i in range(len(games_played_post)):
            games_wr_post.append(round((int(games_won_post[i])/int(games_played_post[i]))*100,2))

        # Create lists of data to be inserted into trees.
        list_pre =  np.array([cards_played_pre,games_played_pre,games_won_pre,games_wr_pre]).T.tolist()
        list_post = np.array([cards_played_post,games_played_post,games_won_post,games_wr_post]).T.tolist()

        list_pre =  sorted(list_pre,key=lambda x: -int(x[1]))
        list_post = sorted(list_post,key=lambda x: -int(x[1]))

        mid_frame7["text"] = "Pre-Sideboard - " + str(n_pre) + " Games" 
        tree1.tag_configure("colored",background="#cccccc")
        tree1.delete(*tree1.get_children())
        tree1["column"] = ["Card","Games Cast","Game Win%","Delta"]
        for i in tree1["column"]:
            tree1.column(i,minwidth=20,stretch=True,width=20)
            tree1.heading(i,text=i)
        for i in range(1,len(tree1["column"])):
            tree1.column(i,anchor="center")
        tagged = False
        for i in list_pre:
            tagged = not tagged
            if tagged == True:
                tree1.insert("","end",values=[i[0],
                                              i[1]+" - ("+to_percent(int(i[1])/n_pre)+"%)",
                                              i[3],
                                              round(float(i[3])-wr_pre,2)],
                                              tags=("colored",))
            else:
                tree1.insert("","end",values=[i[0],
                                              i[1]+" - ("+to_percent(int(i[1])/n_pre)+"%)",
                                              i[3],
                                              round(float(i[3])-wr_pre,2)])

        mid_frame8["text"] = "Post-Sideboard - " + str(n_post) + " Games"
        tree2.tag_configure("colored",background="#cccccc")
        tree2.delete(*tree2.get_children())
        tree2["column"] = ["Card","Games Cast","Game Win%","Delta"]
        for i in tree2["column"]:
            tree2.column(i,minwidth=20,stretch=True,width=20)
            tree2.heading(i,text=i)
        for i in range(1,len(tree2["column"])):
            tree2.column(i,anchor="center")
        tagged = False
        for i in list_post:
            tagged = not tagged
            if tagged == True:
                tree2.insert("","end",values=[i[0],
                                              i[1]+" - ("+to_percent(int(i[1])/n_post)+"%)",
                                              i[3],
                                              round(float(i[3])-wr_post,2)],
                                              tags=("colored",))
            else:
                tree2.insert("","end",values=[i[0],
                                              i[1]+" - ("+to_percent(int(i[1])/n_post)+"%)",
                                              i[3],
                                              round(float(i[3])-wr_post,2)])
                                                     
    def to_percent(fl):
        return str(int(fl*100))
    
    def update_hero(*argv):
        hero = player.get()

        format_options = df0_i[(df0_i.P1 == player.get())].Format.value_counts().keys().tolist()
        format_options.insert(0,"All Formats")
        menu = menu_2["menu"]
        menu.delete(0,"end")
        for i in format_options:
            menu.add_command(label=i,command=lambda x=i: mformat.set(x))
        mformat.set(format_options[0])

        update_deck_menu()
        update_opp_deck_menu()
       
        menu_2["state"]   = tk.NORMAL
        menu_3["state"]   = tk.NORMAL
        menu_4["state"]   = tk.NORMAL
        menu_5["state"]   = tk.NORMAL
        button_1["state"] = tk.NORMAL
        
    def update_format(*argv):
        update_deck_menu()
        update_opp_deck_menu()

    def update_deck_menu(*argv):  
        if mformat.get() == "All Formats":
            decks_played = df0_i[(df0_i.P1 == player.get())].P1_Subarch.value_counts().keys().tolist()
        else:
            decks_played = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())].P1_Subarch.value_counts().keys().tolist()
        if s_type.get() == "Time Data":
            deck_counts  = df0_i[(df0_i.P1 == player.get())].P1_Subarch.value_counts().tolist()
            for index,i in enumerate(deck_counts):
                if i < 20:
                    del decks_played[index:]
                    del deck_counts[index:]
                    break
        decks_played.insert(0,"All Decks")

        menu = menu_3["menu"]
        menu.delete(0,"end")
        for i in decks_played:
            menu.add_command(label=i,command=lambda x=i: deck.set(x))
        deck.set(decks_played[0])

    def update_opp_deck_menu(*argv):
        if mformat.get() == "All Formats":
            opp_decks_played = df0_i[(df0_i.P1 == player.get())].P2_Subarch.value_counts().keys().tolist()
        else:
            opp_decks_played = df0_i[(df0_i.P1 == player.get()) & (df0_i.Format == mformat.get())].P2_Subarch.value_counts().keys().tolist()

        opp_decks_played.insert(0,"All Opp. Decks")

        menu = menu_4["menu"]
        menu.delete(0,"end")
        for i in opp_decks_played:
            menu.add_command(label=i,command=lambda x=i: opp_deck.set(x))
        opp_deck.set(opp_decks_played[0])

    def update_s_type(*argv):
        update_deck_menu()
        update_opp_deck_menu()
        if s_type.get() == "Time Data":
            menu_4["state"]   = tk.DISABLED
        else:
            menu_4["state"]   = tk.NORMAL

    def load_data():
        if s_type.get() == "Match Stats":
            match_stats(player.get(),mformat.get(),deck.get(),opp_deck.get(),s_type.get())
        elif s_type.get() == "Game Stats":
            game_stats(player.get(),mformat.get(),deck.get(),opp_deck.get(),s_type.get())
        elif s_type.get() == "Play Stats":
            play_stats(player.get(),mformat.get(),deck.get(),opp_deck.get(),s_type.get())
        elif s_type.get() == "Time Data":
            time_stats(player.get(),mformat.get(),deck.get(),opp_deck.get(),s_type.get())
        elif s_type.get() == "Card Data":
            card_stats(player.get(),mformat.get(),deck.get(),opp_deck.get(),s_type.get())      
        
    def close_stats_window():
        window.deiconify()
        stats_window.destroy()
        
    p1_options = df0_i.P1.tolist()
    p1_options = sorted(list(set(p1_options)),key=str.casefold)
    
    format_options = [""]
    decks_played = [""]
    opp_decks_played = [""]
    stat_types = ["Match Stats","Game Stats","Play Stats","Time Data","Card Data"]
    
    player = tk.StringVar()
    player.set("Select a Player")
    mformat = tk.StringVar()
    mformat.set("Format")
    deck = tk.StringVar()
    deck.set("Decks Played")
    opp_deck = tk.StringVar()
    opp_deck.set("Opp. Decks")
    s_type = tk.StringVar()
    s_type.set(stat_types[0])
    
    menu_1 = tk.OptionMenu(top_frame,player,*p1_options)     
    menu_2 = tk.OptionMenu(top_frame,mformat,*format_options)
    menu_3 = tk.OptionMenu(top_frame,deck,*decks_played)
    menu_4 = tk.OptionMenu(top_frame,opp_deck,*opp_decks_played)
    menu_5 = tk.OptionMenu(top_frame,s_type,*stat_types)
    button_1 = tk.Button(top_frame,text="GO",state=tk.DISABLED,command=lambda : load_data())
    
    menu_1["state"] = tk.DISABLED
    menu_2["state"] = tk.DISABLED
    menu_3["state"] = tk.DISABLED
    menu_4["state"] = tk.DISABLED
    menu_5["state"] = tk.DISABLED
    
    menu_1.grid(row=0,column=0,padx=10,pady=10)
    menu_2.grid(row=0,column=1,padx=10,pady=10)
    menu_3.grid(row=0,column=2,padx=10,pady=10)
    menu_4.grid(row=0,column=3,padx=10,pady=10)
    menu_5.grid(row=0,column=4,padx=10,pady=10)
    button_1.grid(row=0,column=5,padx=10,pady=10)
    
    player.trace("w",update_hero)
    mformat.trace("w",update_format)
    s_type.trace("w",update_s_type)

    player.set(hero)    
    stats_window.protocol("WM_DELETE_WINDOW", lambda : close_stats_window())

def exit():
    save_settings()
    window.destroy()

#create a window
window = tk.Tk() 
window.title("MTGO-Stats")
window.minsize(main_window_width,main_window_height)
window.resizable(False,False)

window.rowconfigure(0,minsize=600,weight=1)
window.columnconfigure(1,minsize=1400,weight=1)

bottom_frame = tk.LabelFrame(window)
left_frame = tk.Frame(window)
text_frame = tk.LabelFrame(window,text="Dataframe")
bottom_frame.grid(row=1,column=1,sticky="ew")
left_frame.grid(row=0,column=0,sticky="ns")
text_frame.grid(row=0,column=1,sticky="nsew")

button1 = tk.Button(left_frame,text="Match Data",state=tk.DISABLED,
                     command=lambda : [set_display("Matches")])
button2 = tk.Button(left_frame,text="Game Data",state=tk.DISABLED,
                     command=lambda : [set_display("Games")])
button3 = tk.Button(left_frame,text="Play Data",state=tk.DISABLED,
                     command=lambda : [set_display("Plays")])
button7 = tk.Button(left_frame,text="Filter",state=tk.DISABLED,
                     command=lambda : set_filter())
button8 = tk.Button(left_frame,text="Clear Filter",state=tk.DISABLED,
                     command=lambda : [clear_filter(),set_display(display)])
button4 = tk.Button(left_frame,text="Revise Record",state=tk.DISABLED,
                     command=lambda : [revise_record()])
button9 = tk.Button(left_frame,text="Statistics",state=tk.DISABLED,
                     command=lambda : [get_stats()])
back_button = tk.Button(left_frame,text="Back",
                        command=lambda :
                        bb_clicked(),
                        state=tk.DISABLED)

status_label = tk.Label(bottom_frame,text="")
status_label.pack()

menu_bar = tk.Menu(window)

file_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="File",menu=file_menu)

file_menu.add_command(label="Load MTGO Game Logs",command=lambda : import_window())
file_menu.add_command(label="Clear Loaded Data",command=lambda : clear_window(),state=tk.DISABLED)
file_menu.add_command(label="Save Data",command=lambda : save_window(),state=tk.DISABLED)
file_menu.add_separator()
file_menu.add_command(label="Exit",command=lambda : exit())

export_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="Export",menu=export_menu)

export_csv = tk.Menu(export_menu,tearoff=False)
export_csv.add_command(label="Match History",command=lambda : export("CSV",0,False))
export_csv.add_command(label="Match History (Inverse Join)",command=lambda : export("CSV",0,True))
export_csv.add_command(label="Game History",command=lambda : export("CSV",1,False))
export_csv.add_command(label="Game History (Inverse Join)",command=lambda : export("CSV",1,True))
export_csv.add_command(label="Play History",command=lambda : export("CSV",2,False))
export_csv.add_command(label="All Data (3 Files)",command=lambda : export("CSV",3,False))
export_csv.add_command(label="All Data (Inverse Join)",command=lambda : export("CSV",3,True))
export_csv.add_command(label="Currently Displayed Data (with Filters)",command=lambda : export("CSV",4,False))

export_excel = tk.Menu(export_menu,tearoff=False)
export_excel.add_command(label="Match History",command=lambda : export("Excel",0,False))
export_excel.add_command(label="Match History (Inverse Join)",command=lambda : export("Excel",0,True))
export_excel.add_command(label="Game History",command=lambda : export("Excel",1,False))
export_excel.add_command(label="Game History (Inverse Join)",command=lambda : export("Excel",1,True))
export_excel.add_command(label="Play History",command=lambda : export("Excel",2,False))
export_excel.add_command(label="All Data (3 Files)",command=lambda : export("Excel",3,False))
export_excel.add_command(label="All Data (Inverse Join)",command=lambda : export("Excel",3,True))
export_excel.add_command(label="Currently Displayed Data (with Filters)",command=lambda : export("Excel",4,False))

export_menu.add_cascade(label="Export to CSV",menu=export_csv)
export_menu.add_cascade(label="Export to Excel",menu=export_excel)
export_menu.add_separator()
export_menu.add_command(label="Set Default Export Folder",command=lambda : set_default_export())

data_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="Data",menu=data_menu)

data_menu.add_command(label="Input Missing Match Data",command=lambda : get_formats())
data_menu.add_command(label="Input Missing Game_Winner Data",command=lambda : get_winners())
data_menu.add_separator()
data_menu.add_command(label="Set Default 'Hero'",command=lambda : set_default_hero(),state=tk.DISABLED)
data_menu.add_command(label="Set Default Import Folders",command=lambda : set_default_import())

window.config(menu=menu_bar)

button1.grid(row=0,column=0,sticky="ew",padx=5,pady=(20,5))
button2.grid(row=1,column=0,sticky="ew",padx=5,pady=5)
button3.grid(row=2,column=0,sticky="ew",padx=5,pady=5)
button7.grid(row=6,column=0,sticky="ew",padx=5,pady=(50,5))
button8.grid(row=7,column=0,sticky="ew",padx=5,pady=5)
button4.grid(row=8,column=0,sticky="ew",padx=5,pady=5)
button9.grid(row=9,column=0,sticky="ew",padx=5,pady=50)
back_button.grid(row=12,column=0,sticky="ew",padx=5,pady=5)

tree1 = ttk.Treeview(text_frame,show="tree")
tree1.place(relheight=1, relwidth=1)
tree1.bind("<Double-1>",tree_double)
tree1.bind("<ButtonRelease-1>",activate_revise)

tree_scrollx = tk.Scrollbar(text_frame,orient="horizontal",command=tree1.xview)
tree_scrolly = tk.Scrollbar(text_frame,orient="vertical",command=tree1.yview)
tree1.configure(xscrollcommand=tree_scrollx.set,yscrollcommand=tree_scrolly.set)
tree_scrollx.pack(side="bottom",fill="x")
tree_scrolly.pack(side="right",fill="y")

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

#event loop: listens for events (keypress, etc.)
#blocks code after from running until window is closed
window.mainloop()