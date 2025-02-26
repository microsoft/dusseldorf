// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Button,
    createTableColumn,
    DataGrid,
    DataGridBody,
    DataGridCell,
    DataGridRow,
    Divider,
    MessageBar,
    Subtitle2,
    TableCellLayout,
    TableColumnDefinition,
    Text,
    Tooltip
} from "@fluentui/react-components";
import { DeleteRegular, EditRegular } from "@fluentui/react-icons";
import { useState, useEffect } from "react";

import { RuleComponentMenu } from "./RuleComponentMenu";
import { GenericRuleComponent } from "./RuleComponents/GenericRuleComponent";
import { ResultHeaderRuleComponentEdit } from "./RuleComponents/ResultHeaderRuleComponentEdit";
import { ResultHeaderRuleComponent } from "./RuleComponents/ResultHeaderRuleComponent";
import { DusseldorfAPI } from "../../DusseldorfApi";
import { Constants } from "../../Helpers/Constants";
import { Logger } from "../../Helpers/Logger";
import { DnsData } from "../../Types/DssldrfRequest";
import { RuleComponent } from "../../Types/RuleComponent";
import { Rule } from "../../Types/Rule";

export const predicateDictionary: Record<string, string> = {
    "dns.type": "Request type is",
    "http.body": "Body matches regex",
    "http.header": "Headers contain",
    "http.method": "Method is one of",
    "http.path": "Path matches regex"
};

export const resultDictionary: Record<string, string> = {
    "dns.data": "DNS response",
    "dns.type": "Set response type",
    "http.body": "Response body",
    "http.code": "Set HTTP code",
    "http.header": "Send HTTP header",
    "http.passthru": "Forward request to"
};

const actionValueToNiceString = (actionname: string, actionvalue: string) => {
    switch (actionname) {
        case "http.method":
            return actionvalue.toUpperCase().replaceAll(",", ", ");
        case "http.code": {
            const code: number = parseInt(actionvalue);
            const exp = Constants.HttpResultCodes.find((value) => value.key == code);
            return exp?.text ?? actionvalue;
        }
        case "http.body":
            return actionvalue.replaceAll("\n", "\\n");
        case "http.header": {
            const hdrs: string[] = actionvalue.split(":");
            const hdrName: string = hdrs.shift() ?? "";
            const rest: string = hdrs.join(":");
            return `${hdrName}: ${rest}`;
        }
        case "dns.data": {
            try {
                const dnsData = JSON.parse(actionvalue) as DnsData;
                return dnsData.ip ?? dnsData.cname ?? dnsData.mx ?? dnsData.ns ?? dnsData.txt ?? dnsData.data ?? "";
            } catch (error) {
                Logger.Warn(error as string);
                return actionvalue;
            }
        }
        default:
            return actionvalue;
    }
};

interface RuleComponentsProps {
    rule: Rule;
    updateSelectedRule: (rule: Rule | undefined) => void;
}

