from unittest import TestCase
from parameterized import parameterized
from challenge_utils import challenge_score_v2

SPRINT_RACE_IN_TICKS = 20 * 60 * 10000  # 20 minutes
IMSA_RACE_IN_TICKS = 50 * 60 * 10000  # 50 minutes
ENDURO_RACE_IN_TICKS = 360 * 60 * 10000  # 6hrs
ROAR_RACE_IN_TICKS = 144 * 60 * 10000  # 2.4hrs

class TestChallengeScoreV2(TestCase):

    @parameterized.expand([
        ("sprint_grand_slam_from_pole", SPRINT_RACE_IN_TICKS, 15, 0, 1, 1, 482, 14, 12.2),
        ("enduro_grand_slam_from_pole", ENDURO_RACE_IN_TICKS, 15, 0, 1, 1, 482, 14, 45.8),
        ("enduro_mid", ENDURO_RACE_IN_TICKS, 30, 14, 8, 6, 421, 120, 2.3),
        ("zeroex_no_laps", SPRINT_RACE_IN_TICKS, 35, 0, 11, 33, 241, 0, 0),
        ("imsa_grand_slam_from_pole", IMSA_RACE_IN_TICKS, 20, 0, 1, 1, 482, 14, 16.4),
        ("with_incidents", SPRINT_RACE_IN_TICKS, 19, 5, 3, 17, 350, 6, -2.0),
        ("zero_laps_complete", SPRINT_RACE_IN_TICKS, 10, 0, 1, 1, 500, 0, 0),
        ("low_safety_rating", SPRINT_RACE_IN_TICKS, 10, 5, 5, 5, 201, 45, -1.1),
        ("high_safety_rating", SPRINT_RACE_IN_TICKS, 10, 5, 5, 5, 451, 45, -1.0),
        ("ROAR_result", ROAR_RACE_IN_TICKS, 25, 0, 6, 12, 490, 150, 18.8),
        ("many_incidents", SPRINT_RACE_IN_TICKS, 10, 16, 5, 5, 325, 20, -5.0),
        ("missed_race", 0, 35, 0, 11, 33, 241, 0, 0),
    ])
    def test_challenge_score_v2(self, name, race_length, race_participants, incidents, qualifying_position, finish_pos, safety_rating, laps_complete, expected):
        result = challenge_score_v2(
            race_length=race_length,
            race_participants=race_participants,
            incidents=incidents,
            qualifying_position=qualifying_position,
            finish_pos=finish_pos,
            safety_rating=safety_rating,
            laps_complete=laps_complete
        )
        self.assertEqual(expected, result)