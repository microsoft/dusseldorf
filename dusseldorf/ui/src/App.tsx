// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { InteractionType, PublicClientApplication } from "@azure/msal-browser";
import {
    AuthenticatedTemplate,
    MsalAuthenticationTemplate,
    MsalProvider,
    UnauthenticatedTemplate
} from "@azure/msal-react";
import {
    Button,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    DialogTrigger,
    FluentProvider,
    Spinner,
    webDarkTheme,
    webLightTheme
} from "@fluentui/react-components";
import { ArrowSyncRegular, SignOutRegular } from "@fluentui/react-icons";
import { createContext, useEffect, useState } from "react";
import { HashRouter } from "react-router-dom";

import { DusseldorfAPI } from "./DusseldorfApi";
import { CacheHelper } from "./Helpers/CacheHelper";
import { Logger } from "./Helpers/Logger";
import { ThemeHelper } from "./Helpers/ThemeHelper";
import { LeftNav } from "./Navigation/LeftNav";
import { TopNavBar } from "./Navigation/TopNavBar";
import { ScreenRouter } from "./screens/ScreenRouter";
import { Splash } from "./screens/Splash";

import "./App.css";
import "./Styles/Stack.css";

export const DomainsContext = createContext<string[]>([]);

interface IAppProps {
    msal: PublicClientApplication;
}

export const App = ({ msal }: IAppProps) => {
    // Control theme
    const [darkTheme, setDarkTheme] = useState<boolean>(ThemeHelper.Get() === "dark");

    // Control authentication
    const [showRefreshSession, setShowRefreshSession] = useState<boolean>(false);

    // Control API
    const [domains, setDomains] = useState<string[]>();

    useEffect(() => {
        if (!domains || domains.length === 0) {            
            DusseldorfAPI.GetDomains()
                .then((newDomains) => {
                    if (newDomains.length === 0) {
                        Logger.Error("No domains found");
                        setDomains(undefined);
                    } else {
                        setDomains(newDomains);
                    }
                })
                .catch((err) => {
                    Logger.Error(err);
                    setDomains(undefined);
                });
        }
    }, []);

    return (
        <MsalProvider instance={msal}>
            <FluentProvider theme={darkTheme ? webDarkTheme : webLightTheme}>
                <MsalAuthenticationTemplate interactionType={InteractionType.Redirect}>
                    <UnauthenticatedTemplate>
                        <Splash
                            loginClick={() => {
                                msal.loginRedirect().catch((err) => {
                                    Logger.Error(err);
                                });
                            }}
                        />
                    </UnauthenticatedTemplate>

                    <AuthenticatedTemplate>
                        {domains ? (
                            <DomainsContext.Provider value={domains}>
                                <HashRouter basename="/">
                                    <div style={{ height: "100vh", width: "100vw" }}>
                                        <TopNavBar
                                            apiError={false}
                                            darkTheme={darkTheme}
                                            toggleTheme={() => {
                                                setDarkTheme(!darkTheme);
                                                ThemeHelper.Set(darkTheme ? "light" : "dark");
                                            }}
                                        />
                                        <div
                                            className="stack hstack"
                                            style={{ width: "100%", height: "94%" }}
                                        >
                                            <LeftNav
                                                refreshToken={() => {
                                                    Logger.Info("App:refreshToken()");
                                                    msal.acquireTokenSilent({
                                                        scopes: ["openid", "profile", "offline_access"]
                                                    })
                                                        .then((resp) => {
                                                            CacheHelper.SetToken(resp.idToken);
                                                            Logger.Info("App:refreshToken() success");
                                                        })
                                                        .catch((err) => {
                                                            // show popup if this failed; try to relogin
                                                            Logger.Warn("App:refreshToken() failed: " + String(err));
                                                            setShowRefreshSession(true);
                                                        });
                                                }}
                                            />

                                            <ScreenRouter />

                                            <Dialog
                                                open={showRefreshSession}
                                                onOpenChange={(_, data) => {
                                                    setShowRefreshSession(data.open);
                                                }}
                                                modalType="alert"
                                            >
                                                <DialogSurface style={{ width: 450 }}>
                                                    <DialogBody>
                                                        <DialogTitle>Session Expired</DialogTitle>
                                                        <DialogContent>
                                                            Your session has expired. Please reload the page.
                                                        </DialogContent>
                                                        <DialogActions>
                                                            <Button
                                                                appearance="primary"
                                                                icon={<ArrowSyncRegular />}
                                                                onClick={() => {
                                                                    setShowRefreshSession(false);
                                                                    msal.loginRedirect({
                                                                        scopes: ["openid", "profile", "offline_access"]
                                                                    }).catch((err) => {
                                                                        Logger.Error(err);
                                                                    });
                                                                }}
                                                            >
                                                                Refresh
                                                            </Button>
                                                            <DialogTrigger disableButtonEnhancement>
                                                                <Button
                                                                    icon={<SignOutRegular />}
                                                                    onClick={() => {
                                                                        msal.logoutRedirect().catch((err) => {
                                                                            Logger.Error(err);
                                                                        });
                                                                    }}
                                                                >
                                                                    Sign out
                                                                </Button>
                                                            </DialogTrigger>
                                                        </DialogActions>
                                                    </DialogBody>
                                                </DialogSurface>
                                            </Dialog>
                                        </div>
                                    </div>
                                </HashRouter>
                            </DomainsContext.Provider>
                        ) : (
                            <>
                                <TopNavBar
                                    apiError={true}
                                    darkTheme={darkTheme}
                                    toggleTheme={() => {
                                        setDarkTheme(!darkTheme);
                                        ThemeHelper.Set(darkTheme ? "light" : "dark");
                                    }}
                                />
                                <Spinner
                                    size="large"
                                    label="Loading data from API"
                                    role="alertdialog"
                                />
                            </>
                        )}
                    </AuthenticatedTemplate>
                </MsalAuthenticationTemplate>
            </FluentProvider>
        </MsalProvider>
    );
};
