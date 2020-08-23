#  Copyright (c) 2020. Rinze Douma

from random import shuffle, randrange


# Constants
NUM_PLAYERS = 2
CASH = 1000
BET = 100


class Card:
    """Class to hold characteristics of playing card."""

    suits = ["Spades", "Clubs", "Hearts", "Diamonds"]
    values = [None, "Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10,
              "Jack", "Queen", "King", "Ace"]

    def __init__(self, v, s):
        self.value = v
        self.suit = s

    def __str__(self):
        """String representation of playing card."""

        return f"{Card.values[self.value]} of {Card.suits[self.suit]}"


class Deck:
    def __init__(self, n=6):
        """A container to store n times 52 cards."""

        # Create n decks of cards consisting of 52 playing cards each.
        c = [Card(v, s) for v in range(2, 15) for s in range(4)]
        self.cards = c * n
        shuffle(self.cards)

        # A blank signals when the deck should be renewed.
        shoe_size = len(self.cards)
        b_start = int(shoe_size / (n * 2))
        b_end = int(shoe_size / n)
        self.blank = randrange(b_start, b_end)
        self.renew = False

    def deal(self):
        """Check if blank card reached and return a card."""

        if len(self.cards) < self.blank:
            self.renew = True

        return self.cards.pop()


class Player:
    def __init__(self, name, cash, bet):
        """Class to store name, cards drawn and score of Player."""

        self.hand = []
        self.score = 0
        self.name = name
        self.bet = bet
        self.cash = cash
        # Win status. 0: tie, 1: win, 2: loss, 3: natural
        self.win = 0

    def full_hand(self):
        """Return list of card values in player hand."""

        return [c.value for c in self.hand]


