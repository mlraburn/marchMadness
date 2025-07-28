"""
Initializing File

This file creates the analysis of the schedule and generates the ELO values that each team will have to determine
their success throughout the simulated bracket

"""
import pandas   # pip install pandas
import math     # base python

# FILE WIDE VARIABLES
# -------------------

# Schedule information
schedule_dataframe_raw: pandas.DataFrame = pandas.read_excel("03-16-2025-cbb-season-team-feed.xlsx")  # file is downloaded from
# big backet ball data
schedule_dataframe: pandas.DataFrame = schedule_dataframe_raw[['GAME-ID', 'TEAM', 'F']]  # filter these columns in the excel file
# GAME-ID: unique integer for each game.  A game consists of 2 rows one for each team in the game but with the same
# GAME-ID.
# TEAM: team name as string
# F: points scored as an integer

# load the marchMadness table which has initial values of the tourney
# marchMadness table is set manually
tournament_dataframe: pandas.DataFrame = pandas.read_csv('marchMadTable_2025.csv')

# load NS data
other_data_N: pandas.DataFrame = pandas.read_csv('other-data.csv')


def get_game(game_id: int) -> pandas.DataFrame:
    """
    returns the row for the game
    :param game_id: each game gets a unique ID
    :return: the row for the game
    """
    game = schedule_dataframe[schedule_dataframe['GAME-ID'] == game_id]
    return game


def get_games(team: str) -> pandas.DataFrame:
    """
    get all the games a team played in
    :param team: team name according to the downloaded data
    :return: dataframe of games
    """
    game_ids = get_games_as_id_list(team)  # get games ids as a list
    games = schedule_dataframe[schedule_dataframe['GAME-ID'].isin(game_ids)]  # get rows based on ids
    return games


def get_opponent_as_record(team: str, gameID: int) -> pandas.DataFrame:
    """
    Gets the oppenent of a team in a specific game based on game ID
    :param team: team name
    :param gameID: specific game ID
    :return: their opponent
    """
    game = get_game(gameID)
    opponent = game[game['TEAM'] != team]
    return opponent


def get_score(team: str, game_id: int) -> int:
    """
    Gets the final score of a team in a specific game
    :param team: team name
    :param game_id: specific game ID
    :return: final score
    """
    game = get_game(game_id)
    score = game[game['TEAM'] == team]
    return score.iloc[0]['F']


def get_games_as_id_list(team: str) -> list[int]:
    """
    Get games ID list of all games for a team
    :param team: team name
    :return: game ID list
    """
    games = schedule_dataframe[schedule_dataframe['TEAM'] == team]
    return games['GAME-ID'].tolist()


def did_win(team: str, game_id: int) -> bool:
    """
    Checks to see if a team won a specific game
    :param team: team name
    :param game_id: Specific Game ID
    :return: True if they won
    """
    opponent = get_opponent_as_record(team, game_id).iloc[0]['TEAM']  # get opponent in game
    team_score = get_score(team, game_id)  # figure out score of team

    opp_score = get_score(opponent, game_id)  # get opponent score

    # see who won
    if team_score > opp_score:
        return True
    else:
        return False


def get_record(team: str) -> tuple[int, int]:
    """
    Return teams record
    :param team: team name
    :return: record as tuple (W,L)
    """
    games_list = get_games_as_id_list(team)  # get games list

    wins = 0
    losses = 0
    for game_id in games_list:  # check if they won or lost each game
        if did_win(team, game_id):
            wins = wins + 1
        else:
            losses = losses + 1
    return wins, losses  # return tuple


