// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Textarea } from "@fluentui/react-components";
import { useState } from "react";

interface TextareaRuleComponentProps {
    value: string;
    setValue: (value: string) => void;
}

export const TextareaRuleComponent = ({ value, setValue }: TextareaRuleComponentProps): JSX.Element => {
    const [localValue, setLocalValue] = useState<string>(value);

    return (
        <Textarea
            resize="both"
            rows={6}
            placeholder='{"key":"value"}'
            value={localValue}
            onChange={(_, data) => {
                setValue(data.value);
                setLocalValue(data.value);
            }}
        />
    );
};
