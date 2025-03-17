// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Tooltip } from "@fluentui/react-components";
import { CheckmarkFilled, CopyRegular } from "@fluentui/react-icons";
import { useState } from "react";

import { Logger } from "../Helpers/Logger";

interface CopyButtonProps {
    text: string;
}

export const CopyButton = ({ text }: CopyButtonProps): JSX.Element => {
    const [content, setContent] = useState<string>(`Copy ${text} to clipboard`);
    const [icon, setIcon] = useState<JSX.Element>(<CopyRegular />);

    return (
        <Tooltip
            content={content}
            relationship="label"
        >
            <Button
                appearance="subtle"
                icon={icon}
                onClick={() => {
                    navigator.clipboard
                        .writeText(text)
                        .then(() => {
                            setContent("Copied!");
                            setIcon(<CheckmarkFilled color="green" />);

                            setTimeout(() => {
                                setContent(`Copy ${text} to clipboard`);
                                setIcon(<CopyRegular />);
                            }, 2000);
                        })
                        .catch((err) => {
                            Logger.Error(err);
                        });
                }}
            />
        </Tooltip>
    );
};
