// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Input } from "@fluentui/react-components";
import { useState } from "react";

interface InputRuleComponentProps {
    actionName: string;
    value: string;
    setValue: (value: string) => void;
    setIsValid: (valid: boolean) => void;
}

export const InputRuleComponent = ({ actionName, value, setValue, setIsValid }: InputRuleComponentProps): JSX.Element => {
    const [localValue, setLocalValue] = useState<string>(value);

    return (
        <Input
            value={localValue}
            onChange={(_, data) => {
                setValue(data.value);
                setLocalValue(data.value);
                if (actionName === "http.body" || actionName === "http.path") {
                    setIsValid(data.value.length > 0);
                } else if (actionName === "http.passthru") {
                    setIsValid(data.value.startsWith("https://"));
                }
            }}
        />
    );
};
