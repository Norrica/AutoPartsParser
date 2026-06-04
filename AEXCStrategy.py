from ABCPStrategy import ABCPStrategy


class AEXCStrategy(ABCPStrategy):
    def __init__(self, manager, articles,ftp):
        super().__init__(manager, articles,ftp)
        self._domain: str = 'https://aexc.ru'