import random
from datetime import datetime

import utils


class DiceClient(object):
    DEBUG = False
    MIN_BET = 0.01
    SAFE_MODE = False
    LONGEST_ALLOWED_STREAK = 15
    DANGER_STREAK = 10000000
    THRESHOLD_JUMP = 8
    ALL_IN = False

    def __init__(self, server):
        self.server = server
        self.roll_mode = False

    def start(self, minimum_balance, maximum_balance):
        self.minimum_balance = minimum_balance
        self.maximum_balance = maximum_balance
        self.balance = self.current_balance
        self.initial_balance = self.peak_balance = self.balance
        self.will_stop = False

        self.start_time = datetime.now()
        self.last_streak = self.streak = self.longest_streak = 0
        self.last_bet = 0
        self.round_no = -1
        self.switch_countdown = 0
        self.win_round = -1
        self.peak_ratio = 0

        processor = self._process
        self.result = {}
        while not self.will_stop:
            processor()
        return self.result

    def _process(self):
        new_balance = self.current_balance
        is_win = new_balance >= self.balance
        new_streak = 0 if is_win else self.streak + 1

        self.round_no += 1
        self.win_round += 1 if is_win else 0

        self.last_streak = self.streak if is_win else self.last_streak

        if is_win:
            bet_amount = self.get_initial_bet(new_balance)
        else:
            if new_streak > self.DANGER_STREAK:
                bet_amount = self.get_initial_bet(new_balance)
                new_streak = 0
            else:
                bet_amount = self.last_bet * 2
        bet_amount = min(new_balance, bet_amount)

        if (new_balance >= self.maximum_balance) or (
                new_balance - bet_amount <= self.minimum_balance) or (
                new_balance == 0):  # To handle all in strategy
            self.will_stop = True
        elif is_win:
            if self.switch_countdown:
                self.switch_countdown -= 1
            else:
                self.switch_countdown = random.randint(0, 9) + 1
                self.roll_mode = not self.roll_mode

        if self.DEBUG:
            print 'Round %s | %s ::: Balance = %s | Bet = %s | Ratio = %.2f%% | Last = %s' % (  # NOQA
                str(self.round_no).rjust(6),
                ('WIN' if is_win else 'LOST').ljust(4),
                new_balance, bet_amount, self.win_ratio * 100,
                self.last_streak)

        if self.round_no > 100:
            self.peak_ratio = max(self.peak_ratio, self.win_ratio)

        self.streak = new_streak
        self.longest_streak = max(self.streak, self.longest_streak)
        self.last_bet = bet_amount
        self.balance = new_balance
        self.peak_balance = max(self.peak_balance, self.balance)

        if self.will_stop:
            self.stop()
        else:
            self.submit_bet(self.roll_mode, bet_amount)

    @property
    def win_ratio(self):
        if self.round_no:
            return float(self.win_round) / (self.round_no)
        return 0

    def stop(self):
        # self.print_statistics()
        self.result['rounds'] = self.round_no
        self.result['longest_streak'] = self.longest_streak
        self.result['peak_balance'] = self.peak_balance
        self.result['reach_max'] = 1 if (
            self.current_balance >= self.maximum_balance) else 0

    def print_statistics(self):
        profit = self.balance - self.initial_balance
        time_delta = datetime.now() - self.start_time
        running_time = time_delta.total_seconds()
        print '-' * 80
        print 'Rounds = %s' % self.round_no
        # print 'Time   = %.2f seconds' % running_time
        print 'Streak = %s' % self.longest_streak
        print 'Ratio^ = %.2f%%' % (self.peak_ratio * 100)
        print
        print 'Peak   = %.2f' % self.peak_balance
        print 'Begin  = %.2f' % self.initial_balance
        print 'End    = %.2f' % self.balance
        print 'Profit = %s (%.4f%%)' % (
            profit, profit / self.initial_balance * 100)
        print '    per round  = %s (%.8f%%)' % (
            profit / self.round_no,
            profit / self.round_no / self.initial_balance * 100)
        # print '    per second = %s' % (profit / running_time)
        print '-' * 80

    def submit_bet(self, mode, bet_amount):
        self.server.roll(mode, bet_amount)

    @property
    def current_balance(self):
        return self.server.balance

    def get_initial_bet(self, balance):
        accm = 2 ** self.LONGEST_ALLOWED_STREAK - 1
        bet = max(balance / accm, self.MIN_BET)
        if not self.SAFE_MODE:
            bet = min(balance, bet * (self.last_streak + 1))
        if (self.ALL_IN):
            bet = self.current_balance
        return utils.to_2(bet)
