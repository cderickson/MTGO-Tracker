#modo match log cleaning module
import tkinter as tk
import pandas as pd
import copy

uaw = None
test = False
window = []
def user_assigned_winner(player):
    global uaw
    uaw = player
    
def match_header():
    #output: list[match_attrs]

    return ["Match_ID",
            "P1",
            "P1_Arch",
            "P1_Subarch",
            "P2",
            "P2_Arch",
            "P2_Subarch",
            "P1_Roll",
            "P2_Roll",
            "Roll_Winner",
            "P1_Wins",
            "P2_Wins",
            "Match_Winner",
            "Format",
            "Match_Type",
            "Date"]

def game_header():
    #output: list[game_attrs]

    return ["Match_ID",
            "P1",
            "P2",
            "Game_Num",
            "PD_Selector",
            "PD_Choice",
            "On_Play",
            "On_Draw",
            "P1_Mulls",
            "P2_Mulls",
            "Turns",
            "Game_Winner"]

def play_header():
    #output: list[play_attrs]

    return ["Match_ID",
            "Game_Num",
            "Play_Num",
            "Turn_Num",\
            "Casting_Player",
            "Action",
            "Primary_Card",
            "Target1",
            "Target2",
            "Target3",
            "Opp_Target",
            "Self_Target",
            "Cards_Drawn",
            "Attackers",
            "Active_Player",
            "Nonactive_Player"]

def get_arch(subarch):
    #input:  string
    #output: string

    arch_dict = {"Izzet Delver":"Tempo",
                 "Death and Taxes":"Prison",
                 "Snow Miracles":"Control",
                 "Apr":"04",
                 "May":"05",
                 "Jun":"06",
                 "Jul":"07",
                 "Aug":"08",
                 "Sep":"09",
                 "Oct":"10",
                 "Nov":"11",
                 "Dec":"12"}    
    if subarch in arch_dict:
        return arch_dict[subarch]
    else:
        return "ROGUE"

def transpose(data):
    #input:  list[rows]
    #output: list[cols]
    
    return [list(x) for x in zip(*data)]

def swap_cols(data,header,col_a,col_b):
    #input:  list[matchdata or gamedata],colheader string,colheader string
    #output: list[matchdata]   

    for index,i in enumerate(header):
        if i == col_a:
            a = index
        elif i == col_b:
            b = index
    data[a], data[b] = data[b], data[a]
    
def invert_matchdata(data):
    #input:  list[matchdata]
    #output: list[matchdata]

    swap_cols(data,match_header(),"P1","P2")
    swap_cols(data,match_header(),"P1_Arch","P2_Arch")
    swap_cols(data,match_header(),"P1_Subarch","P2_Subarch")
    swap_cols(data,match_header(),"P1_Roll","P2_Roll")
    swap_cols(data,match_header(),"P1_Wins","P2_Wins")

    cols_to_invert = ["Match_Winner","Roll_Winner"]
    for i in cols_to_invert:
        for index,j in enumerate(match_header()):
            if j == i:
                a = index
        if data[a] == "P1":
            data[a] = "P2"
        elif data[a] == "P2":
            data[a] = "P1"

def invert_gamedata(data):
    #input:  list[gamedata]
    #output: list[gamedata]

    swap_cols(data,game_header(),"P1","P2")
    swap_cols(data,game_header(),"P1_Mulls","P2_Mulls")
    swap_cols(data,game_header(),"On_Play","On_Draw")
    
    cols_to_invert = ["PD_Selector","Game_Winner"]
    for i in cols_to_invert:
        for index,j in enumerate(game_header()):
            if j == i:
                a = index
        if data[a] == "P1":
            data[a] = "P2"
        elif data[a] == "P2":
            data[a] = "P1"

def invert_join(ad):
    #input:  list[list[matches],list[games],list[plays]]
    #output: list[list[matches],list[games],list[plays]]
    ad_inverted = copy.deepcopy(ad)
    
    for i in ad_inverted[0]:
        invert_matchdata(i)
    for i in ad_inverted[1]:
        invert_gamedata(i)

    ad_inverted[0] += ad[0]
    ad_inverted[1] += ad[1]

    return ad_inverted

