// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Body1Strong,
    Button,
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
    Select,
    TableCellLayout,
    TableColumnDefinition,
    TableRowId,
    Text,
    Tooltip
} from "@fluentui/react-components";
import { ChevronLeftRegular, ChevronRightRegular } from "@fluentui/react-icons";
import { useEffect, useRef, useState } from "react";

import { ColumnConfig } from "../ColumnManager";
import { DssldrfRequest } from "../../Types/DssldrfRequest";

/**
 * A custom timestamp formatter
 */
const formatTimestamp = (timestamp: string | number): string => {
    // fix timestamp, if needed
    if (typeof timestamp === "string") {
        timestamp = parseInt(timestamp);
    }

    const now = new Date();
    const requestTime = new Date(timestamp * 1000); // requestTime is in seconds
    const diffInSeconds = Math.floor((now.getTime() - requestTime.getTime()) / 1000);

    if (diffInSeconds === 1) {
        return /* literally */ "A second ago";
    } else if (diffInSeconds < 30) {
        return `${diffInSeconds} seconds ago`;
    } else if (diffInSeconds < 60) {
        return `${requestTime.toLocaleTimeString()} (${diffInSeconds}s ago)`;
    } else if (now.toDateString() === requestTime.toDateString()) {
        return requestTime.toLocaleTimeString();
    } else {
        return requestTime.toLocaleString("en-US", {
            month: "short",
            day: "numeric",
            hour: "numeric",
            minute: "numeric"
        });
    }
};

/**
 * All available columns for the requests table
 */
const allColumns: TableColumnDefinition<DssldrfRequest>[] = [
    createTableColumn<DssldrfRequest>({
        columnId: "clientip",
        renderHeaderCell: () => {
            return "Client IP";
        },
        renderCell: (request) => {
            return request.clientip;
        }
    }),
    createTableColumn<DssldrfRequest>({
        columnId: "timestamp",
        renderHeaderCell: () => {
            return "Timestamp";
        },
        renderCell: (request) => {
            return formatTimestamp(request.time);
        }
    }),
    createTableColumn<DssldrfRequest>({
        columnId: "request",
        renderHeaderCell: () => {
            return "Request";
        },
        renderCell: (request) => {
            return request.reqsummary;
        }
    }),
    createTableColumn<DssldrfRequest>({
        columnId: "response",
        renderHeaderCell: () => {
            return "Response";
        },
        renderCell: (request) => {
            return request.respsummary;
        }
    })
];

// Removed unused `defaultColumnConfig` constant.

const columnSizingOptions = {
    clientip: {
        minWidth: 30,
        idealWidth: 100
    },
    timestamp: {
        minWidth: 30,
        idealWidth: 100
    },
    request: {
        minWidth: 30,
        idealWidth: 100
    },
    response: {
        minWidth: 30,
        idealWidth: 100
    }
};

interface RequestTableProps {
    zone: string;
    requests: DssldrfRequest[];
    loaded: boolean;
    hasMoreOlder: boolean;
    loadingOlder: boolean;
    onLoadOlderPage: (pageSize: number) => Promise<boolean>;
    request: DssldrfRequest | undefined;
    setRequest: (request: DssldrfRequest | undefined) => void;
    columnConfig: ColumnConfig[];
}

