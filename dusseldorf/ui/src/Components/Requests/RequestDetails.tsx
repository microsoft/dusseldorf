// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Body1Strong,
    Button,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    MessageBar,
    Subtitle1,
    Text,
    Tooltip
} from "@fluentui/react-components";
import { DeleteRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

import { DnsRequestDetails } from "./DnsRequestDetails";
import { HttpRequestDetails } from "./HttpRequestDetails";
import { DusseldorfAPI } from "../../DusseldorfApi";
import { Logger } from "../../Helpers/Logger";
import { DssldrfRequest } from "../../Types/DssldrfRequest";

/**
 * A custom timestamp formatter
 */
const formatTimestamp = (ts: string | number) => {
    // If the timestamp is a string, convert it to a number
    if (typeof ts === "string") {
        ts = parseInt(ts);
    }
    // tmiestamp is in seconds, make into milliseconds
    ts = ts * 1000;

    const d = new Date(ts).toLocaleString("en-US", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "numeric",
        minute: "numeric",
        second: "numeric"
    });

    return d;
};

interface IRequestDetailsProps {
    zone: string;
    request: DssldrfRequest | undefined;
    onDelete?: () => void;
}

export function RequestDetails({ zone, request, onDelete }: IRequestDetailsProps) {
    // Control what details are shown
    const [component, setComponent] = useState<React.JSX.Element>();

    // Control delete confirmation dialog
    const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
    const [deleteError, setDeleteError] = useState<boolean>(false);

    // When the request changes, update the details
    useEffect(() => {
        if (request !== undefined) {
            if (!request.protocol) {
                setComponent(<Text>{"Invalid protocol"}</Text>);
            } else {
                const newProtocol = request.protocol.toLowerCase();
                if (newProtocol == "dns") {
                    setComponent(<DnsRequestDetails details={request} />);
                }

                if (newProtocol == "http" || newProtocol == "https") {
                    setComponent(<HttpRequestDetails details={request} />);
                }
            }
        }
    }, [request]);

    // If there is no request yet, don't show anything
    if (!request) {
        return <div />;
    }

    const handleDeleteRequest = () => {
        setDeleteError(false);
        DusseldorfAPI.DeleteRequest(zone, String(request.time))
            .then((success) => {
                if (success) {
                    Logger.Info(`Deleted request ${request.time} for zone ${zone}`);
                    setShowDeleteDialog(false);
                    onDelete?.();
                } else {
                    setDeleteError(true);
                }
            })
            .catch((err) => {
                Logger.Error(err);
                setDeleteError(true);
            });
    };

    // If there is a request, show the details
    return (
        <div className="stack vstack-gap">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Subtitle1>Request Details</Subtitle1>
                <Tooltip content="Delete this request" relationship="label">
                    <Button
                        appearance="subtle"
                        icon={<DeleteRegular />}
                        onClick={() => {
                            setDeleteError(false);
                            setShowDeleteDialog(true);
                        }}
                    />
                </Tooltip>
            </div>

            <Dialog
                open={showDeleteDialog}
                onOpenChange={(_, data) => setShowDeleteDialog(data.open)}
            >
                <DialogSurface>
                    <DialogBody>
                        <DialogTitle>Delete this request?</DialogTitle>
                        <DialogContent>
                            This will permanently delete the selected request from <strong>{zone}</strong>.
                            This action cannot be undone.
                            {deleteError && (
                                <MessageBar intent="error" style={{ marginTop: 8 }}>
                                    Failed to delete request. You may not have write access to this zone.
                                </MessageBar>
                            )}
                        </DialogContent>
                        <DialogActions>
                            <Button
                                appearance="secondary"
                                onClick={() => setShowDeleteDialog(false)}
                            >
                                Cancel
                            </Button>
                            <Button
                                appearance="primary"
                                icon={<DeleteRegular />}
                                onClick={handleDeleteRequest}
                                style={{ backgroundColor: "#ef4444", borderColor: "#ef4444" }}
                            >
                                Delete
                            </Button>
                        </DialogActions>
                    </DialogBody>
                </DialogSurface>
            </Dialog>

            {(!request.request || !request.response) && (
                <MessageBar intent="error">We could not load additional details for this request.</MessageBar>
            )}

            <div className="stack hstack-gaplarge">
                <div className="stack vstack">
                    <Body1Strong>Client IP</Body1Strong>
                    {request.clientip}
                </div>

                <div className="stack vstack">
                    <Body1Strong>Protocol</Body1Strong>
                    {request.protocol}
                </div>

                <div className="stack vstack">
                    <Body1Strong>Timestamp</Body1Strong>
                    {formatTimestamp(request.time)}
                </div>
            </div>

            {component}
        </div>
    );
}
