import requests
import os
import time
from bs4 import BeautifulSoup
import pickle
import io
import zipfile
import shutil

count = 0
short_list = []
all_decks = []
ad = {}

# Wait time between format scrapes (seconds). Prevents throttling.
wait_time = 300


def format_deckname(name):
    # Input:  String
    # Output: String

    name_formatted = name

    if ("WUBRG" in name):
        name_formatted = name_formatted.replace("WUBRG", "5c")
    elif ("UBRG" in name) or ("WBRG" in name) or ("WURG" in name) or ("WUBG" in name) or ("WUBR" in name):
        name_formatted = name_formatted.replace("UBRG", "4c")
        name_formatted = name_formatted.replace("WBRG", "4c")
        name_formatted = name_formatted.replace("WURG", "4c")
        name_formatted = name_formatted.replace("WUBG", "4c")
        name_formatted = name_formatted.replace("WUBR", "4c")
    elif ("GUW" in name) or ("GWU" in name) or ("UGW" in name) or ("WGU" in name) or ("UWG" in name) or ("WUG" in name):
        name_formatted = name_formatted.replace("GUW", "Bant")
        name_formatted = name_formatted.replace("GWU", "Bant")
        name_formatted = name_formatted.replace("UGW", "Bant")
        name_formatted = name_formatted.replace("WGU", "Bant")
        name_formatted = name_formatted.replace("UWG", "Bant")
        name_formatted = name_formatted.replace("WUG", "Bant")
    elif ("BUW" in name) or ("BWU" in name) or ("UBW" in name) or ("WBU" in name) or ("UWB" in name) or ("WUB" in name):
        name_formatted = name_formatted.replace("BUW", "Esper")
        name_formatted = name_formatted.replace("BWU", "Esper")
        name_formatted = name_formatted.replace("UBW", "Esper")
        name_formatted = name_formatted.replace("WBU", "Esper")
        name_formatted = name_formatted.replace("UWB", "Esper")
        name_formatted = name_formatted.replace("WUB", "Esper")
    elif ("BRU" in name) or ("BUR" in name) or ("RBU" in name) or ("UBR" in name) or ("RUB" in name) or ("URB" in name):
        name_formatted = name_formatted.replace("BRU", "Grixis")
        name_formatted = name_formatted.replace("BUR", "Grixis")
        name_formatted = name_formatted.replace("RBU", "Grixis")
        name_formatted = name_formatted.replace("UBR", "Grixis")
        name_formatted = name_formatted.replace("RUB", "Grixis")
        name_formatted = name_formatted.replace("URB", "Grixis")
    elif ("BGR" in name) or ("BRG" in name) or ("GBR" in name) or ("RBG" in name) or ("GRB" in name) or ("RGB" in name):
        name_formatted = name_formatted.replace("BGR", "Jund")
        name_formatted = name_formatted.replace("BRG", "Jund")
        name_formatted = name_formatted.replace("GBR", "Jund")
        name_formatted = name_formatted.replace("RBG", "Jund")
        name_formatted = name_formatted.replace("GRB", "Jund")
        name_formatted = name_formatted.replace("RGB", "Jund")
    elif ("GRW" in name) or ("GWR" in name) or ("RGW" in name) or ("WGR" in name) or ("RWG" in name) or ("WRG" in name):
        name_formatted = name_formatted.replace("GRW", "Naya")
        name_formatted = name_formatted.replace("GWR", "Naya")
        name_formatted = name_formatted.replace("RGW", "Naya")
        name_formatted = name_formatted.replace("WGR", "Naya")
        name_formatted = name_formatted.replace("RWG", "Naya")
        name_formatted = name_formatted.replace("WRG", "Naya")
    elif ("BGW" in name) or ("BWG" in name) or ("GBW" in name) or ("WBG" in name) or ("GWB" in name) or ("WGB" in name):
        name_formatted = name_formatted.replace("BGW", "Abzan")
        name_formatted = name_formatted.replace("BWG", "Abzan")
        name_formatted = name_formatted.replace("GBW", "Abzan")
        name_formatted = name_formatted.replace("WBG", "Abzan")
        name_formatted = name_formatted.replace("GWB", "Abzan")
        name_formatted = name_formatted.replace("WGB", "Abzan")
    elif ("RUW" in name) or ("RWU" in name) or ("URW" in name) or ("WRU" in name) or ("UWR" in name) or ("WUR" in name):
        name_formatted = name_formatted.replace("RUW", "Jeskai")
        name_formatted = name_formatted.replace("RWU", "Jeskai")
        name_formatted = name_formatted.replace("URW", "Jeskai")
        name_formatted = name_formatted.replace("WRU", "Jeskai")
        name_formatted = name_formatted.replace("UWR", "Jeskai")
        name_formatted = name_formatted.replace("WUR", "Jeskai")
    elif ("BGU" in name) or ("BUG" in name) or ("GBU" in name) or ("UBG" in name) or ("GUB" in name) or (
            "UGB" in name) or ("Sultai" in name):
        name_formatted = name_formatted.replace("BGU", "BUG")
        # name_formatted = name_formatted.replace("BUG","BUG")
        name_formatted = name_formatted.replace("GBU", "BUG")
        name_formatted = name_formatted.replace("UBG", "BUG")
        name_formatted = name_formatted.replace("GUB", "BUG")
        name_formatted = name_formatted.replace("UGB", "BUG")
        name_formatted = name_formatted.replace("Sultai", "BUG")
    elif ("BRW" in name) or ("BWR" in name) or ("RBW" in name) or ("WBR" in name) or ("RWB" in name) or ("WRB" in name):
        name_formatted = name_formatted.replace("BRW", "Mardu")
        name_formatted = name_formatted.replace("BWR", "Mardu")
        name_formatted = name_formatted.replace("RBW", "Mardu")
        name_formatted = name_formatted.replace("WBR", "Mardu")
        name_formatted = name_formatted.replace("RWB", "Mardu")
        name_formatted = name_formatted.replace("WRB", "Mardu")
    elif ("GRU" in name) or ("GUR" in name) or ("RGU" in name) or ("UGR" in name) or ("RUG" in name) or (
            "URG" in name) or ("Temur" in name):
        name_formatted = name_formatted.replace("GRU", "RUG")
        name_formatted = name_formatted.replace("GUR", "RUG")
        name_formatted = name_formatted.replace("RGU", "RUG")
        name_formatted = name_formatted.replace("UGR", "RUG")
        # name_formatted = name_formatted.replace("RUG","RUG")
        name_formatted = name_formatted.replace("URG", "RUG")
        name_formatted = name_formatted.replace("Temur", "RUG")
    elif ("Azorius" in name) or ("WU" in name):
        name_formatted = name_formatted.replace("Azorius", "UW")
        name_formatted = name_formatted.replace("WU", "UW")
    elif ("RW" in name) or ("WR" in name):
        name_formatted = name_formatted.replace("RW", "Boros")
        name_formatted = name_formatted.replace("WR", "Boros")
    elif ("Dimir" in name) or ("BU" in name):
        name_formatted = name_formatted.replace("Dimir", "UB")
        name_formatted = name_formatted.replace("BU", "UB")
    elif ("Golgari" in name) or ("BG" in name):
        name_formatted = name_formatted.replace("Golgari", "GB")
        name_formatted = name_formatted.replace("BG", "GB")
    elif ("Gruul" in name) or ("GR" in name):
        name_formatted = name_formatted.replace("Gruul", "RG")
        name_formatted = name_formatted.replace("GR", "RG")
    elif ("Izzet" in name) or ("RU" in name):
        name_formatted = name_formatted.replace("Izzet", "UR")
        name_formatted = name_formatted.replace("RU", "UR")
    elif ("Orzhov" in name) or ("WB" in name):
        name_formatted = name_formatted.replace("Orzhov", "BW")
        name_formatted = name_formatted.replace("WB", "BW")
    elif ("Rakdos" in name) or ("BR" in name):
        name_formatted = name_formatted.replace("Rakdos", "RB")
        name_formatted = name_formatted.replace("BR", "RB")
    elif ("Selesnya" in name) or ("WG" in name):
        name_formatted = name_formatted.replace("Selesnya", "GW")
        name_formatted = name_formatted.replace("WG", "GW")
    elif ("Simic" in name) or ("GU" in name):
        name_formatted = name_formatted.replace("Simic", "UG")
        name_formatted = name_formatted.replace("GU", "UG")
    elif ("Mono-White" in name) or ("Mono-white" in name) or ("Mono White" in name) or ("Mono white" in name) or \
            ("MonoWhite" in name) or ("Monowhite" in name) or ("MonoW" in name) or ("Mono W" in name) or (
            "Mono-W" in name):
        name_formatted = name_formatted.replace("Mono-White", "W")
        name_formatted = name_formatted.replace("Mono-white", "W")
        name_formatted = name_formatted.replace("Mono White", "W")
        name_formatted = name_formatted.replace("Mono white", "W")
        name_formatted = name_formatted.replace("MonoWhite", "W")
        name_formatted = name_formatted.replace("Monowhite", "W")
        name_formatted = name_formatted.replace("MonoW", "W")
        name_formatted = name_formatted.replace("Mono W", "W")
        name_formatted = name_formatted.replace("Mono-W", "W")
    elif ("Mono-Blue" in name) or ("Mono-blue" in name) or ("Mono Blue" in name) or ("Mono blue" in name) or \
            ("MonoBlue" in name) or ("Monoblue" in name) or ("MonoU" in name) or ("Mono U" in name) or (
            "Mono-U" in name):
        name_formatted = name_formatted.replace("Mono-Blue", "U")
        name_formatted = name_formatted.replace("Mono-blue", "U")
        name_formatted = name_formatted.replace("Mono Blue", "U")
        name_formatted = name_formatted.replace("Mono blue", "U")
        name_formatted = name_formatted.replace("MonoBlue", "U")
        name_formatted = name_formatted.replace("Monoblue", "U")
        name_formatted = name_formatted.replace("MonoU", "U")
        name_formatted = name_formatted.replace("Mono U", "U")
        name_formatted = name_formatted.replace("Mono-U", "U")
    elif ("Mono-Black" in name) or ("Mono-black" in name) or ("Mono Black" in name) or ("Mono black" in name) or \
            ("MonoBlack" in name) or ("Monoblack" in name) or ("MonoB" in name) or ("Mono B" in name) or (
            "Mono-B" in name):
        name_formatted = name_formatted.replace("Mono-Black", "B")
        name_formatted = name_formatted.replace("Mono-black", "B")
        name_formatted = name_formatted.replace("Mono Black", "B")
        name_formatted = name_formatted.replace("Mono black", "B")
        name_formatted = name_formatted.replace("MonoBlack", "B")
        name_formatted = name_formatted.replace("Monoblack", "B")
        name_formatted = name_formatted.replace("MonoB", "B")
        name_formatted = name_formatted.replace("Mono B", "B")
        name_formatted = name_formatted.replace("Mono-B", "B")
    elif ("Mono-Red" in name) or ("Mono-red" in name) or ("Mono Red" in name) or ("Mono red" in name) \
            or ("MonoRed" in name) or ("Monored" in name) or ("MonoR" in name) or ("Mono R" in name) or (
            "Mono-R" in name):
        name_formatted = name_formatted.replace("Mono-Red", "R")
        name_formatted = name_formatted.replace("Mono-red", "R")
        name_formatted = name_formatted.replace("Mono Red", "R")
        name_formatted = name_formatted.replace("Mono red", "R")
        name_formatted = name_formatted.replace("MonoRed", "R")
        name_formatted = name_formatted.replace("Monored", "R")
        name_formatted = name_formatted.replace("MonoR", "R")
        name_formatted = name_formatted.replace("Mono R", "R")
        name_formatted = name_formatted.replace("Mono-R", "R")
    elif ("Mono-Green" in name) or ("Mono-green" in name) or ("Mono Green" in name) or ("Mono green" in name) \
            or ("MonoGreen" in name) or ("Monogreen" in name) or ("MonoG" in name) or ("Mono G" in name) or (
            "Mono-G" in name):
        name_formatted = name_formatted.replace("Mono-Green", "G")
        name_formatted = name_formatted.replace("Mono-green", "G")
        name_formatted = name_formatted.replace("Mono Green", "G")
        name_formatted = name_formatted.replace("Mono green", "G")
        name_formatted = name_formatted.replace("MonoGreen", "G")
        name_formatted = name_formatted.replace("Monogreen", "G")
        name_formatted = name_formatted.replace("MonoG", "G")
        name_formatted = name_formatted.replace("Mono G", "G")
        name_formatted = name_formatted.replace("Mono-G", "G")

    return name_formatted


