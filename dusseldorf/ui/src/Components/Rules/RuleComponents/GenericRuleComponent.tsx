// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Field, Tooltip } from "@fluentui/react-components";
import { DismissRegular, SaveRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";
import { SelectRuleComponent } from "./SelectRuleComponent";
import { MultiSelectRuleComponent } from "./MultiSelectRuleComponent";
import { ComboboxRuleComponent } from "./ComboboxRuleComponent";
import { TextareaRuleComponent } from "./TextareaRuleComponent";
import { InputRuleComponent } from "./InputRuleComponent";

const defaultValueDictionary: Record<number, Record<string, string>> = {
    0: {
        "dns.type": "A",
        "http.code": "200",
        "http.header": "Cookie: duSSldRF",
        "http.passthru": "https://"
    },
    1: {
        "dns.type": "A",
        "http.body": ".*", // must be regex
        "http.header": "Cookie",
        "http.method": "GET",
        "http.path": "*"
    }
};

const invalidMessageDictionary: Record<number, Record<string, string>> = {
    0: {
        "http.header": "HTTP header name cannot be empty",
        "http.passthru": `URL must start with "https://"`
    },
    1: {
        "http.body": "Invalid regex",
        "http.header": "HTTP header cannot be empty",
        "http.method": "Must select at least one method",
        "http.path": "Invalid regex"
    }
};

const fieldLabelDictionary: Record<number, Record<string, string>> = {
    0: {
        "dns.data": "DNS Response Data",
        "dns.type": "DNS Response Type",
        "http.body": "Response Body",
        "http.code": "Response Code",
        "http.header": "HTTP Response Header",
        "http.passthru": "Passthru URL"
    },
    1: {
        "dns.type": "DNS Type",
        "http.body": "Body must match following regex",
        "http.header": "Headers must contain",
        "http.method": "For following HTTP method(s)",
        "http.path": "Path must match following regex"
    }
};

const getDefaultValue = (isPredicate: boolean, actionName: string, oldValue: string | undefined) => {
    if (oldValue !== undefined) {
        return oldValue;
    } else {
        return defaultValueDictionary[isPredicate ? 1 : 0][actionName] ?? "";
    }
};

const getInvalidMessage = (isPredicate: boolean, actionName: string) => {
    return invalidMessageDictionary[isPredicate ? 1 : 0][actionName] ?? "";
};

const getFieldLabel = (isPredicate: boolean, actionName: string, oldValue: string | undefined) => {
    if (oldValue !== undefined) {
        return "";
    } else {
        return fieldLabelDictionary[isPredicate ? 1 : 0][actionName] ?? "";
    }
};

interface GenericRuleComponentProps {
    isPredicate: boolean;
    actionName: string;
    onDismiss: () => void;
    onSave: (newValue: string) => void;
    oldValue?: string;
}

export const GenericRuleComponent = ({
    isPredicate,
    actionName,
    oldValue,
    onDismiss,
    onSave
}: GenericRuleComponentProps) => {
    const [isValid, setIsValid] = useState<boolean>(true);
    const [value, setValue] = useState<string>(getDefaultValue(isPredicate, actionName, oldValue));
    const [invalidMessage, setInvalidMessage] = useState<string>(getInvalidMessage(isPredicate, actionName));
    const [fieldLabel, setFieldLabel] = useState<string>(getFieldLabel(isPredicate, actionName, oldValue));
    const [component, setComponent] = useState<JSX.Element>(<></>);

    const getElement = (isPredicate: boolean, actionName: string) => {
        if (!isPredicate && actionName === "http.body") {
            return (
                <TextareaRuleComponent
                    value={value}
                    setValue={setValue}
                />
            );
        } else if (actionName === "dns.type" || actionName === "http.code") {
            return (
                <SelectRuleComponent
                    actionName={actionName}
                    value={value}
                    setValue={setValue}
                />
            );
        } else if (actionName === "http.method") {
            return (
                <MultiSelectRuleComponent
                    defaultValue={value}
                    setValueString={setValue}
                    setIsValid={setIsValid}
                />
            );
        } else if (isPredicate && actionName === "http.header") {
            return (
                <ComboboxRuleComponent
                    defaultValue={value}
                    setValueString={setValue}
                    setIsValid={setIsValid}
                />
            );
        } else {
            return (
                <InputRuleComponent
                    actionName={actionName}
                    value={value}
                    setValue={setValue}
                    setIsValid={setIsValid}
                />
            );
        }
    };

    useEffect(() => {
        setValue(getDefaultValue(isPredicate, actionName, oldValue));
        setInvalidMessage(getInvalidMessage(isPredicate, actionName));
        setFieldLabel(getFieldLabel(isPredicate, actionName, oldValue));
        setIsValid(true);
        setComponent(getElement(isPredicate, actionName));
    }, [isPredicate, actionName, oldValue]);

    return (
        <div className="stack hstack-center">
            <Field
                label={fieldLabel}
                validationMessage={!isValid ? invalidMessage : ""}
            >
                {component}
            </Field>

            <Tooltip
                content="Save"
                relationship="label"
            >
                <Button
                    appearance="subtle"
                    style={{ minWidth: 20 }}
                    icon={<SaveRegular />}
                    disabled={oldValue === value || !isValid}
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
                    style={{ minWidth: 20 }}
                    appearance="subtle"
                    icon={<DismissRegular />}
                    onClick={onDismiss}
                />
            </Tooltip>
        </div>
    );
};
