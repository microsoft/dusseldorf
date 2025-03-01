// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Select } from "@fluentui/react-components";
import { useEffect, useState } from "react";

import { Constants } from "../../../Helpers/Constants";

interface SelectRuleComponentProps {
    actionName: string;
    value: string;
    setValue: (value: string) => void;
}

export const SelectRuleComponent = ({ actionName, value, setValue }: SelectRuleComponentProps): JSX.Element => {
    const [options, setOptions] = useState<JSX.Element[]>([]);
    const [localValue, setLocalValue] = useState<string>(value);

    useEffect(() => {
        if (actionName === "dns.type") {
            setOptions(
                ["A", "AAAA", "CNAME", "TXT"].map((dnsType) => (
                    <option
                        key={dnsType}
                        value={dnsType}
                    >
                        {dnsType}
                    </option>
                ))
            );
        } else if (actionName === "http.code") {
            setOptions(
                Constants.HttpResultCodes.map((code) => (
                    <option
                        key={code.key}
                        value={code.key}
                    >
                        {code.text}
                    </option>
                ))
            );
        } else {
            setOptions([]);
        }
    }, [actionName]);

    return (
        <Select
            value={localValue}
            onChange={(_, data) => {
                setValue(data.value);
                setLocalValue(data.value);
            }}
        >
            {options}
        </Select>
    );
};
