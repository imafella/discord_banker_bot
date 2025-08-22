import json, os, random
from datetime import datetime, timedelta
from math import floor

def load_config(name) -> dict:
    """
    Load the configuration file.
    """
    path = os.path.join(os.path.dirname(__file__), '../Configs')
    name = f"{name}.json"
    
    file_name_and_path = os.path.join(path, name)
    # print(f"Looking for config file at: {file_name_and_path}")  # Debugging

    if not os.path.exists(file_name_and_path):
        raise FileNotFoundError(f"Configuration file {name} not found in {path}.")
    with open(file_name_and_path,'r') as f:
        return json.load(f)
    
def load_random_avatar() -> bytes:
    """
    Load a random avatar from the avatars directory.
    """
    path = os.path.abspath(os.getenv('AVATAR_PATH'))
    files = os.listdir(path)

    if not files:
        raise FileNotFoundError("No avatar files found in the Avatars directory.")

    file = ""
    while file == "" or not file.endswith(('.png', '.jpg', '.jpeg')):
        file = random.choice(files)
    
    
    
    random_file = os.path.join(path, file)
    
    with open(random_file, 'rb') as f:
        return f.read()

def is_past_Allowance_Time():
    # Get the current time
    now = datetime.now()

    # Check if today is Allowance Day
    if is_Allowance_Day(): 
        hour = int(os.getenv('ALLOWANCE_TIME', "10"))
        Allowance_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        # Check if the current time is later than 10 AM
        return now > Allowance_time

    # Return False for all other days
    return False

def is_Allowance_Day():
    # Get the current time
    return check_if_day(int(os.getenv('ALLOWANCE_DAY', "5")))  # Monday is 0

def is_classic_lotto_draw_day():
    """
    Check if today is a Classic Lotto draw day.
    """
    return check_if_day(1) or check_if_day(4)

def is_past_classic_lotto_draw_time():
    return check_if_past_time(18)  # Default to 6 PM

def check_if_day(day:int) -> bool:
    """
    Check if today is the specified day of the week.
    :param day: The day of the week to check (0=Monday, 6=Sunday).
    :return: True if today is the specified day, False otherwise.
    """
    now = datetime.now()
    return now.weekday() == day

def check_if_past_time(hour:int) -> bool:
    """
    Check if the current time is past the specified hour.
    :param hour: The hour to check (0-23).
    :return: True if the current time is past the specified hour, False otherwise.
    """
    now = datetime.now()
    return now.hour >= hour

def calculate_Allowance(allowance_info:list) -> dict:
    '''
    Expected dict of dicts. Each sub dict has the following
    keys:
        - guild_id
        - user_id
        - bot_usage
    '''
    updated_allowance_info = {}
    for account in allowance_info:
        # Calculate the allowance for each account
        guild_id = account['guild_id']
        # user_id = account['user_id']
        bot_usage = account['bot_usage']
        amount = 5.0
        if bot_usage > 0:
            amount += 20.0*(1.0+(bot_usage/100))
        
        account['amount'] = amount
        if str(guild_id) not in updated_allowance_info:
            updated_allowance_info[str(guild_id)] = []
        updated_allowance_info[str(guild_id)].append(account)
    
    return updated_allowance_info

def floor_to_2_digits(value: float) -> float:
    return floor(value * 100) / 100
