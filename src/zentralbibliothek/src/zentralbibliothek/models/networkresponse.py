# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# aka.ms/dusseldorf

from abc import ABC, abstractmethod

class NetworkResponse(ABC):
    '''An abstract class for all Network Responses to inherit from.
    '''
    @property
    @abstractmethod
    def json(self):
        '''Implement this in your child classes to return a JSON blob of useful details about the response.
        '''
        pass
    
    @property
    @abstractmethod
    def summary(self):
        '''Implement this in your child classes to return a short text summary of the response.
        '''
        pass