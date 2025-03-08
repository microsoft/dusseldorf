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
    Divider,
    Field,
    Input,
    makeStyles,
    MessageBar,
    Subtitle1,
    Text,
    Tooltip
} from "@fluentui/react-components";
import { DeleteRegular, SaveRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";

import { RuleComponents } from "./RuleComponents";
import { DusseldorfAPI } from "../../DusseldorfApi";
import { Logger } from "../../Helpers/Logger";
import { Rule } from "../../Types/Rule";

const useStyles = makeStyles({
    divider: {
        paddingTop: "20px",
        paddingBottom: "20px"
    }
});

interface IRuleDetailsProps {
    rule: Rule | undefined;
    updateSelectedRule: (rule: Rule | undefined) => void;
}

export const RuleDetails = ({ rule, updateSelectedRule }: IRuleDetailsProps) => {
    const styles = useStyles();

    // Control priority field
    const [priority, setPriority] = useState<number | undefined>(rule?.priority);
    const [showPriorityError, setShowPriorityError] = useState<boolean>(false);

    const isValidPriority = (newPriority: number) => {
        return newPriority >= 1 && newPriority <= 999;
    };

    // Control delete dialog
    const [deleteOpen, setDeleteOpen] = useState<boolean>(false);
    const [deleteMessageType, setDeleteMessageType] = useState<"error" | "success" | "warning">("warning");

    // When rule changes, update priority
    useEffect(() => {
        setPriority(rule?.priority);
        setShowPriorityError(false);
    }, [rule]);

    // If there is no rule yet, don't show anything
    if (!rule || !priority) {
        return <div />;
    }

    // If there is a rule, show the details
    return (
        <div>
            {/* Header */}
            <div className="stack vstack-gap">
                <Subtitle1>Rule Details</Subtitle1>

                <div className="stack hstack">
                    <Field
                        label="Priority"
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
                                    // Priority can't have more than 3 digits
                                    setPriority(Number(newPriority.toString().slice(0, 3)));
                                }
                                setShowPriorityError(false);
                            }}
                            onBlur={() => {
                                // Reset invalid priorities back to the correct value
                                if (!isValidPriority(priority)) {
                                    setPriority(rule.priority);
                                    setShowPriorityError(false);
                                }
                            }}
                        />
                    </Field>

                    <Tooltip
                        content="Save rule priority"
                        relationship="label"
                    >
                        <Button
                            appearance="subtle"
                            icon={<SaveRegular />}
                            disabled={priority === rule.priority || !isValidPriority(priority) || showPriorityError}
                            onClick={() => {
                                DusseldorfAPI.UpdateRule(rule, priority)
                                    .then((newRule) => {
                                        updateSelectedRule(newRule);
                                    })
                                    .catch((err) => {
                                        Logger.Error(err);
                                        setShowPriorityError(true);
                                    });
                            }}
                        />
                    </Tooltip>
                </div>

                {showPriorityError && <MessageBar intent="error">Failed to update rule priority.</MessageBar>}
            </div>

            <Divider className={styles.divider} />

            {/* Rule components */}
            <RuleComponents
                rule={rule}
                updateSelectedRule={updateSelectedRule}
            />

            <Divider className={styles.divider} />

            {/* Footer */}
            <Dialog
                open={deleteOpen}
                onOpenChange={(_, data) => {
                    setDeleteOpen(data.open);
                }}
            >
                <DialogTrigger disableButtonEnhancement>
                    <Button
                        icon={<DeleteRegular />}
                        style={{ width: 130 }}
                    >
                        Delete rule
                    </Button>
                </DialogTrigger>
                <DialogSurface style={{ width: 450 }}>
                    <DialogBody>
                        <DialogTitle>Delete this rule?</DialogTitle>
                        <DialogContent
                            className="stack vstack-gap"
                            style={{ wordWrap: "break-word" }}
                        >
                            <Text>
                                Are you sure you want to delete this rule (<strong>{rule?.name}</strong>)?
                            </Text>
                            <MessageBar intent={deleteMessageType}>
                                {deleteMessageType == "error"
                                    ? "There was an error deleting rule."
                                    : deleteMessageType == "success"
                                    ? "Successfully deleted rule."
                                    : "This action cannot be undone."}
                            </MessageBar>
                        </DialogContent>
                        <DialogActions>
                            <Button
                                appearance="primary"
                                disabled={deleteMessageType != "warning"}
                                onClick={() => {
                                    if (rule) {
                                        DusseldorfAPI.DeleteRule(rule)
                                            .then(() => {
                                                Logger.Info(`rule ${rule.ruleid} for ${rule.zone} deleted`);
                                                setDeleteMessageType("success");
                                            })
                                            .catch((err) => {
                                                Logger.Error(err);
                                                setDeleteMessageType("error");
                                            })
                                            .finally(() => {
                                                setTimeout(() => {
                                                    setDeleteOpen(false);
                                                    updateSelectedRule(undefined);
                                                    setDeleteMessageType("warning");
                                                }, 1337);
                                            });
                                    }
                                }}
                            >
                                Delete
                            </Button>
                            <DialogTrigger disableButtonEnhancement>
                                <Button disabled={deleteMessageType != "warning"}>Cancel</Button>
                            </DialogTrigger>
                        </DialogActions>
                    </DialogBody>
                </DialogSurface>
            </Dialog>
        </div>
    );
};
