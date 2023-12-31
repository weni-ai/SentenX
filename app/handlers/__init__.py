from abc import ABC, abstractmethod


class IDocumentHandler(ABC):
    @abstractmethod
    def index(self):
        pass

    @abstractmethod
    def batch_index(self):
        pass

    @abstractmethod
    def search(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def delete_batch(self):
        pass
