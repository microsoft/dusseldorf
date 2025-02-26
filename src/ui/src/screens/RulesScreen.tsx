// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Accordion,
    AccordionHeader,
    AccordionItem,
    AccordionPanel,
    Button,
    Divider,
    Link,
    makeStyles,
    MessageBar,
    MessageBarActions,
    MessageBarBody,
    MessageBarTitle,
    Subtitle1,
    Text
} from "@fluentui/react-components";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { AddRuleDialog } from "../Components/Rules/AddRuleDialog";
import { RuleDetails } from "../Components/Rules/RuleDetails";
import { RuleTable } from "../Components/Rules/RuleTable";
import { DusseldorfAPI } from "../DusseldorfApi";
import { Logger } from "../Helpers/Logger";
import { Rule } from "../Types/Rule";

/**
 * Create a rule that responds to GET or POST requests with 'hello world'.
 */
const makeHelloWorldRule = async (zone: string): Promise<Rule> => {
    const newRule = await DusseldorfAPI.AddRule(zone, "http", 100, "GET/POST response with hello world").catch(
        (err: Error) => {
            return Promise.reject(err);
        }
    );

    // Respond to HTTP GET and POST responses
    await DusseldorfAPI.AddRuleComponent(newRule, {
        ispredicate: true,
        actionname: "http.method",
        actionvalue: "get,post"
    }).catch((err: Error) => {
        return Promise.reject(err);
    });

    // Send a 200 response
    await DusseldorfAPI.AddRuleComponent(newRule, {
        ispredicate: false,
        actionname: "http.code",
        actionvalue: "200"
    }).catch((err: Error) => {
        return Promise.reject(err);
    });

    // And say hello
    await DusseldorfAPI.AddRuleComponent(newRule, {
        ispredicate: false,
        actionname: "http.body",
        actionvalue: "hello world"
    }).catch((err: Error) => {
        return Promise.reject(err);
    });

    return newRule;
};

/**
 * Create a rule that responds to DNS lookups with localhost.
 */
const makeLocalhostRule = async (zone: string): Promise<Rule> => {
    // IPv4 rule
    DusseldorfAPI.AddRule(zone, "dns", 100, "DNS A response (127.0.0.1)")
        .then(async (newRule4) => {
            // Respond to IPv4 DNS requests
            await DusseldorfAPI.AddRuleComponent(newRule4, {
                ispredicate: true,
                actionname: "dns.type",
                actionvalue: "A"
            })
            .catch((err: Error) => { return Promise.reject(err); });
            return newRule4;
        })
        .then(async (newRule4) => {
            // Respond with IPv4
            await DusseldorfAPI.AddRuleComponent(newRule4, {
                ispredicate: false,
                actionname: "dns.type",
                actionvalue: "A"
            })
            .catch((err: Error) => { return Promise.reject(err); });
            return newRule4;
        })
        .then(async (newRule4) => {
            // With localhost
            await DusseldorfAPI.AddRuleComponent(newRule4, {
                ispredicate: false,
                actionname: "dns.data",
                actionvalue: '{"ip":"127.0.0.1"}'
            })
            .catch((err: Error) => { return Promise.reject(err); });
            return newRule4;
        })
        .catch((err: Error) => {
            Logger.Error(err);
            return Promise.reject(err);
        });

    // IPv6 rule
    const newRule6 = await DusseldorfAPI.AddRule(zone, "dns", 100, "DNS AAAA response (::1)")
        .then(async (newRule6) => {
            // Respond to IPv6 DNS requests
            await DusseldorfAPI.AddRuleComponent(newRule6, {
                ispredicate: true,
                actionname: "dns.type",
                actionvalue: "AAAA"
            })
            .catch((err: Error) => { return Promise.reject(err); });
            return newRule6;
        })
        .then(async (newRule6) => {
            // Respond with IPv6
            await DusseldorfAPI.AddRuleComponent(newRule6, {
                ispredicate: false,
                actionname: "dns.type",
                actionvalue: "AAAA"
            })
            .catch((err: Error) => { return Promise.reject(err); });
            return newRule6;
        })
        .then(async (newRule6) => {
            // With localhost
            await DusseldorfAPI.AddRuleComponent(newRule6, {
                ispredicate: false,
                actionname: "dns.data",
                actionvalue: '{"ip":"::1"}'
            })
            .catch((err: Error) => { return Promise.reject(err); });
            return newRule6;
        })
        .catch((err: Error) => {
            Logger.Error(err);
            return Promise.reject(err);
        });

    return newRule6;
};

