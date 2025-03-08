// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

const localStorageKeyName = 'theme';

export class ThemeHelper {
    static Set = (key: string) => {
        localStorage.setItem(localStorageKeyName, key)
    }
    static Get = () => {
        // if we have something in local storage, return that.
        // else, if the OS is in dark mode, say so.
        let theme = localStorage.getItem(localStorageKeyName);
        if (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            theme = 'dark';
        }
        return theme;
    }
}