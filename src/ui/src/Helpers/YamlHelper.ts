// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import yaml from 'js-yaml';
import { NewRule, NewRuleComponent, YamlRule } from './Types';

export class YamlHelper {
    static ParseToRules = (rawYamls: string) => {

        const parsedYaml = yaml.load(rawYamls) as YamlRule[]
        const retval: NewRule[] = [];

        parsedYaml.forEach(yamlRule => {

            if (!yamlRule.name) {
                throw Error("Invalid rule name")
            } else if (!yamlRule.networkprotocol) {
                throw Error("Invalid rule protocol")
            }

            // make a rule
            const newRule: NewRule = {
                name: yamlRule.name,
                zone: "",
                priority: 1,
                networkprotocol: yamlRule.networkprotocol,
                rulecomponents: [],
            }

            // parse predicates
            yamlRule.predicates?.forEach(predicate => {
                for (const key in predicate) {
                    const component: NewRuleComponent = {
                        isPredicate: true,
                        actionName: key,
                        actionValue: String(predicate[key])
                    }
                    newRule.rulecomponents?.push(component);
                }
            })

            yamlRule.results?.forEach(result => {
                for (const key in result) {
                    const component: NewRuleComponent = {
                        isPredicate: false,
                        actionName: key,
                        actionValue: String(result[key])
                    }
                    newRule.rulecomponents?.push(component);
                }
            })

            retval.push(newRule);
        });
        return retval;
    }
}