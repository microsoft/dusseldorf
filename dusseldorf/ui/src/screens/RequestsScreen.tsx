// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, makeStyles, Subtitle1, Tooltip } from "@fluentui/react-components";
import { ArrowSyncRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

import { ColumnManager, ColumnConfig } from "../Components/ColumnManager";
import { RequestDetails } from "../Components/Requests/RequestDetails";
import { RequestTable } from "../Components/Requests/RequestTable";
import { ResizableSplitPanel } from "../Components/ResizableSplitPanel";
import { DssldrfRequest } from "../Types/DssldrfRequest";

const useStyles = makeStyles({
    header: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "10px"
    },
    headerLeft: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        gap: "8px"
    },
    headerRight: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        gap: "4px"
    }
});

/**
 * Default column configuration
 */
const defaultColumnConfig: ColumnConfig[] = [
    { id: "protocol", label: "Protocol", visible: true },
    { id: "clientip", label: "Client IP", visible: true },
    { id: "timestamp", label: "Timestamp", visible: true, required: true },
    { id: "request", label: "Request", visible: true, required: true },
    { id: "response", label: "Response", visible: true }
];

interface IRequestsScreenProps {
    zone: string;
}

export const RequestsScreen = ({ zone }: IRequestsScreenProps) => {
    const styles = useStyles();

    // Control current request
    const [request, setRequest] = useState<DssldrfRequest | undefined>();

    // Control column management
    const [columnConfig, setColumnConfig] = useState<ColumnConfig[]>(defaultColumnConfig);

    // Control refresh nudge
    const [nudge, setNudge] = useState<boolean>(false);

    // When zone changes, reset current request
    useEffect(() => {
        setRequest(undefined);
    }, [zone]);

    return (
        <ResizableSplitPanel
            leftPanel={
                <div>
                    <div className={styles.header}>
                        <div className={styles.headerLeft}>
                            <Subtitle1>Network Requests</Subtitle1>
                        </div>
                        
                        <div className={styles.headerRight}>
                            <ColumnManager
                                columns={columnConfig}
                                onColumnsChange={setColumnConfig}
                            />
                            
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
                    </div>

                    <RequestTable
                        zone={zone}
                        request={request}
                        setRequest={setRequest}
                        nudge={nudge}
                        columnConfig={columnConfig}
                    />
                </div>
            }
            rightPanel={
                <RequestDetails
                    zone={zone}
                    request={request}
                />
            }
            initialLeftWidth={48}
            minLeftWidth={25}
            maxLeftWidth={75}
        />
    );
};
