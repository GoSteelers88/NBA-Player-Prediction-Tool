import sqlite3
import requests
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import leagueleaders

from nba_api.stats.endpoints import leaguedashplayerstats
import time

current_season = '2023-24'

player_names = [
    "Nikola Jokic", "Joel Embiid", "Giannis Antetokounmpo", "Luka Doncic", "Stephen Curry",
    "Jayson Tatum", "Shai Gilgeous-Alexander", "Kevin Durant", "Devin Booker", "LeBron James",
    "Kawhi Leonard", "Tyrese Haliburton", "Anthony Davis", "Jimmy Butler", "De'Aaron Fox",
    "Damian Lillard", "Anthony Edwards", "Bam Adebayo", "Jamal Murray", "Jalen Brunson",
    "Domantas Sabonis", "Donovan Mitchell", "Paul George", "Karl-Anthony Towns", "Jaylen Brown",
    "Tyrese Maxey", "James Harden", "Trae Young", "Brandon Ingram", "Zion Williamson",
    "Alperen Sengun", "Lauri Markkanen", "Derrick White", "Pascal Siakam", "Desmond Bane",
    "LaMelo Ball", "Darius Garland", "Kyrie Irving", "Rudy Gobert", "Jaren Jackson Jr.",
    "Paolo Banchero", "Julius Randle", "Jrue Holiday", "Dejounte Murray", "Kristaps Porzingis",
    "DeMar DeRozan", "Evan Mobley", "Aaron Gordon", "Cade Cunningham", "OG Anunoby",
    "Jalen Williams", "Fred VanVleet", "Khris Middleton", "Brook Lopez", "Bradley Beal",
    "Jerami Grant", "Tobias Harris", "Zach LaVine", "Draymond Green", "Anfernee Simons",
    "Michael Porter Jr.", "Tyler Herro", "Devin Vassell", "Myles Turner", "Kyle Kuzma",
    "CJ McCollum", "Jarrett Allen", "Jaden McDaniels", "Marcus Smart", "Dillon Brooks",
    "Austin Reaves", "Alex Caruso", "Malcolm Brogdon", "Chris Paul", "Jalen Johnson",
    "Jalen Suggs", "Coby White", "Nikola Vucevic", "Naz Reid", "Nic Claxton",
    "Klay Thompson", "Immanuel Quickley", "Jaime Jaquez Jr.", "RJ Barrett", "Cam Johnson",
    "Herb Jones", "Mike Conley", "Kentavious Caldwell-Pope", "Terry Rozier", "Jabari Smith Jr.",
    "Walker Kessler", "Bruce Brown", "Bogdan Bogdanovic", "Ivica Zubac", "Chet Holmgren",
    "Victor Wembanyama", "Jaime Jaquez Jr.", "Dereck Lively II", "Keyonte George",
    "Brandon Miller", "Cason Wallace", "Brandin Podziemski", "Scoot Henderson", "Jordan Hawkins",
    "Trayce Jackson-Davis", "Ausar Thompson", "Bilal Coulibaly", "Anthony Black", "Duop Reath"
]

def fetch_current_season_stats(player_names):
    all_players = players.get_active_players()
    player_ids = {player['id']: player['full_name'] for player in all_players if player['full_name'] in player_names}
    player_stats_list = []

    try:
        current_season_stats = leaguedashplayerstats.LeagueDashPlayerStats()

        for player_id, player_name in player_ids.items():
            player_data = current_season_stats.get_data_frames()[0]
            player_stats = player_data[player_data['PLAYER_ID'] == player_id]
            if not player_stats.empty:
                player_stats_dict = player_stats.to_dict('records')[0]
                player_stats_list.append(player_stats_dict)

    except Exception as e:
        print(f"An error occurred: {e}")

    return player_stats_list

def print_league_leader_categories():
    # Fetch league leader data
    league_leaders_data = leagueleaders.LeagueLeaders()
    # Get the column headers which represent the statistical categories
    categories = league_leaders_data.get_data_frames()[0].columns.tolist()
    
    # Print each category
    for category in categories:
        print(category)

# Execute the function
print_league_leader_categories()

