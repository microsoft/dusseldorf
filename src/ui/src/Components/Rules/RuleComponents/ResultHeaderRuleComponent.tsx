// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.


import { Button, Combobox, Field, Input, Option, Tooltip } from "@fluentui/react-components";
import { SaveRegular, DismissRegular } from "@fluentui/react-icons";
import { useState } from "react";

import { Constants } from "../../../Helpers/Constants";

interface ResultHeaderRuleComponentProps {
    onSave: (newValue: string) => void;
    onDismiss: () => void;
}

export const ResultHeaderRuleComponent = ({ onSave, onDismiss }: ResultHeaderRuleComponentProps): JSX.Element => {
    const [header, setHeader] = useState<string>("Cookie");
    const [value, setValue] = useState<string>("");
    const [open, setOpen] = useState<boolean>(false);

    return (
        <div className="stack hstack-center">
            <div
                className={"stack hstack-gap"}
                style={{ alignItems: "start" }}
            >
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
                    disabled={header.length == 0}
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
