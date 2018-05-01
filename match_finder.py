import os
import time
from datetime import datetime
import logging
import threading
import tbapy
from sortedcontainers import SortedList

# Define variables 
logger = logging.getLogger('FRCMatchFinderLogger')
tba = tbapy.TBA('9YP15wdwpFPjJri1tGj6BGwWCkHxNVaM9xKmv2Z0aYikXOXOKtOKol9gD5yntLJ5')
teams = []
matches = SortedList()
cond = threading.Condition()

# Range in seconds to check current matches within
MATCH_RANGE = 150

# Range in seconds to check upcoming matches within
UPCOMING_RANGE = 3600

# file for default teams to find
TEAMS_FILE = 'teams.txt'

def main():
    try:
        # read in the teams from textfile
        with open(TEAMS_FILE) as f:
            lines = f.readlines()
            teams.extend([int(line.strip()) for line in lines])

    # will be thrown if teams file not found
    except IOError:
        print("Could not find teams.txt file!")
        return

    # will be thrown if characters present in file
    except ValueError:
        print("Textfile should only contain team numbers!")
        return

    # exit if no teams
    # if not teams:
    #     print("Please add team numbers to the teams.txt file!")
    #     return
    # matches.add(Match('1', '2018esc', 'qf', 1524285900, [5518]))

    # Start the match sync thread
    sync_thread = SyncThread()
    logger.info("Starting thread")
    sync_thread.start()

    # display matches according to time
    cond.acquire()
    while True:
        # wait until update is available
        logger.info("Waiting")
        cond.wait()

        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        current = []
        upcoming = []
        now = time.time()

        # TODO get appropriate matches
        for match in matches:
            logger.info("match: " + str(match))
            # check for current matches
            if now >= match.time and now < (match.time + MATCH_RANGE):
                current.append(match)
                matches.remove(match)
            # check for upcoming matches
            elif now < match.time and match.time <= (now + UPCOMING_RANGE):
                upcoming.append(match)

        # exit if no matches left
        if not (current and upcoming):
            print("Your teams do not have any upcoming matches!")
            continue

        # Print current matches to user
        print("Current Matches:")
        for match in current:
            print(match)

        # Print upcoming matches to user
        print("\nUpcoming Matches:")
        for match in upcoming:
            print(match)

    # clean up code
    cond.release()
    thread.end()

class SyncThread():

    # Constant to execute thread every hour
    SYNC_INTERVAL = 3600

    def __init__(self):
        self.timer = threading.Timer(0, self.run)

    def run(self):
        # define needed variables
        year = datetime.now().year
        today = time.time()

        # sync matches for teams
        for team in teams:
            team_events = tba.team_events(team, year, keys=True)

            # iterate over event keys
            for event in team_events:
                team_matches = tba.team_matches(team, event, simple=True)

                # check if match is yet to be played
                for match in team_matches:
                    if (match.predicted_time >= today):
                        m = Match(match.match_number, match.event_key, match.comp_level, \
                            match.predicted_time, set([team]))

                        # check if match already exists
                        cond.acquire()
                        if not m in matches:
                            matches.add(m)
                        else:
                            m = matches[matches.index(m)]
                            m.add_team(team)
                        cond.notify()
                        cond.release()

        # run this thread again every hour
        self.timer = threading.Timer(self.SYNC_INTERVAL, self.run)
        self.timer.start()

    def start(self):
        self.timer.start()

    def end(self):
        self.timer.cancel()
        self.timer.join()
        self.join()

class Watcher:

    def __init__(self):
        # TODO init

class Match:

    def __init__(self, number, event, match_type, time, teams):
        self.number = number
        self.event = event
        self.type = match_type
        self.time = time
        self.teams = teams

    def add_team(self, team):
        self.teams.add(team)

    @staticmethod
    def translate_type(type):
        if type == "qm":
            return 0
        elif type == "qf":
            return 1
        elif type == "sf":
            return 2
        elif type == "f":
            return 3

    def __str__(self):
        return datetime.fromtimestamp(self.time).strftime('%H:%M:%S %m-%d-%Y') + \
            f' --- {self.event} {self.type} Match {self.number} with {self.teams} playing'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.event == other.event and self.type == other.type \
            and self.number == other.number

    def __lt__(self, other):
        # if self.event == other.event:
        #     if self.type == other.type:
        #         return self.number < other
        #     else:
        #         return translate_type(self.type) < translate_type(other.type)
        # else:
        return self.time < other.time

    def __le__(self, other):
        return self.__eq__ or self.__lt__(other)

    def __gt__(self, other):
        return self.time > other.time

    def __ge__(self, other):
        return self.__eq__ or self.__gt__(other)

# check if main thread
if __name__ == '__main__':
    # configure logging
    log_datefmt = "%H:%M:%S"
    log_format = "%(asctime)s:%(msecs)03d %(levelname)-8s: %(name)-20s: %(message)s"
    logging.basicConfig(level=logging.DEBUG, datefmt=log_datefmt, format=log_format)

    logger.info("Running main")
    main()