"""
File initializes the bracket simulator

Mostly it does this by calculating the MELO scores for each team
"""

import bracket_storage
import bracket

if __name__ == '__main__':

    # grab the 68 table with the following properties
    # TEAM NAME: must align with the season record tables
    # SEED: 1 - 16
    # REGION: ALL CAPS one word
    # FIRST_FOUR: blank or A or B (A for top and B for bottom based on NCAA site bracket)

    positional_id_map = bracket_storage.setup_positional_id_map('marchMadTable_2025.csv')
    initial_bracket = bracket_storage.setup_initial_bracket(positional_id_map)

    games_to_play = bracket.get_games_for_a_round(initial_bracket)

    for game in games_to_play:
        print(game)
