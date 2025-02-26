// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Divider, makeStyles, Subtitle1, Tooltip } from "@fluentui/react-components";
import { ArrowSyncRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

import { RequestDetails } from "../Components/Requests/RequestDetails";
import { RequestTable } from "../Components/Requests/RequestTable";
import { DssldrfRequest } from "../Helpers/Types";

const useStyles = makeStyles({
    root: {
        display: "flex",
        flexDirection: "row"
    },
    left: {
        minWidth: "48%",
        maxWidth: "48%",
        display: "flex",
        flexDirection: "column",
        columnGap: "10px"
    },
    right: {
        minWidth: "48%",
        maxWidth: "48%"
    },
    header: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center"
    },
    divider: {
        paddingLeft: "2%",
        paddingRight: "2%"
    }
});

interface IRequestsScreenProps {
    zone: string;
}

export const RequestsScreen = ({ zone }: IRequestsScreenProps) => {
    const styles = useStyles();

    // Control current request
    const [request, setRequest] = useState<DssldrfRequest | undefined>();
    const [nudge, setNudge] = useState<boolean>(false);

    // When zone changes, reset current request
    useEffect(() => {
        setRequest(undefined);
    }, [zone]);

    return (
        <div className={styles.root}>
            <div className={styles.left}>
                <div className={styles.header}>
                    <Subtitle1>Network Requests</Subtitle1>

                    <Tooltip
                        content="Refresh"
                        relationship="label"
                    >
                        <Button
                            appearance="subtle"
                            icon={<ArrowSyncRegular />}
                            onClick={() => {
                                setNudge(!nudge);
                            }}
                        />
                    </Tooltip>
                </div>

                <RequestTable
                    zone={zone}
                    request={request}
                    setRequest={setRequest}
                    nudge={nudge}
                />
            </div>

            <Divider
                vertical
                className={styles.divider}
            />

            <div className={styles.right}>
                <RequestDetails
                    zone={zone}
                    request={request}
                />
            </div>
        </div>
    );
};