def get_dates(yyyy_mm):
    date1 = yyyy_mm[0:4] + "-" + yyyy_mm[5:7] + "-" + "01"
    date2 = yyyy_mm[0:4] + "-" + yyyy_mm[5:7] + "-"
    if yyyy_mm[5:7] == "01":
        return [date1, date2 + "31"]
    if yyyy_mm[5:7] == "02":
        return [date1, date2 + "28"]
    if yyyy_mm[5:7] == "03":
        return [date1, date2 + "31"]
    if yyyy_mm[5:7] == "04":
        return [date1, date2 + "30"]
    if yyyy_mm[5:7] == "05":
        return [date1, date2 + "31"]
    if yyyy_mm[5:7] == "06":
        return [date1, date2 + "30"]
    if yyyy_mm[5:7] == "07":
        return [date1, date2 + "31"]
    if yyyy_mm[5:7] == "08":
        return [date1, date2 + "31"]
    if yyyy_mm[5:7] == "09":
        return [date1, date2 + "30"]
    if yyyy_mm[5:7] == "10":
        return [date1, date2 + "31"]
    if yyyy_mm[5:7] == "11":
        return [date1, date2 + "30"]
    if yyyy_mm[5:7] == "12":
        return [date1, date2 + "31"]


def get_search_url(format, yyyy_mm):
    # Date: YYYY-MM-DD

    date1 = get_dates(yyyy_mm)[0]
    date2 = get_dates(yyyy_mm)[1]

    url = "https://www.mtggoldfish.com/tournament_searches/create?utf8=%E2%9C%93&tournament_search%5Bname%5D=&tournament_search%5Bformat%5D="
    url += format.lower()
    url += "&tournament_search%5Bdate_range%5D="
    url += date1[5:7] + "%2F" + date1[8:10] + "%2F" + date1[0:4] + "+-+"
    url += date2[5:7] + "%2F" + date2[8:10] + "%2F" + date2[0:4] + "&commit=Search"
    return url


