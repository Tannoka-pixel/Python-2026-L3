from abc import ABC, abstractmethod

class Entity(ABC):
    def __init__(self, entity_id="", name=""):
        self._id = ""
        self._name = ""
        if entity_id:
            self.id = entity_id
        if name:
            self.name = name
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("ID must not be empty.")
        self._id = value
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Name must not be empty.")
        self._name = value
    @classmethod
    @abstractmethod
    def header(cls):
        pass
    @abstractmethod
    def row(self):
        pass
    def list(self):
        print(self.row())
