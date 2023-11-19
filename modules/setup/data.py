import os, json
from .logger import LOGGER

FEATURES = ['birthday','productivity']

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
        LOGGER.debug(f'Saved data file for guild {guild_id}.')
        
def create_guild_data(guild_id:int):
    """Creates a new guild data file."""
    path = os.path.join(DATA_DIR, f'{guild_id}.json')
    with open(path,'w') as f:
        json.dump({'features': {key:{'enabled':True} for key in FEATURES}}, f, indent=2)
        LOGGER.debug(f'Created data file for guild {guild_id}.')

def delete_guild_data(guild_id:int):
    """Deletes the guild data file."""
    path = os.path.join(DATA_DIR, f'{guild_id}.json')
    os.remove(path)
    LOGGER.debug(f'Deleted data file for guild {guild_id}.')

def is_feature_enabled(feature:str,data=None,guild_id=0):
    """Returns True if the feature is enabled in the guild, False otherwise."""
    if data:
        return data['features'][feature]['enabled']
    else:
        return get_guild_data(guild_id)['features'][feature]['enabled']