def update_game_wins(ad,headers):
    #input:  list[matches,games,plays],list[mheader,gheader,pheader]
    #output: list[matches,games,plays]
    
    for index,i in enumerate(headers[0]):
        if i == "P1_Wins":
            p1wins_index = index
        elif i == "P2_Wins":
            p2wins_index = index
        elif i == "Match_Winner":
            mw_index = index
    for index,i in enumerate(headers[1]):
        if i == "Game_Winner":
            gw_index = index

    for i in ad[0]: # Iterate through Matches.
        i[p1wins_index] = 0
        i[p2wins_index] = 0
        i[mw_index]     = "NA"
        for j in ad[1]: # Iterate through Games.
            if i[0] == j[0]: # If Match and Game have matching Match_ID
                if j[gw_index] == "P1": # Check if P1 or P2 won the game.
                    i[p1wins_index] += 1
                elif j[gw_index] == "P2":
                    i[p2wins_index] += 1
                elif j[gw_index] == "NA":
                    pass
            if i[p1wins_index] > i[p2wins_index]:
                i[mw_index] = "P1"
            elif i[p2wins_index] > i[p1wins_index]:
                i[mw_index] = "P2"
            
def to_dataframe(data,headers):
    #input:  list[matchdata/gamedata/playdata],list[headers]
    #output: dataframe

    return pd.DataFrame(data,columns=headers)
    
def format_time(time):
    #input:  string
    #output: string

    time = time.split()
    hhmmss = time[3].split(":")

    month_dict = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05",\
                 "Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10",\
                 "Nov":"11","Dec":"12"}

    time[1] = month_dict[time[1]]
    if len(time[2]) < 2:
        time[2] = "0" + time[2]
        
    return time[4] + time[1] + time[2] + hhmmss[0] + hhmmss[1]
    
def players(init):
    #input:  string or list[strings]
    #output: list[strings]

    if isinstance(init, str):
        init = init.split("@P")
        
    players = []
    
    #initialize list of players in the game
    for i in init:
        if i.find(" joined the game") != -1:
            player = i.split(" joined the game")[0]
            player.replace(" ","+")
            players.append(player)

    #filter duplicates from player list
    players = list(set(players))
    players.sort()
    players.sort(key=len, reverse=True)

    return players

def players_dict(init):
    #input:  string or list[strings]
    #output: dict[string : string]

    if isinstance(init, str):
        init = init.split("@P")
        
    players = {}
    
    #initialize list of players in the game
    for i in init:
        if i.find(" joined the game") != -1:
            player = i.split(" joined the game")[0]
            players[player] = player.replace(" ","+")
    return players

def high_roll(init):
    #input:  string or list[strings]
    #output: dict{string : int}

    if isinstance(init, str):
        init = init.split("@P")

    rolls = {}
    for i in init:
        tstring = i.rsplit(".")[0]
        if i.find(" rolled a ") != -1:
            tlist = tstring.split(" rolled a ")
            if len(tlist[1]) == 1:
                rolls[tlist[0].replace(" ","+")] = int(tlist[1])          
    return rolls        

def mulls(cards):
    #input:  string
    #output: int

    mull_dict = {"seven":0,"six":1,"five":2,"four":3,"three":4,"two":5,\
                 "one":6,"zero":7}
    return mull_dict[cards]
    
def get_winner(curr_game_list,p1,p2):
    #input:  [gameactions],string,string,
    #output: string
    if test:
        return p1
    
    global uaw
    uaw = None

    lastline = curr_game_list[-1]
    #add more lose conditions
    if lastline.find("has conceded") != -1 or \
       lastline.find("is being attacked") != -1 or \
       lastline.find("has lost the game") != -1 or \
       lastline.find("loses because of drawing a card") != -1:
        if lastline.split()[0] == p1:
            return "P2"
        elif lastline.split()[0] == p2:
            return "P1"
    #add more win conditions
    if lastline.find("triggered ability from [Thassa's Oracle]") != -1:
        if lastline.split()[0] == p1:
            return "P1"
        elif lastline.split()[0] == p2:
            return "P2"
    # Could not determine a winner.
    return "NA"
    
