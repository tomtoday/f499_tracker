from iracingdataapi.client import irDataClient

from f499_tracker.config import Config


class IRacingAPIHandler:
    def __init__(self):
        if Config.IRACING_USERNAME is None or Config.IRACING_PASSWORD is None:
            return

        self.client = irDataClient(Config.IRACING_USERNAME, Config.IRACING_PASSWORD)

    def get_499_series(self):
        # List of series names to search for
        series_names = Config.F499_SEASON3_SERIES_KEYWORDS

        # Retrieve the list of series from the client
        series = self.client.series

        # Find series that match any of the names in series_names
        _499_series = [(s['series_id'], s['series_name']) for s in series if
                       any(name in s['series_name'] for name in series_names)]

        return _499_series

    def fetch_series_results_for(self, cust_id, desired_season_quarter, desired_season_week, desired_season_year):
        if desired_season_week is None:
            all_results = self.client.result_search_series(cust_id=cust_id,
                                                                       official_only=True,
                                                                       event_types=[Config.EVENT_TYPE],
                                                                       season_year=desired_season_year,
                                                                       season_quarter=desired_season_quarter,
                                                                       category_ids=[5, 6])
        else:
            all_results = self.client.result_search_series(cust_id=cust_id,
                                                                       official_only=True,
                                                                       event_types=[Config.EVENT_TYPE],
                                                                       season_year=desired_season_year,
                                                                       race_week_num=desired_season_week - 1,
                                                                       season_quarter=desired_season_quarter,
                                                                       category_ids=[5, 6])
        return all_results
