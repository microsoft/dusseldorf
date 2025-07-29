// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Body1Strong,
    createTableColumn,
    DataGrid,
    DataGridBody,
    DataGridCell,
    DataGridHeader,
    DataGridHeaderCell,
    DataGridProps,
    DataGridRow,
    Menu,
    MenuItem,
    MenuList,
    MenuPopover,
    MenuTrigger,
    MessageBar,
    TableCellLayout,
    TableColumnDefinition,
    TableRowId,
    Text
} from "@fluentui/react-components";
import { useEffect, useRef, useState } from "react";

import { ColumnManager, ColumnConfig } from "../ColumnManager";
import { DusseldorfAPI } from "../../DusseldorfApi";
import { Logger } from "../../Helpers/Logger";
import { Rule } from "../../Types/Rule";

const columns: TableColumnDefinition<Rule>[] = [
    createTableColumn<Rule>({
        columnId: "priority",
        compare: (ruleA, ruleB) => {
            return ruleA.priority - ruleB.priority;
        },
        renderHeaderCell: () => {
            return "Priority";
        },
        renderCell: (rule) => {
            return rule.priority;
        }
    }),
    createTableColumn<Rule>({
        columnId: "name",
        // compare: (ruleA, ruleB) => {
        //     return ruleA.name.localeCompare(ruleB.name);
        // },
        renderHeaderCell: () => {
            return "Name";
        },
        renderCell: (rule) => {
            return rule.name;
        }
    }),
    createTableColumn<Rule>({
        columnId: "protocol",
        // compare: (ruleA, ruleB) => {
        //     return ruleA.protocol.localeCompare(ruleB.protocol);
        // },
        renderHeaderCell: () => {
            return "Protocol";
        },

        renderCell: (rule) => {
            return rule.networkprotocol;
        }
    }),
    createTableColumn<Rule>({
        columnId: "components",
        compare: (ruleA, ruleB) => {
            return ruleA.rulecomponents.length - ruleB.rulecomponents.length;
        },
        renderHeaderCell: () => {
            return "Components";
        },
        renderCell: (rule) => {
            return rule.rulecomponents.length.toString();
        }
    })
];

const columnSizingOptions = {
    priority: {
        minWidth: 30,
        defaultWidth: 47
    },
    name: {
        minWidth: 30,
        defaultWidth: 160
    },
    protocol: {
        minWidth: 30,
        defaultWidth: 54
    },
    components: {
        minWidth: 30,
        defaultWidth: 60
    }
};

interface RuleTableProps {
    zone: string;
    ruleId: string | undefined;
    setRuleId: (ruleId: string | undefined) => void;
    rule: Rule | undefined;
    setRule: (rule: Rule | undefined) => void;
    nudge: boolean;
}

