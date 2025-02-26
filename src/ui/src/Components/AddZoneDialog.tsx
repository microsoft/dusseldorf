// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { useEffect, useState } from "react";
import { AddSingleZoneDialog } from "./AddSingleZoneDialog";
import { AddBulkZoneDialog } from "./AddBulkZoneDialog";
import { DusseldorfContext } from "../App";
import { DusseldorfAPI } from "../DusseldorfApi";

interface IAddZoneDialogProps {
    onDismiss: () => void;
    onSuccess: (fqdn?: string) => void;
    open: boolean;
}

export const AddZoneDialog = ({ onDismiss, onSuccess, open }: IAddZoneDialogProps) => {
    const [singleOpen, setSingleOpen] = useState<boolean>(false);
    const [bulkOpen, setBulkOpen] = useState<boolean>(false);

    const [domain, setDomain] = useState<string>("");

    const domains = [
        <option
            key={domain}
            value={domain}
        >
            {domain}
        </option>
    ];

    useEffect(() => {
        DusseldorfAPI.
            GetDomains().
            then((domains) => {
                setDomain(domains[0])
            });
    }, []);

    const onSwitch = () => {
        if (singleOpen) {
            setSingleOpen(false);
            setBulkOpen(true);
        } else {
            setBulkOpen(false);
            setSingleOpen(true);
        }
    };

    useEffect(() => {
        setBulkOpen(false);
        setSingleOpen(open);
    }, [open]);

    return (
        <>
            <AddSingleZoneDialog
                onDismiss={onDismiss}
                onSuccess={onSuccess}
                open={singleOpen}
                onSwitch={onSwitch}
                domain={domain}
                setDomain={setDomain}
                domains={domains}
            />
            <AddBulkZoneDialog
                onDismiss={onDismiss}
                onSuccess={onSuccess}
                open={bulkOpen}
                onSwitch={onSwitch}
                domain={domain}
                setDomain={setDomain}
                domains={domains}
            />
        </>
    );
};
