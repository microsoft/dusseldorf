# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# aka.ms/dusseldorf

from abc import abstractmethod, ABC

class Result(ABC):
    @classmethod
    @abstractmethod
    def execute(cls, result_data:dict, parameter:str) -> dict:
        '''Take in the parameter of this result, and the common data shared amongst all results. 
        Do whatever your result is supposed to do. Store any information needed by future results
        in the result_data dict. 

        The response to the request is result_data['response']. Don't create a new object, read from 
        there and edit the existing one.

        :param result_data: The data to be shared across all results.
        :type result_data: dict
        :param parameter: The parameter for this specific result.
        :type parameter: str
        :return: The "updated" common result_data to pass to the next result.
        :rtype: dict
        '''
        pass