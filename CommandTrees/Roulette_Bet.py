import discord, json
from ThingyDo.Messages import *
from Connections.DB_Connection import DatabaseConnection

import os, traceback
from dotenv import load_dotenv

class Roulette_Bet(discord.app_commands.Group):
    def __init__(self):
        self.database = DatabaseConnection(os.getenv("DB_PATH"))
        self.admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
        super().__init__(name="roulette_bet", description="Roulette betting commands")

    @discord.app_commands.command(name="join",description="Make a bank account. Join the server bank. One of us.")
    async def join(self, interaction: discord.Interaction):
        return

    async def isRouletteOn(self, guild_id:int):
        """
        Check if roulette is on for the given guild.
        """
        try:
            # Get the roulette status from the database
            result = self.database.get_roulette_status(guild_id)
            return result[0] == 1
        except Exception as e:
            print(f"Error checking roulette status: {e}")
            return False
