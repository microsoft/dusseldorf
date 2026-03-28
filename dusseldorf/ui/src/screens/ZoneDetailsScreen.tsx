// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Button, Divider, makeStyles, Title2, Toolbar, ToolbarButton, ToolbarDivider, Tooltip } from "@fluentui/react-components";
import { ListRegular, StarFilled, StarRegular, TaskListLtrRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { RequestsScreen } from "./RequestsScreen";
import { RulesScreen } from "./RulesScreen";
import { AuthDialog } from "../Components/ZoneDetails/AuthDialog";
import { DeleteZoneDialog } from "../Components/ZoneDetails/DeleteZoneDialog";
import { QRCodeDialog } from "../Components/ZoneDetails/QRCodeDialog";
import { OpenInNewTabButton } from "../Components/OpenInNewTabButton";
import { CopyButton } from "../Components/CopyButton";
import { UiHelper } from "../Helpers/UIHelper";

const useStyles = makeStyles({
    root: {
        padding: "20px",
        width: "100%",
        minWidth: "500px",
        overflowX: "hidden"
    },
    header: {
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
        alignItems: "center",
        width: "100%"
    },
    divider: {
        paddingTop: "10px",
        paddingBottom: "10px"
    }
});

interface ZoneDetailsScreenProps {
    showRules?: boolean;
}

export const ZoneDetailsScreen = ({ showRules = false }: ZoneDetailsScreenProps) => {
    const { zone } = useParams();

    const navigate = useNavigate();
    const styles = useStyles();
    const [isFavorite, setIsFavorite] = useState<boolean>(false);

    // TODO: We should never be routed here without a zone, but need to check zone is valid
    if (!zone) {
        return <Navigate to="/zones" />;
    }

    useEffect(() => {
        setIsFavorite(UiHelper.IsFavoriteZone(zone));
    }, [zone]);

    return (
        <div className={styles.root}>
            <div className={styles.header}>
                <Title2
                    title={zone}
                    truncate
                    style={{ display: "block", maxWidth: "50%", overflow: "hidden" }}
                >
                    {zone}
                </Title2>

                <CopyButton text={zone} />

                <OpenInNewTabButton url={zone} />

                <Tooltip
                    content={isFavorite ? "Unfavorite zone" : "Favorite zone"}
                    relationship="label"
                >
                    <Button
                        appearance="subtle"
                        icon={isFavorite ? <StarFilled color="#f0b429" /> : <StarRegular />}
                        onClick={() => {
                            UiHelper.ToggleFavoriteZone(zone);
                            setIsFavorite(UiHelper.IsFavoriteZone(zone));
                        }}
                    />
                </Tooltip>

                <Toolbar>
                    <ToolbarButton
                        icon={<ListRegular />}
                        disabled={!showRules}
                        onClick={() => {
                            navigate(`/zones/${zone}/requests`);
                        }}
                    >
                        Requests
                    </ToolbarButton>
                    <ToolbarButton
                        icon={<TaskListLtrRegular />}
                        disabled={showRules}
                        onClick={() => {
                            navigate(`/zones/${zone}/rules`);
                        }}
                    >
                        Rules
                    </ToolbarButton>

                    <ToolbarDivider />

                    <AuthDialog zone={zone} />
                    <DeleteZoneDialog zone={zone} />
                    <QRCodeDialog zone={zone} />
                </Toolbar>
            </div>

            <Divider className={styles.divider} />

            <div>
                {
                    showRules ? (
                        <RulesScreen zone={zone} />
                    ) : (
                        <RequestsScreen zone={zone} />
                    )
                }
            </div>
        </div>
    );
};
