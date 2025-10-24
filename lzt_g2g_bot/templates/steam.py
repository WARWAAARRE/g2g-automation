def create_steam_offer(account_data: dict, markup_percent: int) -> dict:
    """Создает шаблон для Steam аккаунта"""
    price = account_data.get('price', 0)
    final_price = round(price * (1 + markup_percent / 100), 2)
    
    # Формируем название по вашему шаблону
    title = "50 games / 15 Level / CS2 Prime - 4.17h (Inv: €52.49), Rust - 2.23h (Inv: €0.10), Don't Starve - 0.63h"
    
    # Формируем описание по вашему шаблону  
    description = """It's Available, Click 'view more' to see details. Please don't hesitate to contact us, If you have any question.

Steam Level: 15
Game Count: 50
Account Created: 08/03/2023

Games:
CS2 Prime - 4.17h (Inventory: €52.49)
Rust - 2.23h (Inventory: €0.10)
Don't Starve - 0.63h
Unturned - 0.35h
SLUDGE LIFE - 0.10h
Undertale - 0.03h
Geometry Dash - 0.02h
Portal - 0.00h
Portal 2 - 0.00h
LIMBO - 0.00h
Path of Exile - 0.00h
INSIDE - 0.00h
Don't Starve Together - 0.00h
Wallpaper Engine - 0.00h
Sally Face - Episode One - 0.00h
SCP: Secret Laboratory - 0.00h
SpongeBob SquarePants: Battle for Bikini Bottom - Rehydrated - 0.00h
Destiny 2 - 0.00h
RUSSIAPHOBIA - 0.00h
House of Detention - 0.00h
My Singing Monsters - 0.00h
Goose Goose Duck - 0.00h
Stumble Guys - 0.00h
Fear Therapy - 0.00h
Summoners War: Chronicles - 0.00h
DR LIVESEY ROM AND DEATH EDITION - 0.00h

Counter-Strike 2 Stats:
- Profile Rank: 3
- Wingman Rank ID: Unknown
- Wins: Unknown
- Medals: None

For more detailed information about the account, feel free to contact me!"""
    
    return {
        'title': title,
        'description': description,
        'price': final_price,
        'category': 'Steam',
        'game': 'Steam',
        'offer_data': {
            'title': title,
            'description': description,
            'price': final_price,
            'stock': 1,
            'auto_accept': True,
            'instant_delivery': True
        }
    }