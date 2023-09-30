# MODO GameLog Cleaning Module
import copy
import numpy as np

# To add a column to a database:
# Add the column to modo.header() function.
# Add the column to appropriate modo.XXXX_data() function.
# Any saved data will have to be deleted and reloaded.

# To add a menu option to dropdowns in revision windows:
# Add the option to the appropriate list below.
# Add the option under the appropriate header in the input_options.txt file.

def clean_card_set(card_set, MULTIFACED_CARDS):
    cards = card_set
    for i in list(cards):
        if i == "NA":
            cards.remove(i)
        elif i in MULTIFACED_CARDS['SPLIT']:
            cards.add(i + '/' + MULTIFACED_CARDS['SPLIT'][i])
            cards.remove(i)
        elif i in list(MULTIFACED_CARDS['SPLIT'].values()):
            for key, value in MULTIFACED_CARDS['SPLIT'].items():
                if value == i:
                    cards.add(f'{key}/{value}')
            cards.remove(i)
        elif i in list(MULTIFACED_CARDS['MDFC'].values()):
            for key, value in MULTIFACED_CARDS['MDFC'].items():
                if value == i:
                    cards.add(key)
            cards.remove(i)
        elif i in list(MULTIFACED_CARDS['ADVENTURE'].values()):
            for key, value in MULTIFACED_CARDS['ADVENTURE'].items():
                if value == i:
                    cards.add(key)
            cards.remove(i)
    return cards
def formats(lim=False,con=False,cube=False,booster=False,sealed=False):
    formats = []
    lim_formats =  ["Booster Draft",
                    "Sealed Deck",
                    "Cube"]
    con_formats =  ["Vintage",
                    "Legacy",
                    "Modern",
                    "Standard",
                    "Pioneer",
                    "Pauper",
                    "Other Constructed"]
    cube_formats = ["Cube-Other",
                    "Vintage Cube",
                    "Legacy Cube",
                    "Modern Cube"]
    draft_formats= ["VMA x3",
                    "VOW x3",
                    "MID x3",
                    "AFR x3",
                    "MH2 x3",
                    "STX x3",
                    "TSR x3",
                    "KHM x3",
                    "ZNR x3",
                    "2XM x3",
                    "M21 x3",
                    "IKO x3",
                    "THB x3",
                    "ELD x3",
                    "M20 x3",
                    "MH1 x3",
                    "WAR x3",
                    "RNA x3",
                    "UMA x3",
                    "GRN x3",
                    "M19 x3",
                    "DOM x3",
                    "A25 x3",
                    "RIX x3",
                    "IMA x3",
                    "XLN x3",
                    "HOU x3",
                    "AKH x3",
                    "MM3 x3",
                    "AER x3",
                    "Other Booster Draft"]
    sealed_formats=["VOW x6",
                    "MID x6",
                    "AFR x6",
                    "MH2 x6",
                    "STX x6",
                    "TSR x6",
                    "KHM x6",
                    "ZNR x6",
                    "2XM x6",
                    "M21 x6",
                    "IKO x6",
                    "THB x6",
                    "ELD x6",
                    "M20 x6",
                    "MH1 x6",
                    "WAR x6",
                    "RNA x6",
                    "UMA x6",
                    "GRN x6",
                    "M19 x6",
                    "DOM x6",
                    "A25 x6",
                    "RIX x6",
                    "IMA x6",
                    "XLN x6",
                    "HOU x6",
                    "AKH x6",
                    "MM3 x6",
                    "AER x6",
                    "Other Sealed"]
    if lim:
        formats.extend(lim_formats)
    if con:
        formats.extend(con_formats)
    if cube:
        formats.extend(cube_formats)
    if booster:
        formats.extend(draft_formats)
    if sealed:
        formats.extend(sealed_formats)
    return formats
def match_types(con=False,booster=False,sealed=False):
    match_types = []
    con_types = ["League",
                "Preliminary",
                "Challenge",
                "Premier Constructed",
                "2-Man",
                "Practice",
                "Open Play BO1"]
    booster_types = ["Draft League",
                    "Swiss Draft",
                    "Elimination Draft"]
    sealed_types = ["Friendly Sealed League",
                    "Competitive Sealed League",
                    "Premier Sealed"]
    if con:
        match_types.extend(con_types)
    if booster:
        match_types.extend(booster_types)
    if sealed:
        match_types.extend(sealed_types)
    return match_types
def archetypes():
    return ["Aggro",
            "Midrange",
            "Control",
            "Combo",
            "Prison",
            "Tempo",
            "Ramp",
            "Rogue"]