export const RuleTable = ({ zone, ruleId, setRuleId, rule, setRule, nudge }: RuleTableProps) => {
    // Control what is shown: nothing, helpful rule creation text, or rules
    const [loaded, setLoaded] = useState<boolean>(false);
    const [rules, setRules] = useState<Rule[]>([]);

    // Control what is selected - should always match rule.ruleid
    const [selectedRows, setSelectedRows] = useState(new Set<TableRowId>(ruleId ? [ruleId] : []));
    const onSelectionChange: DataGridProps["onSelectionChange"] = (_, data) => {
        const newRuleId = data.selectedItems.values().next().value as string;
        if (!rule || newRuleId != rule.ruleid) {
            setSelectedRows(data.selectedItems);
            setRuleId(newRuleId);
            setRule(rules.find((r) => r.ruleid == newRuleId));
        }
    };

    // refMap and Menu section of DataGrid used for accessibility reasons
    const refMap = useRef<Record<string, HTMLElement | null>>({});

    /**
     * Don't show the old rules while loading rules for a new zone.
     */
    useEffect(() => {
        setLoaded(false);
        // Refresh rules
        DusseldorfAPI.GetRules(zone)
            .then((newRules) => {
                setRules(newRules);
                setSelectedRows(new Set<TableRowId>([]));
            })
            .catch((err) => {
                Logger.Error(err);
                setRules([]);
                setSelectedRows(new Set<TableRowId>([]));
            })
            .finally(() => {
                setLoaded(true);
            });
    }, [zone]);

    /**
     * Most of the time, we are setting rule and ruleId, so we do not want to
     * refresh every single time ruleId changes. Instead, the parent will change
     * nudge when we should care about external changes to the rules or ruleId.
     *
     * Show the old rules while updating requests for the current zone.
     */
    useEffect(() => {
        // Refresh rules
        DusseldorfAPI.GetRules(zone)
            .then((newRules) => {
                setRules(newRules);
                // Refresh selection and possibly rule
                if (ruleId) {
                    setSelectedRows(new Set<TableRowId>([ruleId]));
                    if (rule?.ruleid != ruleId) {
                        setRule(newRules.find((r) => r.ruleid == ruleId));
                    }
                } else {
                    setSelectedRows(new Set<TableRowId>([]));
                    setRule(undefined);
                }
            })
            .catch((err) => {
                Logger.Error(err);
                setRules([]);
                setSelectedRows(new Set<TableRowId>([]));
                setRule(undefined);
            });
    }, [nudge]);

    // While loading rules from the API, show nothing
    if (!loaded && rules.length === 0) {
        return <div />;
    }

    // If there are no rules, show helpful text to make some
    if (rules.length === 0) {
        return (
            <div className="stack vstack-gap">
                <MessageBar intent="info">
                    <Text wrap>
                        <strong>Info:</strong> No rules are setup for this zone yet.
                    </Text>
                </MessageBar>

                <Text
                    wrap
                    style={{ wordWrap: "break-word" }}
                >
                    Create a new rule to capture network requests sent to <strong>{zone}</strong>. Use rules to provide
                    automated responses to particular network request, based on your filters.
                </Text>

                <Text wrap>
                    Each rule has a certain numeric <strong>priority</strong> which defines the order all rules are
                    executed for this zone/protocol combination.
                </Text>
            </div>
        );
    }

    // If there are rules, show them
    return (
        <DataGrid
            items={rules}
            columns={columns}
            selectionMode="single"
            selectedItems={selectedRows}
            onSelectionChange={onSelectionChange}
            sortable
            getRowId={(rule: Rule) => rule.ruleid}
            resizableColumns
            columnSizingOptions={columnSizingOptions}
            subtleSelection
        >
            <DataGridHeader>
                <DataGridRow selectionCell={null}>
                    {({ renderHeaderCell, columnId }, dataGrid) => (
                        <Menu openOnContext>
                            <MenuTrigger>
                                <DataGridHeaderCell ref={(el) => (refMap.current[columnId] = el)}>
                                    <TableCellLayout truncate>
                                        <Body1Strong>{renderHeaderCell()}</Body1Strong>
                                    </TableCellLayout>
                                </DataGridHeaderCell>
                            </MenuTrigger>
                            <MenuPopover>
                                <MenuList>
                                    <MenuItem onClick={dataGrid.columnSizing_unstable.enableKeyboardMode(columnId)}>
                                        Keyboard Column Resizing
                                    </MenuItem>
                                </MenuList>
                            </MenuPopover>
                        </Menu>
                    )}
                </DataGridRow>
            </DataGridHeader>
            <DataGridBody<Rule>>
                {({ item, rowId }) => (
                    <DataGridRow<Rule>
                        key={rowId}
                        selectionCell={null}
                    >
                        {({ renderCell }) => (
                            <DataGridCell>
                                <TableCellLayout truncate>{renderCell(item)}</TableCellLayout>
                            </DataGridCell>
                        )}
                    </DataGridRow>
                )}
            </DataGridBody>
        </DataGrid>
    );
};
