/**
 * @jest-environment jsdom
 */

// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";

// Regression test for AB#2639: the destructive "Delete" confirmation button
// used white text on #ef4444 (3.76:1, below WCAG AA 4.5:1). Verify it now uses
// the darker #c50f1f red.

jest.mock("./DnsRequestDetails", () => ({ DnsRequestDetails: () => null }));
jest.mock("./HttpRequestDetails", () => ({ HttpRequestDetails: () => null }));
jest.mock("../../DusseldorfApi", () => ({ DusseldorfAPI: { DeleteRequest: () => Promise.resolve(true) } }));
jest.mock("../../Helpers/Logger", () => ({ Logger: { Info: () => {}, Error: () => {} } }));

import { RequestDetails } from "./RequestDetails";
import { DssldrfRequest } from "../../Types/DssldrfRequest";

const request = {
    protocol: "dns",
    time: 1700000000,
    clientip: "1.2.3.4",
    request: {},
    response: {}
} as unknown as DssldrfRequest;

test("delete confirmation button uses the higher-contrast red", async () => {
    render(<RequestDetails zone="example.dssldrf.net" request={request} />);

    // Open the delete confirmation dialog.
    fireEvent.click(screen.getByRole("button", { name: "Delete this request" }));

    const confirm = await screen.findByRole("button", { name: "Delete" });
    expect(confirm).toHaveStyle({ backgroundColor: "#c50f1f" });
});
