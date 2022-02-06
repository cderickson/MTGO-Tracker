# MTGO-Tracker
MTGO-Tracker will break down your play history on Magic Online into a personal database. It will help you format your data for further statistical analysis, or allow you to simply use the built-in descriptive statistics.

Five (5) tables are created: **Matches, Games, Plays, Drafts, Draft Picks**. These tables will help you not only track and analyze your results, but your play patterns as well.

<p align="center">
<img src="https://github.com/cderickson/MTGO-Tracker/blob/main/readme_image.jpg?raw=true" width="808" height="448">
</p>

## Getting Started
Import your data by clicking **'File => Import MTGO GameLogs'** and navigating to the folder containing your GameLog and/or DraftLog files. MTGO saves these files in **"C:\Users\\[User]\AppData\Local\Apps\2.0"** and **"C:\Users\\[User]\Documents"** respectively.

Set the default Hero to your MTGO username by clicking **'Data => Set Default Hero'**. This will make an individualized dataset more readable. The statistics window will also become accessible from the left-panel, allowing you to view general statistics regarding your personal performance.

Complete your dataset by using the **Data Cleaning** methods described below to fill in information for attributes such as Deck Archetype, Deck Name, Match Format, and more.

Continue importing data as you play more matches on MTGO!
## Column Descriptions
<details>
<summary><b>Matches Table</b></summary>
<p></p>
<p>

| Table | Column_Name | Description |
| ------------- | ------------- | ------------- |
| Matches | Match_ID | Unique Match_ID |
| | P1 | Player 1 Username |
| | P1_Arch | Player 1 Deck Archetype (eg. Aggro/Control/etc.) |
| | P1_Subarch | Player 1 Deckname |
| | P2 | Player 2 Username |
| | P2_Arch | Player 2 Deck Archetype (eg. Aggro/Control/etc.) |
| | P2_Subarch | Player 2 Deckname |
| | P1_Roll | Integer: Player 1 Die Roll |
| | P2_Roll | Integer: Player 2 Die Roll |
| | Roll_Winner | Die Roll Winner |
| | P1_Wins | Integer: Player 1 Game Wins |
| | P2_Wins | Integer: Player 2 Game Wins |
| | Match_Winner | Match Winner |
| | Format | Match Format Played |
| | Limited_Format | Limited Format Played ('NA' if Constructed Match) |
| | Match_Type | MTGO Match Type (eg. League/Challenge) |
| | Date | Date/Time at Start of Match: YYYY-MM-DD-HH-MM |
</p>
</details>
<details>
<summary><b>Games Table</b></summary>
<p></p>
<p>

| Table | Column_Name | Description |
| ------------- | ------------- | ------------- |
| Games | Match_ID | Unique Match_ID |
| | P1 | Player 1 Username |
| | P2 | Player 2 Username |
| | Game_Num | Integer: 1, 2, 3 |
| | PD_Selector | Player with Choice of Play/Draw |
| | PD_Choice | Play/Draw Selection |
| | On_Play | On-The-Play Player |
| | On_Draw | On-The-Draw Player |
| | P1_Mulls | Integer: Mulligans by Player 1 |
| | P2_Mulls | Integer: Mulligans by Player 2 |
| | Turns | Integer: Total Turns in Game |
| | Game_Winner | Game Winner |
</p>
</details>
<details>
<summary><b>Plays Table</b></summary>
<p></p>
<p>

| Table | Column_Name | Description |
| ------------- | ------------- | ------------- |
| Plays | Match_ID | Unique Match_ID |
| | Game_Num | Integer: 1, 2, 3 |
| | Play_Num | Integer: Play Number |
| | Turn_Num | Integer: Turn Number |
| | Casting_Player | Player Committing Game Action |
| | Action | Game Action: 'Land Drop', 'Casts', 'Triggers', 'Activated Ability', 'Draws', 'Attacks' |
| | Primary_Card | Card Being Cast/Played/Triggered/etc. |
| | Target1 | Target Card #1 of Primary Card ('NA' if No Targeted Cards)|
| | Target2 | Target Card #2 of Primary Card ('NA' if <2 Targeted Cards) |
| | Target3 | Target Card #3 of Primary Card ('NA' if <3 Targeted Cards) |
| | Opp_Target | Bool (1 or 0): '1' if Current Play is Targetting Opponent |
| | Self_Target | Bool (1 or 0): '1' if Current Play is Self-Targetting |
| | Cards_Drawn | Integer: Total Cards Drawn (Current Action) |
| | Attackers | Integer: Total Attackers (Current Action) |
| | Active_Player | Active Player |
| | Nonactive_Player | Nonactive Player |
</p>
</details>
<details>
<summary><b>Drafts Table</b></summary>
<p></p>
<p>

| Table | Column_Name | Description |
| ------------- | ------------- | ------------- |
| Drafts | Draft_ID | Unique Draft_ID |
| | Hero | Drafting Player Username |
| | Player_1-8 | Username |
| | Match_Wins | Integer: Hero Match Wins |
| | Match_Losses | Integer: Hero Match Losses |
| | Format | Draft Format Played |
| | Date | Date/Time at Start of Match: YYYY-MM-DD-HH-MM |
</p>
</details>
<details>
<summary><b>Draft Picks Table</b></summary>
<p></p>
<p>

