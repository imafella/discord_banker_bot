
class bank_account:
    def __init__(self, id:int, guild_id:int, account_number:int, balance:float=0.0, bot_usage:int=0, archived:bool=False):
        self.id = id
        self.guild_id = guild_id
        self.account_number = account_number
        self.balance = balance
        self.bot_usage = bot_usage
        self.archived = archived

    def get_balance(self) -> str:
        return self.get_formated_bank_balance(self.balance)
    
    def get_formated_bank_balance(self,bank_balance: float) -> str:
        return f"{bank_balance:,.2f}"

    def __str__(self):
        return f"Account({self.account_number}, {self.account_holder}, Balance: {self.balance})"
        
    def to_json(self) -> dict:
        '''
        Returns the account as a dict.
        I dont think this will be called.
        '''
        return {"id":self.id, "guild_id":self.guild_id, "account_number":self.account_number, "balance":self.balance, "bot_usage":self.bot_usage, "archived":self.archived}