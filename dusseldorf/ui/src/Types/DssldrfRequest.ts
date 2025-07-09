// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

export interface DssldrfRequest {
    zone: string;
    id: number;
    time: string;
    fqdn: string;
    protocol: string;
    clientip: string;
    request: object;
    response: object;
    reqsummary: string;
    respsummary: string;
}

/**
 * DNS-related types
 */

export interface DnsRequest {
    ttl: number;
    request_type: string;
}

export interface DnsResponse {
    TTL: number;
    ResponseData: DnsData;
    ResponseType: string;
    ResponseName?: string;
}

export interface DnsData {
    txt?: string;
    ip?: string;
    cname?: string;
    ns?: string;
    mname?: string;
    rname?: string;
    times?: string[];
    mx?: string;
    data?: string;
}

/**
 * HTTP-related types
 */

export interface HttpHeader {
    header: string;
    value: string;
}

export interface HttpRequest {
    tls: boolean;
    body?: string;
    body_b64?: string;
    path: string;
    method: string;
    headers: Record<string, string>;
    version: string;
}

export interface HttpResponse {
    body: string;
    code: number;
    headers: Record<string, string>;
}
