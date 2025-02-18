# Using Dusseldorf

> Please refer to [this guide](install.md) to install and setup Dusseldorf, or check the developer guide to [run Dusseldorf locally](local.md) on your machine prior to using it.

Dusseldorf consists of a frontend and backend component. The frontend exposes both a REST API and an easy-to-use graphical user interface. The backend component exists of several **network listeners** that accept connections and packets on several network protocols.  This guide will use the fictious `https://frontend` and `*.backend.tld` to indicate the domain names of front and back-end components respectively.


## Frontend 
This is the control plane of Dusseldorf to be used by its operators or administrators.  The graphical user interface can be accessed by any modern web browser.  Since the frontend is protected by OpenID connect, it will try to retreive authentication tokens automatically and log you in.  For any auth problems, please consult the troubleshooting guide [here](setup/auth.md).  

When the UI successfully gets a authentication token, it uses it to interact with the REST API, which is available by default on `https://frontend/api`.  The OpenAPI document (or *swagger* docs) can be found on `https://frontend/docs` .

### Using the UI

> TODO:  INSERT UI images when ready

### Using the API directly
To use the API you need to you retreive an authentication token, you can use the following command for that:

```shell 
$ export DSSLDRF_AUTH_TOKEN=`az account get-access-token --resource=<your object id> | jq -r .accessToken```
```

This will make the token available in the `DSSLDRF_AUTH_TOKEN` environment variable which we can then use with a command such as `curl` to interact directly with the Dusseldorf API.  For example, to *ping* the API endpoint, you can use the below

```shell
$ curl -H "Authorization: Bearer $DSSLDRF_AUTH_TOKEN" https://frontend/api/ping
{"pong":1739667208,"user":"mihendri@microsoft.com","build":"2025.3.2"}
```

By querying the `/api/zones` endpoint, we can see if we have any zones available, and we can create a new custom zone, if it's available:

```shell
$ curl -H "Authorization: Bearer $DSSLDRF_AUTH_TOKEN" https://frontend/api/zones
[{"fqdn":"test1.backend.tld","domain":"backend.tld"}, ... ]
```



## Backend
The backend of Dusseldorf is a combination of several network listeners available on the Internet, usually using 2 static IPv4 IP addresses.  By default, these protocols are enabled:

| Protocol   | Port    | Full Name | RFC Link |
| ---------- | ------- | --------- | -------- |
| DNS        | 53/udp  | Domain Name System | [RFC 1035](https://tools.ietf.org/html/rfc1035) |
| HTTP       | 80/tcp  | Hypertext Transfer Protocol | [RFC 2616](https://tools.ietf.org/html/rfc2616) |
| *HTTPS**   | 443/tcp | Hypertext Transfer Protocol (Secure) | [RFC 2818](https://tools.ietf.org/html/rfc2818) |

> Note: HTTPS is only available with the presence of a wildcard certificate, and this poses some restrictions.  See [this page](setup/tls.md) for more inforamtion.

How to interact with each listener is explained below:

### DNS Listener
For normal operations, this network listener must be reachable from anywhere on the Internet on port 53/udp.

When you try to resolve *any* host name in the `*.backend.tld` namespace, a DNS request will be sent to one of the DNS listeners.  For example, if an operator creates a zone named `test1.backend.tld`, then *any* DNS request made to this domain, or any subdomain (such as `foo.test1.backend.tld`) can be seen by the operator and others, if authorized.

 is a valid *zone* in Dusseldorf, it can respond with a custom response; if the subdomain is not explicitely registered as a zone, a defualt DNS respone will be returned.

