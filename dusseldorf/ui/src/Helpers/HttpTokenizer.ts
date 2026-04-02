// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

export type HttpTokenKind =
  | "plain"
  | "method"
  | "path"
  | "query"
  | "version"
  | "status2xx"
  | "status3xx"
  | "status4xx"
  | "status5xx"
  | "headerName"
  | "headerValue"
  | "sensitiveHeaderName"
  | "sensitiveHeaderValue"
  | "body";

export interface HttpToken {
  text: string;
  kind: HttpTokenKind;
}

export interface HttpLine {
  tokens: HttpToken[];
}

const isSensitiveValue = (value: string) => {
  return value.includes("Bearer ") || value.includes("eyJ");
};

const statusKind = (code: string): HttpTokenKind => {
  const numericCode = Number(code);

  if (numericCode >= 200 && numericCode < 300) {
    return "status2xx";
  }

  if (numericCode >= 300 && numericCode < 400) {
    return "status3xx";
  }

  if (numericCode >= 400 && numericCode < 500) {
    return "status4xx";
  }

  if (numericCode >= 500 && numericCode < 600) {
    return "status5xx";
  }

  return "plain";
};

const tokenizeRequestLine = (line: string): HttpLine => {
  const match = line.match(/^(\S+)\s+(\S+)\s+(\S+)$/);

  if (!match) {
    return { tokens: [{ text: line, kind: "plain" }] };
  }

  const [, method, target, version] = match;
  const queryIndex = target.indexOf("?");
  const path = queryIndex >= 0 ? target.slice(0, queryIndex) : target;
  const query = queryIndex >= 0 ? target.slice(queryIndex) : "";

  const tokens: HttpToken[] = [
    { text: method, kind: "method" },
    { text: " ", kind: "plain" },
    { text: path, kind: "path" },
  ];

  if (query) {
    tokens.push({ text: query, kind: "query" });
  }

  tokens.push(
    { text: " ", kind: "plain" },
    { text: version, kind: "version" },
  );

  return { tokens };
};

const tokenizeResponseLine = (line: string): HttpLine => {
  const match = line.match(/^(\S+)\s+(\d{3})(?:\s+(.*))?$/);

  if (!match) {
    return { tokens: [{ text: line, kind: "plain" }] };
  }

  const [, version, code, rest] = match;

  return {
    tokens: [
      { text: version, kind: "version" },
      { text: " ", kind: "plain" },
      { text: code, kind: statusKind(code) },
      ...(rest ? [{ text: ` ${rest}`, kind: "plain" as const }] : []),
    ],
  };
};

const tokenizeHeaderLine = (line: string): HttpLine => {
  const separator = line.indexOf(":");

  if (separator <= 0) {
    return { tokens: [{ text: line, kind: "plain" }] };
  }

  const headerName = line.slice(0, separator);
  const headerValue = line.slice(separator + 1).trimStart();
  const sensitive = isSensitiveValue(headerValue);

  return {
    tokens: [
      {
        text: headerName,
        kind: sensitive ? "sensitiveHeaderName" : "headerName",
      },
      { text: ": ", kind: "plain" },
      {
        text: headerValue,
        kind: sensitive ? "sensitiveHeaderValue" : "headerValue",
      },
    ],
  };
};

export const tokenizeHttp = (raw: string): HttpLine[] => {
  const lines = raw.split(/\r?\n/);

  if (lines.length === 0) {
    return [];
  }

  let inBody = false;

  return lines.map((line, index) => {
    if (index === 0) {
      return line.startsWith("HTTP/")
        ? tokenizeResponseLine(line)
        : tokenizeRequestLine(line);
    }

    if (inBody) {
      return { tokens: [{ text: line, kind: "body" }] };
    }

    if (line.trim() === "") {
      inBody = true;
      return { tokens: [{ text: "", kind: "plain" }] };
    }

    return tokenizeHeaderLine(line);
  });
};
