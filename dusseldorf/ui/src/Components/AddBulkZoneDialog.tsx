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
    Field,
    Input,
    Link,
    MessageBar,
    Select
} from "@fluentui/react-components";
import { AddRegular, DismissRegular } from "@fluentui/react-icons";
import { useContext, useState } from "react";

import { DomainsContext } from "../App";
import { DusseldorfAPI } from "../DusseldorfApi";
import { Logger } from "../Helpers/Logger";

interface AddBulkZoneDialogProps {
    onDismiss: () => void;
    onSuccess: (fqdn?: string) => void;
    open: boolean;
    onSwitch: () => void;
    domain: string;
    setDomain: (domain: string) => void;
}

export const AddBulkZoneDialog = ({
    onDismiss,
    onSuccess,
    open,
    onSwitch,
    domain,
    setDomain
}: AddBulkZoneDialogProps) => {
    const domains = useContext(DomainsContext).map((domainOption) => (
            <option
                key={domainOption}
                value={domainOption}
            >
                {domainOption}
            </option>
        ));
        
    const [numZones, setNumZones] = useState<number>(1);

    const [completeMsg, setCompleteMsg] = useState<boolean>(false);
    const [errorMsg, setErrorMsg] = useState<boolean>(false);

    const addZones = (_domain: string, _numZones: number) => {
        if (Number.isNaN(_numZones) || _numZones <= 0 || _numZones > 100) {
            return;
        }

        DusseldorfAPI.AddZone("", _domain, _numZones)
            .then((success) => {
                if (success) {
                    Logger.Info(`addZone(${_domain}, ${_numZones}): success`);
                    setCompleteMsg(true);
                    setTimeout(() => {
                        onSuccess();
                    }, 1337);
                } else {
                    Logger.Info(`addZone(${_domain}, ${_numZones}): error`);
                    setErrorMsg(true);
                }
            })
            .catch(() => {
                Logger.Info(`addZone(${_domain}, ${_numZones}): error`);
                setErrorMsg(true);
            });
    };

    return (
        <Dialog open={open} onOpenChange={(_, data) => {
            if (data.type == "backdropClick" || data.type == "escapeKeyDown") {
                onDismiss();
            }
        }}>
            <DialogSurface style={{ width: 480 }}>
                <DialogBody>
                    <DialogTitle>Bulk Create DNS Zones</DialogTitle>
                    <DialogContent className="stack vstack-gap">
                        <Field
                            style={{ paddingTop: 20, width: 200 }}
                            label="Domain:"
                            orientation="horizontal"
                        >
                            <Select
                                title="Select a domain"
                                style={{ width: 140 }}
                                value={domain}
                                onChange={(_, data) => {
                                    setDomain(data.value);
                                    setErrorMsg(false);
                                }}
                            >
                                {domains}
                            </Select>
                        </Field>

                        <Field
                            style={{ width: 380 }}
                            label="Number of zones:"
                            orientation="horizontal"
                            validationMessage={"Must be between 1 and 100"}
                            validationState={Number.isNaN(numZones) || numZones > 100 ? "error" : "none"}
                        >
                            <Input
                                title="Number of zones to be created"
                                style={{ width: 140 }}
                                value={Number.isNaN(numZones) ? "" : numZones.toString()}
                                onChange={(_, data) => {
                                    const newNum = parseInt(data.value);
                                    if (Number.isNaN(newNum)) {
                                        setNumZones(NaN);
                                    } else {
                                        setNumZones(Number(newNum.toString().slice(0, 3)));
                                    }
                                }}
                                onBlur={() => {
                                    if (Number.isNaN(numZones) || numZones <= 0) {
                                        setNumZones(1);
                                    } else if (numZones > 100) {
                                        setNumZones(100);
                                    }
                                }}
                            />
                        </Field>

                        <Link
                            onClick={() => {
                                onSwitch();
                            }}
                            title="Create single zone"
                            style={{ paddingTop: "10px" }}
                        >
                            Create single zone &raquo;
                        </Link>

                        {errorMsg && (
                            <MessageBar intent="error">Insufficient permissions to add zones on domain.</MessageBar>
                        )}

                        {completeMsg && <MessageBar intent="success">Zones successfully added.</MessageBar>}
                    </DialogContent>

                    <DialogActions>
                        <Button
                            style={{ width: 120 }}
                            appearance="primary"
                            icon={<AddRegular />}
                            onClick={() => {
                                addZones(domain, numZones);
                            }}
                            disabled={isNaN(numZones) || numZones < 1 || numZones > 100 || errorMsg}
                        >
                            Add zones
                        </Button>
                        <Button
                            icon={<DismissRegular />}
                            onClick={() => onDismiss()}
                        >
                            Close
                        </Button>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
};