const useStyles = makeStyles({
    root: {
        display: "flex",
        flexDirection: "row"
    },
    left: {
        minWidth: "38%",
        maxWidth: "38%",
        display: "flex",
        flexDirection: "column",
        rowGap: "10px",
        height: "100%"
    },
    right: {
        minWidth: "58%",
        maxWidth: "58%"
    },
    divider: {
        paddingLeft: "2%",
        paddingRight: "2%"
    }
});

interface IRulesScreenProps {
    zone: string;
}

export const RulesScreen = ({ zone }: IRulesScreenProps) => {
    const navigate = useNavigate();
    const styles = useStyles();

    // Control current rule
    const [rule, setRule] = useState<Rule | undefined>();
    const [ruleId, setRuleId] = useState<string | undefined>();
    const [nudge, setNudge] = useState<boolean>(false);
    const [openItems, setOpenItems] = useState<unknown[]>([]);

    // When zone changes, reset current rule
    useEffect(() => {
        setRule(undefined);
        setRuleId(undefined);
    }, [zone]);

    return (
        <div className={styles.root}>
            <div className={styles.left}>
                <Subtitle1>Rules</Subtitle1>

                <RuleTable
                    zone={zone}
                    ruleId={ruleId}
                    setRuleId={setRuleId}
                    rule={rule}
                    setRule={setRule}
                    nudge={nudge}
                />

                <AddRuleDialog
                    zone={zone}
                    onSave={(newRule: Rule) => {
                        setRuleId(newRule.ruleid);
                        setNudge(!nudge);
                    }}
                />

                <Divider style={{ paddingBottom: 20, paddingTop: 20 }} />

                <Accordion
                    collapsible
                    openItems={openItems}
                    onToggle={(_, data) => {
                        setOpenItems(data.openItems);
                    }}
                >
                    <AccordionItem value="1">
                        <AccordionHeader>Quick start examples</AccordionHeader>
                        <AccordionPanel>
                            <div className="stack vstack-gap">
                                <MessageBar layout="multiline">
                                    <MessageBarBody className="stack vstack-gap">
                                        <MessageBarTitle>HelloWorld Example:</MessageBarTitle>
                                        <Text
                                            wrap
                                            style={{ wordWrap: "break-word", display: "block" }}
                                        >
                                            This will create a rule that responds to all HTTP(s) GET and POST requests
                                            sent to <strong>{zone}</strong> with <strong>"hello world"</strong>.
                                        </Text>
                                    </MessageBarBody>
                                    <MessageBarActions>
                                        <Button
                                            appearance="primary"
                                            onClick={() => {
                                                makeHelloWorldRule(zone)
                                                    .then((newRule) => {
                                                        setRuleId(newRule.ruleid);
                                                        setNudge(!nudge);
                                                    })
                                                    .catch((err) => Logger.Error(err))
                                                    .finally(() => {
                                                        setOpenItems([]);
                                                    });
                                            }}
                                        >
                                            Create "Hello World"
                                        </Button>
                                    </MessageBarActions>
                                </MessageBar>
                                <MessageBar layout="multiline">
                                    <MessageBarBody className="stack vstack-gap">
                                        <MessageBarTitle>DNS Example:</MessageBarTitle>
                                        <Text
                                            wrap
                                            style={{ wordWrap: "break-word", display: "block" }}
                                        >
                                            This will make 2 rules to make this DNS zone resolve to{" "}
                                            <strong>localhost</strong>. It will respond to both both{" "}
                                            <strong>127.0.0.1</strong> and <strong>::1</strong> for DNS A and AAAA
                                            requests send to <strong>{zone}</strong>.
                                        </Text>
                                    </MessageBarBody>
                                    <MessageBarActions>
                                        <Button
                                            appearance="primary"
                                            onClick={() => {
                                                makeLocalhostRule(zone)
                                                    .then((newRule) => {
                                                        setRuleId(newRule.ruleid);
                                                        setNudge(!nudge);
                                                    })
                                                    .catch((err) => Logger.Error(err))
                                                    .finally(() => {
                                                        setOpenItems([]);
                                                    });
                                            }}
                                        >
                                            Always respond with 127.0.0.1
                                        </Button>
                                    </MessageBarActions>
                                </MessageBar>
                                <Link onClick={() => navigate("/templates")}>More rule templates &raquo;</Link>
                            </div>
                        </AccordionPanel>
                    </AccordionItem>
                </Accordion>
            </div>

            <Divider
                vertical
                className={styles.divider}
            />

            <div className={styles.right}>
                <RuleDetails
                    rule={rule}
                    updateSelectedRule={(newRule: Rule | undefined) => {
                        // Update rule before nudge so that we don't lose selected rule
                        setRuleId(newRule?.ruleid);
                        setNudge(!nudge);
                    }}
                />
            </div>
        </div>
    );
};