def strength_of_schedule_calculator(team: str) -> float:
    """
    Returns the strength of schedule

    This is a Matt R. algorithm for this that takes into account the final seed value of the teams they played
    The more seeded teams a team plays and the higher their seeds the lower the value will be approaching 0

    ** NOTE ** this assumes the first four have already played their game and we know who advanced.

    ** The output distribution is exponential as team over all rank increases. **
    ** About 50% of teams have a strength of schedule below 1 and 50% have a strength of schedule above 50% **

    :param team: team name
    :return: Float indicating difficulty of schedule. 0 means tougher
    """

    game_id_list: list[int] = get_games_as_id_list(team)  # get games the team played in as game-id's

    dif = 0  # tracks the difficulty of the opponents based on seed (golf rules)
    top_64 = 0  # tracks how many top 64 seeds they played

    for game_id in game_id_list:  # loop through games
        o_as_rec = get_opponent_as_record(team, game_id)  # get opponent
        opponent = o_as_rec.iloc[0]['TEAM']  # actually gets the string rather than a data frame of the opponent

        # Check to see if the opponent is in the top 64
        if opponent in tournament_dataframe['TEAM_NAME'].tolist():

            top_64 = top_64 + 1  # Increment the number of top 64 teams they play

            # get opponents seed
            opp_dif = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == opponent]['SEED'].iloc[0]
            dif = dif + opp_dif  # add up the difficulty (golf rules)

    # special case if the team never plays a top 64
    if top_64 == 0:
        return 32  # return 32 this puts them outside of any team that plays at least one top 64 team
    else:
        dif_avg = dif / top_64  # get the average difficulty (golf rules)

        # divide the average difficulty by the number of top 64 teams they played
        # this ensures that a team that played a 1, 1 time will have a higher sos than a team that played 1, 2 times.
        s_o_s = dif_avg / top_64  # divide the average difficulty by the number of top 64 teams they played

        return s_o_s


def perf_inv(seed: int) -> int:
    """
    Returns the inversion of their seed. So a 1's inversion is 16 and a 10's inversion is 7
    :param seed: seed of a team
    :return: The inverted seed
    """
    return 17 - seed


def get_seed(team: str) -> int:
    """
    Return the seed of a team
    :param team: team name
    :return: seed
    """
    return tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['SEED'].iloc[0]


def get_reg_s_perf(team: str) -> int:
    """
    Returns the regular season performance of a team. This is a Matt R. algorithm that looks at all top 64 seed games
    during the regular season and the expected win loss based on the inversion calculator.  The more likely the win the
    less the win counts toward performance.  The harder the win the more the win counts.  Losses take away the
    performance and work in a similar fashion. If the loss is expected then the loss doesn't negatively affect the
    performance that much and vice versa.
    :param team: team name
    :return: performance of team during regular season. The higher the better.
    """
    game_id_list = get_games_as_id_list(team)  # get game list

    perf = 0
    for game_id in game_id_list:  # loop through each game
        o_as_rec = get_opponent_as_record(team, game_id)  # get opponent record
        opponent = o_as_rec.iloc[0]['TEAM']  # silly code that acctually gets their string rather than a dataframe

        # if the opponent is in the top 64
        if opponent in tournament_dataframe['TEAM_NAME'].tolist():
            seed = get_seed(opponent)  # get their seed
            win_or_lose = did_win(team, game_id)  # check to see if they win
            if win_or_lose:
                perf = perf + perf_inv(seed)  # if they win give them more perf based on likelyhood of win
            else:
                perf = perf - get_seed(opponent)  # if they lose make them lose perf based on likelyhood of loss

    return perf


def get_region(team: str) -> str:
    """
    Get region of team
    :param team: team name
    :return: region
    """
    region = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['REGION'].iloc[0]
    return region


def all_caps_to_capital_first(text: str) -> str:
    """
    This takes a string and capitalizes the first letter of each word
    :param text: any text
    :return:
    """
    text = text.lower()
    return text.capitalize()


def get_nate_silver_grade(team: str) -> float:
    """
    Returns the nate silver grade based on the team name
    I realized at this point that each team has a unique AND SHARED ** SEED and REGION **
    This means I probably don't need to ever type in team names in the top 64 I can just use anyone else's team names
    for that
    :param team: team name
    :return: Nate Silver's Team Grade (0 - 100) 100 is better
    """

    return other_data_N[other_data_N['Team'] == team]['Current Elo'].iloc[0]
    # seed = get_seed(team)
    # region = get_region(team)
    # region = all_caps_to_capital_first(region)  # Nate's region is a bit different

    # return other_data_N[(other_data_N['SEED'] == seed) & (other_data_N['REGION'] == region)]['NSGRADE'].iloc[0]


