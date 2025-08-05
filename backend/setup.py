"""
File initializes the bracket simulator

Mostly it does this by calculating the MELO scores for each team
"""

import bracket_storage
import bracket

def main() -> None:
    """
    This function needs to be run once upon the following conditions:

    1. there is a march madness YYYY.csv file with below columns
    # TEAM NAME: must align with the season record tables (and must be same as any other analysis tables)
    # current package its 2 hidden files not in git because of proprietary reasons
    # SEED: 1 - 16
    # REGION: ALL CAPS one word
    # FIRST_FOUR: blank or A or B (A for top and B for bottom based on NCAA site bracket)

    2. there may need to be other analysis tables with matching team names or pos ids (current is team name match)
    """



if __name__ == '__main__':

    # grab the 68 table with the following properties
    # TEAM NAME: must align with the season record tables (and must be same as any other analysis tables)
    # current package its 2 hidden files not in git because of proprietary reasons
    # SEED: 1 - 16
    # REGION: ALL CAPS one word
    # FIRST_FOUR: blank or A or B (A for top and B for bottom based on NCAA site bracket)

    positional_id_map = bracket_storage.setup_positional_id_map('marchMadTable_2025.csv')

    for team in positional_id_map:
        print(f"pos id: {team.ljust(4)} name: {positional_id_map[team]}")

    initial_bracket = bracket_storage.setup_initial_bracket(positional_id_map)

    print(f"initial bracket: {initial_bracket}")
    print()

    games_to_play = bracket.get_games_for_a_round(initial_bracket)

    for game in games_to_play:
        print(game)


