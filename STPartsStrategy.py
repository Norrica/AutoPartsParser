from ABCPStrategy import ABCPStrategy


class STPartsStrategy(ABCPStrategy):
    def __init__(self, manager, articles):
        super().__init__(manager, articles)
        self._domain = 'https://stparts.ru'