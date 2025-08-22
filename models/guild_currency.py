
class GuildCurrency:
    def __init__(self, id:int, guild_id:int, currency_symbol:str="$", currency_name:str="DolleryDoos"):
        self.id = id
        self.guild_id = guild_id
        self.symbol = currency_symbol
        self.name = currency_name

class GuildCurrencyChangeCosts:
    def __init__(self, id:int, guild_id:int, name_cost:float=1.00, symbol_cost:float=1.00):
        self.id = id
        self.guild_id = guild_id
        self.name_cost = name_cost
        self.symbol_cost = symbol_cost