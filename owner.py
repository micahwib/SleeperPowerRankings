import statistics
import operator

class Owner:
    owner_id = ''
    roster_id = 0
    wins = 0
    ties = 0
    losses = 0
    total_moves = 0
    display_name = ''
    avatar = ''
    points_for = []
    points_against = []
    current_rank = 0
    previous_rank = 0
    consistency = 0

    def __init__(self, owner_id, total_moves, display_name, avatar, roster_id):
        self.owner_id = owner_id
        self.wins = 0
        self.ties = 0
        self.losses = 0
        self.total_moves = total_moves
        self.display_name = display_name
        self.avatar = avatar
        self.points_for = []
        self.points_against = []
        self.previous_rank = 0
        self.current_rank = 0
        self.roster_id = roster_id
        self.consistency = 0

    def set_rank(self, rank):
        self.previous_rank = self.current_rank
        self.current_rank = rank

    def set_consistency(self, consistency):
        self.consistency = consistency

    def get_rank(self):
        return self.current_rank

    def get_rank_change(self):
        return self.previous_rank - self.current_rank

    def add_points_for(self, points_for):
        self.points_for.append(points_for)

    def add_points_against(self, points_against):
        self.points_against.append(points_against)

    def add_tie(self):
        self.ties += 1

    def add_win(self):
        self.wins += 1

    def add_loss(self):
        self.losses += 1

    def get_record(self):
        return str(self.wins) + '-' + str(self.losses) + '-' + str(self.ties)

    def get_raw_OIL_score(self):
        avg_points = statistics.mean(self.points_for)
        min_points = max(self.points_for)
        max_points = min(self.points_for)

        week = len(self.points_for)
        if week == 0:
            week = 1

        OIL_raw_score = ((avg_points * 6) + ((max_points + min_points) * 2) + (((self.wins / week) * 200) * 2)) / 10
        return OIL_raw_score

    def get_avg_ppg(self):
        return statistics.mean(self.points_for)

    def get_stdev(self):
        return statistics.stdev(self.points_for)

