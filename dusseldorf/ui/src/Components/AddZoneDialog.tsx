// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { useContext, useEffect, useState } from "react";
import { AddSingleZoneDialog } from "./AddSingleZoneDialog";
import { AddBulkZoneDialog } from "./AddBulkZoneDialog";
import { DomainsContext } from "../App";

interface IAddZoneDialogProps {
    onDismiss: () => void;
    onSuccess: (fqdn?: string) => void;
    open: boolean;
}

export const AddZoneDialog = ({ onDismiss, onSuccess, open }: IAddZoneDialogProps) => {
    // Control domain options
    const domains = useContext(DomainsContext);
    const [domain, setDomain] = useState<string>(domains[0] ?? "");

    // Control dialog
    const [singleOpen, setSingleOpen] = useState<boolean>(false);
    const [bulkOpen, setBulkOpen] = useState<boolean>(false);

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
            />
            <AddBulkZoneDialog
                onDismiss={onDismiss}
                onSuccess={onSuccess}
                open={bulkOpen}
                onSwitch={onSwitch}
                domain={domain}
                setDomain={setDomain}
            />
        </>
    );
};