export const RuleComponents = ({ rule, updateSelectedRule }: RuleComponentsProps) => {
    const [ruleComponents, setRuleComponents] = useState<RuleComponent[]>(rule.rulecomponents);
    const [editComponentId, setEditComponentId] = useState<string | null>(null);
    const [predicateToCreate, setPredicateToCreate] = useState<string | null>(null);
    const [resultToCreate, setResultToCreate] = useState<string | null>(null);

    // reset showAddFilter and showAddResult when the rule changes
    useEffect(() => {
        setEditComponentId(null);
        setPredicateToCreate(null);
        setResultToCreate(null);
        setRuleComponents(rule.rulecomponents);
    }, [rule]);

    const columns: TableColumnDefinition<RuleComponent>[] = [
        createTableColumn<RuleComponent>({
            columnId: "name",
            renderCell: (component) => {
                let name = "";
                if (component.ispredicate) {
                    name = predicateDictionary[component.actionname] ?? component.actionname;
                } else {
                    name = resultDictionary[component.actionname] ?? component.actionname;
                }
                return name;
            }
        }),
        createTableColumn<RuleComponent>({
            columnId: "value",
            renderCell: (component) => {
                if (component.componentid === editComponentId) {
                    // response header is more complicated
                    if (!component.ispredicate && component.actionname == "http.header") {
                        return (
                            <ResultHeaderRuleComponentEdit
                                oldValue={component.actionvalue}
                                onDismiss={() => {
                                    setEditComponentId(null);
                                }}
                                onSave={(newValue) => {
                                    DusseldorfAPI.EditRuleComponent(rule, component, newValue)
                                        .then(() => {
                                            component.actionvalue = newValue;
                                            setRuleComponents([...ruleComponents]);
                                            updateSelectedRule(rule);
                                        })
                                        .catch((err) => {
                                            // don't nudge here, because that would remove the update that the user is doing
                                            Logger.Error(err);
                                        });
                                    setEditComponentId(null);
                                }}
                            />
                        );
                    }
                    return (
                        <GenericRuleComponent
                            isPredicate={component.ispredicate}
                            actionName={component.actionname}
                            onDismiss={() => {
                                setEditComponentId(null);
                            }}
                            onSave={(newValue) => {
                                DusseldorfAPI.EditRuleComponent(rule, component, newValue)
                                    .then(() => {
                                        component.actionvalue = newValue;
                                        setRuleComponents([...ruleComponents]);
                                        updateSelectedRule(rule);
                                    })
                                    .catch((err) => {
                                        // don't nudge here, because that would remove the update that the user is doing
                                        Logger.Error(err);
                                    });
                                setEditComponentId(null);
                            }}
                            oldValue={component.actionvalue}
                        />
                    );
                } else {
                    return (
                        <Text
                            truncate
                            style={{ display: "block", wordWrap: "break-word" }}
                        >
                            {actionValueToNiceString(component.actionname, component.actionvalue)}
                        </Text>
                    );
                }
            }
        }),
        createTableColumn<RuleComponent>({
            columnId: "edit",
            renderCell: (component) => {
                return (
                    <Tooltip
                        content="Edit"
                        relationship="label"
                    >
                        <Button
                            appearance="subtle"
                            icon={<EditRegular />}
                            disabled={editComponentId !== null}
                            onClick={() => {
                                setEditComponentId(component.componentid);
                            }}
                        />
                    </Tooltip>
                );
            }
        }),
        createTableColumn<RuleComponent>({
            columnId: "delete",
            renderCell: (component) => {
                return (
                    <Tooltip
                        content="Delete"
                        relationship="label"
                    >
                        <Button
                            appearance="subtle"
                            icon={<DeleteRegular />}
                            onClick={() => {
                                const savedId = component.componentid;
                                // delete the component and refresh
                                DusseldorfAPI.DeleteRuleComponent(rule, component)
                                    .then(() => {
                                        Logger.Info(
                                            `Deleted component: ${rule.zone}/${rule.ruleid}/${component.componentid}`
                                        );
                                        updateSelectedRule(rule);
                                    })
                                    .catch((err) => {
                                        Logger.Error(err);
                                    })
                                    .finally(() => {
                                        // update rule components
                                        DusseldorfAPI.GetRuleDetails(rule.zone, rule.ruleid)
                                            .then((updatedRule) => {
                                                setRuleComponents(updatedRule.rulecomponents);
                                            })
                                            .catch((err) => {
                                                Logger.Error(err);
                                                setRuleComponents([]);
                                            });
                                        if (savedId === editComponentId) {
                                            setEditComponentId(null);
                                        }
                                    });
                            }}
                        />
                    </Tooltip>
                );
            }
        })
    ];

    const columnSizingOptions = {
        name: {
            minWidth: 90,
            idealWidth: 130
        },
        value: {
            minWidth: 250,
            idealWidth: 420
        },
        edit: {
            minWidth: 30,
            defaultWidth: 30,
            idealWidth: 30
        },
        delete: {
            minWidth: 30,
            defaultWidth: 30,
            idealWidth: 30
        }
    };

    return (
        <div className="stack vstack-gaplarge">
            <Text>
                A rule has one or more components which are either a <strong>Filter</strong> or an{" "}
                <strong>Action</strong>. Use the controls below to add new components:
            </Text>

            <div className="stack hstack-spread">
                <Subtitle2>When this happens:</Subtitle2>
                <RuleComponentMenu
                    isDisabled={predicateToCreate !== null}
                    isHttp={rule.networkprotocol === "http"}
                    isPredicate={true}
                    onCreate={setPredicateToCreate}
                    ruleComponents={ruleComponents}
                />
            </div>

            <div
                className="stack vstack-gap"
                style={{ paddingLeft: 10 }}
            >
                {predicateToCreate && (
                    <GenericRuleComponent
                        isPredicate={true}
                        actionName={predicateToCreate}
                        onDismiss={() => {
                            setPredicateToCreate(null);
                        }}
                        onSave={(newValue) => {
                            DusseldorfAPI.AddRuleComponent(rule, {
                                actionname: predicateToCreate,
                                actionvalue: newValue,
                                ispredicate: true
                            })
                                .then((newComponent) => {
                                    setRuleComponents(ruleComponents.concat(newComponent));
                                    updateSelectedRule(rule);
                                })
                                .catch((err) => {
                                    Logger.Error(err);
                                })
                                .finally(() => {
                                    setPredicateToCreate(null);
                                });
                        }}
                    />
                )}

                <DataGrid
                    items={ruleComponents
                        .filter((c) => c.ispredicate)
                        .sort((a, b) => a.actionname.localeCompare(b.actionname))}
                    columns={columns}
                    resizableColumns
                    columnSizingOptions={columnSizingOptions}
                >
                    <DataGridBody<RuleComponent>>
                        {({ item }) => (
                            <DataGridRow<RuleComponent> style={{ borderWidth: 0 }}>
                                {({ renderCell }) => (
                                    <DataGridCell>
                                        <TableCellLayout truncate>{renderCell(item)}</TableCellLayout>
                                    </DataGridCell>
                                )}
                            </DataGridRow>
                        )}
                    </DataGridBody>
                </DataGrid>

                {ruleComponents.filter((c) => c.ispredicate).length === 0 && (
                    <>
                        <MessageBar intent="warning">
                            <Text wrap>
                                You have no filter(s) set, this rule will not trigger. Use the <b>Add Filter</b> menu
                                above to add one.
                            </Text>
                        </MessageBar>
                        <Divider style={{ paddingTop: 20, paddingBottom: 20 }} />
                    </>
                )}
            </div>

            <div className="stack hstack-spread">
                <Subtitle2>Then do this:</Subtitle2>
                <RuleComponentMenu
                    isDisabled={resultToCreate !== null}
                    isPredicate={false}
                    isHttp={rule.networkprotocol === "http"}
                    ruleComponents={ruleComponents}
                    onCreate={setResultToCreate}
                />
            </div>

            <div
                className="stack vstack-gap"
                style={{ paddingLeft: "10px" }}
            >
                {resultToCreate && resultToCreate == "http.header" && (
                    <ResultHeaderRuleComponent
                        onDismiss={() => {
                            setResultToCreate(null);
                        }}
                        onSave={(newValue) => {
                            DusseldorfAPI.AddRuleComponent(rule, {
                                actionname: resultToCreate,
                                actionvalue: newValue,
                                ispredicate: false
                            })
                                .then((newComponent) => {
                                    setRuleComponents([...ruleComponents, newComponent]);
                                    updateSelectedRule(rule);
                                })
                                .catch((err) => {
                                    Logger.Error(err);
                                    setRuleComponents([...ruleComponents]);
                                })
                                .finally(() => {
                                    setResultToCreate(null);
                                });
                        }}
                    />
                )}

                {resultToCreate && resultToCreate != "http.header" && (
                    <GenericRuleComponent
                        isPredicate={false}
                        actionName={resultToCreate}
                        onDismiss={() => {
                            setResultToCreate(null);
                        }}
                        onSave={(newValue) => {
                            DusseldorfAPI.AddRuleComponent(rule, {
                                actionname: resultToCreate,
                                actionvalue: newValue,
                                ispredicate: false
                            })
                                .then((newComponent) => {
                                    setRuleComponents([...ruleComponents, newComponent]);
                                    updateSelectedRule(rule);
                                })
                                .catch((err) => {
                                    Logger.Error(err);
                                    setRuleComponents([...ruleComponents]);
                                })
                                .finally(() => {
                                    setResultToCreate(null);
                                });
                        }}
                    />
                )}

                <DataGrid
                    items={
                        ruleComponents.filter((c) => !c.ispredicate)
                        // .sort((a, b) => a.actionname.localeCompare(b.actionname))
                    }
                    columns={columns}
                    resizableColumns
                    columnSizingOptions={columnSizingOptions}
                >
                    <DataGridBody<RuleComponent>>
                        {({ item }) => (
                            <DataGridRow<RuleComponent> style={{ borderWidth: 0 }}>
                                {({ renderCell }) => (
                                    <DataGridCell>
                                        <TableCellLayout truncate>{renderCell(item)}</TableCellLayout>
                                    </DataGridCell>
                                )}
                            </DataGridRow>
                        )}
                    </DataGridBody>
                </DataGrid>

                {ruleComponents.filter((c) => !c.ispredicate).length === 0 && (
                    <MessageBar intent="warning">
                        <Text wrap>
                            You have no actions set, this rule will do nothing and just give the default response. Use
                            the <b>Add Result</b> menu above to add one.
                        </Text>
                    </MessageBar>
                )}
            </div>
        </div>
    );
};
