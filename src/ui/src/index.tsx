// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { StrictMode } from "react";
import { createRoot } from 'react-dom/client';
import { App } from "./App";
import { Logger } from "./Helpers/Logger";
import { initializeIcons } from "@fluentui/react/lib/Icons";
import { PublicClientApplication, } from "@azure/msal-browser";
import DusseldorfConfig from "./DusseldorfConfig";
import { CacheHelper } from "./Helpers/CacheHelper";

export const msal = new PublicClientApplication(DusseldorfConfig.msalConfig);
await msal.initialize();

const runDusseldorf = () => {
    const container = document.getElementById("woot");
    if (!container) {
        Logger.Error("No root element found")
    } else {
        const root = createRoot(container);
        root.render(<StrictMode> <App msal={msal} /> </StrictMode>);
    }
}

await msal.handleRedirectPromise().then((resp) => {
    if (resp) {
        Logger.Info("Dusseldorf.redirected()");
        msal.setActiveAccount(resp.account);
        CacheHelper.SetToken(resp.idToken);
        window.location.reload();
    }
});

initializeIcons();

Logger.Info("Dusseldorf.init()");

// setup auth
const accounts = msal.getAllAccounts();

if (accounts.length == 0) {
    msal.loginRedirect({ scopes: ["openid", "profile", "offline_access"] })
        .catch(err => {
            Logger.Error(err)
        })
}
else {
    msal.setActiveAccount(accounts[0]);
    msal.acquireTokenSilent({ scopes: ["openid", "profile", "offline_access"], account: accounts[0] })
        .then(resp => {
            CacheHelper.SetToken(resp.idToken);
            Logger.Info("Dusseldorf.loaded()");
            runDusseldorf();
        })
        .catch(error => {
            Logger.Error("Dusseldorf.error(): " + String(error));
        });
} 
