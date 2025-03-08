// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.


import { Button, Combobox, Field, Input, Option, Tooltip } from "@fluentui/react-components";
import { SaveRegular, DismissRegular } from "@fluentui/react-icons";
import { useState } from "react";

import { Constants } from "../../../Helpers/Constants";

interface ResultHeaderRuleComponentEditProps {
    onSave: (newValue: string) => void;
    onDismiss: () => void;
    oldValue: string;
}

export const ResultHeaderRuleComponentEdit = ({
    onSave,
    onDismiss,
    oldValue
}: ResultHeaderRuleComponentEditProps): JSX.Element => {
    const [header, setHeader] = useState<string>(oldValue.split(":")[0]);
    const [value, setValue] = useState<string>(oldValue.split(":", 2)[1]);
    const [open, setOpen] = useState<boolean>(false);

    return (
        <div className="stack hstack-center">
            <div className={"stack vstack-gap"}>
                <Field
                    label="Header Name"
                    validationMessage={header.length > 0 ? undefined : "Cannot be empty"}
                >
                    <Combobox
                        style={{ minWidth: "unset" }}
                        open={open}
                        freeform={true}
                        value={header}
                        selectedOptions={[header]}
                        onOptionSelect={(_, data) => {
                            if (data.optionText) {
                                setHeader(data.optionText);
                            }
                        }}
                        onInput={(ev: React.ChangeEvent<HTMLInputElement>) => {
                            setHeader(ev.target.value);
                        }}
                        onOpenChange={(_, data) => {
                            setOpen(data.open);
                        }}
                    >
                        {Constants.CommonHttpResponseHeaders.map((header) => (
                            <Option
                                key={header}
                                value={header}
                            >
                                {header}
                            </Option>
                        ))}
                    </Combobox>
                </Field>

                <Field label="Header Value">
                    <Input
                        value={value}
                        onChange={(_, data) => {
                            setValue(data.value);
                        }}
                    />
                </Field>
            </div>

            <Tooltip
                content="Save"
                relationship="label"
            >
                <Button
                    appearance="subtle"
                    icon={<SaveRegular />}
                    disabled={header.length == 0 || `${header}: ${value}` == oldValue}
                    onClick={() => {
                        onSave(`${header}: ${value}`);
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