def get_cards(play):
    #input:  string
    #output: list[strings]

    cards = []
    count = play.count("[")
    
    while count > 0:
        play = play.split("[",1)
        play = play[1].split("]",1)
        cards.append(play[0])
        play = play[1]
        count -= 1

    while len(cards) < 3:
        cards.append("NA")
        
    return cards

def cards_played(plays,*argv):
    #input:  list[plays],string
    #output: set{strings}

    cards_played = []
    if len(argv) == 0: #return all cards played
        for i in plays:
            if (i[5] == "Plays" or i[5] == "Casts"):
                cards_played.append(i[6])        
    elif len(argv) > 0: #return all cards played by player
        for player in argv:
            for i in plays:
                if i[4] == player and (i[5] == "Plays" or i[5] == "Casts"):
                    cards_played.append(i[6])

    return set(cards_played)

def closest_list(cards_played,alldecks):
    #input:  set[cards],list[string,string,set[cards]]
    #output: string
    
    sim_dict = {}
    for i in alldecks:
        sim = len(cards_played.intersection(i[2]))/len(i[2])
        sim = int(sim * 100)
        sim_dict[i[1]] = sim

    if max(sim_dict.values()) > 20:
        return max(sim_dict,key=sim_dict.get)
    else:
        return "Unknown"
    #return max(sim_dict,key=sim_dict.get) + " " + str(max(sim_dict.values()))

def replace_pname(tstring,plist,pdict):
    #input:  string,list,dict
    #output: string

    for i in plist:
        if tstring.find(i) != -1:
            tstring = tstring.replace(i,pdict[i])
    return tstring

def parse_list(filename,init):
    #input:  string,string
    #output: [string,string,set{maindeck+sideboard}]

    initial = init.split("\n")
    name = filename.split(".txt")[0].split("Deck - ")[1]
    maindeck = []
    sideboard = []
    card_count = 0
    card = ""
    sb = False
    
    if initial[-1] == "":
        initial.pop()
    
    for i in initial:
        if i == "" and sb == False:
            sb = True
        else:
            card_count = int(i.split(" ",1)[0])
            card = i.split(" ",1)[1]
            while card_count > 0 and sb == False:
                maindeck.append(card)
                card_count -= 1
            while card_count > 0 and sb == True:
                sideboard.append(card)
                card_count -= 1
                
    return [get_arch(name),name,set(maindeck)]

def game_actions(init,time):
    #input:  string,string
    #output: list[strings]
    
    initial =       init.split("@P")
    gameactions =   []
    p =             players(init)
    pdict =         players_dict(init)
    count =         0
    lost_conn =     0
    
    gameactions.append(format_time(time))
    for i in initial:
        fullstring = i.rsplit(".")[0]
        #player joined game header
        if count == 0:
            count += 1
        elif i.find(" has lost connection to the game") != -1:
            lost_conn = 1
        elif i.find(" joined the game.") != -1:
            if lost_conn == 1:
                lost_conn = 0
            else:
                gameactions.append(replace_pname(fullstring,p,pdict))
        #skip looking at extra cards
        elif i.find(" draws their next card.") != -1:
            None
        #skip leaving to sideboard
        elif i.find(" has left the game.") != -1:
            None
        #new turn header
        elif i.find("Turn ") != -1 and i.find(": ") != -1:
            newstring = i.split()[0] + " " + i.split()[1]
            for j in p:
                if len(newstring.split()) < 3:
                    if i.split(": ")[1].find(j) != -1:
                        newstring += " " + j
            gameactions.append(replace_pname(newstring,p,pdict))
        #remove tags from cards and rules text
        elif fullstring.count("[") > 0:
            newstring = ""
            while fullstring.count("[") > 0:
                tlist = fullstring.split("@",1)
                newstring += replace_pname(tlist[0],p,pdict)
                fullstring = tlist[1]
                tlist = fullstring.split("@",1)
                newstring += tlist[0] + "]"
                fullstring = tlist[1]
                tlist = fullstring.split("]",1)
                fullstring = tlist[1]        
            newstring += replace_pname(tlist[1],p,pdict)
            newstring = newstring.split("(")[0]
            gameactions.append(newstring)
        #everything else
        elif i.find(".") != -1:
            gameactions.append(replace_pname(fullstring,p,pdict))
    return gameactions

