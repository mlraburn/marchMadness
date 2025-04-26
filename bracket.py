import csv
import math
import pandas
import dataDownLoad

regions = ['EAST', 'WEST', 'SOUTH', 'MIDWEST']


def visualize_ncaab_bracket(path: str) -> None:
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
