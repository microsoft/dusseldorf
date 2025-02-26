// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { MessageBar } from "@fluentui/react-components";
import { DusseldorfContext } from "../App";
import { useState, useEffect, useContext } from "react";

/**
 * Displays an error/success banner for Dusseldorf's config and status.
 * @returns
 */
export const SuccesBanner = () => {
    const { domain } = useContext(DusseldorfContext);
    const [success, setSuccess] = useState<boolean>(domain.length > 0);

    useEffect(() => {
        setSuccess(domain.length > 0);
    }, [domain]);

    return (
        <MessageBar intent={success ? "success" : "error"}>
            {success ? `Database loaded` : "Failed to load configuration."}
        </MessageBar>
    );
};
