# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from typing import List
import base64

class PayloadHelper:
    """Helper class for generating DNS payloads"""

    def generate_payloads(self, fqdn: str, use_base64: bool = False) -> List[str]:
        """
        Generates a list of DNS payloads for the given FQDN
        
        Args:
            fqdn: The fully qualified domain name to generate payloads for
            use_base64: Whether to base64 encode the payloads
        
        Returns:
            List of payload strings
        """
        # Basic DNS payload patterns
        prefixes = [
            "0",
            "0.",
            ".",
            "..",
            "../",
            ".\\",
            "..\\",
            "%00",
            "%2e",
            "%2e%2e",
            "%2e/",
            "%2e%5c",
            "%2e%2e%5c",
            "%252e",
            "%252e%252e",
            "%%32%65",
            "%%32%65%%32%65",
            "..;/",
            ".../",
            "..../",
            "...../"
        ]

        # Generate payloads
        payloads = []
        for prefix in prefixes:
            payload = f"{prefix}{fqdn}"
            if use_base64:
                # Encode to base64 and remove padding
                payload_bytes = payload.encode('utf-8')
                payload = base64.b64encode(payload_bytes).decode('utf-8').rstrip('=')
            payloads.append(payload)

        return payloads 