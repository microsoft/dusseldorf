// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { NewRuleComponent, RuleComponent } from "./RuleComponent";

export interface NewRule {
    rulecomponents?: NewRuleComponent[];
    name: string;
    priority: number;
    networkprotocol: string;
    zone: string;
}

export interface Rule {
    rulecomponents: RuleComponent[];
    ruleid: string;
    name: string;
    priority: number;
    networkprotocol: string;
    zone: string;
}
