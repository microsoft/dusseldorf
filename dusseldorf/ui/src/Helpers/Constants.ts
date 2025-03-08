// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

/**
 * A static class of constants
 */

export const Constants = {

    /**
     * Common HTTP Request headers
     */
    CommonHttpRequestHeaders: [
        "Accept",
        // "Accept-Encoding",
        // "Accept-Language",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "Authorization",
        "Connection",
        "Content-Length",
        "Content-Security-Policy",
        "Content-Type",
        "Cookie",
        // "Date",
        "Expect",
        "Forwarded",
        "Host",
        "Origin",
        "Proxy-Authorization",
        "Referer",
        "Transfer-Encoding",
        "User-Agent",
        "Via",
        // non standard
        "X-Csrf-Token",
        "X-Correlation-ID",
        "X-Forwarded-For",
        "X-Requested-With",
    ],

    /**
     * Common HTTP Response headers
     */
    CommonHttpResponseHeaders: [
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Age",
        "Authorization",
        "Cache-Control",
        "Connection-Disposition",
        "Connection-Encoding",
        "Content-Length",
        "Content-Security-Policy",
        "Content-Type",
        "Date",
        "ETag",
        "Last-Modified",
        "Location",
        "Proxy-Authenticate",
        "OData-Version",
        "Server",
        "Set-Cookie",
        "Referer",
        "Transfer-Encoding",
        "Via",
        "WWW-Authenticate",

        // non standard
        "x-ms-blob-type",
        "X-Azure-Ref",
        "X-Powered-By",
    ],



    HttpResultCodes: [
        { key: 100, text: "100 Continue" },
        { key: 101, text: "101 Switching Protocols" },
        { key: 102, text: "102 Processing" },
        { key: 103, text: "103 Early Hints" },
        { key: 104, text: "104 Connection Established" },

        // "success"
        { key: 200, text: "200 Ok" },
        { key: 201, text: "201 Created" },
        { key: 202, text: "202 Accepted" },
        { key: 203, text: "203 Non-Authoritative Information" },
        { key: 204, text: "204 No Content" },
        { key: 205, text: "205 Reset Content" },
        { key: 206, text: "206 Partial Content" },

        // redirections
        { key: 300, text: "300 Multiple Choices" },
        { key: 301, text: "301 Moved Permanently" },
        { key: 302, text: "302 Moved temporarily" },
        { key: 303, text: "303 See Other" }, // sea otter 🦦
        { key: 304, text: "304 Not modified" },
        { key: 305, text: "305 Use Proxy" },
        { key: 306, text: "306 Unused" },
        { key: 307, text: "307 Temporary Redirect" },
        { key: 308, text: "308 Permanent Redirect" },

        { key: 400, text: "400 Bad request" },
        { key: 401, text: "401 Unauthorized" },
        { key: 402, text: "402 Payment Required" }, // future use 💰 
        { key: 403, text: "403 Forbidden" },
        { key: 404, text: "404 Not Found" },
        { key: 405, text: "405 Method not allowed" },
        { key: 406, text: "406 Not Acceptable" },
        { key: 407, text: "407 Proxy Authentication Required" },
        { key: 408, text: "408 Request Timeout" },
        { key: 409, text: "409 Conflict" },
        { key: 410, text: "410 Gone" },
        { key: 411, text: "411 Length Required" },
        { key: 412, text: "412 Precondition Failed" },
        { key: 413, text: "413 Payload Too Large" },
        { key: 414, text: "414 URI Too Long" },

        { key: 415, text: "415 Unsupported Media Type" },
        { key: 416, text: "416 Range Not Satisfiable" },
        { key: 417, text: "417 Expectation failed" },
        { key: 418, text: "418 I am a teapot" }, // 🍵
        { key: 421, text: "421 Misdirected Request" },
        { key: 422, text: "422 Unprocessable Entity" },
        { key: 423, text: "423 Locked" },
        { key: 424, text: "424 Failed Dependency" },
        { key: 425, text: "425 Too Early" },
        { key: 426, text: "426 Upgrade Required" },
        { key: 428, text: "428 Precondition Required" },
        { key: 429, text: "429 Too Many Requests" },
        { key: 431, text: "431 Request Header Fields Too Large" },
        { key: 451, text: "451 Unavailable For Legal Reasons" },

        { key: 500, text: "500 Server error" },
        { key: 501, text: "501 Not Implemented" },
        { key: 502, text: "502 Bad Gateway" },
        { key: 503, text: "503 Service Unavailable" },
        { key: 504, text: "504 Gateway Timeout" },
        { key: 505, text: "505 HTTP Version not allowed" },
        { key: 506, text: "506 Variant Also Negotiates" },
        { key: 507, text: "507 Insufficient Storage" },
        { key: 508, text: "508 Loop Detected" },
        { key: 510, text: "510 Not Extended" },
        { key: 511, text: "511 Network Authorization Required" },
    ],

    Predicates: {
        HttpRequestBodyRegexPredicate: "http.body",
        HttpRequestHeadersPredicate: "http.headers",
        HttpRequestHeadersRegexPredicate: "http.headers.regex",
        HttpRequestMethodPredicate: "http.method",
        HttpRequestUrlPredicate: "http.url",
    },

    Results: {
        Respond: "respond",
        WebHook: "webhook"
    }
}
