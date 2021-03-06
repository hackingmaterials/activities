from abc import ABC, abstractmethod

from monty.json import MSONable

from activities.core.activity import Activity


class Maker(ABC, MSONable):
    @abstractmethod
    def get_activity(self, *args, **kwargs) -> Activity:
        pass
