// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

// const MYURL = window.localStorage.getItem("debug") !== 'production' ? 
//                 "https://dusseldorf.security.azure/" 
//                 :
//                 "http://localhost:3000/" ;

// This is the hostname of the API we talk to.  
// To set a manual one, do the following
// localStorage.setItem("api_host", "https://localhost:1337")
const API_HOST = process.env.REACT_APP_API_HOST ?? window.localStorage.getItem("api_host") ?? "/api";

const config = {
    // https://ms.portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/Overview/appId/dc1b6b75-8167-4baf-9e75-d3d1f755de1b/isMSAApp/
    client_id:      process.env.REACT_APP_CLIENT_ID ?? "dc1b6b75-8167-4baf-9e75-d3d1f755de1b",
    tenant_id:      process.env.REACT_APP_TENANT_ID ?? "72f988bf-86f1-41af-91ab-2d7cd011db47",
    appInsightsId:  "3836b094-0c3a-42b1-a3b3-9a81133f64fb"
}

export default {
    // this is loaded from config
    domain:     "",
    public_zone: "public",

    // auth data, we can put this in config?
    client_id:  config.client_id,
    tenant_id:  config.tenant_id,
    // redir_url:  MYURL,

    // success or not
    loaded:     false,

    // api settings
    api_host:    API_HOST,
    
    telemetryInstrumentationKey: config.appInsightsId,
    
    msalConfig: {
        auth: {
            clientId:    config.client_id,
            redirectUri: '/ui/',
            authority:   `https://login.microsoftonline.com/${config.tenant_id}/`,
            navigateToLoginRequestUrl: false,
            postLogoutRedirectUri: '/ui/',
        },
        cache: {
            storeAuthStateInCookie: true,
            claimsBasedCachingEnabled: true
        }
    }

};