| Table | Column_Name | Description |
| ------------- | ------------- | ------------- |
| Draft Picks | Draft_ID | Unique Draft_ID |
| | Card | Selected/Drafted Card |
| | Pack_Num | Integer: Pack of the Current Draft |
| | Pick_Num | Integer: Pick of the Current Pack |
| | Pick_Ovr | Integer: Overall Pick of the Draft |
| | Avail_1-14 | Other Available Cards During Pick |
</p>
</details>

- - - -
## Data Cleaning
<details>
<summary><b>Data Cleaning Methods</b></summary>

### Missing Match Data:
**Data => Input Missing Match Data**
	
	- Matches import with empty P1/P2_Arch, P1/P2_Subarch, (Limited)_Format, Match_Type columns by default.
	- Cycle through Matches with empty columns and manually fill them in.	
### Missing Game_Winner:
**Data => Input Missing Game_Winner Data**

	- The 'Games.Game_Winner' column will be set to 'NA' if the game's winner could not be determined.
	- Cycle through affected Games and manually select a Game_Winner based on trailing Game Actions. 
	- All tables will be automatically updated accordingly.
### Best Guess Deck Names:
**Data => Apply Best Guess for Deck Names**
	
	- The 'Matches.P1/P2_Subarch' columns will be set to 'NA' by default after importing.
	- Import sample decklists and apply best guess deck names in the 'Matches.P1/P2_Subarch' columns.
	- Sample decklists from YYYY-MM to YYYY-MM are included and will be updated at the end of every month.

	- Clicking 'Apply to All' will overwrite any existing P1/P2_Subarch values.
	- Click 'Apply to Unknowns' if you do not wish to overwrite your previous changes to these columns.
	- Matches with Format set to Draft/Sealed/Cube will have deck name set to colors played (eg. WU/RG/etc.)
### Revise Record(s) Button:
	- Selected row(s) in the 'Matches' table can be manually revised.
	- If multiple rows are selected, the revision will apply to all selected rows.
	- This is only applicable to rows in the 'Matches' table.
### Remove Record(s) Button:
	- Selected row(s) in the 'Matches' table can be removed from your database.
	- All associated Games and Plays data will also be removed.
	- Removed Matches can be ignored, meaning they will not be included in future imports.
	- This is only applicable to rows in the 'Matches' table.
### Input Options File
	- Control the dropdown menu options available when making revisions.
	- Add or delete options under their respective header.
	- Each option MUST be on it's own line.
	- Do not alter the pre-existing headers in this file.
</details>

- - - -
## Data Viewing
<details>
<summary><b>Data Viewing Methods</b></summary>
	
### Filtering: 
	- Manipulate the data being displayed by applying filters accessible using the Filter button.
### Drill Down:
	- Double-clicking on a Match row will display all Games for the selected Match. 
	- Double-clicking on a Game row will display all Plays for the selected Game.
	- Double-clicking on a Draft row will display all Draft Picks for the selected Draft.
	- Click the 'Clear Filter' button to display all data after drilling down.
</details>

- - - -
## Statistics Window
	- 'Hero' setting must be applied before Statistics Window can be viewed.
	
	- View descriptive statistics and basic analysis. 
	- Choose to view Match, Game, Play, Opponent, Time, or Card Data using the top right dropdown menu.
	- Statistics can be filtered using the Format, Deck, and Date Range menus across the top of the window.
<p align="center">
<img src="https://github.com/cderickson/MTGO-Tracker/blob/main/readme_image2.jpg?raw=true" width="808" height="469">
</p>

- - - -
## Settings
<details>
	<summary><b>GameLogs and DraftLogs Folder</b></summary>
	<p></p>
	<p><b>Data => Set Default Import Folders</b></p>
	
	- The folders containing your MTGO GameLog and DraftLog files.
	- MTGO saves GameLog files in "C:\Users\[User]\AppData\Local\Apps\2.0" by default.
	- MTGO saves DraftLog files in "C:\Users\[User]\Documents" by default.
</details>
<details>
	<summary><b>Export Folder</b></summary>
	<p></p>
	<p><b>Export => Set Default Export Folder</b></p>
	
	- The folder where exported .csv and .xlsx files will be saved.
</details>
<details>
	<summary><b>Main Window Size</b></summary>
	<p></p>
	<p><b>File => Set Default Window Size</b></p>
	
	- Small: 1000x500
	- Large: 1750x750
</details>
<details>
	<summary><b>Hero</b></summary>
	<p></p>
	<p><b>Data => Set Default Hero</b></p>
	
	- Setting a default 'Hero' moves the Hero's username into the P1 column by default. 
	- Data in the 'Statistics' window will be shown from the Hero's perspective.
</details>

- - - -
## Saving and Exporting
### Session Data:
- **File => Save Data**
- **Data => Delete Saved Session**
### Previously Imported Files:

	- Previously imported GameLog and DraftLog files are copied and saved.
	- Copied GameLog files are saved in /root/gamelogs/.
	- Copied DraftLog files are saved in /root/draftlogs/.
### Exporting:

	- MTGO-Tracker creates (5) tables: 'Matches', 'Games', 'Plays', 'Drafts', 'Draft Picks'.
	- Use the 'Export' Menu to save any or all of your tables as either .csv or .xlsx files.
	- Filtered tables can be exported.
### Inverse Joined Table Export:

	- MTGO randomly sets each player to P1 or P2 at the beginning of each match. 
	- This makes it difficult to view data for specific players.
	
	- The Inverse Join table creates a second row for each Match/Game with P1 and P2 reversed.
	- This allows filtering on either the P1 or P2 columns to display all games involving a specific player.
	- Keep in mind the tables exported with this option will be twice as large.
- - - -
