// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Button,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    DialogTrigger,
    Field,
    Input,
    MessageBar,
    Select,
    Text
} from "@fluentui/react-components";
import { AddRegular, DismissRegular, SaveRegular } from "@fluentui/react-icons";
import { useState } from "react";

import { DusseldorfAPI } from "../../DusseldorfApi";
import { Logger } from "../../Helpers/Logger";
import { Rule } from "../../Types/Rule";

interface AddRuleDialogProps {
    zone: string;
    onSave: (rule: Rule) => void;
}

export const AddRuleDialog = ({ zone, onSave }: AddRuleDialogProps) => {
    // Control the dialog
    const [open, setOpen] = useState<boolean>(false);
    const [showMsg, setShowMsg] = useState<"error" | "success" | "info">("info");

    // Control the new rule properties
    const [priority, setPriority] = useState<number>(1);
    const [protocol, setProtocol] = useState<string>("http");
    const [ruleName, setRuleName] = useState<string>("");

    const isValidPriority = (newPriority: number) => {
        return newPriority >= 1 && newPriority <= 999;
    };

    return (
        <Dialog
            open={open}
            onOpenChange={(_, data) => {
                setOpen(data.open);
                setShowMsg("info");
                setPriority(1);
                setProtocol("http");
                setRuleName("");
            }}
        >
            <DialogTrigger disableButtonEnhancement>
                <Button
                    appearance="primary"
                    icon={<AddRegular />}
                    style={{ width: 110 }}
                >
                    Add rule
                </Button>
            </DialogTrigger>
            <DialogSurface>
                <DialogBody>
                    <DialogTitle style={{ wordWrap: "break-word" }}>
                        Add a Rule to Zone (<strong>{zone}</strong>)
                    </DialogTitle>
                    <DialogContent>
                        <div
                            className="stack hstack-gap"
                            style={{ alignItems: "start" }}
                        >
                            <Field
                                label="Protocol"
                                required
                            >
                                <Select
                                    value={protocol}
                                    onChange={(_, data) => {
                                        setProtocol(data.value);
                                    }}
                                >
                                    <option>dns</option>
                                    <option>http</option>
                                </Select>
                            </Field>

                            <Field
                                label="Priority"
                                required
                                validationMessage={"Must be between 1 - 999"}
                                validationState={isValidPriority(priority) ? "none" : "error"}
                            >
                                <Input
                                    value={isNaN(priority) ? "" : priority.toString()}
                                    onChange={(_, data) => {
                                        const newPriority = parseInt(data.value);
                                        if (isNaN(newPriority)) {
                                            setPriority(NaN);
                                        } else {
                                            setPriority(Number(newPriority.toString().slice(0, 3)));
                                        }
                                    }}
                                    onBlur={() => {
                                        if (!isValidPriority(priority)) {
                                            setPriority(1);
                                        }
                                    }}
                                />
                            </Field>

                            <Field
                                label="Rule Name (optional)"
                                hint="An descriptive rule name"
                            >
                                <Input
                                    value={ruleName}
                                    onChange={(_, data) => {
                                        setRuleName(data.value);
                                    }}
                                />
                            </Field>
                        </div>
                        <MessageBar
                            intent={showMsg}
                            style={{ marginTop: 20 }}
                        >
                            {showMsg == "info" ? (
                                <Text>
                                    After a new zone is created, you can add various components to it. This allows you
                                    to filter requests based on certain criteria or craft your own responses.
                                </Text>
                            ) : showMsg == "error" ? (
                                <Text>Failed to add rule to zone.</Text>
                            ) : (
                                <Text>Successfully added rule to zone.</Text>
                            )}
                        </MessageBar>
                    </DialogContent>
                    <DialogActions>
                        <Button
                            appearance="primary"
                            icon={<SaveRegular />}
                            disabled={!isValidPriority(priority) || showMsg != "info"}
                            onClick={() => {
                                DusseldorfAPI.AddRule(zone, protocol, priority, ruleName)
                                    .then((newRule) => {
                                        setShowMsg("success");
                                        onSave(newRule);
                                    })
                                    .catch((err) => {
                                        Logger.Error(err);
                                        setShowMsg("error");
                                    })
                                    .finally(() => {
                                        setTimeout(() => {
                                            setOpen(false);
                                        }, 1000);
                                    });
                            }}
                        >
                            Create rule
                        </Button>
                        <DialogTrigger disableButtonEnhancement>
                            <Button
                                icon={<DismissRegular />}
                                disabled={showMsg != "info"}
                            >
                                Cancel
                            </Button>
                        </DialogTrigger>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
};
