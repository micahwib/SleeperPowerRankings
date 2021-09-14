import statistics
import operator
from sleeper_wrapper import League
from sleeper_wrapper import User
from owner import Owner
import requests
import os
from dotenv import load_dotenv

load_dotenv()
league_id = os.getenv('LEAUGE_ID_2020')
league = League(league_id)


# 2020 515656198078787584
# 2021 650071768328945664

# gets user data and creates owner objects and puts them in a dictionary by roster_id
def getUserData():
    rosters = league.get_rosters()
    owners = {}

    for user in rosters:
        user_id = user['owner_id']
        player = User(user_id)
        player_data = player.get_user()
        owner_data = Owner(user['owner_id'], user['settings']['total_moves'],
                           player_data['display_name'], player_data['avatar'], user['roster_id'])
        # user['settings']['wins'], user['settings']['ties'], user['settings']['losses'],
        owners[user['roster_id']] = owner_data

    return owners


# iterate through matchup data for each week until current week and add points for and points against each player
# call set rank and calculate consistency on a given week
def setPointData(owners, week):
    for i in range(1, week + 1):
        id_list = []
        matchups = league.get_matchups(i)
        for player1 in matchups:
            for player2 in matchups:
                if player1['matchup_id'] == player2['matchup_id'] and player1['roster_id'] != player2['roster_id']:
                    if player1['roster_id'] in id_list or player2['roster_id'] in id_list:
                        break

                    owners.get(player1['roster_id']).add_points_for(player1['points'])
                    owners.get(player1['roster_id']).add_points_against(player1['points'])

                    owners.get(player2['roster_id']).add_points_for(player2['points'])
                    owners.get(player2['roster_id']).add_points_against(player1['points'])

                    if player1['points'] == player2['points']:
                        owners.get(player1['roster_id']).add_tie()
                        owners.get(player2['roster_id']).add_tie()

                    elif player1['points'] >= player2['points']:
                        owners.get(player1['roster_id']).add_win()
                        owners.get(player2['roster_id']).add_loss()

                    else:
                        owners.get(player1['roster_id']).add_loss()
                        owners.get(player2['roster_id']).add_win()

                    id_list.append(player1['roster_id'])
                    id_list.append(player2['roster_id'])

        set_rank(owners)
        if i > 1:
            calculate_consistency(owners)


# get the average OIL score for the current week
def get_league_avg_OIL_week(owners):
    OIL_score = []
    for i in range(1, len(owners) + 1):
        OIL_score.append(owners[i].get_raw_OIL_score())
    return statistics.mean(OIL_score)


# get the average PPG for a the current week
def get_league_avg_ppg(owners):
    avg = []
    for i in range(1, len(owners) + 1):
        for j in owners[i].points_for:
            avg.append(j)

    return statistics.mean(avg)


# set the rank of all the players for a given week
def set_rank(owners):
    league_avg_oil = get_league_avg_OIL_week(owners)
    OIL_standardized = {}
    for i in range(1, len(owners) + 1):
        OIL_standardized[owners[i].roster_id] = owners[i].get_raw_OIL_score() / league_avg_oil

    ranked = sorted(OIL_standardized.items(), key=lambda x: x[1], reverse=True)
    for j in range(0, len(ranked)):
        for k in range(1, len(owners) + 1):
            if owners[k].roster_id == ranked[j][0]:
                owners[k].set_rank(j + 1)
                break


# set consistency after week 2
def calculate_consistency(owners):
    for i in range(1, len(owners) + 1):
        owners[i].set_consistency(((owners[i].get_avg_ppg() - 3 * owners[i].get_stdev())
                                   / .75 * get_league_avg_ppg(owners)))


# calculate average consistency in the league after week 2
def calculate_avg_consistency(owners):
    consistencies = []
    for i in range(1, len(owners) + 1):
        consistencies.append(owners[i].consistency)

    avg = statistics.mean(consistencies)
    if avg == 0:
        return 1
    return statistics.mean(consistencies)


if __name__ == '__main__':
    r = requests.get("https://api.sleeper.app/v1/state/nfl")
    week = r.json()['week']
    owners = getUserData()
    setPointData(owners, 3)

    league_avg_cons = calculate_avg_consistency(owners)
    owners = sorted(owners.values(), key=operator.attrgetter('current_rank'))

    for i in range(0, len(owners)):
        print(owners[i].display_name, "previous: ", owners[i].previous_rank, "current: ", owners[i].current_rank,
              "consistency: ", owners[i].consistency / league_avg_cons, "ppg: ", owners[i].get_avg_ppg(), "oil",
              owners[i].get_raw_OIL_score(), "min", min(owners[i].points_for), "max", max(owners[i].points_for))