def header(table):
    # Output: List[Play_Attributes]

    if table == "Matches":
        return ["Match_ID",
                "Draft_ID",
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
                "Limited_Format",
                "Match_Type",
                "Date"]
    elif table == "Games":
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
    elif table == "Plays":
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
    elif table == "Drafts":
        return ["Draft_ID",\
                "Hero",\
                "Player_2",\
                "Player_3",\
                "Player_4",\
                "Player_5",\
                "Player_6",\
                "Player_7",\
                "Player_8",\
                "Match_Wins",\
                "Match_Losses",\
                "Format",\
                "Date"]
    elif table == "Picks":
        return ["Draft_ID",\
                "Card",\
                "Pack_Num",\
                "Pick_Num",\
                "Pick_Ovr",\
                "Avail_1",\
                "Avail_2",\
                "Avail_3",\
                "Avail_4",\
                "Avail_5",\
                "Avail_6",\
                "Avail_7",\
                "Avail_8",\
                "Avail_9",\
                "Avail_10",\
                "Avail_11",\
                "Avail_12",\
                "Avail_13",\
                "Avail_14"]
    return []
def invert_join(ad):
    # Input:  List[List[Matches],List[Games],List[Plays]]
    # Output: List[List[Matches],List[Games],List[Plays]]

    def swap_cols(data,header,col_a,col_b):
        # Input:  List[Matches or Games],List[Headers],String,String
        # Output: List[Matches]   

        for index,i in enumerate(header):
            if i == col_a:
                a = index
            elif i == col_b:
                b = index
        data[a], data[b] = data[b], data[a]

    def invert_matchdata(data):
        # Input:  List[Matches]
        # Output: List[Matches]

        swap_cols(data,header("Matches"),"P1","P2")
        swap_cols(data,header("Matches"),"P1_Arch","P2_Arch")
        swap_cols(data,header("Matches"),"P1_Subarch","P2_Subarch")
        swap_cols(data,header("Matches"),"P1_Roll","P2_Roll")
        swap_cols(data,header("Matches"),"P1_Wins","P2_Wins")

        cols_to_invert = ["Match_Winner","Roll_Winner"]
        for i in cols_to_invert:
            for index,j in enumerate(header("Matches")):
                if j == i:
                    a = index
            if data[a] == "P1":
                data[a] = "P2"
            elif data[a] == "P2":
                data[a] = "P1"

    def invert_gamedata(data):
        # Input:  List[Games]
        # Output: List[Games]

        swap_cols(data,header("Games"),"P1","P2")
        swap_cols(data,header("Games"),"P1_Mulls","P2_Mulls")
        swap_cols(data,header("Games"),"On_Play","On_Draw")
        
        cols_to_invert = ["PD_Selector","Game_Winner"]
        for i in cols_to_invert:
            for index,j in enumerate(header("Games")):
                if j == i:
                    a = index
            if data[a] == "P1":
                data[a] = "P2"
            elif data[a] == "P2":
                data[a] = "P1"

    ad_inverted = copy.deepcopy(ad)
    for i in ad_inverted[0]:
        invert_matchdata(i)
    for i in ad_inverted[1]:
        invert_gamedata(i)

    ad_inverted[0] += ad[0]
    ad_inverted[1] += ad[1]

    return ad_inverted
def update_game_wins(ad,timeout):
    #Input:  List[Matches,Games,Plays]
    #Output: List[Matches,Games,Plays]
    
    p1_index = header("Matches").index("P1")
    p2_index = header("Matches").index("P2")
    p1wins_index = header("Matches").index("P1_Wins")
    p2wins_index = header("Matches").index("P2_Wins")
    mw_index = header("Matches").index("Match_Winner")
    gw_index = header("Games").index("Game_Winner")

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
        else:
            if i[0] in timeout:
                if i[p1_index] == timeout[i[0]]:
                    i[mw_index] = "P2"
                elif i[p2_index] == timeout[i[0]]:
                    i[mw_index] = "P1"
def players(init):
    # Input:  String or List[Strings]
    # Output: List[Strings]

    if isinstance(init, str):
        init = init.split("@P")
        
    players = []
    
    # Initialize list of players in the game
    for i in init:
        if i.find(" joined the game") != -1:
            player = i.split(" joined the game")[0]
            players.append(player)

    # Filter duplicates from player list
    players = list(set(players))
    players.sort()
    players.sort(key=len, reverse=True)

    return players
def alter(player_name,original):
    if original == True:
        player = player_name.replace("+"," ")
        player = player.replace("*",".")
    else:
        player = player_name.replace(" ","+")
        player = player.replace(".","*")
    return player     
