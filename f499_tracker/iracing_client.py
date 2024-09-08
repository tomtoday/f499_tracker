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
