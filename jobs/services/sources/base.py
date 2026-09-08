from abc import ABC, abstractmethod

class JobSource(ABC):

    @abstractmethod
    def fetch_jobs(self, keyword="", location="", results_per_page=10):
        pass

    

