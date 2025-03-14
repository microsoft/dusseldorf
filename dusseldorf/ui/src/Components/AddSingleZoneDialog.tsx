// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { useMsal } from "@azure/msal-react";
import {
    Button,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    Field,
    Input,
    Link,
    MessageBar,
    Select,
    Spinner,
    Text
} from "@fluentui/react-components";
import { AddRegular, BoxMultipleRegular, CheckmarkRegular, DismissRegular } from "@fluentui/react-icons";
import BWFilter from "bad-words";
import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { DomainsContext } from "../App";
import { DusseldorfAPI } from "../DusseldorfApi";
import { Logger } from "../Helpers/Logger";

const DEFAULT_SUBDOMAIN_LENGTH = 12;
const SUBDOMAIN_REGEX = /^[a-z0-9]+([-.][a-z0-9]+)*$/;

/**
 * Generate a random subdomain without checking any availability
 */
const badWordsFilter = new BWFilter();
const generateRandomSubdomain = (): string => {
    let randomSubdomain;
    do {
        randomSubdomain = [...Array<number>(DEFAULT_SUBDOMAIN_LENGTH)]
            .map(() => Math.random().toString(36)[2])
            .join("");
    } while (/^\d/.test(randomSubdomain) || badWordsFilter.isProfane(randomSubdomain)); // If randomSubdomain starts with a number or is profane, run again
    return randomSubdomain;
};

interface AddSingleZoneDialogProps {
    onDismiss: () => void;
    onSuccess: (fqdn?: string) => void;
    open: boolean;
    onSwitch: () => void;
    domain: string;
    setDomain: (domain: string) => void;
}

export const AddSingleZoneDialog = ({
    onDismiss,
    onSuccess,
    open,
    onSwitch,
    domain,
    setDomain
}: AddSingleZoneDialogProps) => {
    const { instance } = useMsal();
    const navigate = useNavigate();

    const domains = useContext(DomainsContext).map((domainOption) => (
        <option
            key={domainOption}
            value={domainOption}
        >
            {domainOption}
        </option>
    ));

    const [subdomain, setSubdomain] = useState<string>("");

    const [isChecking, setIsChecking] = useState<boolean>(false);

    const [subdomainErrorMsg, setSubdomainErrorMsg] = useState<boolean>(false);
    const [errorMsg, setErrorMsg] = useState<boolean>(false);
    const [completeMsg, setCompleteMsg] = useState<boolean>(false);

    const isZoneAvailable = async (_subdomain: string, _domain: string): Promise<boolean> => {
        // Need to have properly formatted subdomain
        if (!_subdomain || !SUBDOMAIN_REGEX.test(_subdomain)) {
            return Promise.resolve(false);
        }

        const zone = `${_subdomain}.${_domain}`;

        // Need to check the API
        return DusseldorfAPI.DoesZoneExist(zone)
            .then((isZoneTaken) => {
                return !isZoneTaken;
            })
            .catch(() => {
                return false;
            });
    };

    const addZone = (_subdomain: string, _domain: string) => {
        DusseldorfAPI.AddZone(_subdomain, _domain, 1)
            .then((success) => {
                if (success) {
                    Logger.Info(`addZone(${_subdomain}, ${_domain}): success`);
                    setCompleteMsg(true);
                    setTimeout(() => {
                        onSuccess(`${_subdomain}.${_domain}`);
                        // redirect to the new zone
                        navigate(`/zones/${_subdomain}.${_domain}`);
                    }, 1337);
                } else {
                    Logger.Info(`addZone(${_subdomain}): error: authz`);
                    setErrorMsg(true);
                }
            })
            .catch((err) => {
                Logger.Error(err);
                setErrorMsg(true);
            });
    };

    // Automatically check zone availability
    useEffect(() => {
        setIsChecking(true);
        isZoneAvailable(subdomain, domain)
            .then((isZoneAvailable) => {
                if (isZoneAvailable) {
                    setSubdomainErrorMsg(false);
                } else {
                    setSubdomainErrorMsg(true);
                }
            })
            .catch(() => {
                setSubdomainErrorMsg(true);
            })
            .finally(() => {
                setIsChecking(false);
            });
    }, [subdomain, domain]);

    useEffect(() => {
        if (open && subdomain.length == 0) {
            const account = instance.getActiveAccount();
            const upn = account?.username.split("@")[0] ?? "";
            
            const numSubStr = Math.floor(Math.random() * 1000)
            .toString()
            .padStart(3, "0");
            // remove the dots from the upn, so we don't create a foo.bar000 zone by by accident.
            const upnSubstr = upn.substring(0, DEFAULT_SUBDOMAIN_LENGTH - 3).replace(/\./g, "");

            setSubdomain(upnSubstr + numSubStr);
        }
    }, [open]);

    return (
        <Dialog
            open={open}
            onOpenChange={(_, data) => {
                if (data.type == "backdropClick" || data.type == "escapeKeyDown") {
                    onDismiss();
                }
            }}
        >
            <DialogSurface style={{ width: 480 }}>
                <DialogBody>
                    <DialogTitle>Create a DNS Zone</DialogTitle>
                    <DialogContent className="stack vstack-gap">
                        <Text>Choose a desired zone name; it cannot already be taken.</Text>
                        <div className="stack hstack-center">
                            <Field
                                validationMessage={
                                    !isChecking && subdomainErrorMsg ? "This zone is already taken." : ""
                                }
                                validationState={!isChecking && subdomainErrorMsg ? "warning" : "none"}
                            >
                                <Input
                                    style={{ width: 140 }}
                                    value={subdomain}
                                    onChange={(_, data) => {
                                        setErrorMsg(false);
                                        setSubdomain(data.value);
                                    }}
                                />
                            </Field>
                            <Text style={{ paddingLeft: "3px", paddingRight: "3px" }}>.</Text>
                            <Select
                                style={{ width: 140 }}
                                value={domain}
                                onChange={(_, data) => {
                                    setErrorMsg(false);
                                    setDomain(data.value);
                                }}
                            >
                                {domains}
                            </Select>
                            <div style={{ paddingLeft: 10 }}>
                                {isChecking && (
                                    <Spinner
                                        size="extra-tiny"
                                        title="Checking for availability"
                                    />
                                )}
                                {!isChecking && !errorMsg && <CheckmarkRegular />}
                            </div>
                        </div>

                        <Link
                            title="Generate a random zone"
                            onClick={() => {
                                setSubdomain(generateRandomSubdomain());
                            }}
                        >
                            <BoxMultipleRegular /> Generate a random zone
                        </Link>

                        <Link
                            onClick={() => {
                                onSwitch();
                            }}
                            title="Bulk create zones"
                            style={{ paddingTop: "10px" }}
                        >
                            Bulk create &raquo;
                        </Link>

                        {errorMsg && <MessageBar intent="error">Failed to add zone.</MessageBar>}

                        {completeMsg && <MessageBar intent="success">Zone successfully added.</MessageBar>}
                    </DialogContent>

                    <DialogActions>
                        <Button
                            style={{ width: 120 }}
                            appearance="primary"
                            icon={<AddRegular />}
                            disabled={errorMsg || isChecking || subdomainErrorMsg}
                            onClick={() => {
                                addZone(subdomain, domain);
                            }}
                        >
                            Add zone
                        </Button>
                        <Button
                            icon={<DismissRegular />}
                            onClick={onDismiss}
                        >
                            Close
                        </Button>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
};
