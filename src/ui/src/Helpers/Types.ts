// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

/**
 * Types used for creating new rules
 */

export interface NewRuleComponent {
    actionName: string,
    actionValue: string,
    isPredicate: boolean
}

export interface NewRule {
    rulecomponents?: NewRuleComponent[]
    name: string,
    priority: number,
    networkprotocol: string,
    zone: string
}


export interface DnsRespData {
    txt?: string,
    ip?: string,
    cname?: string,
    ns?: string,
    mname?: string,
    rname?: string,
    times?: string[],
    mx?: string,
    data?: string;
}

/**
 * Types decribing objects from the Dusseldorf API
 */

export interface User {
    zone: string,
    alias: string,
    authzlevel: number
}

export interface RuleComponent {
    actionname: string,
    actionvalue: string,
    componentid: string,
    ispredicate: boolean
}

export interface Rule {
    rulecomponents: RuleComponent[],
    ruleid: string,
    // components: RuleComponent[],
    // id: string,
    name: string,
    priority: number,
    networkprotocol: string,
    zone: string
}

export interface DssldrfRequest {
    zone: string,
    id: number,
    time: string,
    fqdn: string,
    protocol: string,
    clientip: string,
    request: string,
    response: string,
    reqsummary: string,
    respsummary: string
}

/**
 * Types related to Templates
 */

export interface YamlRule {
    name: string,
    predicates?: Record<string, string>[],
    networkprotocol: string,
    results?: Record<string, string>[]
}

export interface Template {
    id: string,
    description: string,
    rules: YamlRule[],
    title: string
}

