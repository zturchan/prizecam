import tkinter as tk
import base64
import requests
import shutil
import card_fetcher
import card_helper
import re
from datetime import datetime as dt
from PIL import ImageTk, Image
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from urllib.request import urlopen
from autocomplete import Autocomplete
from enum import Enum

class PrizeCardState(Enum):
    UNKNOWN = 1
    KNOWN = 2
    TAKEN = 3

class Format(Enum):
    STANDARD = 1
    EXPANDED = 2

class PrizeCard():
    def __init__(self, button):
        self.card = None
        self.state = PrizeCardState.UNKNOWN
        self.button = button

    def set_card(self, card):
        self.card = card
        self.state = PrizeCardState.KNOWN

    def has_card(self):
        return self.state == PrizeCardState.KNOWN

def getphoto(url, cardid):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open("%s.png" % cardid, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    img = Image.open("%s.png" % cardid)
    p = ImageTk.PhotoImage(img)
    return p

def get_back_photo():
    return ImageTk.PhotoImage(Image.open("back.png"));

def fetch_alternate_version_of_card(card):
    # Subtype filter needed for cases like special darkness energy
    versions_of_card = Card.where(name=card.name, subtype=card.subtype)

    for version in versions_of_card:
        try:
            print(version.id)
            version_photo = getphoto(version.image_url, version.id)
            break
        except AttributeError:
            # Happens due to a bug in pillow 5.4.1 where some cards with EXIF data cause pillow to barf
            # In that case, try and find an alternate card image
            # This mostly occurs on certain secret rares, esp from Ultra Prism
            pass
    if (version_photo):
        return version_photo
    return get_back_photo()

def get_taken_photo():
    return ImageTk.PhotoImage(Image.open("taken.png"));

def createimg(img, left_offset, top_offset):
    return cv.create_image(left_offset, top_offset, image=img, anchor='nw')

def reset_cards():
    for card in state.PrizeCards:
        card.state = PrizeCardState.UNKNOWN
    redraw_cards()

def redraw_cards():
    if len(state.PrizeCards) == 6:
        for row in range(1, 4):
            for col in range(2):
                prize = state.PrizeCards[(row - 1) * 2 + col ]
                if(prize.has_card()):
                    try:
                        photo = getphoto(prize.card.image_url, prize.card.id)
                    except AttributeError:
                        # Happens due to a bug in pillow 5.4.1 where some cards with EXIF data cause pillow to barf
                        # In that case, try and find an alternate card image
                        # This mostly occurs on certain secret rares, esp from Ultra Prism
                        photo = fetch_alternate_version_of_card(prize.card)
                elif(prize.state == PrizeCardState.UNKNOWN):
                    photo = state.backphoto
                else:
                    photo = state.takenphoto
                prize.button.configure(image=photo)
                prize.button.image = photo
                prize.button.grid(row=row, column=col)

def get_card_from_dropdown_selection(dropdown_text):
    # dropdown_text will have the form Card Name (Set Name) for pokemon
    # and just Card Name for non pokemon
    parts = dropdown_text.split(' (')
    card_candidates = []
    if (len(parts) == 1):
        card_candidates = [c for c in state.cards() if c.name==parts[0]]
    else:
        card_candidates = [c for c in state.cards() if c.name==parts[0] and c.set == parts[1][0:-1]]
    return card_candidates[0]

def selected (card):
    # Find the first prize slot that is unknown
    prize_slot = None
    for prize in state.PrizeCards:
        if prize.state == PrizeCardState.UNKNOWN:
            prize_slot = prize
            break
    if prize_slot is not None:
        selected_card_obj = get_card_from_dropdown_selection(card.get())
        prize.set_card(selected_card_obj)
    redraw_cards()

def prize_click(row, col):
    prize = state.PrizeCards[(row - 1) * 2 + col]
    if (prize.state == PrizeCardState.UNKNOWN or prize.state == PrizeCardState.KNOWN):
        prize.state = PrizeCardState.TAKEN
    elif(prize.state == PrizeCardState.TAKEN):
        prize.state = PrizeCardState.UNKNOWN
    redraw_cards()

class State:
    def __init__(self, cards):
        self.PrizeCards = []
        self.format = Format.STANDARD
        self.standard_cards = cards
        self.expanded_cards = []

    def cards(self):
        if (self.format == Format.STANDARD):
            return self.standard_cards
        return self.expanded_cards

    def to_standard(self):
        self.format = Format.STANDARD
        self.entry = Autocomplete(self.card_names(), selected, root, width = 40)
        self.entry.grid(row=0, column=0)

    def to_expanded(self):
        if not self.expanded_cards:
            self.expanded_cards = card_fetcher.fetch(False)
        self.format = Format.EXPANDED
        self.entry = Autocomplete(self.card_names(), selected, root, width = 40)
        self.entry.grid(row=0, column=0)

    def card_names(self):
        return [card_helper.unique_name(card) for card in self.cards()]


def update_cards(is_standard):
    if(is_standard):
        state.to_standard()
    else:
        state.to_expanded()

def create_menu(root):
    menubar = tk.Menu(root)

    format_menu = tk.Menu(menubar, tearoff=0)
    format_menu.add_command(label="Standard", command=lambda : update_cards(True))
    format_menu.add_command(label="Expanded", command=lambda : update_cards(False))
    menubar.add_cascade(label="Format", menu=format_menu)

    root.config(menu=menubar)

if __name__ == "__main__":

        cards = card_fetcher.fetch(True)
        state = State(sorted(cards, key=lambda x: x.name))
        photo_width = 245
        photo_height = 342
        top_padding = 10
        left_padding = 10
        root = tk.Tk()
        root.title("Pokemon TCG Prize Cam")

        create_menu(root)
        # a little more than width and height of image
        w = (photo_width + left_padding) * 2
        h = (photo_height + top_padding) * 3 + 40
        x = 80
        y = 100
        # use width x height + x_offset + y_offset (no spaces!)
        root.geometry("%dx%d+%d+%d" % (w, h, x, y))

        start_time = dt.now()

        state.entry = Autocomplete(state.card_names(), selected, root, width = 40)
        state.entry.grid(row=0, column=0)

        button = tk.Button(root, text = "Reset Prizes", command = reset_cards, width=35)
        button.grid(row=0, column=1)

        state.backphoto = get_back_photo()
        state.takenphoto = get_taken_photo()
        for row in range(1, 4):
            for col in range(2):
                pc = PrizeCard(tk.Button(root, image=state.backphoto))
                pc.button.configure(command=lambda r = row, c = col: prize_click(r, c))
                state.PrizeCards.append(pc)
        redraw_cards()
        root.resizable(False, False)
        root.mainloop()

