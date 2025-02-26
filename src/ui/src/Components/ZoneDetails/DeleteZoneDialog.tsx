// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Button,
    Text,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    DialogTrigger,
    MessageBar,
    makeStyles,
    ToolbarButton,
    Checkbox
} from "@fluentui/react-components";
import { DeleteRegular } from "@fluentui/react-icons";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { DusseldorfAPI } from "../../DusseldorfApi";
import { Logger } from "../../Helpers/Logger";

const useStyles = makeStyles({
    dialog: {
        width: "500px"
    }
})

interface DeleteZoneDialogProps {
    zone: string;
}

export const DeleteZoneDialog = ({ zone }: DeleteZoneDialogProps) => {

    const styles = useStyles();
    const navigate = useNavigate();

    const [open, setOpen] = useState<boolean>(false);

    const [confirmDelete, setConfirmDelete] = useState<boolean>(false);
    const [showDeleted, setShowDeleted] = useState<boolean>(false);

    return (
        <Dialog
            onOpenChange={(_, data) => setOpen(data.open)}
            open={open}
        >
            <DialogTrigger disableButtonEnhancement>
                <ToolbarButton icon={<DeleteRegular />} style={{ width: 140 }}>
                    Delete Zone
                </ToolbarButton>
            </DialogTrigger>
            <DialogSurface className={styles.dialog}>
                <DialogBody>
                    <DialogTitle>Confirm deleting zone?</DialogTitle>
                    <DialogContent className="stack vstack-gap">
                        <div className='stack'>
                            <Text>
                                Do you want to remove the following <strong> zone </strong>:
                            </Text>

                            <Text style={{ paddingLeft: 20 }}>
                                <pre>{zone}</pre>
                            </Text>

                            <Text>
                                This will remove all requests, responses, and rules.
                            </Text>
                        </div>

                        <MessageBar intent="warning">
                            This action cannot be undone.
                        </MessageBar>

                        <Checkbox
                            label="I understand that this will permanently delete the zone and all of its data."
                            onChange={(_, data) => {
                                if (data.checked === true) {
                                    setConfirmDelete(true);
                                } else {
                                    setConfirmDelete(false);
                                }
                            }}
                        />
                        
                        {
                            showDeleted &&
                            <MessageBar intent="success">
                                Successfully deleted zone.
                            </MessageBar>
                        }
                    </DialogContent>
                    <DialogActions>
                        <Button
                            appearance="primary"
                            disabled={showDeleted || !confirmDelete}
                            onClick={() => {
                                setShowDeleted(true);

                                DusseldorfAPI.DeleteZone(zone)
                                    .catch(err => {
                                        Logger.Error(err);
                                    })

                                setTimeout(() => {
                                    setShowDeleted(false);
                                    setOpen(false);
                                    navigate("/zones");
                                }, 1337);
                            }}
                        >
                            Permanently Delete Zone
                        </Button>
                        <DialogTrigger disableButtonEnhancement>
                            <Button onClick={() => { setConfirmDelete(false); }}>
                                Close
                            </Button>
                        </DialogTrigger>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
}
