// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Body1Strong,
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
    TableColumnDefinition,
    Textarea
} from "@fluentui/react-components";
import { DismissRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

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

const columns: TableColumnDefinition<JwtClaim>[] = [
    createTableColumn<JwtClaim>({
        columnId: "keyColumn",
        renderHeaderCell: () => {
            return "Claim";
        },
        renderCell: (claim) => {
            const dictClaim = claimsDictionary[claim.key];
            return (
                <DataGridCell style={{ maxWidth: 300, wordWrap: "break-word" }}>{dictClaim ?? claim.key}</DataGridCell>
            );
        }
    }),
    createTableColumn<JwtClaim>({
        columnId: "valueColumn",
        renderHeaderCell: () => {
            return "Value";
        },
        renderCell: (claim) => {
            return <DataGridCell style={{ maxWidth: 300, wordWrap: "break-word" }}>{claim.value}</DataGridCell>;
        }
    }),
    createTableColumn<JwtClaim>({
        columnId: "copyColumn",
        renderHeaderCell: () => {
            return null;
        },
        renderCell: (claim) => {
            return (
                <DataGridCell style={{ minWidth: 20, maxWidth: 20 }}>
                    <CopyButton text={claim.value} />
                </DataGridCell>
            );
        }
    })
];

interface AnalyzerProps {
    open: boolean;
    setOpen: (newOpen: boolean) => void;
    payload: string;
}

export const Analyzer = ({ open, setOpen, payload }: AnalyzerProps) => {
    // boolean to close
    const [payload1, setPayload1] = useState<string>(payload);
    const [payload2, setPayload2] = useState<string>("");
    const [jwtDecoded, setJwtDecoded] = useState<string>("");

    const [showBase64Blade, setShowBase64Blade] = useState<boolean>(false);
    const [showJwtBlade, setShowJwtBlade] = useState<boolean>(false);

    // the JWT claims
    const [jwtClaims, setJwtClaims] = useState<JwtClaim[]>([]);

    useEffect(() => {
        setPayload1(payload);
        setPayload2("");
        setJwtDecoded("");
        setShowBase64Blade(false);
        setShowJwtBlade(false);
    }, [payload]);

    const base64decode = (input: string) => {
        try {
            const decoded = atob(input);
            return decoded;
        } catch {
            // invalid
            return input;
        }
    };

    return (
        <Drawer
            style={{ width: "40%", padding: 10 }}
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

            <DrawerBody style={{ marginTop: 10 }}>
                <div className="stack">
                    <Body1Strong>Original Payload</Body1Strong>
                    <Textarea
                        //!TODO: fix font
                        rows={5}
                        value={payload1}
                        onChange={(_, data) => {
                            setPayload1(data.value);
                        }}
                    />
                </div>

                <Divider style={{ paddingTop: 20, paddingBottom: 20 }} />

                {/* a normal Base64 decode */}

                <div
                    className="stack hstack-gap"
                    style={{ paddingBottom: "30px" }}
                >
                    <Button
                        onClick={() => {
                            setPayload2(base64decode(payload1));
                            setJwtDecoded("");
                            setShowBase64Blade(true);
                            setShowJwtBlade(false);
                            setJwtClaims([]);
                        }}
                    >
                        Base64 Decode
                    </Button>

                    <Button
                        onClick={() => {
                            // The payload may have a "Bearer " prefix, we need to remove that
                            const hdrName = "Bearer ";
                            let _payload: string = payload1;
                            if (_payload.startsWith(hdrName)) {
                                _payload = _payload.substring(7);
                            }

                            const parts = _payload.split(".");
                            if (parts.length === 3) {
                                const header = base64decode(parts[0]);
                                const payload = base64decode(parts[1]);
                                const signature = parts[2];
                                setJwtDecoded(`${header}.\n${payload}.\n${signature}`);

                                // set the claims
                                const claims = JSON.parse(payload) as Record<string, string>;
                                const _claims: JwtClaim[] = [];
                                Object.entries(claims).forEach(([key, value]) => {
                                    _claims.push({ key: key, value: value });
                                });
                                setJwtClaims(_claims);
                            } else {
                                setJwtDecoded("Error: Invalid JWT");
                                setJwtClaims([]);
                            }

                            setPayload2("");
                            setShowBase64Blade(false);
                            setShowJwtBlade(true);
                        }}
                    >
                        JWT Decode
                    </Button>
                </div>

                {showBase64Blade && (
                    <div className="stack">
                        <Body1Strong>Decoded Payload</Body1Strong>
                        <Textarea
                            //!TODO: fix font
                            rows={5}
                            value={payload2}
                            readOnly={true}
                        />
                    </div>
                )}

                {showJwtBlade && (
                    <div className="stack">
                        <Body1Strong>Decoded JWT</Body1Strong>

                        <Textarea
                            //!TODO: fix font
                            rows={5}
                            value={jwtDecoded}
                            readOnly={true}
                            style={{ marginBottom: 20 }}
                        />

                        <DataGrid
                            items={jwtClaims}
                            columns={columns}
                            noNativeElements={false}
                            style={{ tableLayout: "auto" }}
                        >
                            <DataGridHeader>
                                <DataGridRow>
                                    {({ renderHeaderCell }) => (
                                        <DataGridHeaderCell>
                                            <b>{renderHeaderCell()}</b>
                                        </DataGridHeaderCell>
                                    )}
                                </DataGridRow>
                            </DataGridHeader>
                            <DataGridBody<JwtClaim>>
                                {({ item }) => (
                                    <DataGridRow<JwtClaim> style={{ borderWidth: 0 }}>
                                        {({ renderCell }) => renderCell(item)}
                                    </DataGridRow>
                                )}
                            </DataGridBody>
                        </DataGrid>
                    </div>
                )}
            </DrawerBody>
        </Drawer>
    );
};
