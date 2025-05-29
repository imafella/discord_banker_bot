import discord, json
from ThingyDo.Messages import *
from Connections.DB_Connection import DatabaseConnection

import os, traceback
from dotenv import load_dotenv

class Bank(discord.app_commands.Group):
    def __init__(self):
        self.database = DatabaseConnection(os.getenv("DB_PATH"))
        self.admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
        super().__init__(name="bank", description="Bank commands")


    @discord.app_commands.command(name="join",description="Make a bank account. Join the server bank. One of us.")
    async def join(self, interaction: discord.Interaction):

        # Acknowledge the interaction immediately
        await interaction.response.defer()

        username = interaction.user.id
        if interaction.guild is None:
            await interaction.followup.send(content="You need to be in a server to join the bank.")
            return
        guild_id = interaction.guild.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id):
            self.database.set_up_guild_bank(guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        # Check if the user is already in the bank
        if self.database.is_user_in_guild_bank(username, guild_id):
            bank_account = self.database.get_user_bank_account_details(user_id=username, guild_id=guild_id)
            await interaction.followup.send(content=pickRandomYouAlreadyHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        
        if self.database.is_user_bank_account_archived(username, guild_id):
            did_the_thing = self.database.unarchive_user_bank_account(user_id=username, guild_id=guild_id)
        else:
            did_the_thing = self.database.add_user_to_guild_bank(user_id=username, guild_id=guild_id)
        if not did_the_thing:
            await interaction.followup.send(content="I broke myself trying to add you to the bank.")
            return
        
        bank_account = self.database.get_user_bank_account_details(user_id=username, guild_id=guild_id)
        
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        
        await interaction.followup.send(content=pickRandomBankWelcomeResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
        return


    @discord.app_commands.command(name="get_balance",description="Get your bank balance.")
    async def get_balance(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        user_id = interaction.user.id
        if interaction.guild is None:
            await interaction.response.send_message(content="You need to be in a server to check your bank balance.")
            return
        guild_id = interaction.guild.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id):
            self.database.set_up_guild_bank(guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id, guild_id):
            await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
            return
        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        
        await interaction.response.send_message(content=pickRandomBankBalanceResponse(username=interaction.user.mention, bank_balance=bank_account[3], currency_name=guild_currency[2], currency_symbol=guild_currency[3]))

    @discord.app_commands.command(name="leave_bank",description="Close your bank account.")
    async def leave_bank(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        user_id = interaction.user.id
        if interaction.guild is None:
            await interaction.response.send_message(content="You need to be in a server to close your bank account.")
            return
        guild_id = interaction.guild.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id=guild_id):
            self.database.set_up_guild_bank(guild_id=guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
            return
        
        bank_account = self.database.get_user_bank_account_details(user_id=user_id, guild_id=guild_id)
        
        did_the_thing = self.database.remove_user_from_guild_bank(guild_id= guild_id,user_id=user_id)
        if not did_the_thing:
            await interaction.response.send_message(content=f"I broke myself trying to remove you from the bank. I blame you, {interaction.user.mention}.")
            return
        
        await interaction.response.send_message(content=pickRandomLeavingTheBankResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))

    @discord.app_commands.command(name="get_change_costs",description="Get the costs of changing the currency name and symbol.")
    async def get_change_costs(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if interaction.guild is None:
            await interaction.response.send_message(content="You need to be in a server to get the change costs.")
            return
        guild_id = interaction.guild.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id=guild_id):
            self.database.set_up_guild_bank(guild_id=guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)
        guild_currency_change_costs = self.database.get_change_costs(guild_id=guild_id)
        if guild_currency_change_costs is None:
            await interaction.response.send_message(content="I broke myself trying to get the change costs.")
            return
        
        await interaction.response.send_message(content=pickRandomChangeCostResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3], name_cost=guild_currency_change_costs[2], symbol_cost=guild_currency_change_costs[3]))

    @discord.app_commands.command(name="change_currency_name",description="Change the currency name.")
    async def change_currency_name(self, interaction: discord.Interaction, new_currency_name:str):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if interaction.guild is None:
            await interaction.response.send_message(content="You need to be in a server to change the currency name.")
            return
        guild_id = interaction.guild.id
        user_id=interaction.user.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id=guild_id):
            self.database.set_up_guild_bank(guild_id=guild_id)

        if len(new_currency_name) > 50:
            await interaction.response.send_message(content="The currency name can't be longer than 50 characters.")
            return

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)
        guild_currency_change_costs = self.database.get_change_costs(guild_id=guild_id)

        if new_currency_name.strip() == "":
            await interaction.response.send_message(content="The currency name can't be empty.")
            return

        # Check if new currency name contains letters
        if not any(char.isalpha() for char in new_currency_name):
            await interaction.response.send_message(content="The currency name must contain at least one letter.")
            return

        if guild_currency[2] == new_currency_name:
            #TODO pickRandomThatChangesNothingResponse
            await interaction.response.send_message(content="The currency name is already set to that ya daft monkey.")
            return
        
        if guild_currency_change_costs is None:
            await interaction.response.send_message(content="I broke myself trying to get the change costs.")
            return
        
        bank_account = self.database.get_user_bank_account_details(user_id=user_id, guild_id=guild_id)
        if bank_account is None:
            await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
            return
        
        if bank_account[3] < guild_currency_change_costs[2]:
            #TODO pickRandomYouDontHaveEnoughMoneyResponse
            await interaction.response.send_message(content="You don't have enough money to change the currency name.")
            return
        
        did_the_thing = self.database.change_currency_name(guild_id=guild_id, new_name=new_currency_name, user_id=user_id, cost=guild_currency_change_costs[2], balance=bank_account[3])
        if not did_the_thing:
            await interaction.response.send_message(content="I broke myself trying to change the currency name.")
            return
        #TODO pickRandomChangeCurrencyNameResponse
        await interaction.response.send_message(content=f"Changed the currency name to {new_currency_name}.")

    @discord.app_commands.command(name="change_currency_symbol",description="Change the currency symbol.")
    async def change_currency_symbol(self, interaction: discord.Interaction, new_currency_symbol:str):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if interaction.guild is None:
            await interaction.response.send_message(content="You need to be in a server to change the currency symbol.")
            return
        guild_id = interaction.guild.id
        user_id=interaction.user.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id=guild_id):
            self.database.set_up_guild_bank(guild_id=guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)
        guild_currency_change_costs = self.database.get_change_costs(guild_id=guild_id)

        if new_currency_symbol.strip() == "":
            await interaction.response.send_message(content="The currency symbol can't be empty.")
            return
        
        if len(new_currency_symbol) > 50:
            await interaction.response.send_message(content="The currency symbol can't be longer than 50 characters.")
            return

        if guild_currency[3] == new_currency_symbol:
            #TODO pickRandomThatChangesNothingResponse
            await interaction.response.send_message(content="The currency symbol is already set to that ya daft monkey.")
            return
        
        if guild_currency_change_costs is None:
            await interaction.response.send_message(content="I broke myself trying to get the change costs.")
            return
        
        bank_account = self.database.get_user_bank_account_details(user_id=user_id, guild_id=guild_id)
        if bank_account is None:
            await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
            return
        
        if bank_account[3] < guild_currency_change_costs[3]:
            #TODO pickRandomYouDontHaveEnoughMoneyResponse
            await interaction.response.send_message(content="You don't have enough money to change the currency symbol.")
            return
        
        did_the_thing = self.database.change_currency_symbol(guild_id=guild_id, new_symbol=new_currency_symbol, user_id=user_id, cost=guild_currency_change_costs[3], balance=bank_account[3])
        if not did_the_thing:
            await interaction.response.send_message(content="I broke myself trying to change the currency symbol.")
            return
        #TODO pickRandomChangeCurrencySymbolResponse
        await interaction.response.send_message(content=f"Changed the currency symbol to {new_currency_symbol}.")

    #TODO transfer_money
    @discord.app_commands.command(name="transfer_money",description="Transfer money to another user.")
    async def transfer_money(self, interaction: discord.Interaction, user:discord.User, amount:float, reason:str=None):
        # Acknowledge the interaction immediately
        await interaction.response.defer()

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if interaction.guild is None:
            await interaction.followup.send(content="You need to be in a server to transfer money.")
            return
        guild_id = interaction.guild.id
        user_id=interaction.user.id

        if amount < 0:
            await interaction.followup.send(content="You can't transfer a negative amount of money.")
            return
        if amount == 0:
            await interaction.followup.send(content="You can't transfer 0.")
            return

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id=guild_id):
            self.database.set_up_guild_bank(guild_id=guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.followup.send(content=pickRandomYouDontHaveAnAccountResponse(username=interaction.user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
            return
        
        # Check is target user is in the bank
        if not self.database.is_user_in_guild_bank(user.id, guild_id=guild_id):
            await interaction.followup.send(content=pickRandomYouDontHaveAnAccountResponse(username=user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
            return
        
        bank_account = self.database.get_user_bank_account_details(user_id=user_id, guild_id=guild_id)
        if bank_account is None:
            await interaction.followup.send(content="I broke myself trying to get your bank balance.")
            return
        
        if bank_account[3] < amount:
            #TODO pickRandomYouDontHaveEnoughMoneyResponse
            await interaction.response.followup.send(content="You don't have enough money to transfer.")
            return
        
        did_the_thing = self.database.transfer_money(guild_id=guild_id, sender_user_id=user_id, receiver_user_id=user.id, amount=amount)
        if not did_the_thing:
            await interaction.followup.send(content="I broke myself trying to transfer money.")
            return
        #TODO pickRandomTransferMoneyResponse
        msg = f"Transferred {amount} {guild_currency[2]}s from {interaction.user.mention} to {user.mention}."
        if reason is not None:
            msg+= f"\nReason: {reason}"
        await interaction.followup.send(content=msg)

    @discord.app_commands.command(name="award",description="Award money to a user. Bank Admin Command.")
    async def award(self, interaction: discord.Interaction, user:discord.User, amount:float, reason:str=None):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if interaction.guild is None:
            await interaction.response.send_message(content="You need to be in a server to award money.")
            return
        guild_id = interaction.guild.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id=guild_id):
            self.database.set_up_guild_bank(guild_id=guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        # Check if the awarding user is an admin
        if interaction.user.id not in self.admins:
            await interaction.response.send_message(content=f"{interaction.user.mention}, You are not allowed to award money.")
            return
        
        # Check is target user is in the bank
        if not self.database.is_user_in_guild_bank(user.id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
            return
        
        bank_account = self.database.get_user_bank_account_details(user_id=user.id, guild_id=guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        
        did_the_thing = self.database.award_money(guild_id=guild_id, user_id=user.id, amount=amount)
        if not did_the_thing:
            await interaction.response.send_message(content="I broke myself trying to award money.")
            return
        await interaction.response.send_message(content=pickRandomAwardMoneyResponse(amount=amount, guild_currency_name=guild_currency[2], guild_currency_symbol=guild_currency[3], username = user.mention, reason = reason))

    @discord.app_commands.command(name="set_balance",description="Set the bank balance of a user.")
    async def set_balance(self, interaction: discord.Interaction, user:discord.User, amount:float):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if interaction.guild is None:
            await interaction.response.send_message(content="You need to be in a server to set the bank balance.")
            return
        guild_id = interaction.guild.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id=guild_id):
            self.database.set_up_guild_bank(guild_id=guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        # Check if the awarding user is an admin
        if interaction.user.id not in self.admins:
            await interaction.response.send_message(content=f"{interaction.user.mention}, You are not allowed to set the bank balance.")
            return
        
        # Check is target user is in the bank
        if not self.database.is_user_in_guild_bank(user.id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomYouDontHaveAnAccountResponse(username=user.mention, currency_name=guild_currency[2], currency_symbol=guild_currency[3]))
            return
        
        bank_account = self.database.get_user_bank_account_details(user_id=user.id, guild_id=guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        
        did_the_thing = self.database.set_bank_balance(guild_id=guild_id, user_id=user.id, amount=amount)
        if not did_the_thing:
            await interaction.response.send_message(content="I broke myself trying to set the bank balance.")
            return
        #TODO pickRandomSetBankBalanceResponse
        await interaction.response.send_message(content=f"Set {user.mention}'s bank balance to {amount}.")

    @discord.app_commands.command(name="get_currency_details",description="Get the currency details.")
    async def get_currency_details(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if interaction.guild is None:
            await interaction.response.send_message(content="You need to be in a server to get the currency details.")
            return
        guild_id = interaction.guild.id

        # Check if the guild has its own bank
        if not self.database.is_guild_bank_setup(guild_id=guild_id):
            self.database.set_up_guild_bank(guild_id=guild_id)

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)
        if guild_currency is None:
            await interaction.response.send_message(content="I broke myself trying to get the currency details.")
            return
        
        await interaction.response.send_message(content=f"The currency name is {guild_currency[2]} and the symbol is {guild_currency[3]}.")
