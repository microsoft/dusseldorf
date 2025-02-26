// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Body1Strong, Divider, InfoLabel } from "@fluentui/react-components";

import { DssldrfRequest, DnsRequest, DnsResponse } from "../../Types/DssldrfRequest";

const DnsTitle: Record<string, string> = {
    A: "DNS A Record",
    AAAA: "DNS AAAA Record",
    CNAME: "DNS CNAME Record",
    DNSKEY: "DNS DNSKEY Record",
    DS: "DNS DS Record",
    HTTPS: "DNS HTTPS Record",
    MX: "DNS MX Record",
    NS: "DNS NS Record",
    SOA: "DNS SOA Record",
    TXT: "DNS TXT Record"
};

const DnsSubtitle: Record<string, string> = {
    A: "This DNS records represents an IPv4 address that corresponds to the domain name.",
    AAAA: "This 'QUAD' DNS record represents the IPv6 address that corresponds to the domain name.",
    CNAME: "This canonical name is an alias for the domain name.",
    DNSKEY: "This DNS public key is used to verify the DNSSEC signature.",
    DS: "This DNSSEC record is used to verify the DNSKEY record.",
    HTTPS: "An HTTPS DNS record is used to provide information and parameters on how to access the a service via HTTPS, such as supported protocols, and public keys.",
    MX: "This DNS mail exchange record specifies the mail server responsible for accepting email messages on behalf of a domain name.",
    NS: "Name server",
    SOA: "Start of Authority",
    TXT: "Text record"
};

interface IDnsRequestDetailsProps {
    details: DssldrfRequest;
}

export const DnsRequestDetails = ({ details }: IDnsRequestDetailsProps) => {
    const req = details.request as DnsRequest;
    const resp = details.response as DnsResponse;

    // This is populated if we can parse the DNSResponseData correctly,
    const respData =
        resp.ResponseType == "TXT"
            ? resp.ResponseData.txt
            : resp.ResponseType == "A"
            ? resp.ResponseData.ip
            : resp.ResponseType == "AAAA"
            ? resp.ResponseData.ip
            : resp.ResponseType == "CNAME"
            ? resp.ResponseData.cname
            : resp.ResponseType == "NS"
            ? resp.ResponseData.ns
            : resp.ResponseType == "SOA"
            ? `${resp.ResponseData.mname ?? ""}  ${resp.ResponseData.rname ?? ""} [${
                  resp.ResponseData.times?.join(" ") ?? ""
              }]`
            : JSON.stringify(resp.ResponseData); // default

    return (
        <div className="stack vstack-gap">
            <div className="stack vstack">
                <Body1Strong>DNS Request Type</Body1Strong>
                <InfoLabel
                    info={
                        <div className="stack vstack-gap">
                            <strong>{DnsTitle[req.request_type] ?? "DNS Record"}</strong>
                            {DnsSubtitle[req.request_type] ?? "Unknown record type"}
                        </div>
                    }
                >
                    {req.request_type}
                </InfoLabel>
            </div>

            <div className="stack vstack">
                <Body1Strong>DNS Name</Body1Strong>
                {resp.ResponseName}
            </div>

            <Divider style={{ paddingTop: 10, paddingBottom: 10 }} />

            <div className="stack vstack">
                <Body1Strong>Response Details</Body1Strong>
                {respData}
            </div>

            <div className="stack vstack">
                <Body1Strong>TTL</Body1Strong>
                {resp.TTL}
            </div>
        </div>
    );
};