def closest_list(cards_played,ad,yyyy_mm):
    # Input:  Set{Strings},Dict{String : List[String,String,Set[Strings]]},String
    # Output: [String,String]
    
    decks = []
    yyyy = yyyy_mm[0:4]
    mm = yyyy_mm[5:7]
    if mm == "01":
        mm = "12"
        yyyy = str(int(yyyy) - 1)
    else:
        mm = str(int(mm) - 1).zfill(2)
    yyyy_mm_prev = yyyy + "-" + mm

    if yyyy_mm in ad:
        decks = ad.get(yyyy_mm).copy()
    if yyyy_mm_prev in ad:
        decks.extend(ad.get(yyyy_mm_prev).copy())
    if decks == []:
        return ["Unknown","NA"]

    sim_list = []
    for i in decks:
        if i == None:
            print("error: Null List")
            continue

        if len(i[2]) == 0:
            sim = 0
        else:
            sim = len(cards_played.intersection(i[2]))/len(i[2])
        sim = round((sim * 100),3)
        sim_list.append(sim)

    index = sim_list.index(max(sim_list))
    if max(sim_list) > 20:
        return [decks[index][0],decks[index][1]]
    else:
        return ["Unknown","NA"]
def get_limited_subarch(cards_played):
    # Input:  Set{Strings}
    # Output: [String,String]

    wubrg = ["","","","",""]

    for card in cards_played:
        if card == "Plains":
            wubrg[0] = "W"
        elif card == "Island":
            wubrg[1] = "U"
        elif card == "Swamp":
            wubrg[2] = "B"
        elif card == "Mountain":
            wubrg[3] = "R"
        elif card == "Forest":
            wubrg[4] = "G"

    limited_sa = wubrg[0] + wubrg[1] + wubrg[2] + wubrg[3] + wubrg[4]
    if limited_sa == "":
        return "NA"
    else:
        return limited_sa
def parse_list(filename,init):
    # Input:  String,String
    # Output: [String,String,Set{MaindeckCards+SideboardCards}]

    initial = init.split("\n")
    d_format = filename.split(".txt")[0].split(" - ")[0]
    name = filename.split(".txt")[0].split(" - ")[1]
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
            try:
                card_count = int(i.split(" ",1)[0])
            except ValueError:
                return None
            card = i.split(" ",1)[1]
            while card_count > 0 and sb == False:
                maindeck.append(card)
                card_count -= 1
            while card_count > 0 and sb == True:
                sideboard.append(card)
                card_count -= 1
                
    return [name,d_format,set(maindeck)]
def parse_draft_log(file,initial):
    PICKS_TABLE = []
    DRAFTS_TABLE = []

    DRAFT_ID = ""
    DATE = ""
    EVENT_NUM = ""
    HERO = ""
    PLAYER_LIST = []
    FORMAT = ""
    CARD = ""
    AVAIL_LIST = []
    PACK_NUM = 0
    PICK_NUM = 0
    PICK_OVR = 0
    FORMAT = file.split("-")[-1].split(".")[0]
    EVENT_ID = file.split('-')[-2]

    player_bool = False
    card_bool = False
    last_pack_size = 0
    init = initial.split("\n")

    for i in init:
        if i.find("Event #: ") != -1:
            EVENT_NUM = i.split()[-1]
        elif i.find("Time:    ") != -1:
            year = i.split("/")[2].split()[0]
            month = i.split("/")[0].split()[-1]
            day = i.split("/")[1]
            hour = i.split()[2].split(":")[0]
            minute = i.split()[2].split(":")[1]
            if (i.split()[-1] == "AM") & (hour == "12"):
                hour = "00"
            if (i.split()[-1] == "PM") & (hour != "12"):
                hour = str(int(hour) + 12)
            if len(month) == 1:
                month = "0" + month
            if len(day) == 1:
                day = "0" + day
            if len(hour) == 1:
                hour = "0" + hour
            DATE = f"{year}-{month}-{day}-{hour}:{minute}"
        elif i == "Players:":
            player_bool = True
        elif i == "":
            if player_bool:
                player_bool = False
            if card_bool:
                card_bool = False
                if len(AVAIL_LIST) > last_pack_size:
                    PACK_NUM += 1
                    PICK_NUM = 1
                last_pack_size = len(AVAIL_LIST)
                while len(AVAIL_LIST) < 14:
                    AVAIL_LIST.append("NA")
                PICKS_TABLE.append([DRAFT_ID,CARD,PACK_NUM,PICK_NUM,PICK_OVR] + AVAIL_LIST)
                AVAIL_LIST = []
        elif (i.find("Pack ") != -1) & (i.find(" pick ") != -1) & (len(i.split()) == 4):
            card_bool = True
        elif player_bool:
            if (i.find("--> ") != -1):
                HERO = i[4:]
                DRAFT_ID = f"{year}{month}{day}{hour}{minute}_{HERO}_{FORMAT}_{EVENT_ID}"
            else:
                PLAYER_LIST.append(i.strip())
        elif card_bool:
            if i.find("--> ") != -1:
                CARD = i.split("--> ")[1]
                PICK_NUM += 1
                PICK_OVR += 1
            else:
                AVAIL_LIST.append(i.strip())
    while len(PLAYER_LIST) < 7:
        PLAYER_LIST.append("NA")
    DRAFTS_TABLE.append([DRAFT_ID,HERO] + PLAYER_LIST + [0,0,FORMAT,DATE])

    return (DRAFTS_TABLE,PICKS_TABLE,DRAFT_ID)
