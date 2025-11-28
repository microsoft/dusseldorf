// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { ApplicationInsights, IExceptionTelemetry, ITelemetryPlugin, SeverityLevel } from '@microsoft/applicationinsights-web';
import { ReactPlugin } from '@microsoft/applicationinsights-react-js';
import DusseldorfConfig from '../DusseldorfConfig';

let _appInsights: ApplicationInsights | null = null;
let _reactPlugin: ReactPlugin | ITelemetryPlugin | null = null;

const INSTRUMENTATION_KEY = DusseldorfConfig.telemetryInstrumentationKey;

// @ts-nocheck
export class Logger {
    /**
     * Initialization, obv
     */
    static init = () => {
        if (_reactPlugin === null) {
            _reactPlugin = new ReactPlugin();
        }

        if (!_appInsights) {
            _appInsights = new ApplicationInsights({
                config: {
                    instrumentationKey: INSTRUMENTATION_KEY,
                    extensions: [_reactPlugin],
                }
            });
            _appInsights.loadAppInsights();
        }
    };


    static Trace = (msg: string, level: string) => {

        if (!_appInsights) {
            this.init();
        }

        switch (level) {
            case 'error':
                _appInsights?.trackTrace({
                    message: msg,
                    severityLevel: SeverityLevel.Error
                })
                break;
            case 'info':
                _appInsights?.trackTrace({
                    message: msg,
                    severityLevel: SeverityLevel.Information
                })
                break;
            case 'warn':
                _appInsights?.trackTrace({
                    message: msg,
                    severityLevel: SeverityLevel.Warning
                })
                break;

            default:
                // privacy prevails, if we don't have a proper log level, 
                // don't log anything.
                break;
        }

        // _appInsights?.flush();
    }

    static RESET = "\u001b[0m";
    static RED = "\u001b[1;31m";
    static GREEN = "\u001b[1;32m";
    static YELLOW = "\u001b[1;33m";

    static Info = (msg: string) => {
        console.log(this.GREEN + msg + this.RESET)
        this.Trace(msg, 'info');
    };

    static Warn = (msg: string) => {
        console.log(this.YELLOW + msg + this.RESET)
        this.Trace(msg, 'warn');
    };

    static Error = (msg: string | Error | unknown) => {
        const msgStr = String(msg)
        console.log(this.RED + msgStr + this.RESET)
        this.Trace(msgStr, 'error');
    };

    static Exception = (ex: IExceptionTelemetry) => {
        _appInsights?.trackException(ex);
    }

    static PageView = (path: string) => {
        _appInsights?.trackPageView({ pageType: 'screen', name: path })
    };

}