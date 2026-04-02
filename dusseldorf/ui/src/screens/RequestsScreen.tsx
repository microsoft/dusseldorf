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

const REQUESTS_PROTOCOL_STORAGE_KEY = "requests.activeProtocol";

const getStoredProtocolPreference = (): Protocol => {
    if (typeof window === "undefined") {
        return "dns";
    }

    const storedProtocol = window.localStorage.getItem(REQUESTS_PROTOCOL_STORAGE_KEY);
    return storedProtocol === "http" ? "http" : "dns";
};

const getRequestKey = (request: DssldrfRequest): string => {
    return `${request.id}:${request.time}`;
};

/** How many requests to preload per tab on initial load */
const PRELOAD_LIMIT = 100;

/** How many requests to fetch when paging backward into older traffic */
const OLDER_FETCH_LIMIT = 100;

/** How many new requests to fetch per poll */
const POLL_LIMIT = 50;

/** Polling interval in milliseconds */
const POLL_INTERVAL_MS = 3000;

interface IRequestsScreenProps {
    zone: string;
}

export const RequestsScreen = ({ zone }: IRequestsScreenProps) => {
    const styles = useStyles();
    const initialProtocol = getStoredProtocolPreference();

    // Selected request shown in detail panel
    const [request, setRequest] = useState<DssldrfRequest | undefined>();

    // Column visibility configuration
    const [columnConfig, setColumnConfig] = useState<ColumnConfig[]>(defaultColumnConfig);

    // Active protocol tab
    const [activeTab, setActiveTab] = useState<Protocol>(initialProtocol);
    const activeTabRef = useRef<Protocol>(initialProtocol);

    // Per-protocol request lists and loaded flags
    const [dnsRequests, setDnsRequests] = useState<DssldrfRequest[]>([]);
    const [httpRequests, setHttpRequests] = useState<DssldrfRequest[]>([]);
    const [dnsLoaded, setDnsLoaded] = useState<boolean>(false);
    const [httpLoaded, setHttpLoaded] = useState<boolean>(false);
    const [dnsHasMoreOlder, setDnsHasMoreOlder] = useState<boolean>(true);
    const [httpHasMoreOlder, setHttpHasMoreOlder] = useState<boolean>(true);
    const [dnsLoadingOlder, setDnsLoadingOlder] = useState<boolean>(false);
    const [httpLoadingOlder, setHttpLoadingOlder] = useState<boolean>(false);

    // Unread indicators (bold tab label when new requests arrive on inactive tab)
    const [dnsUnread, setDnsUnread] = useState<boolean>(false);
    const [httpUnread, setHttpUnread] = useState<boolean>(false);

    // Latest timestamp per protocol, stored in refs so the polling interval
    // always reads the current value without needing to restart.
    // 0 = initial load not yet complete; skip polling until set.
    const dnsLastTimestamp = useRef<number>(0);
    const httpLastTimestamp = useRef<number>(0);
    const dnsRequestsRef = useRef<DssldrfRequest[]>([]);
    const httpRequestsRef = useRef<DssldrfRequest[]>([]);

    // Increment to trigger a forced full reload
    const [refreshKey, setRefreshKey] = useState<number>(0);

    useEffect(() => {
        activeTabRef.current = activeTab;
        if (typeof window !== "undefined" && window.localStorage) {
            window.localStorage.setItem(REQUESTS_PROTOCOL_STORAGE_KEY, activeTab);
        }
    }, [activeTab]);

    useEffect(() => {
        dnsRequestsRef.current = dnsRequests;
    }, [dnsRequests]);

    useEffect(() => {
        httpRequestsRef.current = httpRequests;
    }, [httpRequests]);

    // ── Reset on zone change ──────────────────────────────────────────────
    useEffect(() => {
        setRequest(undefined);
        setDnsRequests([]);
        setHttpRequests([]);
        setDnsLoaded(false);
        setHttpLoaded(false);
        setDnsHasMoreOlder(true);
        setHttpHasMoreOlder(true);
        setDnsLoadingOlder(false);
        setHttpLoadingOlder(false);
        setDnsUnread(false);
        setHttpUnread(false);
        dnsLastTimestamp.current = 0;
        httpLastTimestamp.current = 0;
        dnsRequestsRef.current = [];
        httpRequestsRef.current = [];
    }, [zone]);

    // ── Initial / forced preload — both tabs in parallel ─────────────────
    useEffect(() => {
        setDnsLoaded(false);
        setHttpLoaded(false);

        DusseldorfAPI.GetRequests(zone, PRELOAD_LIMIT, 0, "dns")
            .then((reqs) => {
                setDnsRequests(reqs);
                dnsRequestsRef.current = reqs;
                setDnsHasMoreOlder(reqs.length === PRELOAD_LIMIT);
                dnsLastTimestamp.current =
                    reqs.length > 0
                        ? parseInt(String(reqs[0].time))
                        : Math.floor(Date.now() / 1000);
            })
            .catch((err) => {
                Logger.Error(err);
                setDnsRequests([]);
                dnsRequestsRef.current = [];
                setDnsHasMoreOlder(false);
                dnsLastTimestamp.current = Math.floor(Date.now() / 1000);
            })
            .finally(() => setDnsLoaded(true));

        DusseldorfAPI.GetRequests(zone, PRELOAD_LIMIT, 0, "http")
            .then((reqs) => {
                setHttpRequests(reqs);
                httpRequestsRef.current = reqs;
                setHttpHasMoreOlder(reqs.length === PRELOAD_LIMIT);
                httpLastTimestamp.current =
                    reqs.length > 0
                        ? parseInt(String(reqs[0].time))
                        : Math.floor(Date.now() / 1000);
            })
            .catch((err) => {
                Logger.Error(err);
                setHttpRequests([]);
                httpRequestsRef.current = [];
                setHttpHasMoreOlder(false);
                httpLastTimestamp.current = Math.floor(Date.now() / 1000);
            })
            .finally(() => setHttpLoaded(true));
    }, [zone, refreshKey]);

    const loadOlderRequests = async (protocol: Protocol, pageSize: number): Promise<boolean> => {
        const isDns = protocol === "dns";
        const currentRequestsRef = isDns ? dnsRequestsRef : httpRequestsRef;
        const hasMoreOlder = isDns ? dnsHasMoreOlder : httpHasMoreOlder;
        const isLoadingOlder = isDns ? dnsLoadingOlder : httpLoadingOlder;
        const setRequests = isDns ? setDnsRequests : setHttpRequests;
        const setHasMoreOlder = isDns ? setDnsHasMoreOlder : setHttpHasMoreOlder;
        const setLoadingOlder = isDns ? setDnsLoadingOlder : setHttpLoadingOlder;

        if (!hasMoreOlder || isLoadingOlder) {
            return false;
        }

        setLoadingOlder(true);
        let loadedAny = false;
        const requestLimit = Math.max(pageSize, OLDER_FETCH_LIMIT);

        try {
            const skip = currentRequestsRef.current.length;
            const olderRequests = await DusseldorfAPI.GetRequests(zone, requestLimit, skip, protocol);

            if (olderRequests.length === 0) {
                setHasMoreOlder(false);
                return false;
            }

            const existingKeys = new Set(currentRequestsRef.current.map(getRequestKey));
            const uniqueOlderRequests = olderRequests.filter((olderRequest) => !existingKeys.has(getRequestKey(olderRequest)));

            if (uniqueOlderRequests.length > 0) {
                loadedAny = true;
                setRequests((prev) => {
                    const prevKeys = new Set(prev.map(getRequestKey));
                    const uniqueRequests = uniqueOlderRequests.filter((olderRequest) => !prevKeys.has(getRequestKey(olderRequest)));
                    const nextRequests = uniqueRequests.length > 0 ? [...prev, ...uniqueRequests] : prev;
                    currentRequestsRef.current = nextRequests;
                    return nextRequests;
                });
            }

            if (olderRequests.length < requestLimit || uniqueOlderRequests.length === 0) {
                setHasMoreOlder(false);
            }
        } catch (err) {
            Logger.Error(err);
        } finally {
            setLoadingOlder(false);
        }

        return loadedAny;
    };

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
                            dnsLastTimestamp.current = Math.max(
                                dnsLastTimestamp.current,
                                ...newReqs.map((request) => parseInt(String(request.time)))
                            );
                            setDnsRequests((prev) => {
                                const existingKeys = new Set(prev.map(getRequestKey));
                                const uniqueRequests = newReqs.filter((request) => !existingKeys.has(getRequestKey(request)));

                                if (uniqueRequests.length > 0 && activeTabRef.current !== "dns") {
                                    setDnsUnread(true);
                                }

                                return uniqueRequests.length > 0 ? [...uniqueRequests, ...prev] : prev;
                            });
                        }
                    })
                    .catch(() => { /* silently ignore poll errors */ });
            }

            const httpSince = httpLastTimestamp.current;
            if (httpSince > 0) {
                DusseldorfAPI.GetRequests(zone, POLL_LIMIT, 0, "http", httpSince)
                    .then((newReqs) => {
                        if (newReqs.length > 0) {
                            httpLastTimestamp.current = Math.max(
                                httpLastTimestamp.current,
                                ...newReqs.map((request) => parseInt(String(request.time)))
                            );
                            setHttpRequests((prev) => {
                                const existingKeys = new Set(prev.map(getRequestKey));
                                const uniqueRequests = newReqs.filter((request) => !existingKeys.has(getRequestKey(request)));

                                if (uniqueRequests.length > 0 && activeTabRef.current !== "http") {
                                    setHttpUnread(true);
                                }

                                return uniqueRequests.length > 0 ? [...uniqueRequests, ...prev] : prev;
                            });
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
                        hasMoreOlder={activeTab === "dns" ? dnsHasMoreOlder : httpHasMoreOlder}
                        loadingOlder={activeTab === "dns" ? dnsLoadingOlder : httpLoadingOlder}
                        onLoadOlderPage={(pageSize) => loadOlderRequests(activeTab, pageSize)}
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