def win_loss_difference_strength_of_schedule(win: int, loss: int, strength_of_schedule: float) -> float:
    """
    Returns the win loss difference divided by the strenght of schedule

    This means the higher the output the better the team

    :return:
    """

    # In the crazy situation that the team has a win loss delta of 0 or less than 0 then return 0 the lowest score
    if (win - loss) <= 0:
        return 0

    windifsos: float = (win - loss) / strength_of_schedule

    return windifsos


def get_MELO(team: str) -> int:
    """
    Returns the MELO based on the team name
    :param team:
    :return:
    """
    analysis_df = pandas.read_csv('../../../../MattsMarchMadness2/backend/analysis.csv')

    return int(analysis_df[analysis_df['TEAM'] == team]['MELO'].iloc[0])


def normalize_1_to_100(values: list[any]) -> tuple:
    """
    Returns the scaling factor along with the shift required with the new min value and old minimum value

    :param values:
    :return: (scaling factor, new minumum, old minumum)
    """
    new_min: float = 1
    new_max: float = 100

    old_minimum_value = min(values)
    old_maximum_value = max(values)

    old_range = old_maximum_value - old_minimum_value
    new_range = new_max - new_min  # set all values between 100 and 1

    scale_factor = new_range / old_range

    return scale_factor, new_min, old_minimum_value

def create_analysis() -> pandas.DataFrame:
    # get list of teams
    team_list: list[str] = tournament_dataframe['TEAM_NAME'].tolist()

    # declare the analysis dictionary
    analysis_dictionary = {'TEAM': [], 'SEED': [], 'WINS': [], 'LOSSES': [], 'SOS': [], 'REGION': [], 'ORDER': [],
                           'WINDIFSOS': [], 'SCH_PERF': [], 'NSGRADE': [], 'MELO': []}

    # TEAM: name of team as                 str
    # SEED: seed given to team              int
    # WINS: wins during regular season      int
    # LOSSES: losses during regular season  int
    # SOS: strength of schedule (my calc)   float   Most close to 0. The closest to 0 the harder the schedule
    # REGION: region in tourney             str
    # ORDER: order in region                int     This is a visual order and indicates who is playing who in regions
    # WINDIFSOS: ??????????????             float   ????????
    # SHC_PERF: schedule performance        int     How good a team did during their schedule. ?????
    # NSGRADE: Nate Silver Score            float   0-100. The closer to 100 the better.
    # MELO: Matt's ELO                      int     Higher the better. Combination of NSGRADE, WINDIFSOS and SCH_PERF

    # Loop Calculates the values for each team
    for team in team_list:
        sos = strength_of_schedule_calculator(team)  # calculate the strength of schedule

        seed = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['SEED'].iloc[0]  # get the seed

        win_loss = get_record(team)  # get the win loss record as a tuple (W L)
        wins = win_loss[0]
        losses = win_loss[1]

        region = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['REGION'].iloc[0]
        order = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['ORDER_IN_REGION'].iloc[0]

        win_loss_dif_sos = win_loss_difference_strength_of_schedule(wins, losses, sos)
        perf = get_reg_s_perf(team)

        ns_elo = get_nate_silver_grade(team)

        # add data to analysis dictionary
        analysis_dictionary['TEAM'].append(team)
        analysis_dictionary['SEED'].append(seed)
        analysis_dictionary['WINS'].append(wins)
        analysis_dictionary['LOSSES'].append(losses)
        analysis_dictionary['SOS'].append(sos)
        analysis_dictionary['REGION'].append(region)
        analysis_dictionary['ORDER'].append(order)
        analysis_dictionary['WINDIFSOS'].append(win_loss_dif_sos)
        analysis_dictionary['SCH_PERF'].append(perf)
        analysis_dictionary['NSGRADE'].append(ns_elo)

    # ---NORMALIZATION OF DATA---

    normalize_tuple_wds = normalize_1_to_100(analysis_dictionary['WINDIFSOS'])
    normalize_tuple_sp = normalize_1_to_100(analysis_dictionary['SCH_PERF'])
    normalize_tuple_nsg = normalize_1_to_100(analysis_dictionary['NSGRADE'])

    for i, team in enumerate(team_list):
        adjusted_win_dif_sos = (analysis_dictionary['WINDIFSOS'][i] - normalize_tuple_wds[2]) * normalize_tuple_wds[0] + \
                               normalize_tuple_wds[1]
        analysis_dictionary['WINDIFSOS'][i] = adjusted_win_dif_sos

        adjusted_perf = (analysis_dictionary['SCH_PERF'][i] - normalize_tuple_sp[2]) * normalize_tuple_sp[0] + \
                        normalize_tuple_sp[1]
        analysis_dictionary['SCH_PERF'][i] = adjusted_perf

        adjusted_ns_elo = (analysis_dictionary['NSGRADE'][i] - normalize_tuple_nsg[2]) * normalize_tuple_nsg[0] + \
                          normalize_tuple_nsg[1]
        analysis_dictionary['NSGRADE'][i] = adjusted_ns_elo

        weight_windifsos = 0.5
        weight_schedule_performance = 2.5
        weight_nate_silver = 5.0

        melo = (
                (analysis_dictionary['WINDIFSOS'][i] ** weight_windifsos) *
                (analysis_dictionary['SCH_PERF'][i] ** weight_schedule_performance) *
                (analysis_dictionary['NSGRADE'][i] ** weight_nate_silver)
        )

        analysis_dictionary['MELO'].append(int(math.log(melo) * 50))

    sos_df = pandas.DataFrame(analysis_dictionary)

    sos_df['SOS'] = sos_df['SOS'].round(decimals=2)
    sos_df['WINDIFSOS'] = sos_df['WINDIFSOS'].round(decimals=2)
    sos_df['SCH_PERF'] = sos_df['SCH_PERF'].round(decimals=2)
    sos_df['MELO'] = sos_df['MELO'].round(decimals=0)
    sos_df['NSGRADE'] = sos_df['NSGRADE'].round(decimals=2)

    sorted_sos = sos_df.sort_values('MELO', ascending=False).reset_index(drop=True)
    sorted_sos['RANK'] = range(1, len(sorted_sos) + 1)

    # Reorder the columns so RANK is first
    sorted_sos = sorted_sos[['RANK'] + [col for col in sorted_sos.columns if col != 'RANK']]

    return sorted_sos


