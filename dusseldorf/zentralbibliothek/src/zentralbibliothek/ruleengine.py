# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# aka.ms/dusseldorf

import logging, os

from zentralbibliothek.dbclient3 import DatabaseClient
from .models.networkrequest import NetworkRequest
from .models.predicate import Predicate
from .models.result import Result
from azure.monitor.opentelemetry import configure_azure_monitor

if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(
        logger_name="dssldrf.ruleengine",  # Set the namespace for the logger in which you would like to collect telemetry for if you are collecting logging telemetry. This is imperative so you do not collect logging telemetry from the SDK itself.
    )

logger = logging.getLogger('dssldrf.ruleengine')

class RuleEngine:
    """
    This class is responsible for calculating what the response to a request should be, based on the 
    rules that have been set up. 
    """


    @classmethod
    def get_response_from_request(cls, request:NetworkRequest, predicate_class_mappings:dict, result_class_mappings:dict):
        """
        This is the only method you need to call from your listener. 
        It will always return a response of the same type as `request.default_response`.
        """
        db = DatabaseClient.get_instance()
        predicate_sets = db.get_aggregated_rule_predicates_for_zone(request.NetworkProtocol, request.ZoneFqdn)
        
        for rule_id, action_name_list, action_value_list in predicate_sets: 
            if (cls.satisfies_predicate_list(request, action_name_list, action_value_list, predicate_class_mappings)):
                return cls.make_result_from_rule(rule_id, request, result_class_mappings)
        return request.default_response
    
    @classmethod
    def satisfies_predicate_list(cls, request:NetworkRequest, action_names:list, action_value:list, predicate_class_mappings:dict) -> bool:
        """
        Internal.
        
        Take in a list of predicate action names and a list of corresponding action values, and see if the request
        fulfills all of them.
        """
        for predicate_name, predicate_param in zip(action_names, action_value):
            predicate_class:Predicate = predicate_class_mappings.get(predicate_name, None)
            
            if predicate_class is None:
                logger.warning(f"Unknown predicate type `{predicate_name}`")
                continue
            
            if not predicate_class.satisfied_by(request, predicate_param):
                return False
        return True

    @classmethod
    def make_result_from_rule(cls, rule_id:str, request:NetworkRequest, result_class_mappings):
        db = DatabaseClient.get_instance()

        result_set = db.get_aggregated_rule_results(rule_id)
        result_pairs = zip(result_set[1], result_set[2], result_set[3])

        response_obj = request.default_response
        result_data = {            
            'response': response_obj,
            'zone': request.zone_fqdn,
            'metadata': {
                'rule_id': rule_id
            },
            'request': request
        }

        execute_these_last = []

        for result_component_id, result_action_name, result_parameter in result_pairs:
            result_action_class:Result = result_class_mappings.get(result_action_name, None)
            
            if result_action_class is None:
                logger.warning(f"Unknown result action `{result_action_name}`")
                continue

            if result_action_name in ['var']:
                execute_these_last.append((result_action_class, result_parameter))
                continue

            result_data['metadata']['component_id'] = result_component_id
            result_action_class.execute(result_data, result_parameter)

        # do all the ones we pushed to the back
        for result_action_class, result_parameter in execute_these_last:
            result_action_class.execute(result_data, result_parameter)
        
        return result_data['response']