def get_tournaments(search_url):
    page = requests.get(search_url)

    # Get entire site in HTML
    soup = BeautifulSoup(page.content, "html.parser")

    # Find tournament search result table
    table = soup.find("table", class_="table table-striped")

    # Return empty list if no tournaments found.
    t_list = []
    if table == None:
        return t_list

    # Each row in the table is a tournament
    tourneys = table.find_all("tr")

    for i in tourneys:
        # Each element represents information about the tournament
        # [Date, Name, Format]
        elements = i.find_all("td")

        if len(elements) < 1:
            continue

        # Links represents all links found in this row (there is only one link)
        # Link => URL of tournament page
        links = i.find_all("a")
        link = "http://www.mtggoldfish.com"
        for j in links:
            link += j["href"]

        # Attributes represents descriptive details about the tournament
        # List of strings
        # [Date, Name, Format]
        attributes = []
        for j in elements:
            attributes.append(j.text.strip())

        attributes.append(link)
        t_list.append(attributes)
    return t_list


def get_decks(tourney):
    t_format = tourney[2]
    tourney_url = tourney[3]
    page = requests.get(tourney_url)

    # Get entire site in HTML
    soup = BeautifulSoup(page.content, "html.parser")

    decks = soup.find_all("tr", class_="tournament-decklist-event") + soup.find_all("tr",
                                                                                    class_="tournament-decklist-odd")

    link = "http://www.mtggoldfish.com/deck/download/"
    d_list = []
    for i in decks:
        elements = i.find_all("td")
        links = i.find_all("a")
        name = elements[1].text.replace(" \u2744", " Snow")
        name = name.replace("\u2744", " Snow")
        name = name.replace("/", "")
        if ("(" in name) and (")" in name):
            name = name.split("(")[0] + name.split(")")[1]
        name = name.strip()

        attributes = []
        attributes.append(name)
        attributes.append(t_format)
        attributes.append(link + links[0]["href"].split("/deck/")[1])
        attributes.append(1)

        d_list.append(attributes)

    return d_list


