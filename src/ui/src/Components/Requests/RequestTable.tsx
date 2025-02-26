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
    Dropdown,
    Menu,
    MenuItem,
    MenuList,
    MenuPopover,
    MenuTrigger,
    Option,
    Select,
    TableCellLayout,
    TableColumnDefinition,
    TableRowId,
    Text,
    Tooltip
} from "@fluentui/react-components";
import { ChevronLeftRegular, ChevronRightRegular } from "@fluentui/react-icons";
import { useEffect, useRef, useState } from "react";

import { DssldrfRequest } from "../../Helpers/Types";
import { DusseldorfAPI } from "../../DusseldorfApi";
import { Logger } from "../../Helpers/Logger";

/**
 * A custom timestamp formatter
 */
const formatTimestamp = (timestamp: string | number): string => {
    // fix timestamp, if needed
    if (typeof timestamp === "string") { timestamp = parseInt(timestamp); }
    
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
 * Columns: protocol, client ip, timestamp, request, and response
 */
const columns: TableColumnDefinition<DssldrfRequest>[] = [
    createTableColumn<DssldrfRequest>({
        columnId: "protocol",
        renderHeaderCell: () => {
            return "Protocol";
        },
        renderCell: (request) => {
            return request.protocol.toLowerCase();
        }
    }),
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

const columnSizingOptions = {
    protocol: {
        minWidth: 30,
        idealWidth: 54
    },
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
    request: DssldrfRequest | undefined;
    setRequest: (request: DssldrfRequest | undefined) => void;
    nudge: boolean;
}

export const RequestTable = ({ zone, request, setRequest, nudge }: RequestTableProps) => {
    // Control what is shown: nothing, text that there is no reqeust, or requests
    const [loaded, setLoaded] = useState<boolean>(false);
    const [requests, setRequests] = useState<DssldrfRequest[]>([]);

    // Control what is selected - should always match request.id
    const [selectedRows, setSelectedRows] = useState(new Set<TableRowId>(request ? [JSON.stringify(request)] : []));
    const onSelectionChange: DataGridProps["onSelectionChange"] = (_, data) => {
        if (data.selectedItems.size > 0) {
            setSelectedRows(data.selectedItems);

            // could be undefined, check for that.
            const next_req:string  = data.selectedItems.values().next().value;

            if (next_req) {
                try {
                    setRequest(JSON.parse(next_req) as DssldrfRequest);
                } 
                catch (error) {
                    // swallowed since eslint was throwing
                    // issues
                }
            }
        }
    };

    // Control paging
    const [num, setNum] = useState<number>(20);
    const [protocols, setProtocols] = useState<string[]>(["dns", "http"]);
    const [skip, setSkip] = useState<number>(0);

    // refMap and Menu section of DataGrid used for accessibility reasons
    const refMap = useRef<Record<string, HTMLElement | null>>({});

    /**
     * Most of the time, we are setting request, so we do not want to refresh
     * requests and request every single time request changes. Instead, the
     * parent will change nudge when we should care about external changes to
     * the requests or request.
     */
    useEffect(() => {
        // Don't both contacting the API if nothing will match
        if (protocols.length == 0) {
            setProtocols(["http", "dns"]);
            return;
        }

        // Hide old requests
        setLoaded(false);
        // Refresh requests
        DusseldorfAPI.GetRequests(zone, num, skip * num, protocols.join(","))
            .then((newRequests) => {
                setRequests(newRequests);
            })
            .catch((err) => {
                Logger.Error(err);
                setRequests([]);
            })
            .finally(() => {
                // Show new requests
                setLoaded(true);
            });
    }, [zone, num, skip, protocols, nudge]);

    // While loading requests from the API, show nothing
    if (!loaded) {
        return <div />;
    }

    // If there are no requests, say that
    if (requests.length === 0) {
        return (
            <Text
                wrap
                style={{ wordWrap: "break-word" }}
            >
                No requests were found for <b>{zone}</b> When new network traffic is detected for <b>{zone}</b>, it will
                appear here.
            </Text>
        );
    }

    // If there are requests, show them
    return (
        <div>
            <DataGrid
                items={requests}
                columns={columns}
                selectionMode="single"
                selectedItems={selectedRows}
                onSelectionChange={onSelectionChange}
                sortable
                getRowId={(request) => JSON.stringify(request)}
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
                <DataGridBody<Request>>
                    {({ item, rowId }) => (
                        <DataGridRow<Request>
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
                <Dropdown
                    style={{ minWidth: "unset" }}
                    multiselect
                    value={protocols.join(", ")}
                    selectedOptions={protocols}
                    onOptionSelect={(_, data) => {
                        setProtocols(data.selectedOptions);
                    }}
                >
                    <Option key="dns">dns</Option>
                    <Option key="http">http</Option>
                </Dropdown>

                <Select
                    value={num}
                    onChange={(_, data) => {
                        setNum(parseInt(data.value));
                    }}
                >
                    <option>10</option>
                    <option>20</option>
                    <option>50</option>
                    <option>100</option>
                </Select>

                <Tooltip
                    content={`Previous ${num} requests`}
                    relationship="label"
                >
                    <Button
                        appearance="subtle"
                        disabled={skip < 1}
                        onClick={() => {
                            setSkip(skip - 1);
                        }}
                        icon={<ChevronLeftRegular />}
                    />
                </Tooltip>

                <Tooltip
                    content={`Next ${num} requests`}
                    relationship="label"
                >
                    <Button
                        appearance="subtle"
                        disabled={requests.length < num}
                        onClick={() => {
                            setSkip(skip + 1);
                        }}
                        icon={<ChevronRightRegular />}
                    />
                </Tooltip>
            </div>
        </div>
    );
};
