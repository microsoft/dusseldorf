// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

export interface YamlRule {
    name: string;
    predicates?: Record<string, string>[];
    networkprotocol: string;
    results?: Record<string, string>[];
}

export interface Template {
    id: string;
    description: string;
    rules: YamlRule[];
    title: string;
}