def match_data(ga,gd,pd,ad):
    #input:  [gameactions],[gamedata],[playdata],alldecks
    #output: list[match_att]

    match_data =    []
    p1 =            players(ga)[0]
    p1_arch =       "NA"
    p1_subarch =    "NA"
    p2 =            players(ga)[1]
    p2_arch =       "NA"
    p2_subarch =    "NA"
    p1_roll =       high_roll(ga)[p1]
    p2_roll =       high_roll(ga)[p2]
    p1_wins =       0
    p2_wins =       0
    match_winner =  ""
    match_format =  "NA"
    player_count =  len(players(ga))
    prev_string =   ""
    match_type =    "NA"
    date =          ga[0][0:4] + "-" + ga[0][4:6] + "-" + ga[0][6:8] + "-" + ga[0][8:10] + ":" + ga[0][10:]
    if p1_roll > p2_roll:
        roll_winner = "P1"
    else:
        roll_winner = "P2"
    match_id = ga[0] + "_" + players_dict(ga)[p1] + "_" + players_dict(ga)[p2]
    
    for i in gd:
        if i[0] == match_id and i[11] == "P1":
            p1_wins += 1
        elif i[0] == match_id and i[11] == "P2":
            p2_wins += 1
       
    if p1_wins > p2_wins:
        match_winner = "P1"
    elif p2_wins > p1_wins:
        match_winner = "P2"
    else:
        match_winner = "NA"

    p1_subarch = closest_list(cards_played(pd,p1),ad)
    p2_subarch = closest_list(cards_played(pd,p2),ad)
    
    match_data.extend((match_id,
                       p1,
                       p1_arch,
                       p1_subarch,
                       p2,
                       p2_arch,
                       p2_subarch,
                       p1_roll,
                       p2_roll,
                       roll_winner,
                       p1_wins,
                       p2_wins,
                       match_winner,
                       match_format,
                       match_type,
                       date))
    return match_data

