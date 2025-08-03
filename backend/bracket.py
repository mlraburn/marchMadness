"""
Code contains bracket related functions
"""

import csv          # base
import math         # base
import pandas       # pip install pandas
import data_download

regions = ['EAST', 'WEST', 'SOUTH', 'MIDWEST']


def visualize_ncaab_bracket(path: str) -> None:
    """
    Prints out the bracket in terminal
    :param path: path to csv file with schedule data
    :return:
    """
    with open(path, newline='') as bracket_csv:
        data = csv.reader(bracket_csv)

        for region in regions:
            print(f"**{region}**    **{region}**    **{region}**    **{region}**    **{region}**")

            for line in range(30):
                al = get_adjusted_line(line)
                rnd = line_to_round(al, 16)
                tabs = tabs_calc(rnd)
                ub = get_upper_bound(line, rnd)
                lb = get_lower_bound(ub, rnd)

                for tab_count in range(tabs):
                    print("\t", end="")

                team_found = find_teams_in_rounds_in_csv(rnd, int(ub), int(lb), region, path)
                print(f"{team_found[0]} {team_found[1]}")

            print("")

        print(f"**FINAL FOUR**    **FINAL FOUR**    **FINAL FOUR**    **FINAL FOUR**")

        east_winner = find_teams_in_rounds_in_csv(5, 15, 0, regions[0], path)
        west_winner = find_teams_in_rounds_in_csv(5, 15, 0, regions[1], path)
        south_winner = find_teams_in_rounds_in_csv(5, 15, 0, regions[2], path)
        midwest_winner = find_teams_in_rounds_in_csv(5, 15, 0, regions[3], path)

        east_winner_6 = find_teams_in_rounds_in_csv(6, 15, 0, regions[0], path)
        west_winner_6 = find_teams_in_rounds_in_csv(6, 15, 0, regions[1], path)
        south_winner_6 = find_teams_in_rounds_in_csv(6, 15, 0, regions[2], path)
        midwest_winner_6 = find_teams_in_rounds_in_csv(6, 15, 0, regions[3], path)

        print(f"{east_winner[0]} {east_winner[1]}")
        print(f"{midwest_winner[0]} {midwest_winner[1]}")

        if east_winner_6 == midwest_winner_6:
            print(f"\t\t\t\t\t\t\t\t{east_winner_6[0]} {east_winner_6[1]}")
        elif east_winner_6[0] == "________" and midwest_winner_6 != "________":
            print(f"\t\t\t\t\t\t\t\t{midwest_winner_6[0]} {midwest_winner_6[1]}")
        else:
            print(f"\t\t\t\t\t\t\t\t{east_winner_6[0]} {east_winner_6[1]}")

        if south_winner_6 == west_winner_6:
            print(f"\t\t\t\t\t\t\t\t{south_winner_6[0]} {south_winner_6[1]}")
        elif south_winner_6[0] == "________" and west_winner_6 != "________":
            print(f"\t\t\t\t\t\t\t\t{west_winner_6[0]} {west_winner_6[1]}")
        else:
            print(f"\t\t\t\t\t\t\t\t{south_winner_6[0]} {south_winner_6[1]}")

        print(f"{south_winner[0]} {south_winner[1]}")
        print(f"{west_winner[0]} {west_winner[1]}")


        print("")
        print(f"**CHAMPION**    **CHAMPION**    **CHAMPION**    **CHAMPION**")

        east_winner_7 = find_teams_in_rounds_in_csv(7, 15, 0, regions[0], path)
        west_winner_7 = find_teams_in_rounds_in_csv(7, 15, 0, regions[1], path)
        south_winner_7 = find_teams_in_rounds_in_csv(7, 15, 0, regions[2], path)
        midwest_winner_7 = find_teams_in_rounds_in_csv(7, 15, 0, regions[3], path)

        if east_winner_7[0] != "________":
            print(f"{east_winner_7[0]} {east_winner_7[1]}")
        elif west_winner_7[0] != "________":
            print(f"{west_winner_7[0]} {west_winner_7[1]}")
        elif south_winner_7[0] != "________":
            print(f"{south_winner_7[0]} {south_winner_7[1]}")
        elif midwest_winner_7[0] != "________":
            print(f"{midwest_winner_7[0]} {midwest_winner_7[1]}")
        else:
            print(f"{east_winner_7[0]} {east_winner_7[1]}")


def line_to_round(adjusted_line, total_size) -> int:
    r = int(math.sqrt(total_size))

    while not are_you_mid(total_size, adjusted_line):
        r = r - 1
        total_size = midpoint(total_size)
        adjusted_line = abs(total_size - adjusted_line)

    return r


def midpoint(size) -> int:
    return size / 2


