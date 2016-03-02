import random


class DiceServer(object):
    def __init__(self, initial_balance):
        self.balance = float(initial_balance)

    def _generate_random_number(self):
        return random.randint(0, 9999)

    def _get_roll_result(self, mode, rolled_number):
        if mode:
            return rolled_number < 4875
        else:
            return rolled_number > 5124

    def roll(self, mode, bet_amount):
        if bet_amount > self.balance:
            raise Exception('Balance not enough')

        rolled_number = self._generate_random_number()
        result = self._get_roll_result(mode, rolled_number)
        if result:
            self.balance += bet_amount
        else:
            self.balance -= bet_amount
        return result
