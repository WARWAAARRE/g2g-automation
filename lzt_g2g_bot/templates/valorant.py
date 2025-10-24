def create_valorant_offer(account_data: dict, markup_percent: int) -> dict:
    """Создает шаблон для Valorant аккаунта"""
    price = account_data.get('price', 0)
    final_price = round(price * (1 + markup_percent / 100), 2)
    
    title = "KR / Silver 2 / Skins: 17 / Agents: 21 / Inv Value: 12225VP / Nocturnum Phantom / Sovereign Sword / Glitchpop Operator"
    
    description = """It's Available, Click 'view more' to see details. Please don't hesitate to contact us, If you have any question.

Valorant Account Details:
Region: KR
Level: 236
Rank: Silver 2
Agents Unlocked: 21
Skins Owned: 17
Nocturnum Phantom,Sovereign Sword,Glitchpop Operator,Forsaken Vandal,Minima Phantom,Wasteland Spectre,Transition Shorty,Sandswept Sheriff,Bubble Pop Classic,Fiber Optic Ghost,Digihex Ghost,Immortalized Sheriff,Soul Silencer Ghost,RagnaRocker Frenzy,Mythmaker Sheriff,Starlit Odyssey Ghost,9 Lives Classic
Inventory Value: 12225
Wallet VP: 197

For more detailed information about the account, feel free to contact me!"""
    
    return {
        'title': title,
        'description': description,
        'price': final_price,
        'category': 'Valorant',
        'game': 'Valorant',
        'offer_data': {
            'title': title,
            'description': description,
            'price': final_price,
            'stock': 1,
            'auto_accept': True,
            'instant_delivery': True,
            'category_id': 'valorant',  # ID категории G2G
            'game_id': 'valorant'       # ID игры G2G
        }
    }