# Dusseldorf

This folder contains all the components that make up the total platform.  These include:

- `api`: the control plane / API.
- `listener.dns`:  the DNS listener for the data plane.
- `listener.http`: the HTTP/HTTPS listener in the data plane.
- `ui`: the source for the frontend web user interface.
- `zentralbibliothek`: a central library for listeners in the data plane.

## Developer Environment Setup

### Prerequisites
Please ensure that you have the following before starting:
- An Azure AD tenant
- An up-to-date version of Docker & Docker Compose
- A terminal that supports bash (Note: If you are on Windows, it's recommended you use Ubuntu WSL and have your docker compose environment stored there.)

### Setup
In your Azure AD tenant, [create an Azure AD application](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/CreateApplicationBlade/quickStartType~/null/isMSAApp~/false) with `http://localhost:8080/ui/` set as a redirect URI and `Single-page Application (SPA)` selected as the platform. Note the client ID and tenant ID of the newly created application.

Then, clone this repository and enter the `dusseldorf/` directory (the one with this README in it) inside of a Linux-based terminal (if on Windows, use WSL). Then, execute `./generate_devenv.sh` and input your client ID and tenant ID obtained from Azure.

To start your developer environment, ensure you have nothing running locally on port 8080 and run `docker compose up`. After it builds the containers, your environment should be up and running on `http://localhost:8080/ui/` and you should be able to login.

### Testing

Once your developer environment is running, the following services will be accessible on your computer:

- **API & UI server**: The API will be up and running on port 8080
- **HTTPS listener**: The HTTPS listener runs on port 443 by default. This is modifiable in your .env file, but note that it will be overwritten by the generate devenv script.
- **DNS listener**: The DNS listener runs on port 10053.

The API and UI are directly testable on http://localhost:8080/ui/ and you should be able to access them by logging in with an account on your Azure tenant that has access to the application.

To test the HTTPS listener, you can modify the following curl command:

```sh
curl https://localhost:443/your-path-here -k \
  -H "Host: your-zone-here.dusseldorf.local"
```

Make sure to keep the `-k` flag, which allows you to run the request without having to install the certificate. The Host header can be modified to be whatever host you are targeting to make a request to

To test the DNS listener, install the `dig` command in your local environment and use `dig your-zone-here.dusseldorf.local +tcp @localhost -p 10053` to make requests to the DNS server.

## Components

Here is some more information about the different components of this directory:

### API
This is the control plane of Dusseldorf.  This REST API allows an authenticated user to create, manage and delete zones, monitor the requests made to them and manage rules set on their zones. Calls to this API must be authenticated using an authentication token in each request.  

This API is implemented using the FastAPI framework and provide CRUD functionality on zones, rules by interacting with a MongoDB database.  

For more information about this API, please consult the [API docs](api/README.md).


### DNS Listener
This is a network listener that responds to DNS traffic, and listens on port 53/udp for any DNS requests.   The DNS (Domain Name System) protocol is responsible for translating hostnames to an IP address.  By acting as a domains' DNS server, Dusseldorf is able to monitor any name resolutions for those subdomains on the Internet.
By default, this permissive DNS server reponds with its own IP address(es) to a name resolution.  This behaviour can be changed by assigning rules to your zone.   Currently we only support custom `A`, `AAAA`, `CNAME` and `TXT` records.

Check the documentation for the DNS listener [here](listener.dns/README.md).


### HTTP/HTTPS Listener
This network listener can be setup to listen on cleartext HTTP traffic, or it can listen on HTTPS traffic, if you have the correct certificates available.  For a cleartext setup, this listener accepts HTTP requests on port 80/tcp, and respond with default, or customized HTTP responses.
Just like the DNS listener acts as a DNS server, this listener implements a very permissive HTTP server, or web server.  Using rules, you can set custom content, headers and status codes.

If you have an x.509 public/private keypair, is a wildcard certificate (ex: `*.contoso.com`) the you can setup the HTTP listener to listen on HTTPS.

> Note that wildcard certificates cannot contain multiple wildcards.   Ie: a certificate for `*.*.contoso.com` is not compatible.

You can find more information on how to run this listener in the [HTTP documentation](listener.http/README.md).



### UI
This is the frontend web user interface.  It is implemented in React using the amazing [Fluent2](https://fluent2.microsoft.design/) design framework and provides a modern single-page-application (SPA) to communicate with the Dusseldorf API.

These static pages are compiled and placed into a folder in the API, so it references a local `/api` endpoints, but can be setup to call another API endpoint altogether, too.
The user interface's information can be found [here](ui/README.md).


### Zentralbibliothek
This is a central library which holds the rule engine, database logic and utility functions.



