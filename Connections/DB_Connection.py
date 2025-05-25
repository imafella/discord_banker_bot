import sqlite3
import ThingyDo.utility as utility

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.config = utility.load_config("db_config")
        self.setup_database()

    def connect(self):
        # Connect to the SQLite database (or create it if it doesn't exist)
        if self.connection == None:
            self.connection = sqlite3.connect(self.db_name)
        # Create a cursor object to interact with the database
        if self.cursor == None:
            self.cursor = self.connection.cursor()

    def close(self):
        # Close the database connection
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None


    def setup_database(self):
        self.connect()
        # Create the tables if it doesn't exist
        for script in self.config["create"].values():
            self.cursor.execute(script)
        # Commit the changes and close the connection
        self.connection.commit()
        self.close()
        # Close the connection

    def get_user_bank_account_details(self, user_id:int, guild_id:int) -> dict:
         # Connect to the database
        self.connect()

        # Check if the user is in the guild bank
        self.cursor.execute(self.config["select"]["select_user_bank_account_details"], (guild_id, user_id))
        result = self.cursor.fetchone()
        self.close()
        return result

    def is_user_in_guild_bank(self, user_id:int, guild_id:int) -> bool: 
        """
        Check if a user is in the guild bank.
        :param user_id: The ID of the user to check.
        :param guild_id: The ID of the guild to check.
        :return: True if the user is in the guild bank, False otherwise.
        """
        # Connect to the database
        result = self.get_user_bank_account_details(user_id, guild_id)
        # Check if the user is in the guild bank
        return result is not None
    
    def get_guild_details(self, guild_id:int) -> dict:
        """
        Get the details of a guild.
        :param guild_id: The ID of the guild to get details for.
        :return: A dictionary containing the guild details.
        """
        # Connect to the database
        self.connect()

        # Get the guild details
        self.cursor.execute(self.config["select"]["select_guild_details"], (guild_id,))
        result = self.cursor.fetchone()
        self.close()
        return result

    def is_user_bank_account_archived(self, user_id:int, guild_id:int) -> bool:
        """
        Check if a user's bank account is archived.
        :param user_id: The ID of the user to check.
        :param guild_id: The ID of the guild to check.
        :return: True if the user's bank account is archived, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Check if the user's bank account is archived
        self.cursor.execute(self.config["select"]["select_archived_user_bank_account_details"], (guild_id,user_id, ))
        result = self.cursor.fetchone()
        self.close()
        return result is not None
    
    def unarchive_user_bank_account(self, user_id:int, guild_id:int) -> bool:
        """
        Unarchive a user's bank account.
        :param user_id: The ID of the user to unarchive.
        :param guild_id: The ID of the guild to unarchive the user from.
        :return: True if the user's bank account was unarchived successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Unarchive the user's bank account
        self.cursor.execute(self.config["update"]["update_unarchive_bank_account"], (guild_id,user_id, ))
        self.connection.commit()
        self.close()
        return not self.is_user_bank_account_archived(user_id=user_id, guild_id=guild_id)
    
    def is_guild_in_guilds(self, guild_id:int) -> bool:
        result = self.get_guild_details(guild_id)
        return result is not None
    
    def get_guild_currency_details(self, guild_id:int) -> dict:
        """
        Get the currency details for a given guild ID.
        :param guild_id: The ID of the guild to get currency details for.
        :return: A dictionary containing the currency details.
        """
        # Connect to the database
        self.connect()

        # Get the currency details
        self.cursor.execute(self.config["select"]["select_currency_details"], (guild_id,))
        result = self.cursor.fetchone()
        self.close()
        return result
    
    
    def is_guild_bank_setup(self, guild_id:int) -> bool:
        result = self.get_guild_currency_details(guild_id)
        return result is not None

    def add_user_to_guild_bank(self, user_id:int, guild_id:int) -> bool:
        """
        Add a user to the guild bank.
        :param user_id: The ID of the user to add.
        :param guild_id: The ID of the guild to add the user to.
        :return: True if the user was added successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Add the user to the guild bank
        self.cursor.execute(self.config["insert"]["insert_user_into_guild_bank"], (guild_id,user_id, 200.00))
        self.connection.commit()
        self.close()
        return self.is_user_in_guild_bank(user_id, guild_id)
    
    def set_up_guild_bank(self, guild_id:int) -> bool:
        """
        Set up a guild with the given currency name and symbol.
        :param guild_id: The ID of the guild to set up.
        :param currency_name: The name of the currency.
        :param currency_symbol: The symbol of the currency.
        :return: True if the guild was set up successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Set up the guild insert_guild_into_guilds
        self.cursor.execute(self.config["insert"]["insert_guild_currency"], (guild_id,))
        self.cursor.execute(self.config["insert"]["insert_guild_currency_change_cost"], (guild_id,))
        self.connection.commit()
        self.close()
        return True
    
    def remove_user_from_guild_bank(self, guild_id:int, user_id:int) -> bool:
        """
        Remove a user from the guild bank.
        :param user_id: The ID of the user to remove.
        :param guild_id: The ID of the guild to remove the user from.
        :return: True if the user was removed successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Remove the user from the guild bank
        self.cursor.execute(self.config["update"]["update_archive_bank_account"], (guild_id,user_id, ))
        self.connection.commit()
        self.close()
        return not self.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id)
    
    def get_change_costs(self, guild_id:int) -> dict:
        """
        Get the change costs for a given guild ID.
        :param guild_id: The ID of the guild to get change costs for.
        :return: A dictionary containing the change costs.
        """
        # Connect to the database
        self.connect()

        # Get the change costs
        self.cursor.execute(self.config["select"]["select_guild_currency_change_costs"], (guild_id,))
        result = self.cursor.fetchone()
        self.close()
        return result
    
    def change_currency_name(self, guild_id:int, user_id:int, new_name:str, balance:float, cost:float) -> bool:
        """
        Change the currency name for a given guild ID.
        :param guild_id: The ID of the guild to change the currency name for.
        :param new_name: The new currency name.
        :return: True if the currency name was changed successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Change the currency name
        self.cursor.execute(self.config["update"]["update_guild_currency_name"], (new_name, guild_id, ))
        self.cursor.execute(self.config["update"]["update_user_bank_balance"], ((balance-cost), guild_id, user_id, ))
        self.cursor.execute(self.config["update"]["update_guild_currency_name_change_cost"], ((cost+1.75), guild_id,))
        self.connection.commit()
        self.close()
        return True
    
    def change_currency_symbol(self, guild_id:int, user_id:int, new_symbol:str, balance:float, cost:float) -> bool:
        """
        Change the currency symbol for a given guild ID.
        :param guild_id: The ID of the guild to change the currency symbol for.
        :param new_symbol: The new currency symbol.
        :return: True if the currency symbol was changed successfully, False otherwise.
        """    
        # Connect to the database
        self.connect()

        # Change the currency symbol
        self.cursor.execute(self.config["update"]["update_guild_currency_symbol"], (new_symbol, guild_id, ))
        self.cursor.execute(self.config["update"]["update_user_bank_balance"], ((balance-cost), guild_id, user_id, ))
        self.cursor.execute(self.config["update"]["update_guild_currency_symbol_change_cost"], ((cost+1.25), guild_id,))
        self.connection.commit()
        self.close()
        return True
    
    def transfer_money(self, guild_id:int, sender_user_id:int, receiver_user_id:int, amount:float) -> bool:
        """
        Transfer money from a user's bank account to the guild bank.
        :param guild_id: The ID of the guild to transfer money to.
        :param user_id: The ID of the user to transfer money from.
        :param amount: The amount of money to transfer.
        :return: True if the transfer was successful, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Transfer money
        self.cursor.execute(self.config["update"]["update_user_bank_balance_simple"], ((amount), guild_id, sender_user_id, ))
        self.cursor.execute(self.config["update"]["update_user_bank_balance_simple"], ((-amount), guild_id, receiver_user_id,))
        self.connection.commit()
        self.close()
        return True
    
    def award_money(self, guild_id:int, user_id:int, amount:float) -> bool:
        """
        Award money to a user's bank account.
        :param guild_id: The ID of the guild to award money to.
        :param user_id: The ID of the user to award money to.
        :param amount: The amount of money to award.
        :return: True if the award was successful, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Award money
        self.cursor.execute(self.config["update"]["update_user_bank_balance_simple"], ((-amount), guild_id, user_id, ))
        self.connection.commit()
        self.close()
        return True
    
    def set_bank_balance(self, guild_id:int, user_id:int, amount:float) -> bool:
        """
        Set the bank balance for a given user ID.
        :param guild_id: The ID of the guild to set the bank balance for.
        :param user_id: The ID of the user to set the bank balance for.
        :param amount: The amount to set the bank balance to.
        :return: True if the bank balance was set successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Set the bank balance
        self.cursor.execute(self.config["update"]["update_user_bank_balance"], (amount, guild_id, user_id, ))
        self.connection.commit()
        self.close()
        return True
    
    def get_allowance_info(self) -> dict:
        """
        Manage the allowance for all users in the guild bank.
        :return: A list of users who received their allowance.
        """
        # Connect to the database
        self.connect()
        allowance_list = []

        # Get the list of users who received their allowance
        self.cursor.execute(self.config["select"]["select_users_for_allowance"])
        result = self.cursor.fetchall()
        for row in result:
            guild_id =  row[0]
            user_id = row[1]
            bot_usage = row[2]
            allowance_list.append({"guild_id": guild_id, "user_id": user_id, "bot_usage": bot_usage})
        self.close()
        return allowance_list

    def give_allowance(self, allowance_info:dict) -> bool:
        """
        Give allowance to a user.
        :param guild_id: The ID of the guild to give allowance to.
        :param user_id: The ID of the user to give allowance to.
        :param amount: The amount of allowance to give.
        :return: True if the allowance was given successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        for allowance in allowance_info:
            guild_id = allowance["guild_id"]
            user_id = allowance["user_id"]
            amount = float(allowance["amount"])
            # Give allowance
            self.cursor.execute(self.config["update"]["update_user_bank_balance_simple"], ((-amount), guild_id, user_id, ))
        self.cursor.execute(self.config["update"]["update_reset_bot_use"])
        self.connection.commit()
        self.close()
        return True
    
    def incriment_bot_usage(self, guild_id:int, user_id:int) -> bool:
        """
        Increment the bot usage for a given user ID.
        :param guild_id: The ID of the guild to increment the bot usage for.
        :param user_id: The ID of the user to increment the bot usage for.
        :return: True if the bot usage was incremented successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Increment the bot usage
        self.cursor.execute(self.config["update"]["update_increment_bot_use"], (guild_id, user_id, ))
        self.connection.commit()
        self.close()
        return True
    
    def set_up_roulette_tables(self) -> bool:
        """
        Set up the roulette table.
        :return: True if the roulette table was set up successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Set up the roulette table
        self.cursor.execute(self.config["create"]["create_table_live_guild_roulette"])
        self.cursor.execute(self.config["create"]["create_table_roulette_bets"])
        self.connection.commit()
        self.close()
        return True
    
    def isRouletteOn(self, guild_id:int) -> bool:
        """
        Check if roulette is on for the given guild.
        :param guild_id: The ID of the guild to check.
        :return: True if roulette is on, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Check if roulette is on
        self.cursor.execute(self.config["select"]["select_is_roulette_live"], (guild_id,))
        result = self.cursor.fetchone()
        self.close()
        return result[0] == 1
    
    def insert_roulette_table(self, guild_id:int) -> bool:
        """
        Insert a new roulette table for the given guild ID.
        :param guild_id: The ID of the guild to insert the roulette table for.
        :return: True if the roulette table was inserted successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Insert the roulette table
        self.cursor.execute(self.config["insert"]["live_guild_roulette"], (guild_id,0))
        self.connection.commit()
        self.close()
        return True
    
    def place_roulette_bet(self, guild_id:int, user_id:int, bet_amount:float, bet_type:str, bet_details:str) -> bool:
        """
        Place a bet on the roulette table.
        :param guild_id: The ID of the guild to place the bet in.
        :param user_id: The ID of the user placing the bet.
        :param bet_amount: The amount of the bet.
        :param bet_type: The type of bet (e.g., "red", "black", "number").
        :return: True if the bet was placed successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Place the bet
        self.cursor.execute(self.config["insert"]["insert_place_roulette_bet"], (guild_id, user_id, bet_amount, bet_type, bet_details))
        self.connection.commit()
        self.close()
        return True