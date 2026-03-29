// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, makeStyles, Subtitle1, Tab, TabList, Tooltip } from "@fluentui/react-components";
import { ArrowSyncRegular } from "@fluentui/react-icons";
import { useEffect, useRef, useState } from "react";

import { ColumnManager, ColumnConfig } from "../Components/ColumnManager";
import { RequestDetails } from "../Components/Requests/RequestDetails";
import { RequestTable } from "../Components/Requests/RequestTable";
import { ResizableSplitPanel } from "../Components/ResizableSplitPanel";
import { DusseldorfAPI } from "../DusseldorfApi";
import { Logger } from "../Helpers/Logger";
import { DssldrfRequest } from "../Types/DssldrfRequest";

const useStyles = makeStyles({
    header: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "10px"
    },
    headerLeft: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        gap: "8px"
    },
    headerRight: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        gap: "4px"
    }
});

/**
 * Default column configuration
 */
const defaultColumnConfig: ColumnConfig[] = [
    { id: "clientip", label: "Client IP", visible: true },
    { id: "timestamp", label: "Timestamp", visible: true, required: true },
    { id: "request", label: "Request", visible: true, required: true },
    { id: "response", label: "Response", visible: true }
];

type Protocol = "dns" | "http";

/** How many requests to preload per tab on initial load */
const PRELOAD_LIMIT = 100;

/** How many new requests to fetch per poll */
const POLL_LIMIT = 50;

/** Polling interval in milliseconds */
const POLL_INTERVAL_MS = 3000;

interface IRequestsScreenProps {
    zone: string;
}

