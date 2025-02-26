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
    makeStyles,
    MessageBar,
    MessageBarBody,
    Select,
    Text
} from "@fluentui/react-components";
import { ArrowUploadRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { DusseldorfAPI } from "../../DusseldorfApi";
import { CacheHelper } from "../../Helpers/CacheHelper";
import { Logger } from "../../Helpers/Logger";
import { NewRule } from "../../Helpers/Types";
import { Zone } from "../../Types/Zone";

const useStyles = makeStyles({
    button: {
        width: "150px"
    },
    surface: {
        width: "400px"
    }
});

interface CreateAsRuleProps {
    rules: NewRule[];
}

//!TODO: implement error handling
export const CreateAsRuleDialog = ({ rules }: CreateAsRuleProps): JSX.Element => {

    const styles = useStyles();
    const navigate = useNavigate();

    // Control dialog
    const [open, setOpen] = useState<boolean>(false);
    const [newRules, setNewRules] = useState<NewRule[]>(rules);

    // Control zones dropdown
    const [zones] = useState<Zone[]>(CacheHelper.GetZones().sort((a, b) => a.fqdn.localeCompare(b.fqdn)));
    const [fqdn, setFqdn] = useState<string>(zones[0]?.fqdn ?? "");

    // Control message bars
    const [showWarning, setShowWarning] = useState<boolean>(false);
    const [showAdded, setShowAdded] = useState<boolean>(false);

    useEffect(() => {
        setNewRules(rules);
    }, [rules]);

    useEffect(() => {
        DusseldorfAPI.GetRules(fqdn)
            .then(rules => {
                setShowWarning(rules.length > 0);
            })
            .catch(err => {
                Logger.Error(err);
                setShowWarning(false);
            });
    }, [fqdn]);

    const addNewRules = (): void => {
        for (const newRule of newRules) {
            DusseldorfAPI.AddRule(fqdn, newRule.networkprotocol, newRule.priority, newRule.name)
                .then(rule => {
                    newRule.rulecomponents?.forEach(newComponent => {
                        DusseldorfAPI.AddRuleComponent(rule, newComponent)
                            .catch(err => {
                                throw err;
                            });
                    });
                })
                .catch(err => {
                    Logger.Error(err);
                });
        };
    };

    return (
        <Dialog
            onOpenChange={(_, data) => setOpen(data.open)}
            open={open}
        >
            <DialogTrigger disableButtonEnhancement>
                <Button
                    appearance="primary"
                    className={styles.button}
                    disabled={newRules.length === 0}
                    icon={<ArrowUploadRegular />}
                >
                    Create as Rule
                </Button>
            </DialogTrigger>
            <DialogSurface className={styles.surface}>
                <DialogBody>
                    <DialogTitle>Create as Rule</DialogTitle>
                    <DialogContent className="stack vstack-gap">
                        <Text>
                            Create a rule based on this template as a rule for the zone below:
                        </Text>

                        <Select
                            disabled={showAdded}
                            onChange={(_, data) => {
                                setFqdn(data.value);
                            }}
                            value={fqdn}
                        >
                            {zones.map(zone => <option>{zone.fqdn}</option>)}
                        </Select>

                        {
                            showWarning &&
                            <MessageBar>
                                <MessageBarBody>
                                    This will merge with existing rules on <b>{fqdn}</b>.
                                </MessageBarBody>
                            </MessageBar>
                        }

                        {
                            showAdded &&
                            <MessageBar intent="success">
                                <MessageBarBody>
                                    Rule added to <b>{fqdn}</b>.
                                </MessageBarBody>
                            </MessageBar>
                        }
                    </DialogContent>
                    <DialogActions>
                        <Button
                            appearance="primary"
                            disabled={!fqdn || newRules.length === 0 || showAdded}
                            onClick={() => {
                                // disables all dialog actions
                                setShowAdded(true);

                                addNewRules();

                                setTimeout(() => {
                                    setShowAdded(false);
                                    setOpen(false);
                                    navigate("/zones/" + fqdn + "/rules");
                                }, 1337);
                            }}
                        >
                            Create
                        </Button>
                        <DialogTrigger disableButtonEnhancement>
                            <Button
                                appearance="secondary"
                                disabled={showAdded}
                            >
                                Cancel
                            </Button>
                        </DialogTrigger>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
}