def check_timeout(ga):
    for i in ga:
        if i.find(" has lost the game due to disconnection") != -1:
            return (True,i.split(" has lost the game due to disconnection")[0])
    return (False,None)
def game_actions(init,time):
    # Input:  String,String
    # Output: List[Strings]

    def format_time(time):
        month_dict = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05",\
                     "Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10",\
                     "Nov":"11","Dec":"12"}
        time = time.split()
        hhmmss = time[3].split(":")
        time[1] = month_dict[time[1]]
        if len(time[2]) < 2:
            time[2] = "0" + time[2]
        return time[4] + time[1] + time[2] + hhmmss[0] + hhmmss[1]

    initial =       init
    gameactions =   []
    p =             players(init)
    count =         0
    lost_conn =     False

    for i in p:
        initial = initial.replace(i,alter(i,original=False))
    initial = initial.split("@P")

    try:
        gameactions.append(format_time(time))
    except:
        # Time formatted by MTGO-DB Flask App.
        gameactions.append(time)
    for i in initial:
        fullstring = i.replace(" (Alt.)", "")
        fullstring = fullstring.split(".")[0]
        # Player joined game header.
        if count == 0:
            count += 1
        elif i.find("This is a @iMultiplayer Commander@i game.") != -1:
            return 'Multiplayer Game Found.'
        elif i.find(" has lost connection to the game") != -1:
            lost_conn = True
        elif i.find(" joined the game.") != -1:
            if lost_conn:
                lost_conn = False
            else:
                gameactions.append(fullstring)
        # Skip looking at extra cards.
        elif i.find(" draws their next card.") != -1:
            continue
        # Skip leaving to sideboard.
        elif i.find(" has left the game.") != -1:
            continue
        # New turn header.
        elif i.find("Turn ") != -1 and i.find(": ") != -1:
            newstring = i.split()[0] + " " + i.split()[1]
            for j in p:
                if len(newstring.split()) < 3:
                    if i.split(": ")[1].find(alter(j,original=False)) != -1:
                        newstring += " " + alter(j,original=False)
            gameactions.append(newstring)
        # Skip game state changes.
        elif (i.count(".") == 0) and (i.count("is being attacked") == 0):
            #print(i)
            continue
        # Remove tags from cards and rules text
        elif (fullstring.count("@[") > 0) and (fullstring.count("@]") > 0):
            newstring = ""
            while (fullstring.count("@[") > 0) and (fullstring.count("@]") > 0):
                tlist = fullstring.split("@",1)
                newstring += tlist[0]
                fullstring = tlist[1]
                tlist = fullstring.split("@",1)
                newstring += "@" + tlist[0] + "@]"
                fullstring = tlist[1]
                tlist = fullstring.split("@]",1)
                fullstring = tlist[1]        
            newstring += tlist[1]
            newstring = newstring.split("(")[0]
            gameactions.append(newstring)
        # Everything else
        elif i.find(".") != -1:
            gameactions.append(fullstring)
    return gameactions
