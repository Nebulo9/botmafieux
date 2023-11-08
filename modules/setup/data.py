import os, json

DATA_DIR = 'data/'

def get_guild_data(guild_id:int):
    """Reads and returns the dictionary of guild data from the guild's JSON data file."""
    path = os.path.join(DATA_DIR, f'{guild_id}.json')
    with open(path, 'r') as f:
        return json.load(f)

def save_guild_data(guild_id:int, data):
    """Saves the dictionary of guild data to the guild's JSON data file."""
    path = os.path.join(DATA_DIR, f'{guild_id}.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)