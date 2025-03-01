// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Field, Input, Text, Tooltip } from "@fluentui/react-components";
import { DismissRegular, SaveRegular } from "@fluentui/react-icons";
import { useState } from "react";
import { DnsData } from "../../../Types/DssldrfRequest";

interface DnsDataComponentProps {
    onSave: (newValue: string) => void;
    onDismiss: () => void;
    oldValue?: string;
    dnsType?: string;
}

export const DnsDataComponent = ({ onSave, onDismiss, oldValue, dnsType }: DnsDataComponentProps): JSX.Element => {
    const parseValue = (v: string) => {
        try {
            const parsed = JSON.parse(v) as DnsData;
            return parsed.ip || parsed.cname || parsed.txt || v;
        } catch {
            return v;
        }
    }

    const parseKey = (v: string) => {
        try {
            const parsed = JSON.parse(v) as DnsData;
            return Object.keys(parsed).find(k => ["ip","cname","txt"].includes(k)) ?? "ip";
        } catch {
            return "ip";
        }
    }

    const getKey = (v: string | undefined) => {
        if (v == "A" || v == "AAAA") {
            return "ip";
        } else {
            return v?.toLowerCase() ?? "ip";
        }
    }

    const [value, setValue] = useState<string>(oldValue ? parseValue(oldValue) : "duSSeldoRF");
    const [jsonKey] = useState<string>(oldValue ? parseKey(oldValue) : getKey(dnsType));


    return (
        <div className="stack hstack-center">
            <Field
                label={oldValue !== undefined ? "" : "DNS Response Data"}
            >
                <Input
                    value={value}
                    onChange={(_, data) => {
                        setValue(data.value);
                    }}
                />
            </Field>

            <Tooltip
                content="Save"
                relationship="label"
            >
                <Button
                    appearance="subtle"
                    icon={<SaveRegular />}
                    onClick={() => {
                        onSave(`{ "${jsonKey}": "${value}" }`);
                    }}
                />
            </Tooltip>

            <Tooltip
                content="Cancel"
                relationship="label"
            >
                <Button
                    appearance="subtle"
                    icon={<DismissRegular />}
                    onClick={onDismiss}
                />
            </Tooltip>
        </div>
    );
};
