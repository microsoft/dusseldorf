// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Button,
    Text,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    DialogTrigger,
    MessageBar,
    Select,
    Input,
    makeStyles,
    ToolbarButton
} from "@fluentui/react-components";
import { PeopleRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

import { AuthTable } from "./AuthTable";
import { DusseldorfAPI } from "../../DusseldorfApi";
import { Logger } from "../../Helpers/Logger";
import { User } from "../../Types/User";

export class PERMISSION {
    static READONLY = 0;
    static READWRITE = 10;
    static ASSIGNROLES = 20;
    static OWNER = 999;
}

const useStyles = makeStyles({
    dialog: {
        width: "500px"
    }
});

interface AuthDialogProps {
    zone: string;
}

export const AuthDialog = ({ zone }: AuthDialogProps) => {
    const styles = useStyles();

    const [users, setUsers] = useState<User[]>([]);

    const [username, setUsername] = useState<string>("");
    const [permission, setPermission] = useState<number>(PERMISSION.READONLY);
    const [error, setError] = useState<string>("");

    const refreshUsers = () => {
        DusseldorfAPI.GetUsers(zone)
            .then((newUsers) => {
                setUsers(newUsers);
            })
            .catch((err) => {
                setUsers([]);
                Logger.Error(err);
            });
    };

    useEffect(() => {
        refreshUsers();
    }, [zone]);

    return (
        <Dialog>
            <DialogTrigger disableButtonEnhancement>
                <ToolbarButton icon={<PeopleRegular />}>Auth</ToolbarButton>
            </DialogTrigger>
            <DialogSurface className={styles.dialog}>
                <DialogBody>
                    <DialogTitle>Manage Users</DialogTitle>
                    <DialogContent className="stack vstack-gap">
                        <Text>
                            Add or remove users from this zone ({zone}). Please type their alias and select a permission
                            level. Note that currently security groups are not supported.
                        </Text>
                        <AuthTable
                            users={users}
                            refreshUsers={refreshUsers}
                            zone={zone}
                        />
                        <div
                            className="stack hstack-gap"
                            style={{ paddingTop: "20px" }}
                        >
                            <Input
                                aria-label="User alias"
                                placeholder="User alias"
                                onChange={(_, data) => {
                                    setUsername(data.value);
                                }}
                                value={username}
                            />

                            <Select
                                aria-label="Permission"
                                onChange={(_, data) => {
                                    setPermission(parseInt(data.value));
                                }}
                                value={permission}
                            >
                                <option value={PERMISSION.READONLY}>Read Only</option>
                                <option value={PERMISSION.READWRITE}>Read Write</option>
                                <option value={PERMISSION.ASSIGNROLES}>Assign Roles</option>
                                <option value={PERMISSION.OWNER}>Owner</option>
                            </Select>

                            <Button
                                appearance="primary"
                                onClick={() => {
                                    // if the user is empty, show an error
                                    if (username.length == 0) {
                                        setError("Please enter a user alias");
                                        return;
                                    }

                                    // call the api to add the user
                                    DusseldorfAPI.AddUserToZone(zone, username, permission)
                                        .then(() => {
                                            setError("");
                                            setUsername("");
                                            refreshUsers();
                                        })
                                        .catch((err) => {
                                            setError(
                                                "An error occurred. This alias may have access already or not be allowed."
                                            );
                                            Logger.Error(err);
                                        });
                                }}
                            >
                                Add User
                            </Button>
                        </div>
                        {error && <MessageBar intent="error">{error}</MessageBar>}
                    </DialogContent>
                    <DialogActions>
                        <DialogTrigger disableButtonEnhancement>
                            <Button>Close</Button>
                        </DialogTrigger>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
};
