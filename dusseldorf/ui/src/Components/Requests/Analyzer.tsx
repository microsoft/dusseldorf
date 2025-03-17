// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Button,
    createTableColumn,
    DataGrid,
    DataGridBody,
    DataGridCell,
    DataGridHeader,
    DataGridHeaderCell,
    DataGridRow,
    Divider,
    Drawer,
    DrawerBody,
    DrawerHeader,
    DrawerHeaderTitle,
    Field,
    makeStyles,
    Menu,
    MenuItem,
    MenuList,
    MenuPopover,
    MenuTrigger,
    MessageBar,
    SelectTabData,
    SelectTabEvent,
    Tab,
    TableCellLayout,
    TableColumnDefinition,
    TabList,
    TabValue,
    Text,
    Textarea
} from "@fluentui/react-components";
import { DismissRegular } from "@fluentui/react-icons";
import { useEffect, useRef, useState } from "react";

import { CopyButton } from "../CopyButton";

interface JwtClaim {
    key: string;
    value: string;
}

const claimsDictionary: Record<string, string> = {
    aud: "Audience (aud)",
    iss: "Issuer (iss)",
    sub: "Subject (sub)",
    exp: "Expiration (exp)",
    nbf: "Not Before (nbf)",
    iat: "Issued At (iat)",
    jti: "JWT ID (jti)"
};

const columnSizingOptions = {
    claim: {
        minWidth: 100,
        defaultWidth: 200
    },
    value: {
        minWidth: 100,
        defaultWidth: 200
    },
    copy: {
        minWidth: 30,
        maxWidth: 30
    }
};

const base64decode = (input: string) => {
    try {
        const decoded = atob(input);
        return decoded;
    } catch {
        // invalid
        return input;
    }
};

const useStyles = makeStyles({
    drawer: {
        width: "40%",
        minWidth: "400px",
        padding: "10px"
    },
    code: {
        fontFamily: "monospace"
    },
    panel: {
        display: "grid",
        padding: "10px 0px",
        rowGap: "20px"
    },
    divider: {
        padding: "20px 0px"
    },
    text: {
        wordBreak: "break-word"
    },
    row: {
        padding: "5px 0px"
    }
});

interface AnalyzerProps {
    open: boolean;
    setOpen: (newOpen: boolean) => void;
    initPayload: string;
}

