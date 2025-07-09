// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Body1Strong,
    Button,
    createTableColumn,
    DataGrid,
    DataGridBody,
    DataGridCell,
    DataGridRow,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    DialogTrigger,
    Divider,
    Subtitle1,
    TableColumnDefinition,
    Textarea,
    tokens,
    Tooltip
} from "@fluentui/react-components";

import { ArrowDownloadRegular, ChevronDownUpRegular, ChevronUpDownRegular, CopyRegular, FireRegular, StethoscopeRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

import { Analyzer } from "./Analyzer";
import { CopyButton } from "../CopyButton";
import { UiHelper } from "../../Helpers/UIHelper";
import { DssldrfRequest, HttpHeader, HttpRequest, HttpResponse } from "../../Types/DssldrfRequest";

/**
 * Helper functions
 */

const isSuspicious = (value: string) => {
    return value.includes("Bearer ") || value.includes("eyJ");
};

const mapHeaders = (headers: Record<string, string>): HttpHeader[] => {
    return Object.keys(headers).map((item) => ({
        header: item,
        value: headers[item]
    }));
};

const buildRawReq = (req: HttpRequest): string => {
    let newRawReq: string =
        `${req.method} ${req.path} ${req.version}\n` +
        Object.keys(req.headers) // per header
            .map((item) => {
                return `${item}: ${req.headers[item]}`;
            }) // return a name: value
            .join("\n");
    if (req.body) {
        newRawReq = newRawReq.concat("\n\n", req.body);
    } else if (req.body_b64) {
        newRawReq = newRawReq.concat("\n\n", "[binary content not shown]");
    }
    return newRawReq;
};

const buildRawResp = (resp: HttpResponse): string => {
    let newRawResp: string =
        `HTTP/1.0 ${resp.code}\n` +
        Object.keys(resp.headers) // per header
            .map((item) => {
                return `${item}: ${resp.headers[item]}`;
            }) // return a name: value
            .join("\n");
    newRawResp = newRawResp.concat("\n", "Server: dusseldorf v1");
    newRawResp = newRawResp.concat("\n", "Content-Length: ", resp.body.length.toString());
    if (resp.body) {
        newRawResp = newRawResp.concat("\n\n", resp.body);
    }
    return newRawResp;
};

/**
 * HttpRequestDetails component
 */

interface IHttpRequestDetailsProps {
    details: DssldrfRequest;
}

const downloadBase64Content = (b64content: string, filename: string) => {
    const content = atob(b64content);
    const byteArray = new Uint8Array(content.length);
    for (let i = 0; i < content.length; i++) {
        byteArray[i] = content.charCodeAt(i);
    }
    const blob = new Blob([byteArray], { type: "application/octet-stream" });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

export const HttpRequestDetails = ({ details }: IHttpRequestDetailsProps) => {
    const [req, setReq] = useState<HttpRequest>(details.request as HttpRequest);
    const [resp, setResp] = useState<HttpResponse>(details.response as HttpResponse);
    const [rawReq, setRawReq] = useState<string>(buildRawReq(req));
    const [rawResp, setRawResp] = useState<string>(buildRawResp(resp));

    // Control sensitive information displays
    const [showAnalyzer, setShowAnalyzer] = useState<boolean>(false);
    const [payload, setPayload] = useState<string>("");
    const [isSensitiveContent, setIsSensitiveContent] = useState<boolean>(isSuspicious(rawReq));

    // Control how much is displayed
    const [showFullRawReq, setShowFullRawReq] = useState<boolean>(UiHelper.GetPanelSettings("http.req.raw"));
    const [showFullRawResp, setShowFullRawResp] = useState<boolean>(UiHelper.GetPanelSettings("http.resp.raw"));
    const [showReqHeaders, setShowReqHeaders] = useState<boolean>(UiHelper.GetPanelSettings("http.req.parsed"));
    const [showRespHeaders, setShowRespHeaders] = useState<boolean>(UiHelper.GetPanelSettings("http.resp.parsed"));

    // Update variables when details changes
    useEffect(() => {
        const newReq = details.request as HttpRequest;
        const newResp = details.response as HttpResponse;
        const newRawReq = buildRawReq(newReq);

        setReq(newReq);
        setResp(newResp);
        setRawReq(buildRawReq(newReq));
        setRawResp(buildRawResp(newResp));
        setIsSensitiveContent(isSuspicious(newRawReq));
    }, [details]);

    const columns: TableColumnDefinition<HttpHeader>[] = [
        createTableColumn<HttpHeader>({
            columnId: "headerColumn",
            renderCell: (header) => {
                return <DataGridCell style={{ maxWidth: 300, wordWrap: "break-word" }}>{header.header}</DataGridCell>;
            }
        }),
        createTableColumn<HttpHeader>({
            columnId: "valueColumn",
            renderCell: (header) => {
                return <DataGridCell style={{ maxWidth: 300, wordWrap: "break-word" }}>{header.value}</DataGridCell>;
            }
        }),
        createTableColumn<HttpHeader>({
            columnId: "copyColumn",
            renderCell: (header) => {
                return (
                    <DataGridCell style={{ minWidth: 20, maxWidth: 20 }}>
                        <CopyButton text={header.value} />
                    </DataGridCell>
                );
            }
        }),
        createTableColumn<HttpHeader>({
            columnId: "analyzeColumn",
            renderCell: (header) => {
                if (isSuspicious(header.value)) {
                    return (
                        <DataGridCell style={{ minWidth: 20, maxWidth: 20 }}>
                            <Tooltip
                                content="Analyze (experimental)"
                                relationship="description"
                            >
                                <Button
                                    appearance="subtle"
                                    icon={<StethoscopeRegular />}
                                    onClick={() => {
                                        setPayload(header.value);
                                        setShowAnalyzer(true);
                                    }}
                                />
                            </Tooltip>
                        </DataGridCell>
                    );
                } else {
                    return <DataGridCell style={{ minWidth: 20, maxWidth: 20 }} />;
                }
            }
        })
    ];

    const downloadBodyBytes = () => {
        if (!req.body_b64) {
            console.warn("No bytes to download");
            return;
        }

        downloadBase64Content(req.body_b64, `request-content-${Date.now()}.bin`)
    };

    return (
        <div className="stack vstack-gap">
            <div className="stack">
                <div className="stack hstack-spread">
                    <Body1Strong>Raw Request</Body1Strong>
                    <Tooltip
                        content="Shrink or expand raw request"
                        relationship="description"
                    >
                        <Button
                            appearance="subtle"
                            icon={showFullRawReq ? <ChevronDownUpRegular /> : <ChevronUpDownRegular />}
                            onClick={() => {
                                UiHelper.SetPanelSettings("http.req.raw", !showFullRawReq);
                                setShowFullRawReq(!showFullRawReq);
                            }}
                        />
                    </Tooltip>
                </div>

                <Textarea
                    readOnly={true}
                    rows={showFullRawReq ? 10 : 3}
                    value={rawReq}
                    // monospaced font
                    // style={{ fontFamily: tokens.fontFamilyMonospace }}
                />
                {(!req.body && req.body_b64 && showFullRawReq) ? (
                    <div className="stack">
                        <div style={{margin: 5, marginTop: 10}}>
                            Because the body of this request contains binary content, it cannot be shown inside Dusseldorf. You can
                            download the body content or copy it to your clipboard as base64. 
                        </div>
                        <div className="stack hstack-gap" style={{margin: 5}}>
                            <Button
                                appearance="primary"
                                icon={<ArrowDownloadRegular />}
                                onClick={downloadBodyBytes}
                            >
                                Download content
                            </Button>
                            <Button
                                appearance="primary"
                                icon={<CopyRegular />}
                                onClick={() => (
                                    navigator.clipboard.writeText(req.body_b64!)
                                )}
                            >
                                Copy as base64
                            </Button>
                        </div>
                    </div>      
                ) : null}
            </div>

            <div className="stack">
                <div className="stack hstack-spread">
                    <div className="stack hstack-center">
                        <Body1Strong>HTTP Request Headers</Body1Strong>
                        {isSensitiveContent && (
                            <Dialog>
                                <DialogTrigger disableButtonEnhancement>
                                    <Button
                                        appearance="subtle"
                                        icon={<FireRegular />}
                                    />
                                </DialogTrigger>
                                <DialogSurface style={{ width: 400 }}>
                                    <DialogBody>
                                        <DialogTitle>Sensitive content detected</DialogTitle>
                                        <DialogContent>
                                            There may be sensitive content in this request, please handle with care.
                                        </DialogContent>
                                        <DialogActions>
                                            <DialogTrigger disableButtonEnhancement>
                                                <Button>Close</Button>
                                            </DialogTrigger>
                                        </DialogActions>
                                    </DialogBody>
                                </DialogSurface>
                            </Dialog>
                        )}
                    </div>

                    <Tooltip
                        content="Shrink or expand request headers"
                        relationship="description"
                    >
                        <Button
                            appearance="subtle"
                            icon={showReqHeaders ? <ChevronDownUpRegular /> : <ChevronUpDownRegular />}
                            onClick={() => {
                                UiHelper.SetPanelSettings("http.req.parsed", !showReqHeaders);
                                setShowReqHeaders(!showReqHeaders);
                            }}
                        />
                    </Tooltip>
                </div>

                <DataGrid
                    items={showReqHeaders ? mapHeaders(req.headers) : []}
                    columns={columns}
                    noNativeElements={false}
                    style={{ tableLayout: "auto" }}
                >
                    <DataGridBody<HttpHeader>>
                        {({ item }) => (
                            <DataGridRow<HttpHeader> style={{ borderWidth: 0 }}>
                                {({ renderCell }) => renderCell(item)}
                            </DataGridRow>
                        )}
                    </DataGridBody>
                </DataGrid>
            </div>

            <Divider style={{ paddingTop: 10, paddingBottom: 10 }} />

            <Subtitle1>Response Details</Subtitle1>

            <div className="stack">
                <div className="stack hstack-spread">
                    <Body1Strong>Raw Response</Body1Strong>
                    <Tooltip
                        content="Shrink or expand raw response"
                        relationship="description"
                    >
                        <Button
                            appearance="subtle"
                            icon={showFullRawResp ? <ChevronDownUpRegular /> : <ChevronUpDownRegular />}
                            onClick={() => {
                                UiHelper.SetPanelSettings("http.resp.raw", !showFullRawResp);
                                setShowFullRawResp(!showFullRawResp);
                            }}
                        />
                    </Tooltip>
                </div>

                <Textarea
                    readOnly={true}
                    rows={showFullRawResp ? 10 : 3}
                    value={rawResp}
                />
            </div>

            <div className="stack">
                <div className="stack hstack-spread">
                    <Body1Strong>HTTP Response Headers</Body1Strong>
                    <Tooltip
                        content="Shrink or expand response headers"
                        relationship="description"
                    >
                        <Button
                            appearance="subtle"
                            icon={showRespHeaders ? <ChevronDownUpRegular /> : <ChevronUpDownRegular />}
                            onClick={() => {
                                UiHelper.SetPanelSettings("http.resp.parsed", !showRespHeaders);
                                setShowRespHeaders(!showRespHeaders);
                            }}
                        />
                    </Tooltip>
                </div>

                <DataGrid
                    items={showRespHeaders ? mapHeaders(resp.headers) : []}
                    columns={columns}
                    noNativeElements={false}
                    style={{ tableLayout: "auto" }}
                >
                    <DataGridBody<HttpHeader>>
                        {({ item }) => (
                            <DataGridRow<HttpHeader> style={{ borderWidth: 0 }}>
                                {({ renderCell }) => renderCell(item)}
                            </DataGridRow>
                        )}
                    </DataGridBody>
                </DataGrid>
            </div>

            <Analyzer
                payload={payload}
                open={showAnalyzer}
                setOpen={setShowAnalyzer}
            />
        </div>
    );
};
