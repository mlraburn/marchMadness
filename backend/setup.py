"""
File initializes the bracket simulator

Mostly it does this by calculating the MELO scores for each team
"""

import bracket_storage
import bracket
import sys  # base python
from datetime import date
import data_download

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
    if len(sys.argv) > 1:
        tourney_path = sys.argv[1]

    # if no path is given try default and notify user
    if tourney_path == "":
        year = date.today().year
        print(f"No tournament path provided: Using default file path: marchMadness_{year}.csv")
        tourney_path = f"marchMadTable_{year}.csv"

    # create positional_id_map
    positional_id_map = bracket_storage.setup_positional_id_map(tourney_path)

    # DEBUG BLOCK
    for p in positional_id_map:
        print(f"positional id map: {p} value: {positional_id_map[p]}")
    # DEBUG BLOCK

    # create initial bracket map (keys are round made it to)
    initial_bracket = bracket_storage.setup_initial_bracket(positional_id_map)

    # create analysis
    data_download.main()

    # add MELO to the positional_id_map
    pos_id_plus_melo_map = data_download.add_melo_to_positional_map(positional_id_map)

    # print out pos id melo map
    for pos_id in pos_id_plus_melo_map:
        print(f"Position ID: {pos_id} Name: {pos_id_plus_melo_map[pos_id]['name']} Melo: {pos_id_plus_melo_map[pos_id]['melo']}")

    # EVENTUALLY WE WANT TO MAKE THIS MAP IN THIS ORDER TO BE PUT INTO A CONFIG FILE OF SORTS
    # THIS WILL BE THE MAIN WAY WE SIMULATE TOURNAMENTS
    # THE ORDER PRESERVES THE TOURNEY STRUCTURE IN O(1) TIME
    # THE ONLY ISSUE WE NEED TO WORK OUT IS HOW TO HANDLE THE A/B'S

    # DEBUG BLOCK
    # WE WILL HAVE THE SIMULATOR BE ITS OWN FUNCTION
    # BUT FOR NOW WE WILL JUST HAVE IT HERE TO SEE IF IT WORKS

    for round_ in initial_bracket:
        print(f"Round: {round_}")
        print()

        games_to_play = bracket.get_games_for_a_round(initial_bracket)

        initial_bracket = bracket.play_a_round(games_to_play, initial_bracket, pos_id_plus_melo_map)

        for r in initial_bracket:
            print(f"Round: {r}")

        print()


    # END DEBUG BLOCK



if __name__ == '__main__':

    # grab the 68 table with the following properties
    # TEAM NAME: must align with the season record tables (and must be same as any other analysis tables)
    # current package its 2 hidden files not in git because of proprietary reasons
    # SEED: 1 - 16
    # REGION: ALL CAPS one word
    # FIRST_FOUR: blank or A or B (A for top and B for bottom based on NCAA site bracket)

    main()

    """
    positional_id_map = bracket_storage.setup_positional_id_map('marchMadTable_2025.csv')

    for team in positional_id_map:
        print(f"pos id: {team.ljust(4)} name: {positional_id_map[team]}")

    initial_bracket = bracket_storage.setup_initial_bracket(positional_id_map)

    print(f"initial bracket: {initial_bracket}")
    print()

    games_to_play = bracket.get_games_for_a_round(initial_bracket)

    for game in games_to_play:
        print(game)
    """