def game_data(ga):
    #input:  list[gameactions]
    #output: list[g1_list,g2_list,g3_list]

    game_num =      0
    pd_selector =   ""
    pd_choice =     ""
    on_play =       ""
    on_draw =       ""
    p1_mulls =      0
    p2_mulls =      0
    turns =         0
    game_winner =   ""
    game_data =     []
    g1 =            []
    g2 =            []
    g3 =            []
    curr_game_list =[]
    all_games_ga =  []
    p1 =            players(ga)[0]
    p2 =            players(ga)[1]   
    player_count =  len(players(ga))
    prev_string =   ""
    curr_list =     []

    match_id = ga[0] + "_" + players_dict(ga)[p1] + "_" + players_dict(ga)[p2]    
    for i in ga:
        curr_list = i.split()
        if i.find("joined the game") != -1:
            if player_count == 0:
                #new game
                player_count = len(players(ga)) - 1
                game_winner = get_winner(curr_game_list,p1,p2)
                if game_winner == "NA":
                    all_games_ga.append(curr_game_list)
                if game_num == 1:
                    g1.extend((match_id,
                               p1,
                               p2,
                               game_num,
                               pd_selector,
                               pd_choice,
                               on_play,
                               on_draw,
                               p1_mulls,
                               p2_mulls,
                               turns,
                               game_winner))
                    game_data.append(g1)
                elif game_num == 2:
                    g2.extend((match_id,
                               p1,
                               p2,
                               game_num,
                               pd_selector,
                               pd_choice,
                               on_play,
                               on_draw,
                               p1_mulls,
                               p2_mulls,
                               turns,
                               game_winner))
                    game_data.append(g2)
                curr_game_list = []
            else:
                player_count -= 1
        elif i.find("chooses to play first") != -1 or \
             i.find("chooses to not play first") != -1:
            game_num += 1
            if curr_list[0] == p1:
                pd_selector = "P1"
            else:
                pd_selector = "P2"
            if curr_list[3] == "play":
                pd_choice = "Play"
            else:
                pd_choice = "Draw"
            if pd_selector == "P1" and pd_choice == "Play":
                on_play = "P1"
                on_draw = "P2"
            elif pd_selector == "P2" and pd_choice == "Play":
                on_play = "P2"
                on_draw = "P1"
            elif pd_selector == "P1" and pd_choice == "Draw":
                on_play = "P2"
                on_draw = "P1"
            elif pd_selector == "P2" and pd_choice == "Draw":
                on_play = "P1"
                on_draw = "P2"
        elif i.find("begins the game with") != -1 and \
             i.find("cards in hand") != -1:
            if p1 == curr_list[0]:              
                p1_mulls = mulls(i.split(" begins the game with ")[1].split()[0])
            elif p2 == curr_list[0]:
                p2_mulls = mulls(i.split(" begins the game with ")[1].split()[0])
        elif i.find("Turn ") != -1 and \
             len(curr_list) == 3:
            turns = int(curr_list[1].split(":")[0])
        curr_game_list.append(i)
    game_winner = get_winner(curr_game_list,p1,p2)
    if game_winner == "NA":
        all_games_ga.append(curr_game_list)
    if game_num == 1:
        g1.extend((match_id,
                   p1,
                   p2,
                   game_num,
                   pd_selector,
                   pd_choice,
                   on_play,
                   on_draw,
                   p1_mulls,
                   p2_mulls,
                   turns,
                   game_winner))
        game_data.append(g1)
    elif game_num == 2:
        g2.extend((match_id,
                   p1,
                   p2,
                   game_num,
                   pd_selector,
                   pd_choice,
                   on_play,
                   on_draw,
                   p1_mulls,
                   p2_mulls,
                   turns,
                   game_winner))
        game_data.append(g2)
    elif game_num == 3:
        g3.extend((match_id,
                   p1,
                   p2,
                   game_num,
                   pd_selector,
                   pd_choice,
                   on_play,
                   on_draw,
                   p1_mulls,
                   p2_mulls,
                   turns,
                   game_winner))
        game_data.append(g3)
    game_data.append(all_games_ga)
    return game_data

def is_play(play):
    #input:  string
    #output: bool

    action_keywords = ["plays","casts","draws","chooses","discards"]
    action_keyphrases = ["is being attacked by",
                         "puts triggered ability from",
                         "activates an ability of",]
    curr_list = play.split()
    if len(curr_list) > 1:
        for i in action_keyphrases:
            if play.find(i) != -1:
                return True
        if curr_list[1] in action_keywords:
            return True
    return False

def player_is_target(tstring,player):
    #input:  string,string
    #output: 1 or 0

    count = tstring.count("[")
    
    while count > 0:
        tstring = tstring.split("[",1)
        if tstring[0].find(player) != -1:
            return 1
        else:
            tstring = tstring[1].split("]",1)[1]
            count -= 1
    if tstring.find(player) != -1:
        return 1   
    return 0

def cards_drawn(cards_drawn):
    #input:  string
    #output: int

    num_dict = {"a":1,
                "two":2,
                "three":3,
                "four":4,
                "five":5,
                "six":6,
                "seven":7}
    return num_dict[cards_drawn]
    