export const RequestTable = ({
    zone,
    requests,
    loaded,
    hasMoreOlder,
    loadingOlder,
    onLoadOlderPage,
    request,
    setRequest,
    columnConfig
}: RequestTableProps) => {
    // Column management — derived from prop
    const [visibleColumns, setVisibleColumns] = useState<TableColumnDefinition<DssldrfRequest>[]>([]);

    useEffect(() => {
        const visible = allColumns.filter(col =>
            columnConfig.find(config => config.id === col.columnId && config.visible)
        );
        setVisibleColumns(visible);
    }, [columnConfig]);

    // Client-side pagination
    const [num, setNum] = useState<number>(20);
    const [page, setPage] = useState<number>(0);
    const lastPage = Math.max(0, Math.ceil(requests.length / num) - 1);
    const pendingNavigation = useRef<"next" | null>(null);

    const pagedRequests = requests.slice(page * num, (page + 1) * num);

    useEffect(() => {
        setPage((currentPage) => Math.min(currentPage, lastPage));
    }, [lastPage]);

    useEffect(() => {
        if (pendingNavigation.current === "next") {
            setPage((currentPage) => Math.min(currentPage + 1, lastPage));
            pendingNavigation.current = null;
        }
    }, [lastPage, requests.length]);

    // Selection — keyed to JSON representation for DataGrid compatibility
    const [selectedRows, setSelectedRows] = useState(new Set<TableRowId>(request ? [JSON.stringify(request)] : []));

    useEffect(() => {
        if (request) {
            setSelectedRows(new Set<TableRowId>([JSON.stringify(request)]));
        } else {
            setSelectedRows(new Set<TableRowId>());
        }
    }, [request]);
    const onSelectionChange: DataGridProps["onSelectionChange"] = (_, data) => {
        if (data.selectedItems.size > 0) {
            setSelectedRows(data.selectedItems);
            const next_req = data.selectedItems.values().next().value;
            if (next_req) {
                try {
                    setRequest(JSON.parse(next_req as string) as DssldrfRequest);
                } catch {
                    // swallowed
                }
            }
        }
    };

    // refMap used for keyboard column resizing accessibility
    const refMap = useRef<Record<string, HTMLElement | null>>({});

    // While data is loading, show that it's loading instead of an empty table
    if (!loaded) {
        return <div>Loading...</div>;
    }

    // No requests for this zone/protocol
    if (requests.length === 0) {
        return (
            <Text
                wrap
                style={{ wordWrap: "break-word" }}
            >
                &nbsp;<br/>
                No requests were found for <b>{zone}</b>. When network traffic is detected, it appears here.
            </Text>
        );
    }

    return (
        <div>
            <DataGrid
                items={pagedRequests}
                columns={visibleColumns}
                selectionMode="single"
                selectedItems={selectedRows}
                onSelectionChange={onSelectionChange}
                sortable
                getRowId={(req) => JSON.stringify(req)}
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
                <DataGridBody<DssldrfRequest>>
                    {({ item, rowId }) => (
                        <DataGridRow<DssldrfRequest>
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

            <div
                className="stack hstack-gap"
                style={{ paddingTop: 20 }}
            >
                <Select
                    value={num}
                    onChange={(_, data) => {
                        setNum(parseInt(data.value));
                        setPage(0);
                    }}
                >
                    <option>10</option>
                    <option>20</option>
                    <option>50</option>
                    <option>100</option>
                </Select>

                <Tooltip
                    content="Jump to most recent requests"
                    relationship="label"
                >
                    <Button
                        appearance="subtle"
                        disabled={page === 0}
                        onClick={() => setPage(0)}
                    >
                        |&lt;
                    </Button>
                </Tooltip>

                <Tooltip
                    content={`Previous ${num} requests`}
                    relationship="label"
                >
                    <Button
                        appearance="subtle"
                        disabled={page < 1}
                        onClick={() => setPage(page - 1)}
                        icon={<ChevronLeftRegular />}
                    />
                </Tooltip>

                <Tooltip
                    content={`Next ${num} requests`}
                    relationship="label"
                >
                    <Button
                        appearance="subtle"
                        disabled={loadingOlder || (!hasMoreOlder && page >= lastPage)}
                        onClick={async () => {
                            if (page < lastPage) {
                                setPage(page + 1);
                                return;
                            }

                            pendingNavigation.current = "next";
                            const loadedOlder = await onLoadOlderPage(num);
                            if (!loadedOlder) {
                                pendingNavigation.current = null;
                            }
                        }}
                        icon={<ChevronRightRegular />}
                    />
                </Tooltip>
            </div>
        </div>
    );
};
