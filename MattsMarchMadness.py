import random

import pandas
import math
import dataDownLoad
import bracket
import csv

sd_raw = pandas.read_excel("03-16-2024-cbb-season-team-feed.xlsx")
sd = sd_raw[['GAME-ID', 'TEAM', 'F']]

td = pandas.read_csv('marchMadTable.csv')
nsd = pandas.read_csv('NSData.csv')


def create_analysis_df() -> pandas.DataFrame:
    t_list = td['TEAM_NAME'].tolist()

    analysis_dict = {'TEAM': [], 'SEED': [], 'WINS': [], 'LOSSES': [], 'SOS': [], 'REGION': [], 'ORDER': [],
                     'WINDIFSOS': [],
                     'SCH_PERF': [], 'NSGRADE': [], 'MELO': []}

    for team in t_list:
        analysis_dict['TEAM'].append(team)

        seed = td[td['TEAM_NAME'] == team]['SEED'].iloc[0]

        win_loss = dataDownLoad.get_record(team)
        wins = win_loss[0]
        losses = win_loss[1]

        analysis_dict['SEED'].append(seed)
        analysis_dict['WINS'].append(wins)
        analysis_dict['LOSSES'].append(losses)

        sos = dataDownLoad.sched_dif(team)
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

        perf = dataDownLoad.get_reg_s_perf(team) + 1
        analysis_dict['SCH_PERF'].append(perf)

        ns_grade = dataDownLoad.get_nate_silver_grade(team)
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
    a_df = pandas.read_csv('analysis.csv')
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
            return \
            df[(df['ROUND'] == rnd) & (df['REGION'] == region) & (df['ORDER_IN_REGION'] == lower)]['TEAM_NAME'].iloc[0]
        lower = lower + 1
    return team_name


def simulate_mm() -> pandas.DataFrame:
    regions = ['EAST', 'WEST', 'SOUTH', 'MIDWEST']
    tourney_df = pandas.read_csv('marchMadTable.csv')
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

                winning_team = game(top_team, bottom_team)
                seed = dataDownLoad.get_seed(winning_team)
                order = tourney_df[tourney_df['TEAM_NAME'] == winning_team]['ORDER_IN_REGION'].iloc[0]

                row_to_add = {'TEAM_NAME': winning_team, 'SEED': seed, 'REGION': region, 'ORDER_IN_REGION': order,
                              'ROUND': rnd + 1}

                tourney_df = tourney_df._append(row_to_add, ignore_index=True)

        rnd = rnd + 1

    # hard code final four
    east_winner = find_team_in_order_range(5, 'EAST', 15, 0, tourney_df)
    west_winner = find_team_in_order_range(5, 'WEST', 15, 0, tourney_df)
    winner_ew = game(east_winner, west_winner)
    seed = dataDownLoad.get_seed(winner_ew)
    order = tourney_df[tourney_df['TEAM_NAME'] == winner_ew]['ORDER_IN_REGION'].iloc[0]
    region = dataDownLoad.get_region(winner_ew)

    row_to_add = {'TEAM_NAME': winner_ew, 'SEED': seed, 'REGION': region, 'ORDER_IN_REGION': order,
                  'ROUND': rnd + 1}

    tourney_df = tourney_df._append(row_to_add, ignore_index=True)

    south_winner = find_team_in_order_range(5, 'SOUTH', 15, 0, tourney_df)
    midwest_winner = find_team_in_order_range(5, 'MIDWEST', 15, 0, tourney_df)
    winner_sm = game(south_winner, midwest_winner)
    seed = dataDownLoad.get_seed(winner_sm)
    order = tourney_df[tourney_df['TEAM_NAME'] == winner_sm]['ORDER_IN_REGION'].iloc[0]
    region = dataDownLoad.get_region(winner_sm)

    row_to_add = {'TEAM_NAME': winner_sm, 'SEED': seed, 'REGION': region, 'ORDER_IN_REGION': order,
                  'ROUND': rnd + 1}

    tourney_df = tourney_df._append(row_to_add, ignore_index=True)

    rnd = rnd + 1

    champion = game(winner_ew, winner_sm)
    seed = dataDownLoad.get_seed(champion)
    order = tourney_df[tourney_df['TEAM_NAME'] == champion]['ORDER_IN_REGION'].iloc[0]
    region = dataDownLoad.get_region(champion)

    row_to_add = {'TEAM_NAME': champion, 'SEED': seed, 'REGION': region, 'ORDER_IN_REGION': order,
                  'ROUND': rnd + 1}

    tourney_df = tourney_df._append(row_to_add, ignore_index=True)

    return tourney_df


def main():
    a_df = create_analysis_df()
    a_df.to_csv('analysis.csv', index=False)

    print(f"WELCOME TO MATT'S MARCH MADNESS BRACKET PROGRAM")
    print()
    i = ""
    while i != 'Q':
        print("MAIN MENU")
        print("Q: Quit")
        print("S: Score")
        print("M: Make Brackets")
        print("P: Print Bracket")
        i = input(":")
        if i == 'Q':
            exit(0)
        elif i == 'S':
            print("not working yet")
            bracket.visualize_ncaab_bracket('marchMadTable.csv')
        elif i == 'M':
            config = open('config.csv')
            config_data = config.readlines()
            brackets_made = int(config_data[0])
            config.close()

            n = int(input("How Many?:"))
            for b in range(n):
                bracket_serial = (b + 1) + brackets_made
                name_of_file = f"MMM__{bracket_serial}.csv"
                tourney_final_df = simulate_mm()
                tourney_final_df.to_csv(name_of_file, index=False)

            config = open('config.csv', 'w')
            new_serial = brackets_made + n
            writer = csv.writer(config)
            writer.writerow([new_serial])
            config.close()
        elif i == 'P':
            path = input("path:")
            bracket.visualize_ncaab_bracket(path)


def amount_of_games(rnd) -> int:
    return int(8 * ((1 / 2) ** (rnd - 1)))


if __name__ == '__main__':
    main()
