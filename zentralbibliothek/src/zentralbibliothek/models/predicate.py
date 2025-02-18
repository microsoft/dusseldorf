import json
import re

from abc import ABC, abstractmethod
from .networkrequest import NetworkRequest

class Predicate(ABC):
    """
    This is the abstract class that all Predicates should implement. 
    """
    @classmethod
    @abstractmethod
    def satisfied_by(cls, request:NetworkRequest, parameter:str):
        pass