def get_decklist(deck):
    name = deck[0]
    d_format = deck[1]
    deck_url = deck[2]

    page = requests.get(deck_url)

    deck_list = page.text
    deck_list = deck_list.replace("\r", "")

    return [name, d_format, deck_list]


def save_decklist(decklist, yyyy_mm):
    global count
    global short_list

    fp = os.getcwd()
    name = decklist[0]
    dl_format = decklist[1]
    dl_string = decklist[2]

    if os.path.isdir("lists") == False:
        os.mkdir(fp + "\\" + "lists")
    os.chdir(fp + "\\" + "lists")
    if os.path.isdir(yyyy_mm) == False:
        os.mkdir(os.getcwd() + "\\" + yyyy_mm)
    os.chdir(os.getcwd() + "\\" + yyyy_mm)

    file_name = dl_format + " - " + name + ".txt"

    with open(file_name, "w", encoding="utf-8") as txt:
        txt.write(dl_string)
    os.chdir(fp)

    if len(dl_string) < 150:
        short_list.append(dl_format + " - " + name)
        count += 1


def save_receipt(yyyy_mm):
    fp = os.getcwd()
    os.chdir(fp + "\\" + "lists")
    print("number of short lists: " + str(len(short_list)))
    print("number of total lists: " + str(len(all_decks)))
    file_name = yyyy_mm + ".txt"
    with open(file_name, "w", encoding="utf-8") as txt:
        txt.write("number of short lists: " + str(len(short_list)))
        txt.write("\n")
        txt.write("number of total lists: " + str(len(all_decks)))
        txt.write("\n")
        txt.write("------------")
        txt.write("\n")
        for i in short_list:
            txt.write(i)
            txt.write("\n")
        txt.write("------------")
        txt.write("\n")
        for i in all_decks:
            # print(i)
            txt.write("['" + i[0] + "', '" + i[1] + "', '" + i[2] + "', " + str(i[3]) + "]")
            txt.write("\n")
        txt.write("------------")
    os.chdir(fp)


