import sys
import signal
from collections import Counter

from server import DiceServer
from client import DiceClient


initial_balance = float(sys.argv[1])
minimum_balance, maximum_balance = 0, 999999999
if len(sys.argv) > 2:
    minimum_balance = float(sys.argv[2])
    maximum_balance = float(sys.argv[3])

server = DiceServer(initial_balance)
client = DiceClient(server)


def exit_handler(signum, frame):
    client.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

# client.start(minimum_balance, maximum_balance)

# statistic approach
results = []
no_games = 1000
cur_game = 0
while (cur_game < no_games):
    cur_game += 1
    # print "Current round = %d" % cur_game
    server.set_balance(initial_balance)
    results.append(client.start(minimum_balance, maximum_balance))
total_rounds = sum([result['rounds'] for result in results])
min_rounds = min([result['rounds'] for result in results])
max_rounds = max([result['rounds'] for result in results])
avg_rounds = float(total_rounds) / no_games
avg_streak = float(sum(result['longest_streak']
                       for result in results)) / no_games

avg_peak_balance = float(sum(result['peak_balance']
                             for result in results)) / no_games
no_reach_max = sum([result['reach_max'] for result in results])
balances = [result['balance'] for result in results]
print "Total rounds = %s" % total_rounds
print "Min rounds = %s" % min_rounds
print "Max rounds = %s" % max_rounds
print "Average rounds = %f" % avg_rounds
print "Average Streak = %f" % avg_streak
print "Average Peak balance = %f" % avg_peak_balance
print "Number of Success = %s" % no_reach_max
print 'Balances = %s' % Counter(balances)
print '-' * 80
print 'Success Rate: %.2f%%' % (float(no_reach_max) / no_games * 100)