def are_you_mid(size: int, pos: int):
    if size / pos == 2:
        return True
    else:
        return False


def get_upper_bound(line, rnd) -> int:
    if line % 2 == 0:
        return line / 2
    else:
        return math.floor(line / 2) + (2 ** (rnd - 1))


def get_lower_bound(upper, rnd) -> int:
    return upper - (2 ** (rnd - 1) - 1)


def tabs_calc(rnd: int) -> int:
    return (rnd - 1) * 8


def get_adjusted_line(line) -> int:
    if line % 2 == 0:
        return (line + 2) / 2
    else:
        return (line + 1) / 2


def find_teams_in_rounds_in_csv(rnd: int, up: int, lb: int, region: str, path: str) -> tuple:
    bracket_df = pandas.read_csv(path)

    if up == lb:
        name = bracket_df[
            (bracket_df['REGION'] == region) & (bracket_df['ORDER_IN_REGION'] == up) & (bracket_df['ROUND'] == 1)][
            'TEAM_NAME'].iloc[0]
        seed = dataDownLoad.get_seed(name)
        return name, seed
    else:
        for order in range(lb, up + 1):
            if not bracket_df[(bracket_df['REGION'] == region) & (bracket_df['ORDER_IN_REGION'] == order) & (
                    bracket_df['ROUND'] == rnd)]['TEAM_NAME'].empty:
                name = bracket_df[(bracket_df['REGION'] == region) & (bracket_df['ORDER_IN_REGION'] == order) & (
                        bracket_df['ROUND'] == rnd)]['TEAM_NAME'].iloc[0]
                seed = dataDownLoad.get_seed(name)
                return name, seed
        return "________", "__"


def elo_prob(top_melo, bottom_melo) -> float:
    dif_elo = int(top_melo) - int(bottom_melo)

    # 2024 it was .1041 * dif_elo + 51.0099
    # adjusted to 0.07256*X + 53.23
    prob_to_win = (.07256 * dif_elo) + 53.23
    if prob_to_win >= 100:
        return 98.7 # maybe check the calibration
    else:
        return prob_to_win


def get_current_round(bracket_list: list) -> int:
    """
    Takes a bracket state and returns the current round the tourney is in

    0 aligns with first four

    :param bracket_list: rounds are elements in the list and each element is a list of positional ids
    :return: Returns an integer representing the current round of the tournament
    """

    max_round = 0

    # we do range from 1 to len(bracket_list) because we want to skip the 0th round cause that should return a 0
    for i in range(1, len(bracket_list)):
        if len(bracket_list[i]) > 0:
            max_round += 1

    return max_round


def get_games_for_a_round(bracket_list: list) -> list[(str, str)] or None:
    """
    given a certain bracket state - which is defined as positional ids and furthest round
    this function will calculate what games are required to move the round to the next round.

    It will return a list of tuples. Each tuple represents the game
    Tuple: (position id team 1, position id team 2)

    -- Assumption is that all games that must occur to move to the next round will always have happened
    -- before the next round

    -- Assumption is that first four teams are indicated by an extra letter at the end of their position
    -- id

    -- RETURNS NONE WHEN TOURNAMENT CAN HAVE NO MORE GAMES

    :param bracket_list:
    :return: Returns a list of games that must be played to move to the next round. Each element
    in the list is a tuple like (position id team 1, position id team 2)
    """

    # get round we are in
    current_round = get_current_round(bracket_list)

    games_to_play: list[tuple] = []  # what we will return

    # we want to loop through the teams in the current round
    # each team will play the next team in the list so pair wise
    top_team = ""
    bottom_team = ""
    for i, position_id in enumerate(bracket_list[current_round]):
        # when odd so every 2
        if i % 2 == 1:
            bottom_team = position_id
            games_to_play.append((top_team, bottom_team))
        else:
            top_team = position_id

    return games_to_play




def get_possible_seeds(seed_int: int, max_seed: int, current_round: int) -> (list[int], list[int]):
    """
    Returns a list of seeds that could be in the position of where a seed finds itself based on the max seed number,
    its own seed, and the current round As the first element of the tuple, and the second element returns
    the list of seeds it could play against. This assumes a binary balanced tree.  The current round is that round 1
    should be the round where there is only one team possible
    :param seed_int:
    :param max_seed:
    :param current_round:
    :return:
    """

    top_set = [seed_int]  # top is always the one we are looking at with seed_int
    bottom_set = []
    # loop up to round (equivalent of going up the binary tree





def play_a_game(position_id_team_1: str, position_id_team_2: str) -> str:
    """
    play a game between two teams based on position id

    the winner's position ID is returned
    :param position_id_team_1: Position id of team 1
    :param position_id_team_2: Position id of team 2
    :return: the position ID of the winner
    """

    pass

if __name__ == '__main__':
    pass