def play_data(ga):
    #input:  list[gameactions]
    #output: list[plays]
    
    game_num = 0
    play_num = 0
    turn_num = 0
    active_player = ""
    non_active_player = ""
    play_data = []
    all_plays = []
    p1 = players(ga)[0]
    p2 = players(ga)[1]
    curr_list = []

    match_id = ga[0] + "_" + players_dict(ga)[p1] + "_" + players_dict(ga)[p2]    
    for i in ga:
        curr_list = i.split()
        casting_player = ""
        action = ""
        primary_card = "NA"
        target1 = "NA"
        target2 = "NA"
        target3 = "NA"
        opp_target = 0
        self_target = 0
        cardsdrawn = 0
        attackers = 0
        play_data = []
        if i.find("chooses to play first") != -1 or \
             i.find("chooses to draw first") != -1:
            game_num += 1
            play_num = 0
        elif i.find("Turn ") != -1 and \
             len(curr_list) == 3:
            turn_num = int(curr_list[1].split(":")[0])
            active_player = curr_list[2]
            if active_player == p1:
                non_active_player = p2
            else:
                non_active_player = p1
        elif is_play(i):
            play_num += 1
            if curr_list[1] == "plays":
                casting_player = curr_list[0]
                primary_card = get_cards(i)[0]
                action = curr_list[1].capitalize()
            elif curr_list[1] == "casts":
                casting_player = curr_list[0]
                primary_card = get_cards(i)[0]
                action = curr_list[1].capitalize()
                if i.find("targeting") != -1:
                    targets = get_cards(i.split("targeting")[1])
                    target1 = targets[0]
                    target2 = targets[1]
                    target3 = targets[2]
                    if casting_player == p1:
                        self_target = player_is_target(i.split("targeting")[1],p1)
                        opp_target = player_is_target(i.split("targeting")[1],p2)
                    elif casting_player == p2:
                        self_target = player_is_target(i.split("targeting")[1],p2)
                        opp_target = player_is_target(i.split("targeting")[1],p1)                    
            elif curr_list[1] == "draws":
                casting_player = curr_list[0]
                action = curr_list[1].capitalize()
                cardsdrawn = cards_drawn(curr_list[2])
            elif curr_list[1] == "chooses":
                casting_player = curr_list[0]
                action = curr_list[1].capitalize()
            elif curr_list[1] == "discards":
                casting_player = curr_list[0]
                action = curr_list[1].capitalize()
            elif i.find("is being attacked by") != -1:
                casting_player = active_player
                action = "Attacks"
                attackers = len(get_cards(i))
            elif i.find("puts triggered ability from") != -1:
                casting_player = curr_list[0]
                primary_card = get_cards(i)[0]
                action = "Triggers"
                if i.find("targeting") != -1:
                    targets = get_cards(i.split("targeting")[1])
                    target1 = targets[0]
                    target2 = targets[1]
                    target3 = targets[2]
                    if casting_player == p1:
                        self_target = player_is_target(i.split("targeting")[1],p1)
                        opp_target = player_is_target(i.split("targeting")[1],p2)
                    elif casting_player == p2:
                        self_target = player_is_target(i.split("targeting")[1],p2)
                        opp_target = player_is_target(i.split("targeting")[1],p1)
            elif i.find("activates an ability of") != -1:
                casting_player = curr_list[0]
                primary_card = get_cards(i)[0]
                action = "Activated Ability"
                if i.find("targeting") != -1:
                    targets = get_cards(i.split("targeting")[1])
                    target1 = targets[0]
                    target2 = targets[1]
                    target3 = targets[2]
                    if casting_player == p1:
                        self_target = player_is_target(i.split("targeting")[1],p1)
                        opp_target = player_is_target(i.split("targeting")[1],p2)
                    elif casting_player == p2:
                        self_target = player_is_target(i.split("targeting")[1],p2)
                        opp_target = player_is_target(i.split("targeting")[1],p1)
            play_data.extend((match_id,
                              game_num,
                              play_num,
                              turn_num,
                              casting_player,
                              action,
                              primary_card,
                              target1,
                              target2,
                              target3,
                              opp_target,
                              self_target,
                              cardsdrawn,
                              attackers,
                              active_player,
                              non_active_player))
            all_plays.append(play_data)
    return all_plays

def get_all_data(init,mtime,alldecks,w):
    #input:  string,string
    #output: list[matches,games,plays]
    global window
    window = w
    
    gameactions = game_actions(init,mtime)
    gamedata = game_data(gameactions)
    rawdata = gamedata[-1]
    gamedata.pop()
    playdata = play_data(gameactions)
    matchdata = match_data(gameactions,gamedata,playdata,alldecks)

    return [matchdata,gamedata,playdata,rawdata]
