/**
 * @jest-environment jsdom
 */

// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";

// Regression test for AB#2637: the "Filter by FQDN" text was not
// programmatically associated with the filter input, leaving it without an
// accessible name (WCAG 4.1.2). Verify the input now exposes that name.

jest.mock("../DusseldorfApi", () => ({
    DusseldorfAPI: { GetZones: () => Promise.resolve([]) }
}));
jest.mock("../Helpers/Logger", () => ({
    Logger: { PageView: () => {}, Error: () => {}, Info: () => {} }
}));
jest.mock("../Components/Zones/ZonesTable", () => ({ ZonesTable: () => null }));
jest.mock("../Components/AddZoneDialog", () => ({ AddZoneDialog: () => null }));

import { AllZonesScreen } from "./AllZonesScreen";

test("filter input has an accessible name", async () => {
    render(<AllZonesScreen />);

    const filter = await screen.findByRole("textbox", { name: "Filter by FQDN" });
    expect(filter).toBeInTheDocument();
});
