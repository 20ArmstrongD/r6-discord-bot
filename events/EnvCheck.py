from dotenv import load_dotenv
import os
import logging
from .keyHole import DISCORD_BOT_TOKEN, GUILD_ID, R6API


def checkEnvVar():
    env_varibles = {
        "DISCORD_BOT_TOKEN" : os.getenv('DISCORD_BOT_TOKEN'),
        "R6API" : os.getenv('R6_API_KEY'),
        "GUILD_ID" : os.getenv('GUILD_ID')
        }

    for var_name, var_value in env_varibles.items():
        if var_value is None:
            try:
                logging.error(f'{var_name} is not set correctly in .env file')
                raise ValueError(f'{var_name} is not set correctly in .env file')
            except Exception as e:
                logging.error('Unable to do Enviorment variable value check')
        else:
            print(f'{var_name}: "{var_value}"\nAll Systems GO!!')

# checkEnvVar()