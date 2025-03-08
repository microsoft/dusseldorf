# Dusseldorf

This folder contains all the components that make up the total platform.  These include:


- `api`: the control plane / API.
- `listener.dns`:  the DNS listener for the data plane.
- `listener.http`: the HTTP/HTTPS listener in the data plane.
- `ui`: the source for the frontend web user interface.
- `zentralbibliothek`: a central library for listeners in the data plane.

Each component is explained in more details below:

## API
This is the control plane of Dusseldorf.  This REST API allows an authenticated user to create, manage and delete zones, monitor the requests made to them and manage rules set on their zones. Calls to this API must be authenticated using an authentication token in each request.  

This API is implemented using the FastAPI framework and provide CRUD functionality on zones, rules by interacting with a MongoDB database.  

For more information about this API, please consult the [API docs](api/README.md).


## DNS Listener
This is a network listener that responds to DNS traffic, and listens on port 53/udp for any DNS requests.   The DNS (Domain Name System) protocol is reponsible for translating hostnames to an IP address.  By acting as a domains' DNS server, Dusseldorf is able to monitor any name resolutions for those subdomains on the Internet.  

By default, this permissive DNS server reponds with its own IP address(es) to a name resolution.  This behaviour can be changed by assigning rules to your zone.   Currently we only support custom `A`, `AAAA`, `CNAME` and `TXT` records.

Check the documentation for the DNS listener [here](listener.dns/README.md).


## HTTP/HTTPS Listener
This network listener can be setup to listen on cleartext HTTP traffic, or it can listen on HTTPS traffic, you have the correct certificates available.  For a cleartext setup, this listener accepts HTTP reqeusts on port 80/tcp, and respond with default, or customized HTTP responses.

Just like the DNS listener acts as a DNS server, this listener implements a very permissive HTTP server, or web server.  Using rules, you can set custom content, headers and status codes.

If you have an x.509 public/private keypair, is a wildcard certificate (ex: `*.contoso.com`) the you can setup the HTTP listener to listen on HTTPS.

> Note that wildcard certificates cannot contain multiple wildcards.   Ie: a certificate for `*.*.contoso.com` is not compatible.

You can find more information on how to run this listener in the [HTTP documentation](listener.http/README.md).



## UI
This is the frontend web user interface.  It is implemented in React using the amazing [Fluent2](https://fluent2.microsoft.design/) design framework and provides a modern single-page-application (SPA) to communicate with the Dusseldorf API.

These static pages are compiled and placed into a folder in the API, so it references a local `/api` endpoints, but can be setup to call another API endoint altogether, too.  

The user interface's information can be found [here](ui/README.md).


## Zentralbibliothek
This is a central library which holds the rule engine, database logic and utility functions.



