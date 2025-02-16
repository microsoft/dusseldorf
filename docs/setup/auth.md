# Setting up Auth

While Dusseldorf's dataplane is un-authenticated *by design*, anyone can try to resolve `foobar.contoso.com`, the control plane (the API) is protected by only allowing requests with a valid authentication token.  This token must be a JWT, with a `preferred_username` claim.  

> Note that the UI public artifacts, such as the Javascript and CSS files are available without authentication.  They contain no sensitive data.  If you wish to block your UIR and API, you must utilize network filtering rules.

Dusseldorf was designed to work with EntraID, although other identity providers (IdP's) should work as well if they are cmopatible with  the OIDC (OpenID connect) specifications.

# Creating Service Principal in EntraID

# 