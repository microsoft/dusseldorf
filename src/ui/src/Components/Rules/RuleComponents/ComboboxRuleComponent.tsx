// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Combobox, Option } from "@fluentui/react-components";
import { useState } from "react";
import { Constants } from "../../../Helpers/Constants";

interface ComboboxRuleComponentProps {
    defaultValue: string;
    setValueString: (value: string) => void;
    setIsValid: (valid: boolean) => void;
}

export const ComboboxRuleComponent = ({
    defaultValue,
    setValueString,
    setIsValid
}: ComboboxRuleComponentProps): JSX.Element => {
    const [value, setValue] = useState<string>(defaultValue);
    const [open, setOpen] = useState<boolean>(false);

    return (
        <Combobox
            style={{ minWidth: "unset" }}
            open={open}
            freeform={true}
            value={value}
            selectedOptions={[value]}
            onOptionSelect={(_, data) => {
                if (data.optionText) {
                    setValue(data.optionText);
                    setValueString(data.optionText);
                    setIsValid(data.optionText.length > 0);
                }
            }}
            onInput={(ev: React.ChangeEvent<HTMLInputElement>) => {
                setValue(ev.target.value);
                setValueString(ev.target.value);
                setIsValid(ev.target.value.length > 0);
            }}
            onOpenChange={(_, data) => {
                setOpen(data.open);
            }}
        >
            {Constants.CommonHttpRequestHeaders.map((header) => (
                <Option
                    key={header}
                    value={header}
                >
                    {header}
                </Option>
            ))}
        </Combobox>
    );
};
