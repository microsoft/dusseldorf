// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Zone } from "../Types/Zone";
import { Logger } from "./Logger";
const sessionStorageKeyName = 'zones';
export class CacheHelper {
    static SetZones = (zones: Zone[]) => {
        sessionStorage.setItem(sessionStorageKeyName, JSON.stringify(zones))
    };
    static GetZones = () => {
        try {
            const s = sessionStorage.getItem(sessionStorageKeyName) ?? "[]";
            return JSON.parse(s) as Zone[];
        } catch {
            Logger.Error("CacheHelper.GetZones(): parsing error");
            this.SetZones([]);
        }
        return [];
    };

    static SetToken = (token: string) => {
        sessionStorage.setItem("token", token)
    };
    static GetToken = () => sessionStorage.getItem("token") ?? "";
}