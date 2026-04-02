// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { tokenizeHttp } from "./HttpTokenizer";

test("tokenizes request line with query", () => {
  const lines = tokenizeHttp("GET /items?id=10&sort=asc HTTP/1.1");

  expect(lines).toHaveLength(1);
  expect(lines[0].tokens).toEqual([
    { text: "GET", kind: "method" },
    { text: " ", kind: "plain" },
    { text: "/items", kind: "path" },
    { text: "?id=10&sort=asc", kind: "query" },
    { text: " ", kind: "plain" },
    { text: "HTTP/1.1", kind: "version" },
  ]);
});

test("tokenizes response line status class", () => {
  const lines = tokenizeHttp("HTTP/1.1 404 Not Found");

  expect(lines[0].tokens[2]).toEqual({ text: "404", kind: "status4xx" });
});

test("marks sensitive headers", () => {
  const lines = tokenizeHttp(
    "GET / HTTP/1.1\nAuthorization: Bearer token\nX-Test: value",
  );

  expect(lines[1].tokens[0].kind).toBe("sensitiveHeaderName");
  expect(lines[1].tokens[2].kind).toBe("sensitiveHeaderValue");
  expect(lines[2].tokens[0].kind).toBe("headerName");
  expect(lines[2].tokens[2].kind).toBe("headerValue");
});

test("treats lines after first blank line as body", () => {
  const lines = tokenizeHttp("GET / HTTP/1.1\nHost: m.dssldrf.net\n\nhello: world");

  expect(lines[3].tokens[0]).toEqual({ text: "hello: world", kind: "body" });
});
