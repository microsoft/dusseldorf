/**
 * @jest-environment jsdom
 */

// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { tokens } from "@fluentui/react-components";

// Regression test for AB#2642: HTTP status text used fixed hex colors (e.g.
// green #22c55e ~2:1 on the light neutral background) that failed WCAG AA.
// Verify the status text now uses a theme-aware Fluent palette token.

jest.mock("./Analyzer", () => ({ Analyzer: () => null }));
jest.mock("./HttpRawCodeView", () => ({ HttpRawCodeView: () => null }));

import { HttpRequestDetails } from "./HttpRequestDetails";
import { DssldrfRequest } from "../../Types/DssldrfRequest";

const details = {
    request: { method: "GET", path: "/", version: "HTTP/1.1", headers: { Host: "m.dssldrf.net" }, body: "" },
    response: { code: 200, headers: {}, body: "" }
} as unknown as DssldrfRequest;

test("2xx status text uses a theme-aware color token, not a fixed hex", () => {
    render(<HttpRequestDetails details={details} />);

    const status = screen.getByText("HTTP/1.0 200");
    expect(status).toHaveStyle({ color: tokens.colorPaletteGreenForeground1 });
});