class Game:
    """Blackjack game. Play() to execute."""

    def __init__(self):
        """Initialize values for game."""

        self.cash = CASH
        self.shoe = Deck()
        self.dealer = Player("Dealer", 1000000, 0)
        self.players = []
        self.welcome()
        self.active = list(self.players)

    def welcome(self):
        """Display game rules and ask for player names."""

        print("\nWelcome to Ironhack Blackjack.")
        print(f"\nHouse rules:"
              f"\n- {NUM_PLAYERS} Players"
              f"\n- ${CASH} per player"
              f"\n- ${BET} bet"
              f"\n- Bets are final once collected"
              f"\n- Natural (blackjack on first hand) wins 1,5x of player bet"              
              f"\n- Whatever you do, don't go over 21"
              f"\n\n- Enjoy the game and best of luck!\n")
        name_q = "What's the name of player number {}? "

        for p in range(NUM_PLAYERS):
            name = validate_input(name_q.format(str(p + 1)))
            self.players.append(Player(name, CASH, BET))

    def deal_card(self, p, num=1):
        """Deal card. Twice if first round otherwise check score."""

        # Deal card
        for i in range(num):
            p.hand.append(self.check_ace(p, self.shoe.deal()))

        # Check score
        self.check_score(p)

        # In first round check hand after second card
        if num > 1:
            self.hand_details(p, mode="first")

    def check_ace(self, p, c):
        """If already an ace in player hand, second will count as 1."""

        if c.value == 14:
            c.value = 1 if 14 in p.full_hand() else 14

        return c

    def check_score(self, p):
        """Updates sum of cards in current hand."""

        # Recalculate player score
        p.score = 0
        for card in p.hand:
            if card.value == 14:
                p.score += 11
            elif card.value in [10, 11, 12, 13]:
                p.score += 10
            else:
                p.score += card.value

        # If earlier ace would cause >21, change it to a 1
        if p.score > 21 and 14 in p.full_hand():
            for c in p.hand:
                if c.value == 14:
                    c.value = 1
            p.score -= 10
        # If player went bust set score to 0
        elif p.score > 21:
            p.score = 0

    def hand_details(self, p, mode=""):
        """Print details of current hand."""

        hand = ", ".join([str(c) for c in p.hand])

        if p.name == "Dealer":
            if mode == "first":
                # In first round show only 1 round if not a Natural
                if p.score != 21:
                    text = f"The dealer's first card is a {str(p.hand[0])}."
                else:
                    text = f"Dealer has a natural: {hand}."
            elif mode == "stand":
                if p.score == 0:
                    text = f"Dealer went bust!"
                else:
                    text = f"Dealer stands at {p.score}."
            elif mode == "card":
                text = f"Dealer draws a {str(p.hand[-1])}."
            else:
                text = f"\nThe dealer currently has {p.score}: {hand}"

        # For players
        else:
            if mode == "first":
                if p.score == 21:
                    text = f"{p.name} drew a natural! {hand}."
                else:
                    text = f"{p.name}, you are at {p.score} with {hand}."
            elif mode == "card":
                text = f"Your card is a {str(p.hand[-1])}. "
                if p.score == 21:
                    text += f"\nBlackjack! Well done {p.name}."
                elif p.score == 0:
                    text += f"\nBusted! {p.name}'s bet goes to the house."
                else:
                    text += f"You're now at {p.score}."
            else:
                text = f"{p.name}, you're now at {p.score}."

        print(text)

    def update_bet(self, natural=False):
        """Calculate win/lose and update cash of every player."""

        for p in self.players:
            # In Natural mode only execute if this player or dealer has 21
            if natural and (self.dealer.score != 21 and p.score != 21):
                continue

            # Player loses
            if p.score == 0 or p.score < self.dealer.score:
                # Dealer wins
                p.cash -= p.bet
                self.dealer.cash += p.bet
                p.win = 2

            # Player wins
            elif p.score > self.dealer.score:
                p.win = 1
                bet = p.bet
                if natural:
                    # If player has natural but dealer doesn't then bet * 1,5
                    bet *= 1.5
                    p.win = 3
                    self.active.remove(p)
                p.cash += bet
                self.dealer.cash -= bet

    def place_bets(self):
        """Ask every player how much they want to bet."""

        prompt = "{}, how much would you like to bet?"
        for p in self.players:
            q = validate_input(prompt.format(p.name), int, min_=2, max_=500)
            p.bet = q

    def first_round(self):
        """Deal first hand to all players and dealer."""

        # Deal first cards
        print("\nOff we go. The first cards are dealt.\n")
        for p in self.players:
            self.deal_card(p, num=2)
        self.deal_card(self.dealer, num=2)

        # Update bets if any Natural drawn
        p_nat = [True if p.score == 21 else False for p in self.players]
        if any(p_nat + [self.dealer.score == 21]):
            self.update_bet(natural=True)

            # End round if dealer Natural. Player natural is done in update_bet
            if self.dealer.score == 21:
                self.end_or_continue()

    def play_round(self):
        """Second round deal one by one."""

        s_or_h = ["hit", "h", "y", "stand", "s", "n"]

        for p in self.active:
            print("")

            # Ask to deal a card to every active player
            while 0 < p.score < 21:
                self.hand_details(p)
                prompt = f"Do you want to stand (s) or hit (h)?"
                q = validate_input(prompt, str, options=s_or_h)
                if q.lower() in s_or_h[:3]:
                    self.deal_card(p)
                    self.hand_details(p, mode="card")
                else:
                    print(f"Good choice. Moving on.")
                    break

        d = self.dealer
        self.hand_details(d)

        # Dealer must stand when 17 or over
        while 0 < d.score < 17:
            self.deal_card(d)
            self.hand_details(d, mode="card")
        self.hand_details(d, mode="stand")

        # Finally update all bets
        self.update_bet()

    def game_stats(self):
        """Show score and cash of players ."""

        print("\n\nGame stats:")
        if self.dealer.score == 0:
            txt = f"\n{self.dealer.name} went bust."
        else:
            txt = f"Dealer has a score of {self.dealer.score}."
        print(txt)

        w_l = {0: "kept", 1: "won", 2: "lost", 3: "took 1,5x"}
        for p in self.players:
            if p.score == 0:
                txt = f"\n{p.name} went bust and lost their bet of {p.bet}."
            else:
                txt = "\n{} has a score of {} and {} their bet of {}.".format(
                    p.name, p.score, w_l[p.win], p.bet)
            print(txt)
            print(f"Current cash is {p.cash}")

    def end_or_continue(self):
        """Ask to end game or continue playing."""

        prompt = f"\nWould you like to continue playing?"
        y_n = ["yes", "y", "no", "n", ]
        q = validate_input(prompt, str, options=y_n)

        if q.lower() in y_n[:2]:
            self.reset_players()
            self.play()
        else:
            print("Thank you for playing Blackjack. Goodbye.")

    def reset_players(self):
        """Reset player hand and score before next round."""

        for p in (self.players + [self.dealer]):
            p.hand.clear()
            p.score = p.win = 0

        self.active = list(self.players)

    def play(self):
        """Run the game and clean up after."""

        self.place_bets()
        self.first_round()
        self.play_round()
        self.game_stats()

        # If blank card has been reached then renew the deck
        if self.shoe.renew:
            self.shoe = Deck()

        self.end_or_continue()


def validate_input(prompt, type_=None, min_=None, max_=None, options=None):
    """ Request user input and clean it before return.
    :param prompt: Question to ask user.
    :param type_: Type of value asked. str, int, float.
    :param min_: Minimum length of str of lower value of int.
    :param max_: Maximum length of str of upper value of int.
    :param options: List of options allowed
    :return: str, int or float.
    
    adapted from https://stackoverflow.com/questions/23294658/
        asking-the-user-for-input-until-they-give-a-valid-response
    """

    if (min_ is not None
            and max_ is not None
            and max_ < min_):
        raise ValueError("min_ must be less than or equal to max_.")
    while True:
        ui = input(prompt)
        if type_ is not None:
            try:
                ui = type_(ui)
            except ValueError:
                print(f"Input type must be {type_.__name__}")
                continue
        if isinstance(ui, str):
            ui_num = len(ui)
        else:
            ui_num = ui
        if max_ is not None and ui_num > max_:
            print(f"Input must be less than or equal to {max_}.")
        elif min_ is not None and ui_num < min_:
            print(f"Input must be more than or equal to {min_}.")
        elif options is not None and ui.lower() not in options:
            print("Input must be one of the following: " + ", ".join(options))
        else:
            return ui


if __name__ == '__main__':
    """Load game if script executed directly."""

    game = Game()
    game.play()
