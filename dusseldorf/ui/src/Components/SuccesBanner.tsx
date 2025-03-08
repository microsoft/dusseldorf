// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { MessageBar } from "@fluentui/react-components";
import { useState, useEffect, useContext } from "react";

import { DomainsContext } from "../App";

/**
 * Displays an error/success banner for Dusseldorf's config and status.
 * @returns
 */
export const SuccesBanner = () => {
    const domains = useContext(DomainsContext);
    const [success, setSuccess] = useState<boolean>(domains.length > 0);

    useEffect(() => {
        setSuccess(domains.length > 0);
    }, [domains]);

    return (
        <MessageBar intent={success ? "success" : "error"}>
            {success ? `Database loaded` : "Failed to load configuration."}
        </MessageBar>
    );
};
