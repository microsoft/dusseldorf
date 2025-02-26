// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Body1Strong, MessageBar, Subtitle1, Text } from "@fluentui/react-components";
import { useEffect, useState } from "react";

import { DnsRequestDetails } from "./DnsRequestDetails";
import { HttpRequestDetails } from "./HttpRequestDetails";
import { DssldrfRequest } from "../../Helpers/Types";

/**
 * A custom timestamp formatter
 */
const formatTimestamp = (ts: string|number) => {
    // If the timestamp is a string, convert it to a number
    if (typeof ts === "string") { ts = parseInt(ts); }
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
}

export function RequestDetails({ request }: IRequestDetailsProps) {
    // Control what details are shown
    const [component, setComponent] = useState<React.JSX.Element>();

    // When the request changes, update the details
    useEffect(() => {

        if (request !== undefined) {
            if(!request.protocol)
            {
                setComponent(<Text>{"Invalid protocol"}</Text>);                
            }
            else
            {
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

    // If there is a request, show the details
    return (
        <div className="stack vstack-gap">
            <Subtitle1>Request Details</Subtitle1>

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
