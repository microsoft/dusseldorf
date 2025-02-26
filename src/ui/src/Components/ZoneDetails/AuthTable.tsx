// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Body1Strong,
    Button,
    Caption1,
    createTableColumn,
    DataGrid,
    DataGridBody,
    DataGridCell,
    DataGridHeader,
    DataGridHeaderCell,
    DataGridRow,
    makeStyles,
    TableColumnDefinition,
    Tooltip
} from "@fluentui/react-components";
import { DeleteRegular } from "@fluentui/react-icons";

import { User } from "../../Helpers/Types"
import { DusseldorfAPI } from "../../DusseldorfApi";
import { Logger } from "../../Helpers/Logger";
import { PERMISSION } from "./AuthDialog";

const useStyles = makeStyles({
    aliasColumn: {
        minWidth: "100px",
        maxWidth: "250px",
        wordWrap: "break-word"
    },
    permissionColumn: {
        minWidth: "80px",
        maxWidth: "80px",
    }
});

export const mapPermission = (authzlevel: number) => {
    switch (authzlevel) {
        case PERMISSION.READONLY:
            return "read only";
        case PERMISSION.READWRITE:
            return "read write";
        case PERMISSION.ASSIGNROLES:
            return "assign roles";
        case PERMISSION.OWNER:
            return "owner";
        default:
            return "unknown";
    }
}

interface AuthTableProps {
    users: User[],
    refreshUsers: () => void
}

export const AuthTable = ({ users, refreshUsers }: AuthTableProps): JSX.Element => {

    const styles = useStyles();

    const columns: TableColumnDefinition<User>[] = [
        createTableColumn<User>({
            columnId: "aliasColumn",
            // compare: (userA, userB) => {
            //     return userA.alias.localeCompare(userB.alias);
            // },
            renderHeaderCell: () => {
                return (
                    <Body1Strong className={styles.aliasColumn}>
                        Alias
                    </Body1Strong>
                );
            },
            renderCell: (user) => {
                return (
                    <DataGridCell className={styles.aliasColumn}>
                        <Caption1>
                            {user.alias}
                        </Caption1>
                    </DataGridCell>
                );
            }
        }),
        createTableColumn<User>({
            columnId: "permissionColumn",
            compare: (userA, userB) => {
                return userB.authzlevel - userA.authzlevel;
            },
            renderHeaderCell: () => {
                return (
                    <Body1Strong>
                        Permission
                    </Body1Strong>
                );
            },
            renderCell: (user) => {
                return (
                    <DataGridCell>
                        <Caption1>
                            {mapPermission(user.authzlevel)}
                        </Caption1>
                    </DataGridCell>
                );
            }
        }),
        createTableColumn<User>({
            columnId: "deleteColumn",
            renderHeaderCell: () => {
                return "";
            },
            renderCell: (user) => {
                return (
                    <DataGridCell>
                        <Tooltip content={`Delete user: ${user.alias}`} relationship="label">
                            <Button
                                appearance="transparent"
                                icon={<DeleteRegular />}
                                disabled={
                                    // don't delete the only owner
                                    user.authzlevel === PERMISSION.OWNER && 
                                    users.filter(value => value.authzlevel === PERMISSION.OWNER).length === 1
                                }
                                onClick={() => {
                                    DusseldorfAPI.RemoveUserFromZone(user.zone, user.alias)
                                        .then(() => {
                                            refreshUsers();
                                        })
                                        .catch(err => {
                                            Logger.Error(err);
                                        })
                                }}
                            >
                            {user.zone}
                            </Button>
                        </Tooltip>
                    </DataGridCell>
                );
            }
        })
    ];

    return (
        <DataGrid
            items={users}
            columns={columns}
            sortable
            noNativeElements={false}
            style={{ tableLayout: "auto" }}
        >
            <DataGridHeader>
                <DataGridRow>
                    {({ renderHeaderCell }) => (
                        <DataGridHeaderCell>{renderHeaderCell()}</DataGridHeaderCell>
                    )}
                </DataGridRow>
            </DataGridHeader>
            <DataGridBody<User>>
                {({ item }) => (
                    <DataGridRow<User>>
                        {({ renderCell }) => (
                            <DataGridCell>{renderCell(item)}</DataGridCell>
                        )}
                    </DataGridRow>
                )}
            </DataGridBody>
        </DataGrid>
    );
}