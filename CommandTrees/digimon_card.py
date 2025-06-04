import discord, json
from Connections.digimon_api_Connection import digimon_api
from ThingyDo.Messages import *
from Connections.DB_Connection import DatabaseConnection
import enum
import random
from ThingyDo import utility

import os, traceback
from dotenv import load_dotenv



class Card(discord.app_commands.Group):
    def __init__(self):
        self.database = DatabaseConnection(os.getenv("DB_PATH"))
        self.admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
        self.digimon_guild_id = int(os.getenv("DIGIMON_GUILD_ID", "0"))
        self.digimon_api = digimon_api()
        
        super().__init__(
            name="card", 
            description="Digimon TCG commands"
        )


    

    @discord.app_commands.command(name="keyword", description="Get the definition of a keyword.") 
    async def keyword(self, interaction: discord.Interaction, keyword:str):
        """Get a Digimon card keyword definition."""
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        digimon_keywords = utility.load_config("digimon")["card_keywords"]
        key = keyword.lower().strip()
        keyword_dict = digimon_keywords.get(key, None)

        if keyword_dict is None: # Base keyword not found
            if "security" in key:
                keyword_dict = digimon_keywords.get("security attack", None)
            if "armor" in key or "purge" in key:
                keyword_dict = digimon_keywords.get("armor purge", None)
            if "material" in key:
                keyword_dict = digimon_keywords.get("material save", None)
            if "blast" in key and "dna" in key:
                keyword_dict = digimon_keywords.get("blast dna digivolve", None)
            if "blast" in key and "dna" not in key:
                keyword_dict = digimon_keywords.get("blast digivolve", None)
            if "mind" in key:
                keyword_dict = digimon_keywords.get("mind link", None)
            if "partition" in key:
                keyword_dict = digimon_keywords.get("partition", None)
        if keyword_dict is None:
            await interaction.response.send_message(content=f"Keyword '{keyword}' not found. Please check the spelling or try a different keyword... or yell at Imafella.")
            return
        await interaction.response.send_message(content=f"**{keyword_dict['name']}**\n{keyword_dict['definition']}")
    
    @discord.app_commands.command(name="search", description="Get a Digimon card by name. or ID.")
    async def search(self, interaction: discord.Interaction, card_id:str=None, card_name:str=None, pack:str=None,color:str=None, type:str=None):
        """Get a Digimon card by name or ID."""
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        if pack is not None:
            # Check if pack is format BTXX or EXXX and not BT-XX or E-XX
            if "-" not in pack:
                #split pack into prefix and number
                if "p" in pack.lower():
                    pack = "P"
                else:
                    prefix, number = pack[:2], pack[2:]
                    if int(number) < 10:
                        number = f"0{number}"
                    pack = f"{prefix}-{number}"
        
        card_response = await self.digimon_api.get_card(card_id=card_id, name=card_name, color=color, type=type, pack=pack)

        if card_response is None or len(card_response) == 0:
            await interaction.response.send_message(
                content=f"Card '{card_name}' not found. Please check the spelling or try a different name... or yell at Imafella."
            )
            return
        
        # if multiple cards are returned
        if len(card_response) > 1:
            msg = f"Multiple cards found:\nPlease specify a card ID or name to narrow down the search."
            msg+= f"\nCards found:\n"
            for index, card in enumerate(card_response):
                msg += f"{index+1}) ID: {card['id']} Name: {card['name']} Type: {card['type']}\n"
            if len(card_response) >= 15:
                msg = "Too many cards found. Please narrow down your search by providing additional paramseters like ID, name, color, or type. Or try specifying the pack ID"
            await interaction.response.send_message(
                content=msg
            )
            return

        if "id" in card_response[0]:
            await interaction.response.send_message(content=f"https://images.digimoncard.io/images/cards/{card_response[0]["id"]}.jpg")
            return
        
        await interaction.response.send_message(
            content=json.dumps(card_response[0], indent=4, ensure_ascii=False)
        )

    @discord.app_commands.command(name="view_card_info", description="Details about the card commands")
    async def view_card_info(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        msg = "This is the Digimon TCG card command group. You can use the following commands to interact with the Digimon TCG card database.\n" 
        msg+="**Commands:**"
        for command in self.commands:
            msg+= f"\n\n/card {command.name} - {command.description}"
        await interaction.response.send_message(content=msg)