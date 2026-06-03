from ABCPStrategy import ABCPStrategy


class AEXCStrategy(ABCPStrategy):
    def __init__(self, manager, articles):
        super().__init__(manager, articles)
        self._domain: str = 'https://aexc.ru'