# Using Dusseldorf

Use this guide after deployment to operate Dusseldorf as a private OAST platform.

- Installation paths: [docs/install.md](install.md)
- Local deployment: [docs/local/readme.md](local/readme.md)
- Azure deployment: [docs/azure/readme.md](azure/readme.md)

## Audience

- Security researchers and operators using Dusseldorf to capture and inspect network interactions.
- Developers extending Dusseldorf behavior through listeners, rules, and APIs.

## Platform Overview

Dusseldorf consists of:

- Frontend control plane (UI and REST API)
- Backend listeners (DNS, HTTP, HTTPS)

This guide uses `https://frontend` and `*.backend.tld` as example hostnames.

## Frontend

The frontend is the control plane used by operators and researchers. It is protected by OpenID Connect and uses an access token to call the API.

- UI base URL: `https://frontend`
- API base URL: `https://frontend/api`
- API docs: `https://frontend/docs`

For Entra ID setup and token troubleshooting, see [cli/ENTRAID_SETUP.md](../cli/ENTRAID_SETUP.md).

### Using the UI

Use the UI to:

- Create and manage zones
- Inspect captured DNS and HTTP/HTTPS requests
- Configure per-zone response behavior

### Using the API Directly

Export an access token:

```sh
export DSSLDRF_AUTH_TOKEN=$(az account get-access-token --resource <your-app-client-id> | jq -r .accessToken)
```

Ping the API:

```sh
curl -H "Authorization: Bearer $DSSLDRF_AUTH_TOKEN" https://frontend/api/ping
```

List zones:

```sh
curl -H "Authorization: Bearer $DSSLDRF_AUTH_TOKEN" https://frontend/api/zones
```

Create a zone (example):

```sh
curl -X POST \
  -H "Authorization: Bearer $DSSLDRF_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fqdn":"test1.backend.tld"}' \
  https://frontend/api/zones
```

## Backend Listeners

By default, Dusseldorf exposes these listeners:

| Protocol | Port | Description | RFC |
| --- | --- | --- | --- |
| DNS | 53/udp | Domain Name System | [RFC 1035](https://tools.ietf.org/html/rfc1035) |
| HTTP | 80/tcp | Hypertext Transfer Protocol | [RFC 2616](https://tools.ietf.org/html/rfc2616) |
| HTTPS | 443/tcp | Hypertext Transfer Protocol Secure | [RFC 2818](https://tools.ietf.org/html/rfc2818) |

HTTPS requires valid certificates. For local certificate setup, see [docs/local/readme.md](local/readme.md#2-generate-credentials-and-certificates).

## DNS Workflow

For normal operations, DNS listeners must be publicly reachable on port 53/udp.

If a zone `test1.backend.tld` exists, requests for that zone or its subdomains (for example `foo.test1.backend.tld`) are captured and visible to authorized users.

When a queried subdomain matches a configured zone and rules, Dusseldorf can return custom responses. If no specific zone mapping exists, the default DNS behavior is applied.

## Extending Dusseldorf

For developers extending functionality:

- Service composition and component map: [dusseldorf/README.md](../dusseldorf/README.md)
- CLI extension and automation workflows: [cli/README.md](../cli/README.md)
- API and listener source roots: [dusseldorf/api](../dusseldorf/api), [dusseldorf/listener.dns](../dusseldorf/listener.dns), [dusseldorf/listener.http](../dusseldorf/listener.http)
