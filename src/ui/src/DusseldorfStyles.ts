// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { FontSizes, FontWeights } from "@fluentui/react/lib/Styling";

const _leftNavWidth = 40;

export const DusseldorfStyles = { 

    boldStyle: { root: { fontWeight: FontWeights.semibold } },

    leftNavWidth: _leftNavWidth,

    bladeWidth: 570,

    leftNav: {         
        root: {
            minWidth: _leftNavWidth, 
            maxwidth: _leftNavWidth, 
            width: _leftNavWidth, 
            paddingBottom: 'auto',
    }},

    secondaryNav: { root: { 
        minWidth: 250, 
        maxwidth: 250, 
        width: 250, 
    }},

    monospaced: "Consolas, Moncao, Menlo",

    padding: { root: { marginTop: 10, marginBottom: 10 } },

    paddedStack: { root: {
        paddingLeft: 20,
        paddingRight: 20,
    }},

    userLabel: { 
        root: { 
            fontSize: FontSizes.size14,
            paddingLeft: 4,
            paddingRight: 4,
    }},

    w20: { root: {
        width: 220,
        paddingRight: 10
    }},

    // templates
    templateCard:  {
        root: {
            display: 'inline-block',
            marginRight: 20,
            width: 140,
        }
    }
    
}