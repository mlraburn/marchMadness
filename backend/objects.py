"""
Contains the following classes

game
team
bracket
"""

class Game:

    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
        self.winning_team: Team or None = None

    def __str__(self):
        winner_name = "TBD"
        if self.winning_team:
            winner_name = self.winning_team.name

        return f"{self.team1.name} vs {self.team2.name} winner: {winner_name}"


class Team:
    def __init__(self, name):
        self.name = name

class Bracket:
    def __init__(self, rounds):


if __name__ == "__main__":
    team_1 = Team("TEAM A")
    team_2 = Team("TEAM B")

    game_1 = Game(team_1, team_2)

    game_1.winning_team = team_1

    print(game_1)