def main():
    """
    Main Initializing function

    Creates the analysis.csv file which contains the ELO values for all the teams which determines their success
    during the simulated tournament

    It also prints out the values of the CSV file in the end

    :return:
    """

    # get list of teams
    team_list: list[str] = tournament_dataframe['TEAM_NAME'].tolist()

    # declare the analysis dictionary
    analysis_dictionary = {'TEAM': [], 'SEED': [], 'WINS': [], 'LOSSES': [], 'SOS': [], 'REGION': [], 'ORDER': [],
                                 'WINDIFSOS': [], 'SCH_PERF': [], 'NSGRADE': [], 'MELO': []}

    # TEAM: name of team as                 str
    # SEED: seed given to team              int
    # WINS: wins during regular season      int
    # LOSSES: losses during regular season  int
    # SOS: strength of schedule (my calc)   float   Most close to 0. The closest to 0 the harder the schedule
    # REGION: region in tourney             str
    # ORDER: order in region                int     This is a visual order and indicates who is playing who in regions
    # WINDIFSOS: ??????????????             float   ????????
    # SHC_PERF: schedule performance        int     How good a team did during their schedule. ?????
    # NSGRADE: Nate Silver Score            float   0-100. The closer to 100 the better.
    # MELO: Matt's ELO                      int     Higher the better. Combination of NSGRADE, WINDIFSOS and SCH_PERF

    # Loop Calculates the values for each team
    for team in team_list:
        sos = strength_of_schedule_calculator(team)  # calculate the strength of schedule

        seed = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['SEED'].iloc[0]  # get the seed

        win_loss = get_record(team)  # get the win loss record as a tuple (W L)
        wins = win_loss[0]
        losses = win_loss[1]

        region = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['REGION'].iloc[0]
        order = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['ORDER_IN_REGION'].iloc[0]

        win_loss_dif_sos = win_loss_difference_strength_of_schedule(wins, losses, sos)
        perf = get_reg_s_perf(team)

        ns_elo = get_nate_silver_grade(team)

        # add data to analysis dictionary
        analysis_dictionary['TEAM'].append(team)
        analysis_dictionary['SEED'].append(seed)
        analysis_dictionary['WINS'].append(wins)
        analysis_dictionary['LOSSES'].append(losses)
        analysis_dictionary['SOS'].append(sos)
        analysis_dictionary['REGION'].append(region)
        analysis_dictionary['ORDER'].append(order)
        analysis_dictionary['WINDIFSOS'].append(win_loss_dif_sos)
        analysis_dictionary['SCH_PERF'].append(perf)
        analysis_dictionary['NSGRADE'].append(ns_elo)


    # ---NORMALIZATION OF DATA---

    normalize_tuple_wds = normalize_1_to_100(analysis_dictionary['WINDIFSOS'])
    normalize_tuple_sp = normalize_1_to_100(analysis_dictionary['SCH_PERF'])
    normalize_tuple_nsg = normalize_1_to_100(analysis_dictionary['NSGRADE'])

    for i, team in enumerate(team_list):

        adjusted_win_dif_sos = (analysis_dictionary['WINDIFSOS'][i] - normalize_tuple_wds[2]) * normalize_tuple_wds[0] + normalize_tuple_wds[1]
        analysis_dictionary['WINDIFSOS'][i] = adjusted_win_dif_sos

        adjusted_perf = (analysis_dictionary['SCH_PERF'][i] - normalize_tuple_sp[2]) * normalize_tuple_sp[0] + normalize_tuple_sp[1]
        analysis_dictionary['SCH_PERF'][i] = adjusted_perf

        adjusted_ns_elo = (analysis_dictionary['NSGRADE'][i] - normalize_tuple_nsg[2]) * normalize_tuple_nsg[0] + normalize_tuple_nsg[1]
        analysis_dictionary['NSGRADE'][i] = adjusted_ns_elo

        weight_windifsos = 0.5
        weight_schedule_performance = 2.5
        weight_nate_silver = 5.0

        melo = (
            (analysis_dictionary['WINDIFSOS'][i] ** weight_windifsos) *
            (analysis_dictionary['SCH_PERF'][i] ** weight_schedule_performance) *
            (analysis_dictionary['NSGRADE'][i] ** weight_nate_silver)
        )

        analysis_dictionary['MELO'].append(int(math.log(melo) * 50))

    sos_df = pandas.DataFrame(analysis_dictionary)

    sos_df['SOS'] = sos_df['SOS'].round(decimals=2)
    sos_df['WINDIFSOS'] = sos_df['WINDIFSOS'].round(decimals=2)
    sos_df['SCH_PERF'] = sos_df['SCH_PERF'].round(decimals=2)
    sos_df['MELO'] = sos_df['MELO'].round(decimals=0)
    sos_df['NSGRADE'] = sos_df['NSGRADE'].round(decimals=2)

    sorted_sos = sos_df.sort_values('MELO', ascending=False).reset_index(drop=True)
    sorted_sos['RANK'] = range(1, len(sorted_sos) + 1)

    # Reorder the columns so RANK is first
    sorted_sos = sorted_sos[['RANK'] + [col for col in sorted_sos.columns if col != 'RANK']]

    sorted_sos.to_csv('analysis.csv', index=False)

    print(sorted_sos.to_string())

    # bracket.visualize_ncaab_bracket('marchMadTable_2024.csv')
    # print(bracket.line_to_round(12,16))
    # print(bracket.get_upper_bound(23,3))

    # name = bracket.find_team_name_in_csv(1, 15, 15, 'SOUTH', 'marchMadTable_2024.csv')
    # print(name)


if __name__ == '__main__':
    main()
