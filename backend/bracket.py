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


def get_current_round(bracket_dict: dict) -> int:
    """
    Takes a bracket state and returns the current round the tourney is in

    0 aligns with first four

    :param bracket_dict: positional ids and furthest round
    :return: Returns an integer representing the current round of the tournament
    """

    max_round = 0
    first_four_teams_advanced = 0
    first_four_teams_in_bracket = 0
    # find max round in furthest round in bracket
    for team in bracket_dict:
        # logic to advance the max round as it finds larger furthest rounds
        if bracket_dict[team] > max_round:
            max_round = bracket_dict[team]

        # logic to handle edge case where first four hasn't happened yet or completed
        if len(team) == 4:

            # this is to handle the edge case of some brackets not having
            # the first four at all
            first_four_teams_in_bracket += 1  # this is to handle the edge case of some brackets not having
            if int(bracket_dict[team]) >= 1:  # this length is only for first four teams
                first_four_teams_advanced += 1  # add up first four advanced counter

    # if we have a max round of 1 but first four teams in bracket are 4 and 2 of them haven't advanced then
    # we actually are in round 0
    if max_round == 1 and first_four_teams_advanced < 4 and first_four_teams_in_bracket == 8:
        max_round = 0

    return max_round


def get_games_for_a_round(bracket_dict: dict) -> list[(str, str)] or None:
    """
    given a certain bracket state - which is defined as positional ids and furthest round
    this function will calculate what games are required to move the round to the next round.

    It will return a list of tuples. Each tuple represents the game
    Tuple: (position id team 1, position id team 2)

    -- Assumption is that some games might have happened already that are required for the next round.
    -- in that assumption we will not return that game

    -- Assumption is that all games that must occur to move to the next round will always have happened
    -- before the next round

    -- Assumption is that first four teams are indicated by an extra letter at the end of their position
    -- id

    -- RETURNS NONE WHEN TOURNAMENT CAN HAVE NO MORE GAMES

    **************************************************************************
    * COOL PATTERN NOTICED THAT HELPS TO AUTOMATICALLY CALCULATE WHO SHOULD  *
    * PLAY WHO IN A CERTAIN REGION AND ROUND                                 *
    * First round is kinda obvious same region and should add to 17          *
    * Second round is the following algorith                                 *
    * get seed X then calculate compliment to 17                             *
    * take minimum and then find min(X, compliment to 17) + Y = 9            *
    * Y is another seed that can be a possibility then the last              *
    * possibility is Y + Z = 17                                              *
    * teams are {X, compliment to 17, Y, Z} as stated above                  *
    * or {X, C, Y, Z} where X + C = 17 = Y + Z and min(X,C) + min(Y,Z) = 9   *
    *                                                                        *
    * Algorithm for round 3 is similar but with                              *
    * min(top-game-set) + min(bottom-game-set) = 5                           *
    * so X is seed then C is compliment then get Y and Z per above           *
    * then find min(X,C,Y,Z) + A = 5                                         *
    * A is one seed option in the other team they will play                  *
    * from there you can calculate the other team options using the pattern  *
    * A + B = 17 and min(A,B) + D = 9                                        *
    * D + E = 17                                                             *
    * so top team is {X,C,Y,Z} and bottom team is {A,B,D,E}                  *
    * round 4 is trivial because there are only two teams per region         *
    * round 5 is hard coded because specific regions play specific regions   *
    * round 6 is hard coded because region {F,G} can play {H,I}              *
    * round 7 has no game                                                    *
    **************************************************************************

    :param bracket_dict:
    :return: Returns a list of games that must be played to move to the next round. Each element
    in the list is a tuple like (position id team 1, position id team 2)
    """

    # to find what round we are in we will look for the furthest round any team is in
    # EXCEPTION TO THIS RULE IS ROUND 0
    # ROUND 0 COULD BE THE CURRENT ROUND WHILE OTHERS ARE IN ROUND 1 ALREADY

    # get round we are in
    current_round = get_current_round(bracket_dict)

    games_remaining: list[tuple] = []  # what we will return

    # edge case for first four
    if current_round == 0:

        # get first four teams that play which should be 8 teams
        first_four_teams = []
        for team in bracket_dict:
            if len(team) == 4:
                first_four_teams.append(team)

        # sort them
        first_four_teams.sort()

        # get games that need to happen
        # every region seed A B combo need one of the A B to be at 1 or the game hasn't occured yet

        i = 0
        while i < len(first_four_teams):
            a_team = first_four_teams[i]
            b_team = first_four_teams[i + 1]

            a_team_round = bracket_dict[a_team]
            b_team_round = bracket_dict[b_team]

            # in this case one team has advanced
            if a_team_round == 1 or b_team_round == 1:
                continue
            # in this case one team has not advanced so we must return this game
            else:
                games_remaining.append((a_team, b_team))

            # increment the counter by 2
            i += 2

        return games_remaining

    # edge case for tournament being over
    if current_round == 7:
        return None  # because no games are left



def play_a_game(position_id_team_1: str, position_id_team_2: str) -> str:
    """
    play a game between two teams based on position id

    the winner's position ID is returned
    :param position_id_team_1: Position id of team 1
    :param position_id_team_2: Position id of team 2
    :return: the position ID of the winner
    """

    pass