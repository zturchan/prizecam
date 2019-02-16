from pokemontcgsdk import Card
from pokemontcgsdk import Type

def unique_name(card):
    # If card is a Pokemon, append the set name in parens
    if (is_pokemon(card)):
        return card.name + ' (%s)' % card.set
    else:
        return card.name

def is_pokemon(card):
    return card.supertype == 'Pokémon'