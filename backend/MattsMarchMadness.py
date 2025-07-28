
import random
import pandas
import math
import csv
import sys  # base python
import datetime
import bracket_storage
import data_download
import bracket

#sd_raw = pandas.read_excel("03-16-2025-cbb-season-team-feed.xlsx")
#sd = sd_raw[['GAME-ID', 'TEAM', 'F']]

#td = pandas.read_csv('marchMadTable_2025.csv')


def get_games_for_a_round(bracket_dict: dict) -> list[(str, str)]:
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

    :param bracket_dict:
    :return: Returns a list of games that must be played to move to the next round. Each element
    in the list is a tuple like (position id team 1, position id team 2)
    """

    # to find what round we are in we will look for the furthest round any team is in
    # EXCEPTION TO THIS RULE IS ROUND 0
    # ROUND 0 COULD BE THE CURRENT ROUND WHILE OTHERS ARE IN ROUND 1 ALREADY

    # get round we are in

    current_round = get_current_round(bracket_dict)

    print(current_round)

    pass



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
        if int(bracket_dict[team]) > max_round:
            max_round = int(bracket_dict[team])

        # logic to handle edge case where first four hasn't happened yet or completed
        if len(team) == 4:

            # this is to handle the edge case of some brackets not having
            # the first four at all
            first_four_teams_in_bracket += 1  # this is to handle the edge case of some brackets not having
            if int(bracket_dict[team]) >= 1:  # this length is only for first four teams
                first_four_teams_advanced += 1  # add up first four advanced counter

    # if we have a max round of 1 but first four teams in bracket are 4 and 2 of them haven't advanced then
    # we actually are in round 0
    if max_round == 1 and first_four_teams_advanced < 2 and first_four_teams_in_bracket == 4:
        max_round = 0

    return max_round

def create_analysis_df() -> pandas.DataFrame:
    t_list = td['TEAM_NAME'].tolist()

    analysis_dict = {'TEAM': [], 'SEED': [], 'WINS': [], 'LOSSES': [], 'SOS': [], 'REGION': [], 'ORDER': [],
                     'WINDIFSOS': [],
                     'SCH_PERF': [], 'NSGRADE': [], 'MELO': []}

    for team in t_list:
        analysis_dict['TEAM'].append(team)

        seed = td[td['TEAM_NAME'] == team]['SEED'].iloc[0]

        win_loss = data_download.get_record(team)
        wins = win_loss[0]
        losses = win_loss[1]

        analysis_dict['SEED'].append(seed)
        analysis_dict['WINS'].append(wins)
        analysis_dict['LOSSES'].append(losses)

        sos = data_download.strength_of_schedule_calculator(team)
        analysis_dict['SOS'].append(sos)

        region = td[td['TEAM_NAME'] == team]['REGION'].iloc[0]
        analysis_dict['REGION'].append(region)

        order = td[td['TEAM_NAME'] == team]['ORDER_IN_REGION'].iloc[0]
        analysis_dict['ORDER'].append(order)

        # minimum is -4 + (2/3.0)
        # adjust by adding the above min
        win_loss_sos = (wins - losses) / sos
        win_loss_sos = abs(win_loss_sos + 4 + (2 / 3))
        win_loss_sos = win_loss_sos.__round__(1) + 1
        analysis_dict['WINDIFSOS'].append(win_loss_sos)

        perf = data_download.get_reg_s_perf(team) + 1
        analysis_dict['SCH_PERF'].append(perf)

        ns_grade = data_download.get_nate_silver_grade(team)
        analysis_dict['NSGRADE'].append(ns_grade)

        melo = win_loss_sos * perf * ns_grade + 1
        analysis_dict['MELO'].append((math.log(melo) * 100).__round__(0))

    analysis_df = pandas.DataFrame(analysis_dict)

    analysis_df_sorted = analysis_df.sort_values('MELO', ascending=False)

    return analysis_df_sorted


def wierd_function(rnd) -> int:
    return 2 ** (rnd - 1)


def game(top_team, bottom_team) -> str:
    # print(top_team)
    # print(bottom_team)
    a_df = pandas.read_csv('../../../../MattsMarchMadness2/backend/analysis.csv')
    melo_top = a_df[a_df['TEAM'] == top_team]['MELO'].iloc[0]
    melo_bottom = a_df[a_df['TEAM'] == bottom_team]['MELO'].iloc[0]

    if melo_top >= melo_bottom:
        prob_top_win = bracket.elo_prob(melo_top, melo_bottom)
    else:
        prob_bottom_win = bracket.elo_prob(melo_bottom, melo_top)
        prob_top_win = 100 - prob_bottom_win

    random_num = random.uniform(0.0, 100.0)

    if random_num <= prob_top_win:
        return top_team
    else:
        return bottom_team


def find_team_in_order_range(rnd, region, upper, lower, df: pandas.DataFrame) -> str:
    team_name = ""
    while lower != upper + 1:
        if not df[(df['ROUND'] == rnd) & (df['REGION'] == region) & (df['ORDER_IN_REGION'] == lower)][
            'TEAM_NAME'].empty:
            return df[(df['ROUND'] == rnd) & (df['REGION'] == region) & (df['ORDER_IN_REGION'] == lower)]['TEAM_NAME'].iloc[0]
        lower = lower + 1
    return team_name


def simulate_mm() -> pandas.DataFrame:
    regions = ['EAST', 'WEST', 'SOUTH', 'MIDWEST']
    tourney_df = pandas.read_csv('marchMadTable_2025.csv')
    rnd = 1

    while rnd < 5:
        # print(f"ROUND: {rnd}")
        for region in regions:
            # print(f"REGION: {region}")
            range_to_search = wierd_function(rnd)
            games_to_play = amount_of_games(rnd)
            cur_pos = 0
            for game_number in range(games_to_play):
                top_team = ""
                bottom_team = ""
                if range_to_search == 1:
                    top_team = \
                        tourney_df[(tourney_df['REGION'] == region) & (tourney_df['ORDER_IN_REGION'] == cur_pos)][
                            'TEAM_NAME'].iloc[0]
                    cur_pos = cur_pos + 1
                    bottom_team = \
                        tourney_df[(tourney_df['REGION'] == region) & (tourney_df['ORDER_IN_REGION'] == cur_pos)][
                            'TEAM_NAME'].iloc[0]
                    cur_pos = cur_pos + 1
                else:
                    top_team = find_team_in_order_range(rnd, region, cur_pos + range_to_search - 1, cur_pos, tourney_df)
                    cur_pos = cur_pos + range_to_search
                    bottom_team = find_team_in_order_range(rnd, region, cur_pos + range_to_search - 1, cur_pos,
                                                           tourney_df)
                    cur_pos = cur_pos + range_to_search

                """
                THIS IS ALL FOR TESTING AND FIXING THE ISSUE WITH UNDER DOGS WINNING TOO MUCH

                print(f"Top Team: {top_team}")
                print(f"Bottom Team: {bottom_team}")
                print(f"{top_team} {dataDownLoad.get_seed(top_team)} vs {bottom_team} {dataDownLoad.get_seed(bottom_team)}:")
                print(f"ELOs: {dataDownLoad.get_MELO(top_team)} vs {dataDownLoad.get_MELO(bottom_team)}")
                print(f"ELO dif: {int(dataDownLoad.get_MELO(top_team))-int(dataDownLoad.get_MELO(bottom_team))}")
                if int(dataDownLoad.get_MELO(top_team)) - int(dataDownLoad.get_MELO(bottom_team)) <= 0:
                    print(f"Probability of 2nd team winning: {elo_prob(dataDownLoad.get_MELO(bottom_team), dataDownLoad.get_MELO(top_team))}")
                else:
                    print(f"Probability of 1st team winning: {elo_prob(dataDownLoad.get_MELO(top_team), dataDownLoad.get_MELO(bottom_team))}")

                print()
                """

                winning_team = game(top_team, bottom_team)
                seed = data_download.get_seed(winning_team)
                order = tourney_df[tourney_df['TEAM_NAME'] == winning_team]['ORDER_IN_REGION'].iloc[0]

                row_to_add = {'TEAM_NAME': winning_team, 'SEED': seed, 'REGION': region, 'ORDER_IN_REGION': order,
                              'ROUND': rnd + 1}

                tourney_df = tourney_df._append(row_to_add, ignore_index=True)

        rnd = rnd + 1

    # hard code final four
    east_winner = find_team_in_order_range(5, 'EAST', 15, 0, tourney_df)
    west_winner = find_team_in_order_range(5, 'WEST', 15, 0, tourney_df)
    south_winner = find_team_in_order_range(5, 'SOUTH', 15, 0, tourney_df)
    midwest_winner = find_team_in_order_range(5, 'MIDWEST', 15, 0, tourney_df)

    winner_emw = game(east_winner, midwest_winner)
    seed = data_download.get_seed(winner_emw)
    order = tourney_df[tourney_df['TEAM_NAME'] == winner_emw]['ORDER_IN_REGION'].iloc[0]
    region = data_download.get_region(winner_emw)

    row_to_add = {'TEAM_NAME': winner_emw, 'SEED': seed, 'REGION': region, 'ORDER_IN_REGION': order,
                  'ROUND': rnd + 1}

    tourney_df = tourney_df._append(row_to_add, ignore_index=True)


    winner_sw = game(south_winner, west_winner)
    seed = data_download.get_seed(winner_sw)
    order = tourney_df[tourney_df['TEAM_NAME'] == winner_sw]['ORDER_IN_REGION'].iloc[0]
    region = data_download.get_region(winner_sw)

    row_to_add = {'TEAM_NAME': winner_sw, 'SEED': seed, 'REGION': region, 'ORDER_IN_REGION': order,
                  'ROUND': rnd + 1}

    tourney_df = tourney_df._append(row_to_add, ignore_index=True)

    rnd = rnd + 1

    champion = game(winner_emw, winner_sw)
    seed = data_download.get_seed(champion)
    order = tourney_df[tourney_df['TEAM_NAME'] == champion]['ORDER_IN_REGION'].iloc[0]
    region = data_download.get_region(champion)

    row_to_add = {'TEAM_NAME': champion, 'SEED': seed, 'REGION': region, 'ORDER_IN_REGION': order,
                  'ROUND': rnd + 1}

    tourney_df = tourney_df._append(row_to_add, ignore_index=True)

    return tourney_df


def main():
    a_df = pandas.read_csv('../../../../MattsMarchMadness2/backend/analysis.csv')
    # a_df.to_csv('analysis.csv', index=False)

    print(f"WELCOME TO MATT'S MARCH MADNESS BRACKET PROGRAM")
    print()

    i = ""

    if len(sys.argv) > 1:
        i = sys.argv[1].split()[0]

    while i != 'Q':
        print("MAIN MENU")
        print("Q: Quit")
        print("S: Score")
        print("M: Make Brackets")
        print("P: Print Bracket")
        print("A: Print Analysis")
        if len(sys.argv) == 1:
            i = input(":")
        if i == 'Q':
            exit(0)
        elif i == 'S':
            print("not working yet")
            bracket.visualize_ncaab_bracket('marchMadTable_2025.csv')
        elif i == 'M':
            config = open('../../config.csv')
            config_data = config.readlines()
            brackets_made = int(config_data[0])
            config.close()

            n = int(input("How Many?:"))
            for b in range(n):
                bracket_serial = (b + 1) + brackets_made
                name_of_file = f"MMM__{bracket_serial}.csv"
                tourney_final_df = simulate_mm()
                tourney_final_df.to_csv(name_of_file, index=False)

            config = open('../../config.csv', 'w')
            new_serial = brackets_made + n
            writer = csv.writer(config)
            writer.writerow([new_serial])
            config.close()
        elif i == 'P':
            if len(sys.argv) > 1:
                path = sys.argv[1].split()[1]
            else:
                path = input("path:")
            bracket.visualize_ncaab_bracket(path)
        elif i == "A":
            a_df.sort_values(by='MELO', ascending=False)
            print(a_df.to_string(index=False))
        elif i == "toast":
            print("toast")

        if len(sys.argv) > 1:
            break


def amount_of_games(rnd) -> int:
    return int(8 * ((1 / 2) ** (rnd - 1)))


def generate_web_bracket():
    """
    Function called by the web interface to generate a new bracket.
    Returns the filename of the generated bracket CSV.
    """
    try:
        # Read the current bracket count from config
        config = open('../../config.csv')
        config_data = config.readlines()
        brackets_made = int(config_data[0])
        config.close()

        # Generate a unique timestamp for the bracket
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

        # Create a new bracket serial number
        bracket_serial = brackets_made + 1

        # Create the filename
        name_of_file = f"static/MMM__{bracket_serial}_{timestamp}.csv"

        # Simulate the bracket
        tourney_final_df = simulate_mm()

        # Save the bracket to a CSV file
        tourney_final_df.to_csv(name_of_file, index=False)

        # Update the config file with the new bracket count
        config = open('../../config.csv', 'w')
        writer = csv.writer(config)
        writer.writerow([bracket_serial])
        config.close()

        # Return the filename for potential use by the web interface
        return name_of_file

    except Exception as e:
        print(f"Error generating bracket: {str(e)}")
        return None


if __name__ == '__main__':
    """
    testing the new code base below
    """

    position_id_map = bracket_storage.setup_positional_id_map()
    initial_bracket = bracket_storage.setup_initial_bracket(position_id_map)

    # Print to test
    for position_id, team_name in position_id_map.items():
        print(f"{position_id}: {team_name}")

    print()

    for position_id, last_round in initial_bracket.items():
        print(f"{position_id}: {last_round}")

    print()

    get_games_for_a_round(initial_bracket)

    # main()
