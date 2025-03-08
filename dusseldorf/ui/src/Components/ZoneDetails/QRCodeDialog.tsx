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
    makeStyles,
    ToolbarButton,
    Link
} from "@fluentui/react-components";
import { QrCodeRegular } from "@fluentui/react-icons";
import QRCode from "react-qr-code";

const useStyles = makeStyles({
    dialog: {
        width: "350px"
    }
})

interface QRCodeDialogProps {
    zone: string;
}

export const QRCodeDialog = ({ zone }: QRCodeDialogProps) => {

    const styles = useStyles();

    const zoneLink = `https://${zone}`;

    return (
        <Dialog>
            <DialogTrigger disableButtonEnhancement>
                <ToolbarButton icon={<QrCodeRegular />}>
                    QRCode
                </ToolbarButton>
            </DialogTrigger>
            <DialogSurface className={styles.dialog}>
                <DialogBody className="stack vstack-gap">
                    <DialogTitle>QRCode</DialogTitle>
                    <DialogContent className="stack vstack-gap">
                        <Text style={{paddingBottom: 20}}>
                            Scan this QR code to go to{" "}
                            <Link href={zoneLink} inline>{zoneLink}</Link>
                            .
                        </Text>
                        <QRCode
                            value={zoneLink}
                            size={300}
                        />
                    </DialogContent>
                    <DialogActions>
                        <DialogTrigger disableButtonEnhancement>
                            <Button>Close</Button>
                        </DialogTrigger>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
}
