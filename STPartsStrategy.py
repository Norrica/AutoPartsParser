from ABCPStrategy import ABCPStrategy


class STPartsStrategy(ABCPStrategy):
    def __init__(self, manager, articles, ftp):
        super().__init__(manager, articles, ftp)
        self._domain = 'https://stparts.ru'