def save_all_lists(d_format, yyyy_mm):
    global all_decks
    global short_list
    short_list = []

    url = get_search_url(d_format, yyyy_mm)

    # Tourneys represents list of Tournament objects
    # [Date, Name, Format, URL]
    tourneys = get_tournaments(url)

    # Decks represents list of Deck objects
    # [Name, Format, URL, Count]
    # Get all deck objects from our list of Tournaments
    decks = []
    decks_filtered = []
    deck_set = set()
    for tourney in tourneys:
        new_decks = get_decks(tourney)
        for i in new_decks:
            if (i[0] in deck_set):
                for j in decks:
                    if j[0] == i[0]:
                        j[3] += 1
                        break
            else:
                deck_set.add(i[0])
                decks.append(i)

    for i in decks:
        if i[3] > 1:
            decks_filtered.append(i)

    # Decklists represents list of Decklist objects
    # [Name, Format, DecklistString]
    # Get all Decklist objects from our list of Decks
    decklists = []
    for i in decks_filtered:
        decklists.append(get_decklist(i))

    # For each Decklist object found, save the Decklist as a .txt file
    for i in decklists:
        save_decklist(i, yyyy_mm)

    all_decks += decks_filtered
    print(d_format + " done. " + str(len(decks_filtered)) + " decklists saved.")


def save_multiple_months(q, months, formats):
    global all_decks
    for yyyy_mm in months:
        all_decks = []
        print("starting month: " + yyyy_mm)
        for fmt in formats:
            save_all_lists(fmt, yyyy_mm)
            q.get()
            if (yyyy_mm == months[-1]) and (fmt == formats[-1]):
                pass
            else:
                time.sleep(wait_time)
        print(yyyy_mm + " done.")
        # save_receipt(yyyy_mm)


def parse_list(filename, init):
    # Input:  String,String
    # Output: [String,String,Set{MaindeckCards}]

    initial = init.split("\n")
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
                card_count = int(i.split(" ", 1)[0])
            except ValueError:
                return None
            card = i.split(" ", 1)[1]
            while card_count > 0 and sb == False:
                maindeck.append(card)
                card_count -= 1
            while card_count > 0 and sb == True:
                sideboard.append(card)
                card_count -= 1

    # Customize Deck Naming Conventions
    d_format = filename.split(".txt")[0].split(" - ")[0]
    name = filename.split(".txt")[0].split(" - ")[1]

    old = name
    name = format_deckname(name)
    # if ("Mono" in old) or ("mono" in old):
    #     print(name)

    return [name, d_format, set(maindeck)]


def get_lists():
    global ad
    errors = []

    root = os.getcwd()
    zf = zipfile.ZipFile('Lists.zip', mode='w')
    os.chdir(os.getcwd() + "\\" + "lists")
    fp = os.getcwd()
    folders = os.listdir()
    for i in folders:
        if i == 'Lists.zip':
            continue
        print("Parsing Month: " + i)
        last = i
        # zf.write(fp + "\\" + i, arcname=i)
        os.chdir(fp + "\\" + i)
        files = os.listdir()
        month_decks = []
        for j in files:
            zf.write(j, (i + '\\' + j))
            with io.open(j, "r", encoding="ansi") as decklist:
                initial = decklist.read()
            deck = parse_list(j, initial)
            if deck == None:
                errors.append((i, j))
            month_decks.append(deck)
        ad[i] = month_decks

    zf.close()
    label = f"Imported Sample Decklists. {str(len(errors))} error(s) found"
    if len(errors) == 0:
        label += "."
    else:
        label += ": "
        for index, i in enumerate(errors):
            if index > 0:
                label += ", "
            label += i[0] + "/" + i[1]
    print(label)

    os.chdir(root)
    pickle.dump(ad, open(f'ALL_DECKS_{last}', "wb"))


def scrape_lists(q, months, formats):
    save_multiple_months(q, months, formats)
    get_lists()
    while not q.empty():
        q.get()
