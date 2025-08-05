"""
File initializes the bracket simulator

Mostly it does this by calculating the MELO scores for each team
"""

import bracket_storage
import bracket
import sys  # base python
from datetime import date

def main() -> None:
    """
    function can be ran from terminal with
    ```
    python [tournament_info_file.csv]
    ```

    if file is ran without this argument then it will default to looking for:
    marchMadness_YYYY.csv

    This function needs to be run once upon the following conditions:

    1. there is a march madness YYYY.csv file with below columns
    # TEAM NAME: must align with the season record tables (and must be same as any other analysis tables)
    # current package its 2 hidden files not in git because of proprietary reasons
    # SEED: 1 - 16
    # REGION: ALL CAPS one word
    # FIRST_FOUR: blank or A or B (A for top and B for bottom based on NCAA site bracket)

    2. there may need to be other analysis tables with matching team names or pos ids (current is team name match)
    """

    # check to see if there were arguments
    tourney_path = ""
    if len(sys.argv) == 1:
        tourney_path = sys.argv[1]

    # if no path is given try default and notify user
    if tourney_path == "":
        year = date.today().year
        print(f"No tournament path provided: Using default file path: marchMadness_{year}.csv")
        tourney_path = f"marchMadness_{year}.csv"

    # create positional_id_map
    positional_id_map = bracket_storage.setup_positional_id_map(tourney_path)

    # create initial bracket map (keys are round made it to)
    initial_bracket = bracket_storage.setup_initial_bracket(positional_id_map)

    # create analysis and add to positional_id_map





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