def match_data(ga,gd,pd,fname):
    # Input:  List[GameActions],List[GameData],List[PlayData]
    # Output: List[Match_Attributes]

    def high_roll(init):
        remove_trailing = False
        if isinstance(init, str):
            init = init.split("@P")
            remove_trailing = True
        rolls = {}
        for i in init:
            if remove_trailing:
                tstring = i.rsplit(".",1)[0]
            else:
                tstring = i
            if i.find(" rolled a ") != -1:
                tlist = tstring.split(" rolled a ")
                if len(tlist[1]) == 1:
                    rolls[tlist[0].replace(" ","+")] = int(tlist[1])
        return rolls

    MATCH_DATA =    []
    P1 =            players(ga)[0]
    P1_ARCH =       "NA"
    P1_SUBARCH =    "NA"
    P2 =            players(ga)[1]
    P2_ARCH =       "NA"
    P2_SUBARCH =    "NA"
    try:
        P1_ROLL =       high_roll(ga)[P1]
        P2_ROLL =       high_roll(ga)[P2]
    except KeyError:
        return "High Rolls not Found."
    P1_WINS =       0
    P2_WINS =       0
    MATCH_WINNER =  ""
    MATCH_FORMAT =  "NA"
    LIM_FORMAT =    "NA"
    MATCH_TYPE =    "NA"
    DATE =          f"{ga[0][0:4]}-{ga[0][4:6]}-{ga[0][6:8]}-{ga[0][8:10]}:{ga[0][10:]}"
    # MATCH_ID =      f"{ga[0]}_{P1}_{P2}"
    MATCH_ID =      fname
    DRAFT_ID =      "NA"

    if P1_ROLL > P2_ROLL:
        ROLL_WINNER = "P1"
    else:
        ROLL_WINNER = "P2"
    
    for i in gd:
        if i[0] == MATCH_ID and i[header("Games").index("Game_Winner")] == "P1":
            P1_WINS += 1
        elif i[0] == MATCH_ID and i[header("Games").index("Game_Winner")] == "P2":
            P2_WINS += 1
       
    if P1_WINS > P2_WINS:
        MATCH_WINNER = "P1"
    elif P2_WINS > P1_WINS:
        MATCH_WINNER = "P2"
    else:
        timeout = check_timeout(ga)
        if timeout[0] == True:
            if timeout[1] == P1:
                MATCH_WINNER = "P2"
            else:
                MATCH_WINNER = "P1"
        else:
            MATCH_WINNER = "NA"

    MATCH_DATA.extend((MATCH_ID,
                       DRAFT_ID,
                       alter(P1,original=True),
                       P1_ARCH,
                       P1_SUBARCH,
                       alter(P2,original=True),
                       P2_ARCH,
                       P2_SUBARCH,
                       P1_ROLL,
                       P2_ROLL,
                       ROLL_WINNER,
                       P1_WINS,
                       P2_WINS,
                       MATCH_WINNER,
                       MATCH_FORMAT,
                       LIM_FORMAT,
                       MATCH_TYPE,
                       DATE))
    if len(MATCH_DATA) != len(header("Matches")):
        return "Match Header is Wrong Size."
    return MATCH_DATA
