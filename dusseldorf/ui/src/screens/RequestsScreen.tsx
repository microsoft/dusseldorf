// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Button,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    makeStyles,
    MessageBar,
    Subtitle1,
    Tooltip
} from "@fluentui/react-components";
import { ArrowSyncRegular, DeleteRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

import { ColumnManager, ColumnConfig } from "../Components/ColumnManager";
import { RequestDetails } from "../Components/Requests/RequestDetails";
import { RequestTable } from "../Components/Requests/RequestTable";
import { ResizableSplitPanel } from "../Components/ResizableSplitPanel";
import { DusseldorfAPI } from "../DusseldorfApi";
import { Logger } from "../Helpers/Logger";
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

    // Control clear-results confirmation dialog
    const [showClearDialog, setShowClearDialog] = useState<boolean>(false);
    const [clearError, setClearError] = useState<boolean>(false);

    // When zone changes, reset current request
    useEffect(() => {
        setRequest(undefined);
    }, [zone]);

    const handleClearResults = () => {
        setClearError(false);
        DusseldorfAPI.DeleteRequests(zone)
            .then((success) => {
                if (success) {
                    Logger.Info(`Cleared requests for zone ${zone}`);
                    setRequest(undefined);
                    setNudge(!nudge);
                } else {
                    setClearError(true);
                }
            })
            .catch((err) => {
                Logger.Error(err);
                setClearError(true);
            })
            .finally(() => {
                setShowClearDialog(false);
            });
    };

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
                                content="Clear all requests for this zone"
                                relationship="label"
                            >
                                <Button
                                    appearance="subtle"
                                    icon={<DeleteRegular />}
                                    onClick={() => {
                                        setClearError(false);
                                        setShowClearDialog(true);
                                    }}
                                />
                            </Tooltip>

                            <Dialog
                                open={showClearDialog}
                                onOpenChange={(_, data) => setShowClearDialog(data.open)}
                            >
                                <DialogSurface>
                                    <DialogBody>
                                        <DialogTitle>Clear all requests?</DialogTitle>
                                        <DialogContent>
                                            This will permanently delete all captured requests for <strong>{zone}</strong>.
                                            This action cannot be undone.
                                            {clearError && (
                                                <MessageBar intent="error" style={{ marginTop: 8 }}>
                                                    Failed to clear requests. You may not have write access to this zone.
                                                </MessageBar>
                                            )}
                                        </DialogContent>
                                        <DialogActions>
                                            <Button
                                                appearance="secondary"
                                                onClick={() => setShowClearDialog(false)}
                                            >
                                                Cancel
                                            </Button>
                                            <Button
                                                appearance="primary"
                                                icon={<DeleteRegular />}
                                                onClick={handleClearResults}
                                                style={{ backgroundColor: "#ef4444", borderColor: "#ef4444" }}
                                            >
                                                Clear Results
                                            </Button>
                                        </DialogActions>
                                    </DialogBody>
                                </DialogSurface>
                            </Dialog>
                            
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
