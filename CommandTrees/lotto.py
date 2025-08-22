import discord, json
from ThingyDo.Messages import *
from Connections.DB_Connection import DatabaseConnection
import enum
import random

import os, traceback
from dotenv import load_dotenv
from models.bank_account import bank_account as BankAccount



class Lotto(discord.app_commands.Group):
    def __init__(self):
        self.database = DatabaseConnection(os.getenv("DB_PATH"))
        self.admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
        self.ticket_types = {
            1: "Classic",
            2: "Quickdraw",
            3: "Scratch-er"
        }
        super().__init__(name="lotto", description="Lotto commands")    

    async def check_ticket_matches(self, ticket_type:int, ticket_numbers:list, draw_numbers:list=None) -> int:
        """Check the validity of the ticket and return the result."""
        matches = 0
        if ticket_type == 1:
            for number in ticket_numbers:
                if int(number) in draw_numbers:
                    matches += 1
        return matches
    
    async def generate_classic_lotto_draw(self) -> list:
        """Generate a Classic Lotto draw with 6 unique numbers between 1 and 49."""
        return random.sample(range(1, 50), 6)

    @discord.app_commands.command(name="buy_classic_ticket", description="Get a Classic Lotto ticket.")
    async def buy_classic_ticket(self, interaction: discord.Interaction, number1:int, number2:int, number3:int, number4:int, number5:int, number6:int):
        """Get a Classic Lotto ticket with 6 unique numbers between 1 and 49."""
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        
        user_id = interaction.user.id
        ticket_bought_for_someone_else = False
                   
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get the bank balance.")
            return
        # Check if the user has enough money to buy a ticket
        game_type = utility.load_config("lotto_config")["1"] 
        # game_type = {type, name, description, ticket_price, matches}
        # matches = {winnings, description, odds}
        ticket_cost = game_type["ticket_price"]
        
        if ticket_cost > bank_account.balance:
            # TODO - Add a response for when the user doesn't have enough money
            await interaction.response.send_message(content=f"{username}, you don't have enough {guild_currency.name}s to buy a ticket. You need at least {ticket_cost} {guild_currency.name}s.")
            return
        numbers = [number1, number2, number3, number4, number5, number6]

        # Validate numbers
        if len(numbers) != 6 or any(not (1 <= n <= 49) for n in numbers):
            await interaction.response.send_message(content="Please provide exactly 6 unique numbers between 1 and 49.")
            return
        # Validate uniqueness
        if len(set(numbers)) != 6:
            await interaction.response.send_message(content="Please provide 6 unique numbers.")
            return
        ticket_numbers = ",".join(map(str, numbers))

        self.database.add_lotto_ticket(guild_id=guild_id, user_id=user_id, ticket_numbers=ticket_numbers, ticket_type=1, ticket_cost=ticket_cost)
        
        await interaction.response.send_message(content=f"{username}, your Classic Lotto ticket number is: {" ".join(map(str, numbers))}")

    @discord.app_commands.command(name="view_active_tickets", description="View your active Lotto tickets.")
    async def view_active_tickets(self, interaction: discord.Interaction):
        """View your active Lotto tickets."""
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=interaction.user.mention))
            return
        #  {id, guild_id, user_id, ticket_type, ticket_numbers, ticket_time_stamp, archived, matches, winnings}        
        tickets = self.database.get_user_active_lotto_tickets(user_id=user_id, guild_id=guild_id)
        
        if not tickets:
            await interaction.response.send_message(content="You have no active Lotto tickets.")
            return
        
        msg = "Your active Lotto tickets:\n"
        for ticket in tickets:
            ticket_type = self.ticket_types[int(ticket[3])]
            msg += f"Type: {ticket_type}, Numbers: {(" ").join(ticket[4].split(','))}, Timestamp: {ticket[5]}\n"
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="view_historic_tickets", description="View your historic Lotto tickets.")
    async def view_historic_tickets(self, interaction: discord.Interaction):
        """View your historic Lotto tickets."""
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=interaction.user.mention))
            return
        #  {id, guild_id, user_id, ticket_type, ticket_numbers, ticket_time_stamp, archived, matches, winnings}        
        tickets = self.database.get_user_historic_lotto_tickets(user_id=user_id, guild_id=guild_id)
        
        if not tickets:
            await interaction.response.send_message(content="You have no historic Lotto tickets.")
            return
        
        msg = "Your historic Lotto tickets:\n"
        for ticket in tickets:
            ticket_type = self.ticket_types[int(ticket[3])]
            msg += f"Timestamp: {ticket[5]} Type: {ticket_type}, Numbers: {(" ").join(ticket[4].split(','))}, Matches: {ticket[7]}, Winnings: {ticket[8]} {guild_currency.name}s\n"
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="view_lotto_info", description="Details about the Lotto game.")
    async def view_lotto_info(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        msg = "There is actually a number of different Lotto games you can play. Here are the details:\n\n"
        lotto_config = utility.load_config("lotto_config")
        for key in list(lotto_config.keys()): 
            # game_type = {type, name, description, ticket_price, matches}
            # matches = {winnings, description, odds}
            msg += f"**{lotto_config[key]['name']}**:\n" 
            msg+=f"{lotto_config[key]['description']}\nTicket Price: {lotto_config[key]['ticket_price']} {guild_currency.name}s\n"
            jack_pot_matches = list(lotto_config[key]['matches'].keys())[0]
            msg+=f"Jackpot: {lotto_config[key]['matches'][jack_pot_matches]['winnings']} {guild_currency.name}s (Odds: {lotto_config[key]['matches'][jack_pot_matches]['odds']})\n\n"
        msg+="**Commands:**"
        for command in self.commands:
            msg+= f"\n\n/lotto {command.name} - {command.description}"
        await interaction.response.send_message(content=msg)