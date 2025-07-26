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

if __name__ == "__main__":
    """
    Contains testing for file
    """

    # grab bracket start file (manually typed or created)
    # convert to a starting bracket database store with all final positions being 0
    with open('analysis.csv', 'r') as file:
        reader = csv.DictReader(file)
        teams = list(reader)

        # 1. Make a map of position id to team data
        # 2. Make the initial bracket state
        position_id_map = {}
        bracket_result_dict = {}
        for team in teams:
            team_name = team['TEAM']

            # create the position ID
            seed = team['SEED']
            region = team['REGION']

            position_id = f"{region[0]}{seed.zfill(2)}"

            # add position ID to map with name being the value
            position_id_map[position_id] = team_name

            # create the initial bracket database situation
            bracket_result_dict[position_id] = 0


    # Print to test
    for position_id, team_name in position_id_map.items():
        print(f"{position_id}: {team_name}")

    print()

    for position_id, last_round in bracket_result_dict.items():
        print(f"{position_id}: {last_round}")














