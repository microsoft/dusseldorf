// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Field, Input, Text, Tooltip } from "@fluentui/react-components";
import { DismissRegular, SaveRegular } from "@fluentui/react-icons";
import { useState } from "react";

interface DnsDataComponentProps {
    onSave: (newValue: string) => void;
    onDismiss: () => void;
    oldValue?: string;
}

export const DnsDataComponent = ({ onSave, onDismiss, oldValue }: DnsDataComponentProps): JSX.Element => {
    const [value, setValue] = useState<string>(oldValue ?? '{ "data": "duSSeldoRF" }');
    const [validationMsg, setValidationMsg] = useState<string>("");

    const getValidationMsg = (newValue: string) => {
        try {
            const parsed = JSON.parse(newValue) as object;
            if (Object.keys(parsed).length == 0) {
                return `Must be valid JSON of the form '{ "dnsType": "value" }'`;
            } else if (Object.keys(parsed).length != 1) {
                return "Can only have one key in JSON";
            } else {
                if (["ip", "cname", "mx", "ns", "txt", "data"].includes(Object.keys(parsed)[0])) {
                    return "";
                } else {
                    console.log(Object.keys(parsed)[0])
                    return "JSON key, must be one of: ip, cname, mx, ns, txt, or data";
                }
            }
        } catch {
            return `Must be valid JSON of the form '{ "dnsType": "value" }'`;
        }
    };

    return (
        <div className="stack hstack-center">
            <Field
                label={oldValue !== undefined ? "" : "DNS Response Data"}
                validationMessage={validationMsg ? <Text truncate>{validationMsg}</Text> : ""}
            >
                <Input
                    value={value}
                    onChange={(_, data) => {
                        setValue(data.value);
                        setValidationMsg(getValidationMsg(data.value));
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
                    disabled={validationMsg.length != 0}
                    onClick={() => {
                        onSave(value);
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