export const Analyzer = ({ open, setOpen, initPayload }: AnalyzerProps) => {
    const styles = useStyles();

    // Control tabbing
    const [selectedValue, setSelectedValue] = useState<TabValue>("base64");

    const onTabSelect = (_: SelectTabEvent, data: SelectTabData) => {
        setSelectedValue(data.value);
    };

    // Control payload
    const [payload, setPayload] = useState<string>(initPayload);

    useEffect(() => {
        if (open) {
            setPayload(initPayload);
        }
    }, [initPayload, open]);

    // refMap and Menu section of DataGrid used for accessibility reasons
    const refMap = useRef<Record<string, HTMLElement | null>>({});

    // Base64 Decode Tab
    const Base64Tab = () => {
        return (
            <div
                className={styles.panel}
                role="tabpanel"
                aria-labelledby="base64-tab-id"
            >
                <Field label="Decoded Payload">
                    <Textarea
                        textarea={{ className: styles.code }}
                        rows={5}
                        value={base64decode(payload)}
                        readOnly={true}
                    />
                </Field>
            </div>
        );
    };

    // JWT claims table
    const columns: TableColumnDefinition<JwtClaim>[] = [
        createTableColumn<JwtClaim>({
            columnId: "claim",
            renderHeaderCell: () => {
                return "Claim";
            },
            renderCell: (claim) => {
                return <Text className={styles.text}>{claimsDictionary[claim.key] ?? claim.key}</Text>;
            }
        }),
        createTableColumn<JwtClaim>({
            columnId: "value",
            renderHeaderCell: () => {
                return "Value";
            },
            renderCell: (claim) => {
                return <Text className={styles.text}>{claim.value}</Text>;
            }
        }),
        createTableColumn<JwtClaim>({
            columnId: "copy",
            renderHeaderCell: () => {
                return null;
            },
            renderCell: (claim) => {
                return <CopyButton text={claim.value} />;
            }
        })
    ];

    // JWT Decode Tab
    const JwtTab = () => {
        let jwt = payload;

        // The payload may have a "Bearer " prefix, we need to remove that
        if (jwt.startsWith("Bearer ")) {
            jwt = jwt.substring(7);
        }

        let decoded = "";
        let claims: JwtClaim[] = [];
        let error: "decoded" | "claims" | "none" = "none";

        const parts = jwt.split(".");
        if (parts.length === 3) {
            // Decode the JWT
            const header = base64decode(parts[0]);
            const body = base64decode(parts[1]);
            const signature = parts[2];
            decoded = `${header}.\n${body}.\n${signature}`;

            // Parse the claims
            try {
                const claimsRecord = JSON.parse(body) as Record<string, string>;
                Object.entries(claimsRecord).forEach(([key, value]) => {
                    claims.push({ key: key, value: value.toString() });
                });
            } catch {
                error = "claims";
            }
        } else {
            error = "decoded";
        }

        return (
            <div
                className={styles.panel}
                role="tabpanel"
                aria-labelledby="jwt-tab-id"
            >
                {
                    // Show the decoded JWT if it could be decoded
                    error !== "decoded" ? (
                        <Field label="Decoded JWT">
                            <Textarea
                                textarea={{ className: styles.code }}
                                rows={5}
                                value={decoded}
                                readOnly={true}
                            />
                        </Field>
                    ) : (
                        <MessageBar intent="warning">Error: Invalid JWT format</MessageBar>
                    )
                }

                {
                    // Show the claims if they could be parsed
                    error === "none" && (
                        <DataGrid
                            aria-label="JWT Claims"
                            items={claims}
                            columns={columns}
                            resizableColumns
                            columnSizingOptions={columnSizingOptions}
                        >
                            <DataGridHeader>
                                <DataGridRow selectionCell={null}>
                                    {({ renderHeaderCell, columnId }, dataGrid) => (
                                        <Menu openOnContext>
                                            <MenuTrigger>
                                                <DataGridHeaderCell ref={(el) => (refMap.current[columnId] = el)}>
                                                    <TableCellLayout truncate>{renderHeaderCell()}</TableCellLayout>
                                                </DataGridHeaderCell>
                                            </MenuTrigger>
                                            <MenuPopover>
                                                <MenuList>
                                                    <MenuItem
                                                        onClick={dataGrid.columnSizing_unstable.enableKeyboardMode(
                                                            columnId
                                                        )}
                                                    >
                                                        Keyboard Column Resizing
                                                    </MenuItem>
                                                </MenuList>
                                            </MenuPopover>
                                        </Menu>
                                    )}
                                </DataGridRow>
                            </DataGridHeader>
                            <DataGridBody<JwtClaim>>
                                {({ item }) => (
                                    <DataGridRow<JwtClaim> className={styles.row}>
                                        {({ renderCell }) => (
                                            <DataGridCell>
                                                <TableCellLayout truncate>{renderCell(item)}</TableCellLayout>
                                            </DataGridCell>
                                        )}
                                    </DataGridRow>
                                )}
                            </DataGridBody>
                        </DataGrid>
                    )
                }

                {
                    // Show an error message if the claims could not be parsed but the JWT could be decoded
                    error === "claims" && <MessageBar intent="warning">Error: Could not parse JWT claims</MessageBar>
                }
            </div>
        );
    };

    return (
        <Drawer
            className={styles.drawer}
            position="end"
            separator
            open={open}
            onOpenChange={(_, data) => setOpen(data.open)}
        >
            <DrawerHeader>
                <DrawerHeaderTitle
                    action={
                        <Button
                            appearance="subtle"
                            aria-label="Close"
                            icon={<DismissRegular />}
                            onClick={() => setOpen(false)}
                        />
                    }
                >
                    HTTP Payload Analyzer
                </DrawerHeaderTitle>
            </DrawerHeader>

            <DrawerBody>
                <Field label="Original Payload">
                    <Textarea
                        textarea={{ className: styles.code }}
                        rows={5}
                        value={payload}
                        onChange={(_, data) => {
                            setPayload(data.value);
                        }}
                    />
                </Field>

                <Divider className={styles.divider} />

                <TabList
                    selectedValue={selectedValue}
                    onTabSelect={onTabSelect}
                    appearance="subtle-circular"
                >
                    <Tab
                        id="base64-tab-id"
                        value="base64"
                    >
                        Base64 Decode
                    </Tab>
                    <Tab
                        id="jwt-tab-id"
                        value="jwt"
                    >
                        JWT Decode
                    </Tab>
                </TabList>

                <div>
                    {selectedValue === "base64" && <Base64Tab />}
                    {selectedValue === "jwt" && <JwtTab />}
                </div>
            </DrawerBody>
        </Drawer>
    );
};
