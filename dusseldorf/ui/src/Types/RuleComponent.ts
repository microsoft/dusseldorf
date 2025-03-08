// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

export interface NewRuleComponent {
    actionname: string;
    actionvalue: string;
    ispredicate: boolean;
}

export interface RuleComponent {
    actionname: string;
    actionvalue: string;
    componentid: string;
    ispredicate: boolean;
}
