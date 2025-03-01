// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Tooltip } from "@fluentui/react-components";
import { CopyRegular } from "@fluentui/react-icons";
import { Logger } from "../Helpers/Logger";

interface CopyButtonProps {
    text: string;
}

export const CopyButton = ({ text }: CopyButtonProps): JSX.Element => {
    return (
        <Tooltip
            content={`Copy ${text} to clipboard`}
            relationship="label"
        >
            <Button
                appearance="subtle"
                icon={<CopyRegular />}
                onClick={() => {
                    navigator.clipboard.writeText(text).catch((err) => {
                        Logger.Error(err);
                    });
                }}
            />
        </Tooltip>
    );
};
