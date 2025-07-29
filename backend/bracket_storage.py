"""
File contains functions for storing and loading bracket data

Bracket schema

Each team gets a positional name
E01 indicates the East regions number one seed

The extra 68 teams get a positional name that has an extra A or B at the end
so E16A for a team that is in the 0th round of the tournament

SW play each other in final four

EM play each other in final four

The bracket gets stored where

{E16A, 0} would indicate that this team lost in the first 4 games which is sorta the 0th round
this would imply that E16B would have a record in the bracket storage that was at least a 1 or greater

"""

import csv  #base

def setup_positional_id_map(csv_file) -> dict:
    """
    Creates a positional id for each team
    Positional Map: Team Name

    CSV file must contain the following headers below
    Headers: TEAM_NAME,SEED,REGION
    Optional Headers: FIRST_FOUR with A or B as the value for the teams that play each other

    :param csv_file: default to analysis.csv but can be set to any file name
    :return: Returns a dictionary mapping positional id with Team name
    """
    positional_id_map = {}

    # open csv file and read file
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        teams = list(reader)

        # loop through each team and create map
        for team in teams:
            team_name = team['TEAM_NAME']
            seed = team['SEED']
            region = team['REGION']

            # this is an extra identifier for the first four teams
            a_or_b = ""
            if 'FIRST_FOUR' in team:
                a_or_b = team['FIRST_FOUR']

                if a_or_b not in ['A', 'B']:
                    a_or_b = ""

            # create region identifier by first letter of region {E W M S}
            positional_id = f"{region[0]}{seed.zfill(2)}{a_or_b}"

            positional_id_map[positional_id] = team_name

    return positional_id_map

def setup_initial_bracket(positional_id_dict: dict) -> dict:
    """
    Creates the initial bracket using the positional id map

    This function is pretty simple because it sets up all teams to round 1

    ** EXCEPT IT PUTS FIRST FOUR TEAMS AT ROUND 0 **

    :param positional_id_dict:
    :return: returns a dictionary with initial bracket positions
    """

    initial_bracket = {}

    for positional_id in positional_id_dict:

        if positional_id[-1] in ['A', 'B']:
            initial_bracket[positional_id] = 0
        else:
            initial_bracket[positional_id] = 1

    return initial_bracket

if __name__ == "__main__":
    """
    Contains testing for file
    """

    positional_id_map = setup_positional_id_map()
    initial_bracket = setup_initial_bracket(positional_id_map)

    # Print to test
    for position_id, team_name in positional_id_map.items():
        print(f"{position_id}: {team_name}")

    print()

    for position_id, last_round in initial_bracket.items():
        print(f"{position_id}: {last_round}")