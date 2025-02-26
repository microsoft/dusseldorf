// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { InteractionType, PublicClientApplication } from "@azure/msal-browser";
import {
    AuthenticatedTemplate,
    MsalAuthenticationTemplate,
    MsalProvider,
    UnauthenticatedTemplate
} from "@azure/msal-react";
import { createContext, useEffect, useState } from "react";
import { HashRouter } from "react-router-dom";
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

import { DusseldorfAPI } from "./DusseldorfApi";
import { CacheHelper } from "./Helpers/CacheHelper";
import { Logger } from "./Helpers/Logger";
import { ThemeHelper } from "./Helpers/ThemeHelper";
import { LeftNav } from "./Navigation/LeftNav";
import { TopNavBar } from "./Navigation/TopNavBar";
import { ScreenRouter } from "./screens/ScreenRouter";
import { Splash } from "./screens/Splash";
import { IDusseldorfContext } from "./Types/IDusseldorfContext";

import "./App.css";
import "./Styles/Stack.css";

const initialState: IDusseldorfContext = {
    domain: ""
};

export const DusseldorfContext = createContext<IDusseldorfContext>(initialState);

interface IAppProps {
    msal: PublicClientApplication;
}

export const App = ({ msal }: IAppProps) => {
    const [darkTheme, setDarkTheme] = useState<boolean>(ThemeHelper.Get() === "dark");
    const [apiError, setApiError] = useState<boolean>(false);

    const [showRefreshSession, setShowRefreshSession] = useState<boolean>(false);

    const [loaded, setLoaded] = useState<boolean>(false);

    // the global context
    const [context] = useState<IDusseldorfContext>({
        domain: "dusseldorf.local"
    });

    useEffect(() => {
        // empty out the token cache
        if (!loaded) {
            DusseldorfAPI.HeartBeat()
                .then(() => {
                    Logger.Info(`api success: ${DusseldorfAPI.ENDPOINT}`);
                    setLoaded(true);
                    setApiError(false);

                    // set the domain
                    DusseldorfAPI.GetDomains()
                        .then((domains) => {
                            if (domains.length === 0) {
                                Logger.Error("No domains found");
                                setApiError(true);
                                return;
                            } else {
                                context.domain = domains[0];
                            }
                        })
                        .catch((err) => {
                            Logger.Error(err);
                            setApiError(true);
                            context.domain = "dusseldorf.local";
                        });
                })
                .catch((err) => {
                    Logger.Error(err);
                    setApiError(true);
                });
        }
    }, [loaded, apiError]);

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
                        <DusseldorfContext.Provider value={context}>
                            <HashRouter basename="/">
                                {loaded ? (
                                    <div style={{ height: "100vh", width: "100vw" }}>
                                        <TopNavBar // 6% of height
                                            apiError={apiError}
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
                                ) : (
                                    <>
                                        <TopNavBar
                                            apiError={apiError}
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
                            </HashRouter>
                        </DusseldorfContext.Provider>
                    </AuthenticatedTemplate>
                </MsalAuthenticationTemplate>
            </FluentProvider>
        </MsalProvider>
    );
};
