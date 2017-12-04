# python project fall 2017
# scrape/parsing
# initial

from lxml import html
import time
import urllib.request
import requests

def printTeams():
    print("Teams to choose from:\n")
    f = open("teams.txt", 'r')
    for team in f:
        team = team.strip("\n")
        print(str(team))
    print("\n")
    return True

# scrapes and parses team data
def getTeams(team1, team2):
    url = "https://basketball.realgm.com/nba/teams/"
    end_url = "/Stats/2018/Averages"

    list = []
    f = open("urls.txt", 'r')

    # load teams into list
    for urls in f:
        urls = urls.strip("\n")
        list.append(url + urls + end_url)

    print("Selected Teams (by index): \n")
    print("Comparing: " + str(team1) + " vs. " + str(team2))
    print(list[team1])
    print(list[team2])

    # both lists are parsed with values
    t1 = scrapeUrl(list[team1])
    t2 = scrapeUrl(list[team2])

    print("\nList Data Team 1:")
    print("Player Stats: " + str(t1[0]))
    print("Team Stats: " + str(t1[1]))
    print("Previous Games (Splits): " + str(t1[2]))

    print("\nList Data Team 2:")
    print("Player Stats: " + str(t2[0]))
    print("Team Stats: " + str(t2[1]))
    print("Previous Games (Splits): " + str(t2[2]))

    # calling compareTeams to compare team data and determine winner
    compareTeams(t1, t2)

def parseTeamData(data, iter, max, index):
    team_stats = []
    # stats: each player needs to be in their own list
    for j in range(1, iter+1):
        stat_list = []
        for i in range(1, max):
            test_entry = data.xpath("//*/tbody/tr[" + str(j) + "]/td[" + str(i) + "]/text()")
            # test to make sure the HTML does not have a broken value
            #print("test entry" + str(test_entry))

            if test_entry:
                # for team stats
                # adjustment
                size = len(test_entry)
                # if length is 2, we want index

                if index is 1 and i is 2:
                    pstat = test_entry[0]
                elif index is 2 and size is not 3:
                    #print("test entry" + str(test_entry))
                    pstat = test_entry[size-1]
                    #print("Select = " + pstat)
                else:
                    #print("else test entry" + str(test_entry))
                    pstat = test_entry[index]

            else:
                """ pad with NULL to indicate broken HTML value
                    we can change this to a different value if needed
                """
                pstat = 'NULL'

            stat_list.append(pstat)

        team_stats.append(stat_list)

    return team_stats

# scrapes urls for each team and parses them into respective lists
# lists are then passed into compareTeams() in order to apply comparison algorithm
def scrapeUrl(url):
    try:
        # NOTE: Returning 0 for success, 1 for failure
        session_requests = requests.session()
        r = session_requests.get(url, headers=dict(referer=url))

        # status code 200 indicates html page access = successful
        if r.status_code == 200:
            print("Web page scraped successfully!")

            # tree is the HTML content we are parsing
            tree = html.fromstring(r.content)
            # HTML content (commented out because we do not need to see this)
            #print(str(r.content))

            # HTML target (commented out because we do not need to see this)
            #print("Our HTML Target: ", tree)

            roster_spots = 0
            team_stat_fields = 0
            team_splits = 0

            full_body = tree.xpath("//*/tbody")
            for tbody in full_body:

                # get number of team splits fields for parsing
                if team_stat_fields > 1:
                    for tr in tbody:
                        team_splits = team_splits + 1

                # get number of team stat fields for parsing
                if roster_spots > 1 and team_stat_fields is 0:
                    for tr in tbody:
                        team_stat_fields = team_stat_fields + 1

                # get number of roster spots for individual player parsing
                if roster_spots is 0:
                    for tr in tbody:
                        roster_spots = roster_spots + 1

            print("# of roster spots: " + str(roster_spots))
            print("# of team stat fields: " + str(team_stat_fields))
            print("# of team splits (games played): " + str(team_splits))

            parsed_team_stats = parseTeamData(tree, team_stat_fields, 22, 1)
            parsed_team_splits = parseTeamData(tree, team_splits, 22, 2)

            # Parse roster data (separate from team data)
            team_stats = []
            # stats: each player needs to be in their own list
            for j in range(1, roster_spots+1):
                stat_list = []

                for i in range(1, 24):
                    test_entry = tree.xpath("//*/tbody/tr[" + str(j) + "]/td[" + str(i) + "]/text()")

                    # test to make sure the HTML does not have a broken value
                    if test_entry:
                        # for player stats
                        pstat = test_entry[0]

                    else:
                        """ pad with NULL to indicate broken HTML value
                            we can change this to a different value if needed
                        """
                        pstat = 'NULL'

                    if i == 1:
                        stat_list.append("Player #" + pstat)
                    elif i == 2:
                        test_entry = tree.xpath("//*/tbody/tr[" + str(j) + "]/td[" + str(i) + "]/a/text()")
                        stat_list.append(test_entry[0])
                    else:
                        stat_list.append(pstat)

                team_stats.append(stat_list)

    except Exception as e:
        print("Error: ", e)
        return 1

    # make final list of lists
    data_pack = []
    data_pack.append(team_stats)
    data_pack.append(parsed_team_stats)
    data_pack.append(parsed_team_splits)

    return data_pack

# This is where we will implement algorithm to compare the team's player stats/other stats
def compareTeams(data1, data2):
    """
    REGULAR SEASON INDIVIDUAL PLAYER STATS:
        Location: data[0][index]
        Entry Format:
            Player#, Player Name, Team, GP, MPG, FGM, FGA, FG%, 3PM, 3PA, 3P%, FTM, FTA, FT%, TOV, PF, ORB, DRB, RPG, APG, SPG, BPG, PPG

    REGULAR SEASON TEAM STATS:
        Location: data[1][index]
        Entry Format:
            Totals, GP, MPG, FGM, FGA, FG%, 3PM 3PA, 3P%, FTM, FTA, FT%, TOV, PF, ORB, DRB, TRB, APG, SPG, BPG, PPG

    REGULAR SEASON TEAM SPLITS:
        Location: data[2][index]
        Entry Format:
            v. Team, GP, MPG, FGM, FGA, FG%, 3PM, 3PA, 3P%, FTM, FTA, FT%, TOV, PF, ORB, DRB, TRB, APG, SPG, BPG, PPG

    """

    # Tests
    print("\n")
    print("Roster Player (1): " + str(data1[0][0][1]) + ", Team: " + str(data1[0][0][2]))
    print("Team Stats for " + str(data1[0][0][2]) + ": " + str(data1[1][0]))
    print("Team Splits (one game) for " + str(data1[0][0][2]) + " " + str(data1[2][0]))

    print("\n")
    print("Roster Player(1): " + str(data2[0][0][1]) + ", Team: " + str(data2[0][0][2]))
    print("Team Stats for " + str(data2[0][0][2]) + ": " + str(data2[1][0]))
    print("Team Splits (one game) for " + str(data2[0][0][2]) + " " + str(data2[2][0]))

    return True

if __name__ == "__main__":

    # all valid teams located in teams.txt
    # call prints all to screen for testing purposes
    printTeams()

    print("Please enter two teams #s to determine a winner:")
    print("\n")

    # ideally this would be done via a drop down/method on gui
    # select via indexed teams
    team1 = int(input("Team 1: "))
    team2 = int(input("Team 2: "))

    # team1 & team2 are indexed in urls with corresponding team in urls.txt
    getTeams(team1, team2)
