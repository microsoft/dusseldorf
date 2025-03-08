// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Card, Text } from "@fluentui/react-components";
import { TargetAddRegular, TargetRegular } from "@fluentui/react-icons";

interface ZoneCardProps {
    addIcon: boolean,
    title: string,
    subTitle: string,
    onClick: () => void
}

export const ZoneCard = ({ addIcon, title, subTitle, onClick }: ZoneCardProps) => {
    return (
        <Card
            style={{
                minWidth: 210,
                maxWidth: 210,
                minHeight: 200,
                maxHeight: 200
            }}
            onClick={onClick}
        >
            <div className="stack vstack-gap" style={{ padding: 10 }}>
                {addIcon ? <TargetAddRegular fontSize={"3em"} /> : <TargetRegular fontSize={"3em"} />}
                <Text size={500} style={{ maxWidth: 190, wordWrap: "break-word" }}>{title}</Text>
                <Text size={300} style={{ maxWidth: 190, wordWrap: "break-word" }}>{subTitle}</Text>
            </div>
        </Card>
    );
}
