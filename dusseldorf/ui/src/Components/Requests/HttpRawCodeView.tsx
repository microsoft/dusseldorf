// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { makeStyles, tokens } from "@fluentui/react-components";
import { useMemo } from "react";

import { HttpTokenKind, tokenizeHttp } from "../../Helpers/HttpTokenizer";

interface IHttpRawCodeViewProps {
  value: string;
  rows: number;
  monospaced: boolean;
}

const useStyles = makeStyles({
  container: {
    border: `1px solid ${tokens.colorNeutralStroke1}`,
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground1,
    paddingTop: "8px",
    paddingRight: "10px",
    paddingBottom: "8px",
    paddingLeft: "10px",
    overflowY: "auto",
    overflowX: "hidden",
    lineHeight: "20px",
    fontSize: "13px",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  mono: {
    fontFamily: "Consolas, Courier New, monospace",
  },
  ui: {
    fontFamily: "Segoe UI, sans-serif",
  },
  method: {
    color: tokens.colorBrandForeground1,
    fontWeight: tokens.fontWeightSemibold,
  },
  path: {
    color: tokens.colorNeutralForeground1,
  },
  query: {
    color: tokens.colorPaletteTealForeground2,
  },
  version: {
    color: tokens.colorNeutralForeground3,
  },
  status2xx: {
    color: tokens.colorStatusSuccessForeground1,
    fontWeight: tokens.fontWeightSemibold,
  },
  status3xx: {
    color: tokens.colorPaletteGoldForeground2,
    fontWeight: tokens.fontWeightSemibold,
  },
  status4xx: {
    color: tokens.colorStatusWarningForeground2,
    fontWeight: tokens.fontWeightSemibold,
  },
  status5xx: {
    color: tokens.colorStatusDangerForeground1,
    fontWeight: tokens.fontWeightSemibold,
  },
  headerName: {
    color: tokens.colorBrandForeground2,
  },
  headerValue: {
    color: tokens.colorNeutralForeground1,
  },
  sensitiveHeaderName: {
    color: tokens.colorStatusWarningForeground2,
    fontWeight: tokens.fontWeightSemibold,
  },
  sensitiveHeaderValue: {
    color: tokens.colorStatusWarningForeground2,
    fontWeight: tokens.fontWeightSemibold,
  },
  body: {
    color: tokens.colorNeutralForeground2,
  },
  plain: {
    color: tokens.colorNeutralForeground1,
  },
});

const tokenClass = (
  kind: HttpTokenKind,
  styles: ReturnType<typeof useStyles>,
): string => {
  switch (kind) {
    case "method":
      return styles.method;
    case "path":
      return styles.path;
    case "query":
      return styles.query;
    case "version":
      return styles.version;
    case "status2xx":
      return styles.status2xx;
    case "status3xx":
      return styles.status3xx;
    case "status4xx":
      return styles.status4xx;
    case "status5xx":
      return styles.status5xx;
    case "headerName":
      return styles.headerName;
    case "headerValue":
      return styles.headerValue;
    case "sensitiveHeaderName":
      return styles.sensitiveHeaderName;
    case "sensitiveHeaderValue":
      return styles.sensitiveHeaderValue;
    case "body":
      return styles.body;
    default:
      return styles.plain;
  }
};

export const HttpRawCodeView = ({
  value,
  rows,
  monospaced,
}: IHttpRawCodeViewProps) => {
  const styles = useStyles();
  const lines = useMemo(() => tokenizeHttp(value), [value]);

  return (
    <div
      className={`${styles.container} ${monospaced ? styles.mono : styles.ui}`}
      style={{ maxHeight: `${rows * 20 + 16}px` }}
      role="textbox"
      aria-readonly="true"
    >
      {lines.map((line, lineIndex) => (
        <div key={`line-${lineIndex}`}>
          {line.tokens.length === 0 ||
          (line.tokens.length === 1 && line.tokens[0].text === "") ? (
            <span className={styles.plain}>&nbsp;</span>
          ) : (
            line.tokens.map((token, tokenIndex) => (
              <span
                key={`line-${lineIndex}-token-${tokenIndex}`}
                className={tokenClass(token.kind, styles)}
              >
                {token.text}
              </span>
            ))
          )}
        </div>
      ))}
    </div>
  );
};
