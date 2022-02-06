def header(table):
	if table == "Drafts":
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
			if len(i.split()) > 1:
				HERO = i.split("--> ")[1]
				DRAFT_ID = f"{year}{month}{day}{hour}{minute}_{HERO}_{FORMAT}_{EVENT_NUM}"
			else:
				PLAYER_LIST.append(i.split()[0])
		elif card_bool:
			if i.find("--> ") != -1:
				CARD = i.split("--> ")[1]
				PICK_NUM += 1
				PICK_OVR += 1
			else:
				AVAIL_LIST.append(i.split("    ")[1])
	while len(PLAYER_LIST) < 7:
		PLAYER_LIST.append("NA")
	DRAFTS_TABLE.append([DRAFT_ID,HERO] + PLAYER_LIST + [0,0,FORMAT,DATE])

	return (DRAFTS_TABLE,PICKS_TABLE,DRAFT_ID)

def test():
	parsed_data = ()

	os.chdir(os.getcwd() + "\\" + "draftlogs")
	for (root,dirs,files) in os.walk(os.getcwd()):
		break
	for i in files:
		print(i)
		os.chdir(root)
		with io.open(i,"r",encoding="ansi") as gamelog:
			initial = gamelog.read()
		parsed_data = parse_draft_log(i,initial)