// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Dropdown, Option } from "@fluentui/react-components";
import { useState } from "react";

const options = [
    <Option key="delete">DELETE</Option>,
    <Option key="head">HEAD</Option>,
    <Option key="get">GET</Option>,
    <Option key="options">OPTIONS</Option>,
    <Option key="patch">PATCH</Option>,
    <Option key="post">POST</Option>,
    <Option key="put">PUT</Option>
];

interface MultiSelectRuleComponentProps {
    defaultValue: string;
    setValueString: (value: string) => void;
    setIsValid: (valid: boolean) => void;
}

export const MultiSelectRuleComponent = ({
    defaultValue,
    setValueString,
    setIsValid
}: MultiSelectRuleComponentProps): JSX.Element => {
    const [value, setValue] = useState<string[]>(defaultValue.toUpperCase().split(","));

    return (
        <Dropdown
            style={{ minWidth: "unset" }}
            multiselect
            value={value.join(", ")}
            selectedOptions={value}
            onOptionSelect={(_, data) => {
                setValue(data.selectedOptions);
                setValueString(data.selectedOptions.join(","));
                setIsValid(data.selectedOptions.length > 0);
            }}
        >
            {options}
        </Dropdown>
    );
};
