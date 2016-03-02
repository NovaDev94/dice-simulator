import sys
import signal

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

client.start(minimum_balance, maximum_balance)
