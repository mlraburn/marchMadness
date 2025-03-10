"""
Initializing File

This file creates the analysis of the schedule and generates the ELO values that each team will have to determine
their success throughout the simulated bracket

"""
import pandas   # pip install pandas
import math     # base python
import bracket  # custom package with bracket functions

# FILE WIDE VARIABLES
# -------------------

# Schedule information
schedule_dataframe_raw: pandas.DataFrame = pandas.read_excel("03-16-2024-cbb-season-team-feed.xlsx")  # file is downloaded from ???
schedule_dataframe: pandas.DataFrame = schedule_dataframe_raw[['GAME-ID', 'TEAM', 'F']]  # filter these columns in the excel file
# GAME-ID: unique integer for each game.  A game consists of 2 rows one for each team in the game but with the same
# GAME-ID.
# TEAM: team name as string
# F: points scored as an integer

# load the marchMadness table which has initial values of the tourney
# marchMadness table is set manually
tournament_dataframe: pandas.DataFrame = pandas.read_csv('marchMadTable.csv')

# load Nate Silvers Data
nate_silver_data: pandas.DataFrame = pandas.read_csv('NSData.csv')


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


def sched_dif(team: str) -> float:
    """
    Returns the difficulty of schedule

    This is a Matt R. algorithm for this that takes into account the final seed value of the teams they played
    The more seeded teams a team plays and the higher their seeds the lower the value will be approaching 0

    ** NOTE ** this assumes the first four have already played their game and we know who advanced.

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
            top_64 = top_64 + 1
            opp_info = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == opponent]
            opp_dif = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == opponent]['SEED'].iloc[0]  # get opponents seed
            dif = dif + opp_dif  # add up the difficulty

    # special case if the team never plays a top 64
    if top_64 == 0:
        return 32 * 64  # no clue if this is correct but it makes them have the weakest schedule no matter what
    else:
        dif_avg = dif / top_64  # get the average difficulty (golf rules)
        s_o_s = dif_avg / top_64  # I don't remembe why I did this but there was a reason
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
    :return: performance of team during regular season.  The higher the better.
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

    # -43 was lowest on first run
    # perf + 43 adds the adjustment so they don't have any negative values
    return perf + 43


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
    seed = get_seed(team)
    region = get_region(team)
    region = all_caps_to_capital_first(region)  # Nate's region is a bit different

    return nate_silver_data[(nate_silver_data['SEED'] == seed) & (nate_silver_data['REGION'] == region)]['NSGRADE'].iloc[0]


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
        sos = sched_dif(team)
        analysis_dictionary['TEAM'].append(team)
        seed = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['SEED'].iloc[0]
        win_loss = get_record(team)
        wins = win_loss[0]
        losses = win_loss[1]
        analysis_dictionary['SEED'].append(seed)
        analysis_dictionary['WINS'].append(wins)
        analysis_dictionary['LOSSES'].append(losses)
        analysis_dictionary['SOS'].append(sos)
        region = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['REGION'].iloc[0]
        analysis_dictionary['REGION'].append(region)
        order = tournament_dataframe[tournament_dataframe['TEAM_NAME'] == team]['ORDER_IN_REGION'].iloc[0]
        analysis_dictionary['ORDER'].append(order)

        # minimum is -4 + (2/3.0)
        # adjust by adding the above min
        win_loss_sos = (wins - losses) / sos
        win_loss_sos = abs(win_loss_sos + 4 + (2 / 3))
        win_loss_sos = win_loss_sos.__round__(1) + 1
        analysis_dictionary['WINDIFSOS'].append(win_loss_sos)
        perf = get_reg_s_perf(team) + 1
        analysis_dictionary['SCH_PERF'].append(perf)
        ns_grade = get_nate_silver_grade(team)
        analysis_dictionary['NSGRADE'].append(ns_grade)
        melo = win_loss_sos * perf * ns_grade + 1
        analysis_dictionary['MELO'].append((math.log(melo) * 100).__round__(0))

    sos_df = pandas.DataFrame(analysis_dictionary)

    sorted_sos = sos_df.sort_values('MELO', ascending=False)
    sos_df.to_csv('analysis.csv')

    print(sorted_sos.to_string())

    print(bracket.elo_prob(1148, 1037))

    # bracket.visualize_ncaab_bracket('marchMadTable.csv')
    # print(bracket.line_to_round(12,16))
    # print(bracket.get_upper_bound(23,3))

    # name = bracket.find_team_name_in_csv(1, 15, 15, 'SOUTH', 'marchMadTable.csv')
    # print(name)


if __name__ == '__main__':
    main()
