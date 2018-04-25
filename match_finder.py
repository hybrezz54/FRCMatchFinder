import os
import time
from datetime import datetime
import threading
import keyboard
import tbapy
# from sortedcontainers import SortedList

# Define variables 
tba = tbapy.TBA('9YP15wdwpFPjJri1tGj6BGwWCkHxNVaM9xKmv2Z0aYikXOXOKtOKol9gD5yntLJ5')
teams = []
matches = []

# Range in seconds to check current matches within
MATCH_RANGE = 150

# Range in seconds to check upcoming matches within
UPCOMING_RANGE = 600

# file for default teams to find
teams_file = 'teams.txt'

def main():
    try:
        # read in the teams from textfile
        with open(teams_file) as f:
            lines = f.readlines()
            teams = [int(line.strip()) for line in lines]

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

    matches.append(Match('1', '2018esc', 'qf', 1524285900, [5518]))

    # Start the match sync thread
    thread = SyncThread()
    thread.start()

    # display matches according to time
    while True:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        current = [matches[0]]
        upcoming = [matches[0]]
        now = time.time()

        # TODO get appropriate matches
        with self.lock:
            for match in matches:
                # check for current matches
                if now >= match.time and now < (match.time + self.MATCH_RANGE):
                    current.append(match)
                    matches.remove(match)
                # check for upcoming matches
                elif now < match.time and match.time <= (now + self.UPCOMING_RANGE):
                    upcoming.append(match)

        # exit if no matches left
        if not (current and upcoming):
            print("Your teams do not have any upcoming matches!")
            break

        # Print current matches to user
        print("Current Matches:")
        for match in current:
            print(match)

        # Print upcoming matches to user
        print("\nUpcoming Matches:")
        for match in upcoming:
            print(match)

    # End the sync thread
    thread.end()

class SyncThread(threading.Thread):

    # Constant to execute thread every hour
    SYNC_INTERVAL = 3600

    def __init__(self):
        threading.Thread.__init__(self)
        self.threadID = 1
        self.name = 'SyncThread'
        self.counter = 1
        self.timer = threading.Timer(self.SYNC_INTERVAL, self.run)

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
                for match in reversed(team_matches):
                    if (match.predicted_time > today):
                        m = Match(match.match_number, match.event_key, match.comp_level, \
                            match.predicted_time, set(team))

                        # check if match already exists
                        if not contains(matches, lambda x: x == m):
                            matches.append(m)
                        else:
                            m = get(matches, m)
                            m.addTeam(team)               

        # run this thread again every hour
        self.timer.start()

    def end(self):
        self.timer.cancel()
        self.join()

    def contains(list, filter):
        for x in list:
            if filter(x):
                return True
        return False

    def get(list, item):
        for x in list:
            if x == item:
                return x
        return item

class Match:

    def __init__(self, number, event, match_type, time, teams):
        self.number = number
        self.event = event
        self.type = match_type
        self.time = time
        self.teams = teams

    def addTeam(self, team):
        self.teams.add(team)

    def __str__(self):
        return datetime.fromtimestamp(self.time).strftime('%H:%M:%S %m-%d-%Y') + \
            f' --- {self.event} {self.type} Match {self.number} with {self.teams} playing'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.event == other.event and self.type == other.type \
            and self.number == other.number

# check if main thread
if __name__ == '__main__':
    main()