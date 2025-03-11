// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Subtitle2 } from "@fluentui/react-components";
import '../Styles/Stack.css';

export const Logo = () => {
    return (
        <div className='stack hstack-center'>
            <Subtitle2 style={{ color: "#ffffff" }} >Du</Subtitle2>
            <Subtitle2 style={{ color: "#f0fcdc" }} >ss</Subtitle2>
            <Subtitle2 style={{ color: "#ffffff" }} >eldo</Subtitle2>
            <Subtitle2 style={{ color: "#f0fcdc" }} >rf</Subtitle2>
        </div>
    );
}