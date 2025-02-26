// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Tooltip } from "@fluentui/react-components";
import { OpenRegular } from "@fluentui/react-icons";

interface OpenInNewTabProps {
    url: string;
}

export const OpenInNewTabButton = ({ url }: OpenInNewTabProps): JSX.Element => {

    // to prevent any xss issues, the url must start with https://
    if (!url.startsWith('https://')) {
        url = 'https://' + url;
    }

    return (
        <Tooltip content={`Open ${url} in a new tab`} relationship="label">
            <Button
                appearance="transparent"
                icon={<OpenRegular />}
                onClick={() => {
                    window.open(url, '_blank');
                }}
            />
        </Tooltip>
    );
}
