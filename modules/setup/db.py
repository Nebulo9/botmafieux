import os, psycopg2
from dotenv import load_dotenv
from typing import Optional, Callable, Any, Union
from .logger import LOGGER

load_dotenv()
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

def check_conn():
    """Tests the database connection."""
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432"
    )
    if connection.status:
        LOGGER.debug('Established connection to database.')
        LOGGER.debug(f'Connection status: {connection.status}')
    else:
        LOGGER.error('Failed to connect to database.')
    connection.close()
    LOGGER.debug('Closed connection to database.')

def insert(table:str,**kwargs):
    """
    Inserts the given data into the given table.
    
    Global_User
        user_id: int
        user_mention: str
        user_mention: str
        
    Guild
        guild_id: int
    
    Birthday_Settings
        guild_id: int
        is_enabled: bool
        channel_id: int
        
    Productivity_Settings
        guild_id: int
        is_enabled: bool
        
    Guild_User_Birthday
        user_id: int
        guild_id: int
        birthday: int
        birthday_message: str | None
        is_enabled: bool
        
    Guild_User_Productivity
        user_id: int
        guild_id: int
        is_enabled: bool
        channel_id: int
        cooldown: int
        next_reminder: int
        reminder_message: str | None
    """
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432",
    )
    cursor = connection.cursor()

    query = f"INSERT INTO {table} ("
    params = []
    for key,value in kwargs.items():
        query += f"{key},"
        params.append(value)
    query = query.rstrip(",")  # Remove trailing comma
    query += ") VALUES ("
    for _ in range(len(params)):
        query += "%s,"
    query = query.rstrip(",")  # Remove trailing comma
    query += ")"

    query = cursor.mogrify(query, params)
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    LOGGER.debug(f'Inserted data into {table}.')

def update(table:str,where:str,**kwargs):
    """
    Updates the given data in the given table.
    
    Global_User
        user_id: int
        user_mention: str
        user_mention: str
        
    Guild
        guild_id: int
    
    Birthday_Settings
        guild_id: int
        is_enabled: bool
        channel_id: int
        
    Productivity_Settings
        guild_id: int
        is_enabled: bool
        
    Guild_User_Birthday
        user_id: int
        guild_id: int
        birthday: int
        birthday_message: str | None
        is_enabled: bool
        
    Guild_User_Productivity
        user_id: int
        guild_id: int
        is_enabled: bool
        channel_id: int
        cooldown: int
        next_reminder: int
        reminder_message: str | None
    """
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432",
    )
    cursor = connection.cursor()

    query = f"UPDATE {table} SET "
    params = []
    for key,value in kwargs.items():
        query += f"{key} = %s,"
        params.append(value)
    query = query.rstrip(",")  # Remove trailing comma
    query += f" WHERE {where}"

    query = cursor.mogrify(query, params)
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    LOGGER.debug(f'Updated data in {table}.')

def delete(table:str,where:str):
    """
    Deletes the given data from the given table.
    
    Global_User
        user_id: int
        user_mention: str
        user_mention: str
        
    Guild
        guild_id: int
    
    Birthday_Settings
        guild_id: int
        is_enabled: bool
        channel_id: int
        
    Productivity_Settings
        guild_id: int
        is_enabled: bool
        
    Guild_User_Birthday
        user_id: int
        guild_id: int
        birthday: int
        birthday_message: str | None
        is_enabled: bool
        
    Guild_User_Productivity
        user_id: int
        guild_id: int
        is_enabled: bool
        channel_id: int
        cooldown: int
        next_reminder: int
        reminder_message: str | None
    """
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432",
    )
    cursor = connection.cursor()
    
    query = f"DELETE FROM {table} WHERE {where}"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    LOGGER.debug(f'Deleted data from {table}.')
    
def select(table:str,where:str,*columns:str) -> dict[str,Any] | None:
    """
    Selects the given data from the given table, and returns it as a dictionary.
    
    Global_User
        user_id: int
        user_mention: str
        user_mention: str
        
    Guild
        guild_id: int
    
    Birthday_Settings
        guild_id: int
        is_enabled: bool
        channel_id: int
        
    Productivity_Settings
        guild_id: int
        is_enabled: bool
        
    Guild_User_Birthday
        user_id: int
        guild_id: int
        birthday: int
        birthday_message: str | None
        is_enabled: bool
        
    Guild_User_Productivity
        user_id: int
        guild_id: int
        is_enabled: bool
        channel_id: int
        cooldown: int
        next_reminder: int
        reminder_message: str | None
    """
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432"
    )
    connection.readonly = True
    cursor = connection.cursor()
    
    query = f"SELECT "
    if columns:
        for column in columns:
            query += f"{column},"
        query = query.rstrip(",")
    else:
        query += "*"
    query += f" FROM {table} WHERE {where}"
    cursor.execute(query)
    record = cursor.fetchone()
    result = None
    if record is None:
        LOGGER.debug(f'No data found in {table} for {where}.')
    else:
        result = {}
        if len(columns) > 0:
            for i in range(len(columns)):
                result[columns[i]] = record[i]
        else:
            if table.lower() == 'global_user':
                result['user_id'] = record[0]
                result['user_name'] = record[1]
                result['user_mention'] = record[2]
            elif table.lower() == 'guild':
                result['guild_id'] = record[0]
            elif table.lower() == 'birthday_settings':
                result['guild_id'] = record[0]
                result['is_enabled'] = record[1]
                result['channel_id'] = record[2]
            elif table.lower() == 'productivity_settings':
                result['guild_id'] = record[0]
                result['is_enabled'] = record[1]
            elif table.lower() == 'guild_user_birthday':
                result['user_id'] = record[0]
                result['guild_id'] = record[1]
                result['birthday'] = record[2]
                result['is_enabled'] = record[3]
            elif table.lower() == 'guild_user_productivity':
                result['user_id'] = record[0]
                result['guild_id'] = record[1]
                result['is_enabled'] = record[2]
                result['channel_id'] = record[3]
                result['cooldown'] = record[4]
                result['next_reminder'] = record[5]
                result['reminder_message'] = record[6]
            else:
                LOGGER.error(f'Unknown table {table}.')
    cursor.close()
    connection.close()
    return result