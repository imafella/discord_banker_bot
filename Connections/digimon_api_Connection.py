import os
import requests

class digimon_api:
    def __init__(self):
        self.base_url = os.getenv("digimon_base_url", "")

    async def get_card(self, card_id:str=None, name:str=None, color:str=None, type:str=None, pack:str=None):
        """Fetch a Digimon card by its ID or name."""
        url = self.base_url
        limit = 100
        # Build the URL based on the provided parameters
        if card_id is not None:
            url+=f"&card={card_id}"
        if name is not None:
            url+=f"&n={name}"
        if type is not None and type.lower() in ["digimon", "option", "tamer", "digi-egg"]:
            url+=f"&type={type.lower()}"
        if color is not None and color.lower() in ["black", "blue", "green", "purple", "red", "white", "yellow", "colorless"]:
            url+=f"&color={color.lower()}"
        if pack is not None:    
            url+=f"&pack={pack}"
        
        url+=f"&limit={limit}"

        print(f"Fetching Digimon card data from URL: {url}")

        # Make the request to the Digimon API
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                return data
        else:
            print(f"Error fetching data from Digimon API: {response.status_code} - {response.text}")
            return []
        