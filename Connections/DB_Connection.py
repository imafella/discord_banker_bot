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
    
    def place_bet_roulette(self, guild_id:int, user_id:int, bet_amount:float, bet_type:str, bet_details:str, bet_input:str="0") -> bool:
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
        self.cursor.execute(self.config["insert"]["insert_place_roulette_bet"], (guild_id, user_id, bet_amount, bet_type, bet_details, bet_input,))
        self.cursor.execute(self.config["update"]["update_decrease_user_bank_balance"], (bet_amount, guild_id, user_id,))
        self.connection.commit()
        self.close()
        return True
    
    def get_placed_guild_roulette_bets(self, guild_id:int):
        '''
        Returns list of dicts {id, user_id, amount, type, details, datetime}
        '''
        response = []
        self.connect()
        self.cursor.execute(self.config["select"]["select_placed_guild_roulette_bets"], (guild_id,))
        result = self.cursor.fetchall()
        for row in result:
            bet = {}
            bet['id'] = row[0]
            bet['user_id'] = row[2]
            bet['amount'] = row[3]
            bet['type'] = row[4]
            bet['details'] = row[5]
            bet['datetime'] = row[7]
            bet['input'] = row[9]
            response.append(bet)
        self.close()

        return response
    
    def get_placed_guild_user_roulette_bets(self, guild_id:int, user_id:int):
        '''
        Returns list of dicts {id, user_id, amount, type, details, datetime, input}
        '''
        response = []
        self.connect()
        self.cursor.execute(self.config["select"]["select_active_user_roulette_bets"], (guild_id, user_id,))
        result = self.cursor.fetchall()
        for row in result:
            bet = {}
            bet['id'] = row[0]
            bet['user_id'] = row[2]
            bet['amount'] = row[3]
            bet['type'] = row[4]
            bet['details'] = row[5]
            bet['datetime'] = row[7]
            bet['input'] = row[9]
            response.append(bet)
        self.close()

        return response
    
    def get_historic_guild_user_roulette_bets(self, guild_id:int, user_id:int):
        '''
        Returns list of dicts {id, user_id, amount, type, details, datetime}
        '''
        response = []
        self.connect()
        self.cursor.execute(self.config["select"]["select_historic_user_roulette_bets"], (guild_id, user_id,))
        result = self.cursor.fetchall()
        for row in result:
            bet = {}
            bet['id'] = row[0]
            bet['user_id'] = row[2]
            bet['amount'] = row[3]
            bet['type'] = row[4]
            bet['details'] = row[5]
            bet['status'] = row[6]
            bet['datetime'] = row[7]
            bet['input'] = row[9]
            response.append(bet)
        self.close()

        return response
    
    def set_guild_user_roulette_bet_results(self, guild_id:int, user_id:int, bet_id:int, bet_win:bool, amount:float, multiplier:int=0):

        self.connect()
        if bet_win:
            self.cursor.execute(self.config["update"]["update_set_guild_roulette_bets_win_status"],(bet_id,))
            self.cursor.execute(self.config["update"]["update_increase_user_bank_balance"], ((amount*multiplier)+ amount, guild_id, user_id,))
        else:
            self.cursor.execute(self.config["update"]["update_set_guild_roulette_bets_lose_status"],(bet_id,))
            # self.cursor.execute(self.config["update"]["update_decrease_user_bank_balance"], (amount, guild_id, user_id,))
        
        self.connection.commit()
        self.close()
        
        return True
    
    def get_sunshine_list(self, guild_id:int) -> list:
        """
        Get the sunshine list for a given guild ID.
        :param guild_id: The ID of the guild to get the sunshine list for.
        :return: A list of dictionaries containing the sunshine list.
        """
        # Connect to the database
        self.connect()

        # Get the sunshine list
        self.cursor.execute(self.config["select"]["select_sunshine_list"], (guild_id,))
        result = self.cursor.fetchall()
        self.close()
        
        return result
    
    def get_bottomboard(self, guild_id:int) -> list:
        """
        Get the bottomboard for a given guild ID.
        :param guild_id: The ID of the guild to get the sunshine list for.
        :return: A list of dictionaries containing the sunshine list.
        """
        # Connect to the database
        self.connect()

        # Get the sunshine list
        self.cursor.execute(self.config["select"]["select_bottomboard"], (guild_id,))
        result = self.cursor.fetchall()
        self.close()
        
        return result
    
    # add_lotto_ticket(guild_id=guild_id, user_id=user_id, ticket_numbers=ticket, ticket_type=1, ticket_cost=ticket_cost)
    def add_lotto_ticket(self, guild_id:int, user_id:int, ticket_numbers:str, ticket_type:int, ticket_cost:float) -> bool:
        """
        Add a lotto ticket for a user.
        :param guild_id: The ID of the guild to add the ticket to.
        :param user_id: The ID of the user to add the ticket for.
        :param ticket_numbers: The lotto ticket numbers as a string seperated by a comma.
        :param ticket_type: The type of lotto ticket (1 for Classic).
        :param ticket_cost: The cost of the lotto ticket.
        :return: True if the ticket was added successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Add the lotto ticket
        self.cursor.execute(self.config["insert"]["insert_lotto_ticket"], (guild_id, user_id, ticket_type, ticket_numbers,))
        self.cursor.execute(self.config["update"]["update_decrease_user_bank_balance"], (ticket_cost, guild_id, user_id,))
        self.connection.commit()
        self.close()
        
        return True
    def get_user_active_lotto_tickets(self, guild_id:int, user_id:int) -> list:
        """
        Get the active lotto tickets for a user.
        :param guild_id: The ID of the guild to get the tickets from.   
        :param user_id: The ID of the user to get the tickets for.
        :return: A list of dictionaries containing the active lotto tickets.
        {id, guild_id, user_id, ticket_type, ticket_numbers, ticket_time_stamp, archived, matches, winnings}
        """ 
        # Connect to the database
        self.connect()

        # Get the active lotto tickets
        self.cursor.execute(self.config["select"]["select_user_active_lotto_tickets"], (guild_id, user_id,))
        result = self.cursor.fetchall()
        self.close()
        
        return result
    def get_user_historic_lotto_tickets(self, guild_id:int, user_id:int) -> list:
        """
        Get the historic lotto tickets for a user.
        :param guild_id: The ID of the guild to get the tickets from.
        :param user_id: The ID of the user to get the tickets for.
        :return: A list of dictionaries containing the historic lotto tickets.
        """
        # Connect to the database
        self.connect()

        # Get the historic lotto tickets
        self.cursor.execute(self.config["select"]["select_user_historic_lotto_tickets"], (guild_id, user_id,))
        result = self.cursor.fetchall()
        self.close()
        
        return result
    def set_lotto_ticket_results(self, guild_id:int, user_id:int, ticket_id:int, matches:int, winnings:float) -> bool:
        """
        Set the results for a lotto ticket.
        :param guild_id: The ID of the guild to set the results for.
        :param user_id: The ID of the user to set the results for.
        :param ticket_id: The ID of the lotto ticket to set the results for.
        :param matches: The number of matches for the ticket.
        :param winnings: The winnings for the ticket.
        :return: True if the results were set successfully, False otherwise.
        """
        # Connect to the database
        self.connect()

        # Set the lotto ticket results
        self.cursor.execute(self.config["update"]["update_lotto_ticket_results"], ( matches, winnings, ticket_id, ))
        if winnings > 0:
            # If the user won, update their bank balance
            self.cursor.execute(self.config["update"]["update_increase_user_bank_balance"], (winnings, guild_id, user_id,))
        self.connection.commit()
        self.close()
        
        return True

    def get_guild_typed_active_lotto_tickets(self, guild_id:int, ticket_type:int) -> list:
        """
        Get the active lotto tickets for a guild by ticket type.
        :param guild_id: The ID of the guild to get the tickets from.
        :param ticket_type: The type of lotto ticket (1 for Classic).
        :return: A list of dictionaries containing the active lotto tickets.
        {id, guild_id, user_id, ticket_type, ticket_numbers, ticket_time_stamp, archived, matches, winnings}
        """
        # Connect to the database
        self.connect()

        # Get the active lotto tickets
        self.cursor.execute(self.config["select"]["select_guild_active_lotto_tickets"], (guild_id, ticket_type,))
        result = self.cursor.fetchall()
        self.close()
        tickets = []
        # ( id INTEGER, guild_id INTEGER, user_id INTEGER, ticket_type TEXT , ticket_numbers TEXT, ticket_time_stamp TEXT , archived INTEGER, matches INTEGER, winnings real"
    
        for row in result:
            ticket = {}
            ticket['id'] = row[0]
            ticket['guild_id'] = row[1]
            ticket['user_id'] = row[2]
            ticket['ticket_type'] = row[3]
            ticket['ticket_numbers'] = row[4]
            ticket['ticket_time_stamp'] = row[5]
            ticket['archived'] = row[6]
            ticket['matches'] = row[7]
            ticket['winnings'] = row[8]
            tickets.append(ticket)
        
        return tickets