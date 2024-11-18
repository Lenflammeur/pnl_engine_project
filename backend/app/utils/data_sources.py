class DataSource:
    def fetch_prices(self):
        """
        Fetch prices from the data source.
        Override this method for specific data sources.
        """
        raise NotImplementedError("This method should be overridden.")

class ExampleSource(DataSource):
    def fetch_prices(self):
        return {"AAPL": 155, "MSFT": 310, "GOOG": 2600}