def game_data(ga,fname):
    # Input:  List[GameActions]
    # Output: List[G1_List,G2_List,G3_List,NA_Games_Dict{}]

    def mulls(cards):
        mull_dict = {"seven":0,"six":1,"five":2,"four":3,"three":4,"two":5,"one":6,"zero":7}
        try:
            return mull_dict[cards]
        except KeyError:
            return "NA"
    
    def get_winner(curr_game_list,p1,p2):
        # Look for a concession string.
        # Add more lose conditions here.
        for index,i in enumerate(curr_game_list):
            if i.find("has conceded") != -1:
                if i.split()[0] == p1:
                    return "P2"
                elif i.split()[0] == p2:
                    return "P1"
            elif i.find("has lost the game") != -1:
                if i.split()[0] == p1:
                    return "P2"
                elif i.split()[0] == p2:
                    return "P1"
            elif i.find("loses because of drawing a card") != -1:
                if i.split()[0] == p1:
                    return "P2"
                elif i.split()[0] == p2:
                    return "P1"
            elif i.find("wins the game") != -1:
                if i.split()[0] == p1:
                    return "P1"
                elif i.split()[0] == p2:
                    return "P2"

        lastline = curr_game_list[-1]
        # Check last GameAction. Add more lose conditions here.
        if lastline.find("is being attacked") != -1:
            if lastline.split()[0] == p1:
                return "P2"
            elif lastline.split()[0] == p2:
                return "P1"
        # Add more win conditions here.
        if lastline.find("triggered ability from [Thassa's Oracle]") != -1:
            if lastline.split()[0] == p1:
                return "P1"
            elif lastline.split()[0] == p2:
                return "P2"
        # Could not determine a winner.
        return "NA" 

    GAME_DATA =     []
    G1 =            []
    G2 =            []
    G3 =            []    
    ALL_GAMES_GA =  {}

    GAME_NUM =      0
    PD_SELECTOR =   ""
    PD_CHOICE =     ""
    ON_PLAY =       ""
    ON_DRAW =       ""
    P1_MULLS =      0
    P2_MULLS =      0
    TURNS =         0
    GAME_WINNER =   ""

    try:
        P1 =            players(ga)[0]
        P2 =            players(ga)[1]
    except IndexError:
        return "Players not Found."
    curr_game_list =[]
    curr_list =     []
    # MATCH_ID = f"{ga[0]}_{P1}_{P2}"
    MATCH_ID = fname

    for i in ga:
        curr_list = i.split()
        if i.find("joined the game") != -1:
            continue
        elif (i.find("chooses to play first") != -1) or (i.find("chooses to not play first") != -1):
            if GAME_NUM != 0:
                GAME_WINNER = get_winner(curr_game_list,P1,P2)
                if GAME_WINNER == "NA":
                    ALL_GAMES_GA[f"{MATCH_ID}-{GAME_NUM}"] = curr_game_list
                if GAME_NUM == 1:
                    G1.extend((MATCH_ID,
                               alter(P1,original=True),
                               alter(P2,original=True),
                               GAME_NUM,
                               PD_SELECTOR,
                               PD_CHOICE,
                               ON_PLAY,
                               ON_DRAW,
                               P1_MULLS,
                               P2_MULLS,
                               TURNS,
                               GAME_WINNER))
                    GAME_DATA.append(G1)
                elif GAME_NUM == 2:
                    G2.extend((MATCH_ID,
                               alter(P1,original=True),
                               alter(P2,original=True),
                               GAME_NUM,
                               PD_SELECTOR,
                               PD_CHOICE,
                               ON_PLAY,
                               ON_DRAW,
                               P1_MULLS,
                               P2_MULLS,
                               TURNS,
                               GAME_WINNER))
                    GAME_DATA.append(G2)
                curr_game_list = []
            GAME_NUM += 1
            if curr_list[0] == P1:
                PD_SELECTOR = "P1"
            else:
                PD_SELECTOR = "P2"
            if curr_list[3] == "play":
                PD_CHOICE = "Play"
            else:
                PD_CHOICE = "Draw"
            if PD_SELECTOR == "P1" and PD_CHOICE == "Play":
                ON_PLAY = "P1"
                ON_DRAW = "P2"
            elif PD_SELECTOR == "P2" and PD_CHOICE == "Play":
                ON_PLAY = "P2"
                ON_DRAW = "P1"
            elif PD_SELECTOR == "P1" and PD_CHOICE == "Draw":
                ON_PLAY = "P2"
                ON_DRAW = "P1"
            elif PD_SELECTOR == "P2" and PD_CHOICE == "Draw":
                ON_PLAY = "P1"
                ON_DRAW = "P2"
        elif i.find("begins the game with") != -1 and \
             i.find("cards in hand") != -1:
            if P1 == curr_list[0]:              
                P1_MULLS = mulls(i.split(" begins the game with ")[1].split()[0])
            elif P2 == curr_list[0]:
                P2_MULLS = mulls(i.split(" begins the game with ")[1].split()[0])
        elif i.find("Turn ") != -1 and \
             len(curr_list) == 3:
            TURNS = int(curr_list[1].split(":")[0])
        curr_game_list.append(i)
    GAME_WINNER = get_winner(curr_game_list,P1,P2)
    if GAME_WINNER == "NA":
        ALL_GAMES_GA[f"{MATCH_ID}-{GAME_NUM}"] = curr_game_list
    if (GAME_NUM == 1) and (len(G1) == 0):
        G1.extend((MATCH_ID,
                   alter(P1,original=True),
                   alter(P2,original=True),
                   GAME_NUM,
                   PD_SELECTOR,
                   PD_CHOICE,
                   ON_PLAY,
                   ON_DRAW,
                   P1_MULLS,
                   P2_MULLS,
                   TURNS,
                   GAME_WINNER))
        GAME_DATA.append(G1)
    elif (GAME_NUM == 2) and (len(G2) == 0):
        G2.extend((MATCH_ID,
                   alter(P1,original=True),
                   alter(P2,original=True),
                   GAME_NUM,
                   PD_SELECTOR,
                   PD_CHOICE,
                   ON_PLAY,
                   ON_DRAW,
                   P1_MULLS,
                   P2_MULLS,
                   TURNS,
                   GAME_WINNER))
        GAME_DATA.append(G2)
    elif (GAME_NUM == 3) and (len(G3) == 0):
        G3.extend((MATCH_ID,
                   alter(P1,original=True),
                   alter(P2,original=True),
                   GAME_NUM,
                   PD_SELECTOR,
                   PD_CHOICE,
                   ON_PLAY,
                   ON_DRAW,
                   P1_MULLS,
                   P2_MULLS,
                   TURNS,
                   GAME_WINNER))
        GAME_DATA.append(G3)
    if (len(G1) != len(header("Games"))) and (len(G1) != 0):
        return "Game 1 Header is Wrong Size."
    elif (len(G2) != len(header("Games"))) and (len(G2) != 0):
        return "Game 2 Header is Wrong Size."
    elif (len(G3) != len(header("Games"))) and (len(G3) != 0):
        return "Game 3 Header is Wrong Size."
    if (len(GAME_DATA) == 0):
        return "Match has no Games"
    return (GAME_DATA,ALL_GAMES_GA)
