from f499_tracker.utils import convert_ticks_to_timedelta

LONG_RACE_LENGTH = 45


def challenge_score(start, finish, incident_count):
    return (start - finish) + (4 if incident_count == 0 else -1 * (2 * incident_count))


def challenge_score_v2(race_length, race_participants, incidents, qualifying_position, finish_pos, safety_rating, laps_complete):
    # print the values of the parameters
    race_length_in_minutes = convert_ticks_to_timedelta(race_length).seconds // 60
    print(
        f'race_length_in_minutes: {race_length_in_minutes}, race_participants: {race_participants}, incidents: {incidents}, '
        f'qualifying_position: {qualifying_position}, finish_pos: {finish_pos}, safety_rating: {safety_rating}')

    race_time_leveller = (race_length_in_minutes // LONG_RACE_LENGTH) + 1
    qualifying_points = qualifying_score(qualifying_position, race_participants)
    race_points = race_score(finish_pos, race_participants)
    incident_points = incident_score(incidents, race_time_leveller, safety_rating)
    print(
        f"race_time_leveller: {race_time_leveller}, qualifying_points: {qualifying_points}, race_points: {race_points}, incident_points: {incident_points}")
    calculated_challenge_score = qualifying_points + race_points + incident_points

    # if the laps_completed is 0 and the incident_points is 0, then set the calculated_challenge_score to 0
    if laps_complete == 0 and incidents == 0:
        calculated_challenge_score = 0

    print(f"calculated_challenge_score: {calculated_challenge_score}")
    return calculated_challenge_score


def qualifying_score(qualifying_position, race_participants):
    if qualifying_position == 1:
        return 2
    elif qualifying_position / race_participants <= .33:
        return 1
    else:
        return 0


def race_score(finish_position, race_participants):
    finish_percentile = finish_position / race_participants
    print(f"finish_percentile: {finish_percentile}")
    if finish_position == 1:
        return 6
    elif finish_position == 2:
        return 4
    elif finish_position == 3:
        return 3
    elif finish_percentile <= .33:
        return 2
    elif finish_percentile <= .66:
        return 1
    else:
        return -1


def incident_score(incidents, race_time_leveller, safety_rating):
    if incidents == 0:
        score = 4
    elif incidents <= 4:
        score = 0
    elif incidents <= 8:
        score = -2
    elif incidents <= 12:
        score = -4
    elif incidents <= 16:
        score = -6
    else:
        score = -8

    if score > 0:
        score = score * race_time_leveller
        if safety_rating >= 400:
            score = score * 1.05
    elif score < 0:
        score = score / race_time_leveller
        if safety_rating < 300:
            score = score * 1.05

    # round score to the nearest tenth
    score = round(score, 1)
    return score


def session_link(subsession_id, new_ui=False):
    if new_ui:
        tmpl = "https://members-ng.iracing.com/racing/results-stats/results?subsessionid="
    else:
        tmpl = "https://members.iracing.com/membersite/member/EventResult.do?&subsessionid="

    return f"{tmpl}{subsession_id}"


def construct_499_race_data(raw_result, racer_name):
    start_position = raw_result['starting_position_in_class'] + 1
    finish_position = raw_result['finish_position_in_class'] + 1
    week_number = raw_result['race_week_num'] + 1
    _499_points = challenge_score(start_position, finish_position, raw_result['incidents'])
    iracing_session_link = session_link(raw_result['subsession_id'], True)

    return {
        "start_position": start_position,
        "finish_position": finish_position,
        "incident_count": (raw_result['incidents']),
        "track_name": (raw_result['track']['track_name']),
        "subsession_id": (raw_result['subsession_id']),
        "start_time": (raw_result['start_time']),
        "week_number": week_number,
        "season_year": (raw_result['season_year']),
        "season_quarter": (raw_result['season_quarter']),
        "_499_points": _499_points,
        "session_link": iracing_session_link,
        "series_name": (raw_result['series_name']),
        "series_id": (raw_result['series_id']),
        "racer_name": racer_name,
        "cust_id": raw_result['cust_id'],
        "car_name": raw_result['car_name'],
        "license_category": raw_result['license_category'],
        "laps_complete": raw_result['license_category'],
    }
