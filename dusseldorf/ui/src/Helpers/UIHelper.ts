// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

// TODO: mihendri - remove this or make this better.
export class UiHelper {

    static readonly KEYZONES = 'uihelper.hidden_zones';
    static readonly delim = ";";

    static GetPanelSettings = (key: string) => {
        const items = window.localStorage.getItem("panel")?.split(UiHelper.delim) ?? false;
        return items ? items.includes(key) : true;
    }

    static SetPanelSettings = (key: string, value: boolean) => {
        let items = window.localStorage.getItem("panel")?.split(UiHelper.delim) ?? [];
        if (value) {
            items.push(key)
        }
        else {
            items = items.filter(x => x != key)
        }
        window.localStorage.setItem("panel", items.join(UiHelper.delim))
    }

    static _hidden_zones: string[] = localStorage.getItem(UiHelper.KEYZONES)?.split(UiHelper.delim) ?? [];

    static ToggleZone = (key: string) => {
        if (key == "") return;
        if (UiHelper._hidden_zones.includes(key)) {
            // is hidden already, unhide it by removing it from the list
            UiHelper._hidden_zones = UiHelper._hidden_zones.filter(x => x != key)
        }
        else {
            // add the zone 
            UiHelper._hidden_zones.push(key);
        }

        // set local storage too 
        localStorage.setItem(UiHelper.KEYZONES, UiHelper._hidden_zones.join(UiHelper.delim))
    }

    /**
     * Whether a zone is hidden
     * @param key : the zone name
     * @returns : true if it's hidden
     */
    static IsZoneHidden = (key: string) =>
        UiHelper._hidden_zones.includes(key);

}