def play_data(ga,fname):
    # Input:  List[GameActions]
    # Output: List[Plays]

    def is_play(play):
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
        num_dict = {"zero":0,"a":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7}
        if cards_drawn not in num_dict:
            return 8
        return num_dict[cards_drawn]
    
    def get_cards(play):
        cards = []
        count = play.count("@[")
        if play.count("@]") < count:
            count = play.count("@]")
        while count > 0:
            try:
                play = play.split("@[",1)
                play = play[1].split("@]",1)
                cards.append(play[0])
                play = play[1]
            except IndexError:
                pass
            count -= 1
        return cards

    PLAY_DATA = []
    ALL_PLAYS = []

    GAME_NUM = 0
    PLAY_NUM = 0
    TURN_NUM = 0
    ACTIVE_PLAYER = ""
    NON_ACTIVE_PLAYER = ""

    P1 = players(ga)[0]
    P2 = players(ga)[1]
    curr_list = []
    # MATCH_ID = f"{ga[0]}_{P1}_{P2}"
    MATCH_ID = fname

    for i in ga:
        curr_list = i.split()
        CASTING_PLAYER = ""
        ACTION = ""
        PRIMARY_CARD = "NA"
        TARGET_1 = "NA"
        TARGET_2 = "NA"
        TARGET_3 = "NA"
        OPP_TARGET = 0
        SELF_TARGET = 0
        CARDS_DRAWN = 0
        ATTACKERS = 0
        PLAY_DATA = []
        if (i.find("chooses to play first") != -1) or (i.find("chooses to not play first") != -1):
            GAME_NUM += 1
            PLAY_NUM = 0
        elif (i.find("Turn ") != -1) and (len(curr_list) == 3):
            TURN_NUM = int(curr_list[1].split(":")[0])
            ACTIVE_PLAYER = curr_list[2]
            if ACTIVE_PLAYER == P1:
                NON_ACTIVE_PLAYER = P2
            else:
                NON_ACTIVE_PLAYER = P1
        elif is_play(i):
            if curr_list[1] == "plays":
                CASTING_PLAYER = curr_list[0]
                if curr_list[2] in [P1, P2]:
                    PRIMARY_CARD = 'NA'
                else:
                    try:
                        PRIMARY_CARD = get_cards(i)[0]
                    # MODO Bug Encountered. Primary_Card = "NA"
                    except IndexError:
                        pass
                ACTION = "Land Drop"
            elif curr_list[1] == "casts":
                CASTING_PLAYER = curr_list[0]
                if curr_list[2] in [P1, P2]:
                    PRIMARY_CARD = 'NA'
                else:
                    try:
                        PRIMARY_CARD = get_cards(i)[0]
                    # MODO Bug Encountered. Primary_Card = "NA"
                    except IndexError:
                        pass
                ACTION = curr_list[1].capitalize()
                if i.find("targeting") != -1:
                    targets = get_cards(i.split("targeting")[1])
                    try:
                        TARGET_1 = targets[0]
                    except IndexError:
                        pass
                    try:
                        TARGET_2 = targets[1]
                    except IndexError:
                        pass
                    try:
                        TARGET_3 = targets[2]
                    except IndexError:
                        pass
                    if CASTING_PLAYER == P1:
                        SELF_TARGET = player_is_target(i.split("targeting")[1],P1)
                        OPP_TARGET = player_is_target(i.split("targeting")[1],P2)
                    elif CASTING_PLAYER == P2:
                        SELF_TARGET = player_is_target(i.split("targeting")[1],P2)
                        OPP_TARGET = player_is_target(i.split("targeting")[1],P1)                    
            elif curr_list[1] == "draws":
                CASTING_PLAYER = curr_list[0]
                ACTION = curr_list[1].capitalize()
                CARDS_DRAWN = cards_drawn(curr_list[2])
            elif curr_list[1] == "chooses":
                continue
            elif curr_list[1] == "discards":
                continue
            elif i.find("is being attacked by") != -1:
                CASTING_PLAYER = ACTIVE_PLAYER
                ACTION = "Attacks"
                ATTACKERS = len(get_cards(i.split("is being attacked by")[1]))
            elif i.find("puts triggered ability from") != -1:
                CASTING_PLAYER = curr_list[0]
                try:
                    PRIMARY_CARD = get_cards(i)[0]
                except IndexError:
                    PRIMARY_CARD = i.split("triggered ability from ")[1].split(" onto the stack ")[0]
                    # MODO Bug Encountered. Primary_Card = "NA"
                    if (PRIMARY_CARD == P1) or (PRIMARY_CARD == P2):
                        PRIMARY_CARD = "NA"
                ACTION = "Triggers"
                if i.find("targeting") != -1:
                    targets = get_cards(i.split("targeting")[1])
                    try:
                        TARGET_1 = targets[0]
                    except IndexError:
                        pass
                    try:
                        TARGET_2 = targets[1]
                    except IndexError:
                        pass
                    try:
                        TARGET_3 = targets[2]
                    except IndexError:
                        pass
                    if CASTING_PLAYER == P1:
                        SELF_TARGET = player_is_target(i.split("targeting")[1],P1)
                        OPP_TARGET = player_is_target(i.split("targeting")[1],P2)
                    elif CASTING_PLAYER == P2:
                        SELF_TARGET = player_is_target(i.split("targeting")[1],P2)
                        OPP_TARGET = player_is_target(i.split("targeting")[1],P1)
            elif i.find("activates an ability of") != -1:
                CASTING_PLAYER = curr_list[0]
                try:
                    PRIMARY_CARD = get_cards(i)[0]
                except IndexError:
                    PRIMARY_CARD = i.split("activates an ability of ")[1].split(" (")[0]
                    # MODO Bug Encountered. Primary_Card = "NA"
                    if (PRIMARY_CARD == P1) or (PRIMARY_CARD == P2):
                        PRIMARY_CARD = "NA"
                ACTION = "Activated Ability"
                if i.find("targeting") != -1:
                    targets = get_cards(i.split("targeting")[1])
                    try:
                        TARGET_1 = targets[0]
                    except IndexError:
                        pass
                    try:
                        TARGET_2 = targets[1]
                    except IndexError:
                        pass
                    try:
                        TARGET_3 = targets[2]
                    except IndexError:
                        pass
                    if CASTING_PLAYER == P1:
                        SELF_TARGET = player_is_target(i.split("targeting")[1],P1)
                        OPP_TARGET = player_is_target(i.split("targeting")[1],P2)
                    elif CASTING_PLAYER == P2:
                        SELF_TARGET = player_is_target(i.split("targeting")[1],P2)
                        OPP_TARGET = player_is_target(i.split("targeting")[1],P1)
            PLAY_NUM += 1
            PLAY_DATA.extend((MATCH_ID,
                              GAME_NUM,
                              PLAY_NUM,
                              TURN_NUM,
                              alter(CASTING_PLAYER,original=True),
                              ACTION,
                              PRIMARY_CARD,
                              TARGET_1,
                              TARGET_2,
                              TARGET_3,
                              OPP_TARGET,
                              SELF_TARGET,
                              CARDS_DRAWN,
                              ATTACKERS,
                              alter(ACTIVE_PLAYER,original=True),
                              alter(NON_ACTIVE_PLAYER,original=True)))
            if len(PLAY_DATA) != len(header("Plays")):
                return "Play Header is Wrong Size."
            ALL_PLAYS.append(PLAY_DATA)
    if len(ALL_PLAYS) == 0:
        return "Match has no Plays."
    return ALL_PLAYS
def get_all_data(init,mtime,fname):
    # Input:  String,String,String
    # Output: List[Matches,Games,Plays]
    
    gameactions = game_actions(init,mtime)
    if isinstance(gameactions, str):
        return gameactions
    gamedata = game_data(gameactions,fname)
    if isinstance(gamedata, str):
        return gamedata
    playdata = play_data(gameactions,fname)
    if isinstance(playdata, str):
        return playdata
    matchdata = match_data(gameactions,gamedata[0],playdata,fname)
    if isinstance(matchdata, str):
        return matchdata
    timeout = check_timeout(gameactions)

    return [matchdata,gamedata[0],playdata,gamedata[1],timeout]