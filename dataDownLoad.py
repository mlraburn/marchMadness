import pandas
import math

sd_raw = pandas.read_excel("03-16-2024-cbb-season-team-feed.xlsx")
sd = sd_raw[['GAME-ID', 'TEAM', 'F']]

td = pandas.read_csv('marchMadTable.csv')
nsd = pandas.read_csv('NSData.csv')


def get_game(game_id) -> pandas.DataFrame:
    game = sd[sd['GAME-ID'] == game_id]
    return game


def get_games(team) -> pandas.DataFrame:
    game_ids = get_games_as_id_list(team)
    games = sd[sd['GAME-ID'].isin(game_ids)]
    return games


def get_opponent_as_record(team, gameID) -> pandas.DataFrame:
    game = get_game(gameID)
    opponent = game[game['TEAM'] != team]
    return opponent


def get_score(team: str, game_id: int) -> int:
    game = get_game(game_id)
    score = game[game['TEAM'] == team]
    return score.iloc[0]['F']


def get_games_as_id_list(team) -> list:
    games = sd[sd['TEAM'] == team]

    return games['GAME-ID'].tolist()


def did_win(team, game_id) -> bool:
    opponent = get_opponent_as_record(team, game_id).iloc[0]['TEAM']
    team_score = get_score(team, game_id)

    opp_score = get_score(opponent, game_id)

    if team_score > opp_score:
        return True
    else:
        return False


def get_record(team) -> tuple:
    games_list = get_games_as_id_list(team)

    wins = 0
    losses = 0
    for game_id in games_list:
        if did_win(team, game_id):
            wins = wins + 1
        else:
            losses = losses + 1
    return wins, losses


def sched_dif(team) -> int:
    game_id_list = get_games_as_id_list(team)

    dif = 0
    top_64 = 0
    for game_id in game_id_list:
        o_as_rec = get_opponent_as_record(team, game_id)
        opponent = o_as_rec.iloc[0]['TEAM']

        if opponent in td['TEAM_NAME'].tolist():
            top_64 = top_64 + 1
            opp_info = td[td['TEAM_NAME'] == opponent]
            opp_dif = td[td['TEAM_NAME'] == opponent]['SEED'].iloc[0]
            dif = dif + opp_dif
    if top_64 == 0:
        return 32 * 64
    else:
        dif_avg = dif / top_64
        s_o_s = dif_avg / top_64
        return s_o_s


def perf_inv(seed) -> int:
    return 17 - seed


def get_seed(team) -> int:
    return td[td['TEAM_NAME'] == team]['SEED'].iloc[0]


def get_reg_s_perf(team) -> int:
    game_id_list = get_games_as_id_list(team)

    perf = 0
    for game_id in game_id_list:
        o_as_rec = get_opponent_as_record(team, game_id)
        opponent = o_as_rec.iloc[0]['TEAM']

        if opponent in td['TEAM_NAME'].tolist():
            seed = get_seed(opponent)
            win_or_lose = did_win(team, game_id)
            if win_or_lose:
                perf = perf + perf_inv(seed)
            else:
                perf = perf - get_seed(opponent)

    # -43 was lowest on first run
    # perf + 43 adds the adjustment
    return perf + 43


def get_region(team) -> str:
    region = td[td['TEAM_NAME'] == team]['REGION'].iloc[0]
    return region


def all_caps_to_capital_first(text: str) -> str:
    text = text.lower()
    return text.capitalize()


def get_nate_silver_grade(team) -> float:
    seed = get_seed(team)
    region = get_region(team)
    region = all_caps_to_capital_first(region)

    return nsd[(nsd['SEED'] == seed) & (nsd['REGION'] == region)]['NSGRADE'].iloc[0]


def main():
    t_list = td['TEAM_NAME'].tolist()

    sos_dict = {'TEAM': [], 'SEED': [], 'WINS': [], 'LOSSES': [], 'SOS': [], 'REGION': [], 'ORDER': [], 'WINDIFSOS': [],
                'SCH_PERF': [], 'NSGRADE': [], 'MELO': []}

    for team in t_list:
        sos = sched_dif(team)
        sos_dict['TEAM'].append(team)
        seed = td[td['TEAM_NAME'] == team]['SEED'].iloc[0]
        win_loss = get_record(team)
        wins = win_loss[0]
        losses = win_loss[1]
        sos_dict['SEED'].append(seed)
        sos_dict['WINS'].append(wins)
        sos_dict['LOSSES'].append(losses)
        sos_dict['SOS'].append(sos)
        region = td[td['TEAM_NAME'] == team]['REGION'].iloc[0]
        sos_dict['REGION'].append(region)
        order = td[td['TEAM_NAME'] == team]['ORDER_IN_REGION'].iloc[0]
        sos_dict['ORDER'].append(order)

        # minimum is -4 + (2/3.0)
        # adjust by adding the above min
        win_loss_sos = (wins - losses) / sos
        win_loss_sos = abs(win_loss_sos + 4 + (2/3))
        win_loss_sos = win_loss_sos.__round__(1) + 1
        sos_dict['WINDIFSOS'].append(win_loss_sos)
        perf = get_reg_s_perf(team) + 1
        sos_dict['SCH_PERF'].append(perf)
        ns_grade = get_nate_silver_grade(team)
        sos_dict['NSGRADE'].append(ns_grade)
        melo = win_loss_sos*perf*ns_grade + 1
        sos_dict['MELO'].append((math.log(melo)*100).__round__(0))

    sos_df = pandas.DataFrame(sos_dict)

    sorted_sos = sos_df.sort_values('MELO',ascending=False)

    print(sorted_sos.to_string())


if __name__ == '__main__':
    main()
