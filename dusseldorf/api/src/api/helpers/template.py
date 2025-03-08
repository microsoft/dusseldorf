# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from typing import Dict, Any, Optional
from jinja2 import Environment, BaseLoader
import logging

logger = logging.getLogger(__name__)

class TemplateHelper:
    """Helper for processing DNS record templates"""
    
    def __init__(self):
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=True
        )

    def render_template(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> Optional[str]:
        """Render a template with provided variables"""
        try:
            template_obj = self.env.from_string(template)
            return template_obj.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            return None

    def validate_template(self, template: str) -> bool:
        """Validate template syntax"""
        try:
            self.env.from_string(template)
            return True
        except Exception as e:
            logger.debug(f"Template validation failed: {str(e)}")
            return False

    def extract_variables(self, template: str) -> set:
        """Extract variable names from template"""
        try:
            template_obj = self.env.from_string(template)
            return set(template_obj.variables)
        except Exception as e:
            logger.error(f"Failed to extract variables: {str(e)}")
            return set()

    def render_bulk_templates(
        self,
        templates: Dict[str, str],
        variables: Dict[str, Any]
    ) -> Dict[str, Optional[str]]:
        """Render multiple templates with the same variables"""
        results = {}
        for name, template in templates.items():
            results[name] = self.render_template(template, variables)
        return results 