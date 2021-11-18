# MTGO-Tracker
MTGO-Tracker will break down your play history on Magic Online into a personal database. It will help you format your data for further statistical analysis, or allow you to simply use the built-in descriptive statistics.

## Importing Data
Data can be imported by clicking <b>'File => Load MTGO GameLogs'</b>. Select the folder containing your GameLog files (if it has not already been set, or you wish to import from a different folder).

MTGO saves these files in <b>"C:\Users\\[User]\AppData\Local\Apps\2.0"</b> by default.
## Column Descriptions
<details>
<summary><b>Match Table</b></summary>
<p></p>
<p>

| Table | Column_Name | Description |
| ------------- | ------------- | ------------- |
| Matches | Match_ID | Unique Match ID |
| | P1 | Player 1 Username |
| | P1_Arch | Player 1 Deck Archetype (eg. Aggro/Control) |
| | P1_Subarch | Player 1 Deckname |
| | P2 | Player 2 Username |
| | P2_Arch | Player 2 Deck Archetype (eg. Aggro/Control) |
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
<summary><b>Game Table</b></summary>
<p></p>
<p>

| Table | Column_Name | Description |
| ------------- | ------------- | ------------- |
| Games | Match_ID | Unique Match ID |
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
<summary><b>Play Table</b></summary>
<p></p>
<p>

| Table | Column_Name | Description |
| ------------- | ------------- | ------------- |
| Plays | Match_ID | Unique Match ID |
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
| | Cards_Drawn | Integer: Total Cards Drawn (Current Play Only) |
| | Attackers | Integer: Total Attackers (Current Play Only) |
| | Active_Player | Active Player |
| | Nonactive_Player | Nonactive Player |
</p>
</details>

## Data Cleaning
<details>
	<summary><b>Missing Match Data:</b> Matches will import with some empty columns by default.</summary>
	<p></p>
	<p>Selecting <b>'Data => Input Missing Match Data'</b> will cycle through each Match with an empty P1/P2_Arch, P1/P2_Subarch, (Limited)_Format, and/or Match_Type column and allow you to manually fill them in. All tables will be updated accordingly.</p>
</details>
	
- - - -
<details>
	<summary><b>Missing Game_Winner:</b> The 'Games.Game_Winner' column will be set to 'NA' if the game's winner could not be determined.</summary>
	<p></p>
	<p>Selecting <b>'Data => Input Missing Game_Winner Data'</b> will allow you to cycle through each affected Game and manually select a Game_Winner based on the trailing Game Actions. All tables will be updated accordingly.</p>
</details>
	
- - - -
<details>
	<summary><b>Best Guess Deck Names:</b> The 'Matches.P1/P2_Subarch' column will be set to 'NA' by default.</summary>
	<p></p>
	<p>Selecting <b>'Data => Apply Best Guess for Deck Names'</b> will allow you to import sample decklists and apply best guess deck names in the 'Matches.P1/P2_Subarch' columns. Click 'Apply to Unknowns' if you do not wish to overwrite your previous changes to these columns.</p>
</details>
	
- - - -
<details>
	<summary><b>Revise Record(s):</b> Selected records in the 'Matches' table can be revised.</summary>
	<p></p>
	<p>Clicking the <b>'Revise Record(s)'</b> button will allow you to manually revise fields in the selected row(s). If multiple rows are selected, the revision will apply to all selected records. This is only applicable to records in the 'Matches' table.</p>
</details>
	
- - - -
## Data Viewing
<b>Filtering: </b>Manipulate the data being displayed by using the <b>Filter</b> button.

<b>Drill Down: </b>Double-clicking on a Match row will display all Games for the selected Match. Similarly, double-clicking on a Game row will display all Plays for the selected Game. Click the <b>Clear Filter</b> button to display all data.
## Statistics Window
Click the <b>Statistics</b> button to view descriptive statistics and basic analysis.  

Choose to view <b>Match, Game, Play, Time, or Card Data</b> using the top right dropdown menu. The statistics being displayed can be filtered using the Format, Deck, and Date Range menus across the top of the window. 
## Settings
<details>
	<summary><b>GameLogs Folder:</b> Go to 'Data => Set Import Folders'.</summary>
	<p></p>
	<p>The folder containing your MTGO GameLog files.</p>
	<p>MTGO saves these files in <b>"C:\Users\[User]\AppData\Local\Apps\2.0"</b> by default.</p>
</details>
	
- - - -
<details>
	<summary><b>Export Folder:</b> Go to 'Export => Set Default Export Folder'.</summary>
	<p></p>
	<p>The folder where exported .csv and .xlsx files will be saved.</p>
</details>
	
- - - -
<details>
	<summary><b>Hero:</b> Go to 'Data => Set Default Hero'.</summary>
	<p></p>
	<p>Setting a default 'Hero' moves the Hero's username into the P1 column by default. Data in the 'Statistics' window will be shown from the Hero's perspective.</p>
</details>
	
- - - -
## Exporting
MTGO-Tracker creates (3) Tables: 'Matches', 'Games', 'Plays'. Use the <b>'Export' Menu</b> to save your tables as either .csv or .xlsx files.

<b>Inverse Join: </b>Each match, MTGO sets each player to P1 or P2 at random. This makes it difficult to analyze your tables for specific players. The Inverse Join table will create a second row for each Match/Game with P1 and P2 reversed. Keep in mind the tables exported with this option will be twice as large.
## Saving
Save your session by clicking <b>'File => Save Data'</b>.

Delete your saved session by clicking <b>'Data => Delete Saved Session'</b>
