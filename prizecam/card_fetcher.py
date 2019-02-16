from pokemontcgsdk import Card
from pokemontcgsdk import Set
from card_helper import is_pokemon

def fetch(is_standard):
    if (is_standard):
        return fetch_standard()
    return fetch_expanded()

def remove_duplicate_card_names(cards):
    seen_card_names = []
    distinct_cards = []
    for card in cards:
        if (is_pokemon(card)):
            if not card.name + card.set_code in seen_card_names:
                seen_card_names.append(card.name + card.set_code)
                distinct_cards.append(card)
        else:
            if not card.name in seen_card_names:
                seen_card_names.append(card.name)
                distinct_cards.append(card)
    return distinct_cards

def fetch_standard():
    sets = Set.where(standardLegal=True)
    return get_cards_from_sets(sets)

def fetch_expanded():
    sets = Set.where(expandedLegal=True)
    return get_cards_from_sets(sets)

def get_cards_from_sets(sets):
    cards = []
    for set in sets:
        print(set.name)
        set_cards = Card.where(set=set.name)
        for card in set_cards:
            cards.append(card)
    return remove_duplicate_card_names(cards)