def update_or_insert_player_stats(cur, player_stats):
    for stats in player_stats:
        data_values = (
            stats.get('PLAYER_ID'),
            stats.get('RANK'),
            stats.get('PLAYER'),
            stats.get('TEAM_ID'),
            stats.get('TEAM'),
            stats.get('GP'),
            # ... (Continue adding all other columns here)
        )

        cur.execute('SELECT 1 FROM NewPlayerStats WHERE PLAYER_ID = ?', (stats.get('PLAYER_ID'),))
        exists = cur.fetchone()

        if exists:
            update_query = 'UPDATE NewPlayerStats SET RANK = ?, PLAYER = ?, TEAM_ID = ?, TEAM = ?, GP = ?, MIN = ?, FGM = ?, FGA = ?, FG_PCT = ?, FG3M = ?, FG3A = ?, FG3_PCT = ?, FTM = ?, FTA = ?, FT_PCT = ?, OREB = ?, DREB = ?, REB = ?, AST = ?, STL = ?, BLK = ?, TOV = ?, PF = ?, PTS = ?, EFF = ?, AST_TOV = ?, STL_TOV = ? WHERE PLAYER_ID = ?'
            cur.execute(update_query, data_values[1:] + (data_values[0],))
        else:
            insert_query = 'INSERT INTO NewPlayerStats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            cur.execute(insert_query, data_values)

def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    # Execute each SQL command separately
    cur.execute('''
        CREATE TABLE IF NOT EXISTS NewPlayerStats (
            PLAYER_ID INTEGER PRIMARY KEY,
            RANK INTEGER,
            PLAYER TEXT,
            TEAM_ID INTEGER,
            TEAM TEXT,
            GP INTEGER,
            MIN REAL,
            FGM REAL,
            FGA REAL,
            FG_PCT REAL,
            FG3M REAL,
            FG3A REAL,
            FG3_PCT REAL,
            FTM REAL,
            FTA REAL,
            FT_PCT REAL,
            OREB REAL,
            DREB REAL,
            REB REAL,
            AST REAL,
            STL REAL,
            BLK REAL,
            TOV REAL,
            PF REAL,
            PTS REAL,
            EFF REAL,
            AST_TOV REAL,
            STL_TOV REAL
        );
    ''')
    # If you have more SQL commands, add more cur.execute() calls here

    return conn, cur


def update_or_insert_player_stats(cur, player_stats):
    for stats in player_stats:
        data_values = [stats.get(column, None) for column in ['PLAYER_ID', 'RANK', 'PLAYER', 'TEAM_ID', 'TEAM', 'GP', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'EFF', 'AST_TOV', 'STL_TOV']]
        
        cur.execute('SELECT 1 FROM NewPlayerStats WHERE PLAYER_ID = ?', (stats['PLAYER_ID'],))
        exists = cur.fetchone()

        if exists:
            update_query = 'UPDATE NewPlayerStats SET RANK = ?, PLAYER = ?, TEAM_ID = ?, TEAM = ?, GP = ?, MIN = ?, FGM = ?, FGA = ?, FG_PCT = ?, FG3M = ?, FG3A = ?, FG3_PCT = ?, FTM = ?, FTA = ?, FT_PCT = ?, OREB = ?, DREB = ?, REB = ?, AST = ?, STL = ?, BLK = ?, TOV = ?, PF = ?, PTS = ?, EFF = ?, AST_TOV = ?, STL_TOV = ? WHERE PLAYER_ID = ?'
            cur.execute(update_query, data_values[1:] + (data_values[0],))
        else:
            insert_query = 'INSERT INTO NewPlayerStats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            cur.execute(insert_query, data_values)
def print_player_stats(conn, player_name):
    cur = conn.cursor()
    cur.execute('SELECT * FROM NewPlayerStats WHERE PLAYER = ?', (player_name,))
    player_data = cur.fetchone()

    if player_data:
        print(f"Data for {player_name}:")
        print(player_data)
    else:
        print(f"No data found for {player_name}")

def main():
    player_stats = fetch_current_season_stats(player_names)
    if player_stats is not None:
        conn, cur = create_database('nba_player_stats.db')
        update_or_insert_player_stats(cur, player_stats)
        conn.commit()
        conn.close()
    else:
        print("No player stats were fetched.")

if __name__ == "__main__":
    main()
    