import os

from azure.monitor.opentelemetry import configure_azure_monitor

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
import os
import logging

from opentelemetry._logs import (
    get_logger_provider,
    set_logger_provider,
)
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

class Logger:
    @classmethod
    def setup_logger(cls, connstr:str=""):
        """
            Call this and then do a:
            logger = logging.getLogger(__name__)            
        """
        logger_provider = LoggerProvider()
        set_logger_provider(logger_provider)
        
        # get connection string of fallback to hardcoded value
        DEFAULT_CONNSTR =  ("InstrumentationKey=fbc14150-6890-45f0-9472-30c415bd09e4;" + 
                            "IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;" + 
                            "LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/;" +  
                            "ApplicationId=883538dd-7301-4542-994e-807e8f28afc4")
        connstr = os.environ.get("DSSLDRF_APPINSIGHTS", DEFAULT_CONNSTR)
        
        exporter = AzureMonitorLogExporter.from_connection_string(
            connstr            
        )

        get_logger_provider().add_log_record_processor(
            BatchLogRecordProcessor(exporter, schedule_delay_millis= 60 * 1000))
