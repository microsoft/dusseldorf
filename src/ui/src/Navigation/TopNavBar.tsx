// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { useMsal } from "@azure/msal-react";
import {
    Avatar,
    Button,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    DialogTrigger,
    Link,
    Menu,
    MenuItem,
    MenuItemSwitch,
    MenuList,
    MenuPopover,
    MenuTrigger,
    MessageBar,
    Switch,
    Text
} from "@fluentui/react-components";

import { Logger } from "../Helpers/Logger";
import { Logo } from "../Components/Logo";
import { DismissRegular, SignOutRegular, WeatherMoonRegular, WeatherSunnyRegular } from "@fluentui/react-icons";
import { useState } from "react";
import { msal } from "..";

interface ITopNavBarProps {
    apiError: boolean;
    darkTheme: boolean;
    toggleTheme: () => void;
}

export const TopNavBar = ({ apiError, darkTheme, toggleTheme }: ITopNavBarProps) => {
    const { instance } = useMsal();
    const account = instance.getActiveAccount();

    const [open, setOpen] = useState<boolean>(false);

    /**
     * Shows an error bar when the API is not working.
     * @returns
     */
    const ApiErrorBar = () => {
        if (apiError) {
            return (
                <MessageBar intent="error">
                    <Text>
                        The API is not responding.{" "}
                        <Link
                            inline
                            onClick={() => {
                                instance.setActiveAccount(account);
                                Logger.Info("apierrorbar.reload()");
                                sessionStorage.clear();
                                window.location.reload();
                            }}
                        >
                            Reload
                        </Link>
                    </Text>
                </MessageBar>
            );
        } else return <></>;
    };

    return (
        <>
            <div
                className="stack hstack-spread"
                style={{ height: "6%", backgroundColor: "#003846", paddingLeft: 10, paddingRight: 10 }}
            >
                <Logo />

                <Menu>
                    <MenuTrigger disableButtonEnhancement>
                        <Button appearance="transparent">
                            <div style={{ display: "flex", flexDirection: "row", alignItems: "center" }}>
                                <Avatar name={account?.name} />
                                <Text style={{ color: "#ffffff", paddingLeft: 10 }}> {account?.name}</Text>
                            </div>
                        </Button>
                    </MenuTrigger>

                    <MenuPopover>
                        <MenuList>
                            <MenuItem
                                onClick={toggleTheme}
                                persistOnClick
                            >
                                <div style={{ display: "flex", flexDirection: "row", alignItems: "center" }}>
                                    {darkTheme ? (
                                        <WeatherMoonRegular fontSize={20} />
                                    ) : (
                                        <WeatherSunnyRegular fontSize={20} />
                                    )}
                                    <Switch
                                        checked={darkTheme}
                                        label={darkTheme ? "Use light theme" : "Use dark theme"}
                                        labelPosition="before"
                                    />
                                </div>
                            </MenuItem>
                            <MenuItem
                                icon={<SignOutRegular fontSize={20} />}
                                onClick={() => setOpen(true)}
                            >
                                Sign out
                            </MenuItem>
                        </MenuList>
                    </MenuPopover>
                </Menu>
            </div>

            <Dialog
                open={open}
                onOpenChange={(_, data) => {
                    setOpen(data.open);
                }}
            >
                <DialogSurface>
                    <DialogBody>
                        <DialogTitle>Sign Out</DialogTitle>
                        <DialogContent>Do you want to sign out from Dusseldorf and clear the cache?</DialogContent>
                        <DialogActions>
                            <Button
                                appearance="primary"
                                icon={<SignOutRegular />}
                                onClick={() => {
                                    Logger.Info("Sign out confirmed");
                                    setOpen(false);
                                    localStorage.clear();
                                    sessionStorage.clear();
                                    msal.logoutRedirect().catch((err) => {
                                        Logger.Error(err);
                                    });
                                }}
                            >
                                Sign out
                            </Button>
                            <DialogTrigger disableButtonEnhancement>
                                <Button
                                    appearance="secondary"
                                    icon={<DismissRegular />}
                                >
                                    Cancel
                                </Button>
                            </DialogTrigger>
                        </DialogActions>
                    </DialogBody>
                </DialogSurface>
            </Dialog>

            <ApiErrorBar />
        </>
    );
};
