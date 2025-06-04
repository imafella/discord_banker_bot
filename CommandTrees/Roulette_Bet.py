import discord, json
from ThingyDo.Messages import *
from Connections.DB_Connection import DatabaseConnection
import enum
import random

import os, traceback
from dotenv import load_dotenv



class Roulette(discord.app_commands.Group):
    def __init__(self):
        self.database = DatabaseConnection(os.getenv("DB_PATH"))
        self.admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
        self.bet_types = ["straight", "split", "street", "corner", "sixline", "red/black", "color", "odd/even", "parity", "low/high", "lowhigh," "dozen", "column"]
        self.wheel = { 0: "green",
                1: "red", 2: "black", 3: "red", 
                4: "black", 5: "red", 6: "black",
                7: "red", 8: "black", 9: "red",   
                10: "black", 11: "black", 12: "red",
                13: "black", 14: "red", 15: "black", 
                16: "red", 17: "black", 18: "red",
                19: "black", 20: "black", 21: "red",   
                22: "black", 23: "red", 24: "black",
                25: "red",   26: "black", 27: "red",   
                28: "red", 29: "black", 30: "red",
                31: "black", 32: "red", 33: "black", 
                34: "red", 35: "black", 36: "red",
            }
        self.payouts = {
            "straight": 35,
            "split": 17,
            "street": 11,
            "corner": 8,
            "sixline": 5,
            "color": 1,
            "parity": 1,
            "lowhigh": 1,
            "dozen": 2,
            "column": 2
        }
        super().__init__(name="roulette", description="Roulette betting commands")

    async def are_adjacent_split(self, num1: int, num2: int) -> bool:
        # Both numbers must be between 1 and 36
        if not (1 <= num1 <= 36 and 1 <= num2 <= 36):
            return False

        # Ensure num1 < num2 for easier checks
        n1, n2 = sorted([num1, num2])

        # Horizontal: next to each other in the same row
        if n2 - n1 == 1 and (n1 - 1) // 3 == (n2 - 1) // 3:
            return True

        # Vertical: same column, one above the other
        if n2 - n1 == 3:
            return True

        return False
    
    async def get_row_start(self, the_first_number_in_the_row:int=1, valid_options:list=[]) -> int:
        if the_first_number_in_the_row in valid_options:
            return the_first_number_in_the_row
        valid_options.reverse()
        for x in valid_options:
            if the_first_number_in_the_row > x:
                return x
        return 0

    async def is_valid_corner(self, top_left_of_corner: int) -> bool:
        """
        Validates that the four numbers form a square (corner) on a standard roulette table.
        """
        # All numbers must be between 1 and 36
        if top_left_of_corner< 1 or top_left_of_corner > 36:
            return False

        if top_left_of_corner % 3 == 0:
            # If the number is a multiple of 3, it can't be a corner
            return False
        
        if top_left_of_corner > 33:
            # If the number is greater than 33, it can't form a corner
            return False

        return True

    async def is_valid_six_line(self, row_start: int) -> bool:
        # Valid row starts for a double street (must have a row below)
        valid_starts = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31]
        if row_start not in valid_starts:
            return False
        # The next row must also exist (row_start + 3 <= 34)
        if row_start + 3 > 34:
            return False
        # All numbers must be within 1-36
        numbers = [row_start + i for i in range(6)]
        return all(1 <= n <= 36 for n in numbers)

    async def get_table(self) -> discord.File:
        image_path = os.path.expanduser(os.getenv("roulette_table_path"))  # Adjust filename as needed

        if image_path != None and not os.path.exists(image_path):
            return None
        
        return discord.File(image_path, filename="roulette_table.png")
        
    async def roll_roulette(self):
        roll = random.randint(0,36)
        return roll
    
    async def get_roulette_roll_color(self,roll:int, use_emojis:bool=False) -> str:
        if use_emojis:
            if roll == 0:
                return "🟢"
            elif self.wheel[roll] == "red":
                return "🔴"
            elif self.wheel[roll] == "black":
                return "⚫️"
            else:
                return "❓"
        return self.wheel[roll]

    async def did_bet_win(self,bet:dict, result:dict) -> bool:
        '''
        ingets bet {id, user_id, amount, type, details, datetime, input}
        ingests result {number, color}
        '''
        target_numbers = bet['details'].split(',')
        if result['number'] in [int(num) for num in target_numbers]:
            return True
        return False
    
    async def get_bet_payout(self, bet_type:str) -> int:
        '''
        Gets the payout for the bet type
        '''
        if bet_type in self.payouts:
            return self.payouts[bet_type]
        return 0
    
    async def apply_roulette_results(self,guild_id:int, bet:dict, result:dict)-> tuple:
        """
        Applies the roulette results to the bet.
        ingets bet {id, user_id, amount, type, details, datetime, input}
        ingests result {number, color}
        Returns a tuple of (win_amount, win_status).
        """
        did_win = await self.did_bet_win(bet=bet, result=result)

        payout_multiplier = self.payouts.get(bet['type'], 0)
        self.database.set_guild_user_roulette_bet_results(guild_id=guild_id, user_id=bet['user_id'], bet_id=bet['id'], bet_win=did_win, amount=bet['amount'], multiplier=payout_multiplier)
        
        if did_win:
            win_amount = bet['amount'] * payout_multiplier
            return (win_amount, did_win)
        
        return (bet['amount'], did_win)
    

    @discord.app_commands.command(name="view_table", description="View the roulette table layout.")
    async def view_table(self, interaction: discord.Interaction):
        """Send the roulette table image to the #casino channel or the system channel."""
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        
        file = await self.get_table()

        if file == None:
            await interaction.response.send_message(content="I've lost my table! Yell at my dad. He can find it, I am sure!")
            return
                
        await interaction.response.send_message(file=file, content="Here is my roulette table:")

        # await interaction.response.send_message(f"Roulette table sent to {target_channel.mention}.", ephemeral=True)
        
    # --- Inside Bets ---

    @discord.app_commands.command(name="straight_bet", description="Bet on a single number (0 or 1–36). Payout: 35:1")
    async def straight_bet(self, interaction: discord.Interaction, number: int, amount: float):
        """Place a straight up bet on a single number."""
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return

        # Validate bet
        if number > 36 or number < 0:
            await interaction.response.send_message(f"Straight bet needs to be placed on a number 0-36. You picked {number}. Do better.")
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        
        bet_type = "Straight"
        bet_input = str(number)
        
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type=bet_type, bet_details=bet_input, bet_input=bet_input)
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="split_bet", description="Bet on two adjacent numbers. Payout: 17:1")
    async def split_bet(self, interaction: discord.Interaction, number1: int, number2: int, amount: float):
        """Place a split bet between two adjacent numbers."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        
        # Validate bet
        if number1 > 36 or number1 < 0 or number2 > 36 or number2 < 0:
            await interaction.response.send_message(f"Split bet needs to be placed on two numbers 0-36. You picked {number1} and {number2}. Do better.")
        are_adjacent = await self.are_adjacent_split(num1=number1, num2=number2)
        if not are_adjacent:
            await interaction.response.send_message(content="You need to pick two adjacent numbers. Try looking at my table with your eyes.", file = await self.get_table())
            return
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return

        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="split", bet_details=f"{number1},{number2}", bet_input=f"{number1},{number2}")
        
        bet_type = "Split"
        bet_input = f"{number1} & {number2}"
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="street_bet", description="Bet on a row of three numbers. Payout: 11:1")
    async def street_bet(self, interaction: discord.Interaction, row_start:int, amount:float):
        """Place a street bet (row of three numbers, e.g., 1-2-3)."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        
        valid_options = [1,4,7,10,13,16,19,22,25,28,31,34]
        start_of_row = await self.get_row_start(valid_options=valid_options, the_first_number_in_the_row=row_start)
        # Validate bet
        if start_of_row not in [1,4,7,10,13,16,19,22,25,28,31,34]:
            file = await self.get_table()
            await interaction.response.send_message(content=f"Street bet needs to be placed on the start of a row. You picked {start_of_row}. Do better. Look at the table!", file=file)
            return
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="street", bet_details=f"{start_of_row},{start_of_row+1},{start_of_row+2}", bet_input=start_of_row)
        
        bet_type = "Street"
        bet_input = f"the street starting with {start_of_row}"
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="corner_bet", description="Bet on four numbers in a square. You select the one on the bottom left of the square Payout: 8:1")
    async def corner_bet(self, interaction: discord.Interaction, bottom_left_of_corner:int, amount: float):
        """Place a corner bet on four numbers in a square."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        
        # Validate bet
        is_valid_corner = await self.is_valid_corner(top_left_of_corner = bottom_left_of_corner)
        if not is_valid_corner:
            file = await self.get_table()
            await interaction.response.send_message(content=f"Corner bet needs to be placed on four numbers in a square. You didn't do that. Do better. Look at the table!", file=file)
            return
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        
        bet_type = "Corner"
        bet_input = f"corner starting with {bottom_left_of_corner}"
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="corner", bet_details=f"{bottom_left_of_corner},{bottom_left_of_corner+1},{bottom_left_of_corner+3},{bottom_left_of_corner+4}", bet_input=bet_input)
        
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="sixline_bet", description="Bet on two adjacent rows (six numbers) Also called a Double Street. Payout: 5:1")
    async def sixline_bet(self, interaction: discord.Interaction, row_start: int, amount: float):
        """Place a six line bet (two adjacent rows, e.g., 1-6)."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        
        # Validate bet
        valid_options = [1,4,7,10,13,16,19,22,25,28,31,34]
        row_start = await self.get_row_start(the_first_number_in_the_row=row_start, valid_options=valid_options)
        is_valid_sixline = await self.is_valid_six_line(row_start=row_start)
        if not is_valid_sixline:
            file = await self.get_table()
            await interaction.response.send_message(content=f"Sixline bet needs to be placed on the left most number of the top of two rows. You didn't do that. Do better. Look at the table!", file=file)
            return
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="sixline", bet_details=f"{row_start},{row_start+1},{row_start+2},{row_start+3},{row_start+4},{row_start+5}", bet_input=row_start)

        bet_type = "Sixline"
        bet_input = f"rows starting with {row_start} & {row_start+3}"
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    # --- Outside Bets ---

    @discord.app_commands.command(name="color_bet", description="Bet on red or black. Payout: 1:1")
    @discord.app_commands.choices(choice=[
        discord.app_commands.Choice(name="Blacks", value="black"),
        discord.app_commands.Choice(name="Reds", value="red")
    ])
    async def color_bet(self, interaction: discord.Interaction, choice:discord.app_commands.Choice[str], amount: float):
        """Bet on color: 'red' or 'black'."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        color = choice.value
        # Validate bet
        if color.lower() != "red" and color.lower() != "black":
            await interaction.response.send_message(content=f"Color bet needs to be on Red or Black. You picked {color}. Do better. Learn colors, or at least how to spell. Yes black isn't a color. Bite me.")
        bet_details = ""
        # if red, sets bet_details to all the red numbers
        if color.lower() == "red":
            bet_details = f"1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36"
        # if black, sets bet_details to all the black numbers
        if color.lower() == "black":
            bet_details = f"2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35"
        
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="color", bet_details=f"{bet_details}", bet_input=color)                

        bet_type = "Color"
        bet_input = f"{color}"
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="oddeven_bet", description="Bet on odd or even. Payout: 1:1")
    @discord.app_commands.choices(choice=[
        discord.app_commands.Choice(name="Odds", value="odd"),
        discord.app_commands.Choice(name="Evens", value="even")
    ])
    async def oddeven_bet(self, interaction: discord.Interaction, choice:discord.app_commands.Choice[str], amount: float):
        """Bet on 'odd' or 'even'."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        parity = choice.value
        # Validate bet
        if parity.lower() != "odd" and parity.lower() != "even":
            await interaction.response.send_message(content=f"Parity bet needs to be odd or even. You picked {parity}. Do better. O-D-D or E-V-E-N. It isn't hard.")
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        bet_details = ""
        # if red, sets bet_details to all the red numbers
        if parity.lower() == "odd":
            bet_details = f"1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35"
        # if black, sets bet_details to all the black numbers
        if parity.lower() == "even":
            bet_details = f"2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36"
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="parity", bet_details=f"{bet_details}", bet_input=parity)                                    

        bet_type = "Parity"
        bet_input = f"{parity}s"
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="lowhigh_bet", description="Bet on low (1–18) or high (19–36). Payout: 1:1")
    @discord.app_commands.choices(choice=[
        discord.app_commands.Choice(name="Low", value="low"),
        discord.app_commands.Choice(name="High", value="high")
    ])
    async def lowhigh_bet(self, interaction: discord.Interaction, choice:discord.app_commands.Choice[str], amount: float):
        """Bet on 'low' (1–18) or 'high' (19–36)."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        selection = choice.value
        # Validate bet
        if selection.lower() != "low" and selection.lower() != "high":
            await interaction.response.send_message(content=f"Low or High bet needs to be.. low or high. You picked {selection}. Do better.")
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        bet_details = ""
        # if low, sets bet_details to all the low numbers
        if selection.lower() == "low":
            bet_details = f"1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18"
        # if high, sets bet_details to all the high numbers
        if selection.lower() == "high":
            bet_details = f"19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36"
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="lowhigh", bet_details=f"{bet_details}", bet_input=selection)                                    

        bet_type = "Low/High"
        bet_input = f"{selection}"
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="dozen_bet", description="Bet on a dozen (1:1–12, 2:13–24, 3:25–36). Payout: 2:1")
    @discord.app_commands.choices(choice=[
        discord.app_commands.Choice(name="1st", value=1),
        discord.app_commands.Choice(name="2nd", value=2),
        discord.app_commands.Choice(name="3rd", value=3)
    ])
    async def dozen_bet(self, interaction: discord.Interaction, choice:discord.app_commands.Choice[int], amount: float):
        """Bet on a dozen: 1 (1–12), 2 (13–24), or 3 (25–36)."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        dozen = choice.value
        # Validate bet
        if dozen < 1 or dozen > 37:
            await interaction.response.send_message(content=f"You need to select one of the dozens. 1, 2, or 3.")
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        bet_details = ""
        # Adjusts the value of dozen so that it is either 1, 2, or 3.
        if 13 > dozen > 3:
            dozen = 1
        if 25 > dozen > 12:
            dozen = 2
        if 37 > dozen > 24:
            dozen = 3 

        if dozen == 1:
            bet_details = "1,2,3,4,5,6,7,8,9,10,11,12"
        if dozen == 2:
            bet_details = "13,14,15,16,17,18,19,20,21,22,23,24"
        if dozen == 3:
            bet_details = "25,26,27,28,29,30,31,32,33,34,35,36"
        else: # Get fucked on this error
            bet_details = "0"
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="dozen", bet_details=f"{bet_details}", bet_input=dozen)                                             

        bet_type = "Dozen"
        bet_input = f"dozen #{dozen}"
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="column_bet", description="Bet on a column (1st, 2nd, 3rd). Payout: 2:1")
    @discord.app_commands.choices(choice=[
        discord.app_commands.Choice(name="1st", value=1),
        discord.app_commands.Choice(name="2nd", value=2),
        discord.app_commands.Choice(name="3rd", value=3)
    ])
    async def column_bet(self, interaction: discord.Interaction, choice:discord.app_commands.Choice[int], amount: float):
        """Bet on a column: 1 (1st), 2 (2nd), or 3 (3rd)."""

        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        user_id = interaction.user.id
        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=interaction.guild_id)

        # Check if the user is already in the bank
        if not self.database.is_user_in_guild_bank(user_id=user_id, guild_id=guild_id):
            await interaction.response.send_message(content=pickRandomRouletteNoAccountResponse(username=username))
            return        
        bank_account = self.database.get_user_bank_account_details(user_id, guild_id)
        if bank_account is None:
            await interaction.response.send_message(content="I broke myself trying to get your bank balance.")
            return
        # Does user have enough money for the bet
        if amount > bank_account[3]:
            await interaction.response.send_message(content=pickRandomRouletteBetTooBigResponse(username=username, amount=amount, currency_name=guild_currency[2], currency_symbol=guild_currency[3], bank_balance=bank_account[3]))
            return
        column = choice.value
        # Validate bet
        if  column < 0 or column > 3:
            await interaction.response.send_message(content=f"You need to select one of the columns. 1, 2, or 3.")
        if  0 >= amount:
            await interaction.response.send_message(content="No negative bets! Do I need to call a bouncer?")
            return
        bet_details = ""

        if column == 1:
            bet_details = "1,4,7,10,13,16,19,22,25,28,31,34"
        elif column == 2:
            bet_details = "2,5,8,11,14,17,20,23,26,29,32,35"
        elif column == 3:
            bet_details = "3,6,9,12,15,18,21,24,27,30,33,36"
        else: # Get fucked on this error
            bet_details = "0"
        self.database.place_bet_roulette(guild_id=interaction.guild_id, user_id=interaction.user.id, bet_amount=amount, bet_type="column", bet_details=f"{bet_details}", bet_input=column)          
        
        bet_type = "Column"
        bet_input = f"column #{column}"
        
        msg = pickRandomRouletteBetResponse(username=username, amount=amount,currency_name=guild_currency[2], currency_symbol=guild_currency[3], bet_type=bet_type, bet_details=bet_input )
        
        await interaction.response.send_message(content=msg)

    @discord.app_commands.command(name="view_live_bets", description="List all the current bets in this round of Roulette")
    async def view_live_bets(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        await interaction.response.defer()

        username = interaction.user.mention
        guild_id = interaction.guild_id

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        list_of_bets = self.database.get_placed_guild_roulette_bets(guild_id=guild_id)
        output = f"{username}, here are a list of all currently placed bets:"
        for index, bet in enumerate(list_of_bets):
            member = await interaction.guild.fetch_member(bet['user_id'])
            if member == None:
                print(f"Member not found: {bet['user_id']}")
                continue
            output+= f"\n{index+1}) {member.mention} has placed a {bet['type']} bet on {bet['input']} for {bet['amount']} {guild_currency[2]}s at {bet['datetime']} NST"

        await interaction.followup.send(content=output)

    @discord.app_commands.command(name="view_your_bet_history", description="List all the historic bets you have placed.")
    async def view_your_bet_history(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        await interaction.response.defer()

        username = interaction.user.mention
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        list_of_bets = self.database.get_historic_guild_user_roulette_bets(guild_id=guild_id, user_id=user_id)
        if len(list_of_bets) == 0:
            await interaction.followup.send(content=f"By Golly! {username}, you have never placed a bet!")
            return
        output = f"{username}, here are a list of all your previous bets:"
        for index, bet in enumerate(list_of_bets):            
            output+= f"\n{index+1}) {bet['datetime']} NST, you placed a {bet['type']} bet on {bet['input']} for {bet['amount']} {guild_currency[2]}s. It {bet['status']}."

        await interaction.followup.send(content=output)


    @discord.app_commands.command(name="view_your_active_bets", description="List all the current bets you have placed.")
    async def view_your_active_bets(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)

        await interaction.response.defer()

        username = interaction.user.mention
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        guild_currency = self.database.get_guild_currency_details(guild_id=guild_id)

        list_of_bets = self.database.get_placed_guild_user_roulette_bets(guild_id=guild_id, user_id=user_id)
        if len(list_of_bets) == 0:
            await interaction.followup.send(content=f"By Golly! {username}, you haven't placed a bet!")
            return
        output = f"{username}, here are a list of all your bets:"
        for index, bet in enumerate(list_of_bets):            
            output+= f"\n{index+1}) {bet['datetime']} NST, you placed a {bet['type']} bet on {bet['input']} for {bet['amount']} {guild_currency[2]}s."

        await interaction.followup.send(content=output)

    @discord.app_commands.command(name="view_roulette_info", description="Details about the Roulette game.")
    async def view_roulette_info(self, interaction: discord.Interaction):
        self.database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
        msg = "Roulette is a game of chance where players can place bets on various outcomes. The game features a spinning wheel with numbered slots, and players can bet on specific numbers, colors, or ranges of numbers using the /roulette bet type commands (ending in _bet). The payouts vary based on the type of bet placed." 
        msg+="\n\n**Commands:**"
        for command in self.commands:
            msg+= f"\n\n/roulette {command.name} - {command.description}"
        await interaction.response.send_message(content=msg)