export const RequestsScreen = ({ zone }: IRequestsScreenProps) => {
    const styles = useStyles();

    // Selected request shown in detail panel
    const [request, setRequest] = useState<DssldrfRequest | undefined>();

    // Column visibility configuration
    const [columnConfig, setColumnConfig] = useState<ColumnConfig[]>(defaultColumnConfig);

    // Active protocol tab
    const [activeTab, setActiveTab] = useState<Protocol>("dns");
    const activeTabRef = useRef<Protocol>("dns");

    // Per-protocol request lists and loaded flags
    const [dnsRequests, setDnsRequests] = useState<DssldrfRequest[]>([]);
    const [httpRequests, setHttpRequests] = useState<DssldrfRequest[]>([]);
    const [dnsLoaded, setDnsLoaded] = useState<boolean>(false);
    const [httpLoaded, setHttpLoaded] = useState<boolean>(false);

    // Unread indicators (bold tab label when new requests arrive on inactive tab)
    const [dnsUnread, setDnsUnread] = useState<boolean>(false);
    const [httpUnread, setHttpUnread] = useState<boolean>(false);

    // Latest timestamp per protocol, stored in refs so the polling interval
    // always reads the current value without needing to restart.
    // 0 = initial load not yet complete; skip polling until set.
    const dnsLastTimestamp = useRef<number>(0);
    const httpLastTimestamp = useRef<number>(0);

    // Increment to trigger a forced full reload
    const [refreshKey, setRefreshKey] = useState<number>(0);

    // ── Reset on zone change ──────────────────────────────────────────────
    useEffect(() => {
        setRequest(undefined);
        setActiveTab("dns");
        activeTabRef.current = "dns";
        setDnsRequests([]);
        setHttpRequests([]);
        setDnsLoaded(false);
        setHttpLoaded(false);
        setDnsUnread(false);
        setHttpUnread(false);
        dnsLastTimestamp.current = 0;
        httpLastTimestamp.current = 0;
    }, [zone]);

    // ── Initial / forced preload — both tabs in parallel ─────────────────
    useEffect(() => {
        setDnsLoaded(false);
        setHttpLoaded(false);

        DusseldorfAPI.GetRequests(zone, PRELOAD_LIMIT, 0, "dns")
            .then((reqs) => {
                setDnsRequests(reqs);
                dnsLastTimestamp.current =
                    reqs.length > 0
                        ? parseInt(String(reqs[0].time))
                        : Math.floor(Date.now() / 1000);
            })
            .catch((err) => {
                Logger.Error(err);
                setDnsRequests([]);
                dnsLastTimestamp.current = Math.floor(Date.now() / 1000);
            })
            .finally(() => setDnsLoaded(true));

        DusseldorfAPI.GetRequests(zone, PRELOAD_LIMIT, 0, "http")
            .then((reqs) => {
                setHttpRequests(reqs);
                httpLastTimestamp.current =
                    reqs.length > 0
                        ? parseInt(String(reqs[0].time))
                        : Math.floor(Date.now() / 1000);
            })
            .catch((err) => {
                Logger.Error(err);
                setHttpRequests([]);
                httpLastTimestamp.current = Math.floor(Date.now() / 1000);
            })
            .finally(() => setHttpLoaded(true));
    }, [zone, refreshKey]);

    // ── Polling — every POLL_INTERVAL_MS, fetch new requests per protocol ─
    // Uses refs for timestamps and activeTab so the interval never needs to
    // restart except on zone change.
    useEffect(() => {
        const interval = setInterval(() => {
            const dnsSince = dnsLastTimestamp.current;
            if (dnsSince > 0) {
                DusseldorfAPI.GetRequests(zone, POLL_LIMIT, 0, "dns", dnsSince)
                    .then((newReqs) => {
                        if (newReqs.length > 0) {
                            dnsLastTimestamp.current = parseInt(String(newReqs[0].time));
                            setDnsRequests((prev) => [...newReqs, ...prev]);
                            if (activeTabRef.current !== "dns") {
                                setDnsUnread(true);
                            }
                        }
                    })
                    .catch(() => { /* silently ignore poll errors */ });
            }

            const httpSince = httpLastTimestamp.current;
            if (httpSince > 0) {
                DusseldorfAPI.GetRequests(zone, POLL_LIMIT, 0, "http", httpSince)
                    .then((newReqs) => {
                        if (newReqs.length > 0) {
                            httpLastTimestamp.current = parseInt(String(newReqs[0].time));
                            setHttpRequests((prev) => [...newReqs, ...prev]);
                            if (activeTabRef.current !== "http") {
                                setHttpUnread(true);
                            }
                        }
                    })
                    .catch(() => { /* silently ignore poll errors */ });
            }
        }, POLL_INTERVAL_MS);

        return () => clearInterval(interval);
    }, [zone]);

    // ── Tab switch handler ────────────────────────────────────────────────
    const handleTabSelect = (tab: Protocol) => {
        setActiveTab(tab);
        activeTabRef.current = tab;
        if (tab === "dns") setDnsUnread(false);
        if (tab === "http") setHttpUnread(false);
        // Reset selected request when switching protocols
        setRequest(undefined);
    };

    return (
        <ResizableSplitPanel
            leftPanel={
                <div>
                    <div className={styles.header}>
                        <div className={styles.headerLeft}>
                            <Subtitle1>Network Requests</Subtitle1>
                        </div>

                        <div className={styles.headerRight}>
                            <ColumnManager
                                columns={columnConfig}
                                onColumnsChange={setColumnConfig}
                            />

                            <Tooltip
                                content="Refresh"
                                relationship="label"
                            >
                                <Button
                                    appearance="subtle"
                                    icon={<ArrowSyncRegular />}
                                    onClick={() => setRefreshKey((k) => k + 1)}
                                />
                            </Tooltip>
                        </div>
                    </div>

                    <TabList
                        selectedValue={activeTab}
                        onTabSelect={(_, data) => handleTabSelect(data.value as Protocol)}
                    >
                        <Tab value="dns">
                            <span style={{ fontWeight: dnsUnread ? 700 : 400 }}>DNS</span>
                        </Tab>
                        <Tab value="http">
                            <span style={{ fontWeight: httpUnread ? 700 : 400 }}>HTTP</span>
                        </Tab>
                    </TabList>

                    <RequestTable
                        key={`${zone}-${activeTab}`}
                        zone={zone}
                        requests={activeTab === "dns" ? dnsRequests : httpRequests}
                        loaded={activeTab === "dns" ? dnsLoaded : httpLoaded}
                        request={request}
                        setRequest={setRequest}
                        columnConfig={columnConfig}
                    />
                </div>
            }
            rightPanel={
                <RequestDetails
                    zone={zone}
                    request={request}
                />
            }
            initialLeftWidth={48}
            minLeftWidth={25}
            maxLeftWidth={75}
        />
    );
};
