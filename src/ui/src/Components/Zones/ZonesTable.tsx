// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Body1Strong,
    Button,
    Caption1,
    createTableColumn,
    DataGrid,
    DataGridBody,
    DataGridCell,
    DataGridHeader,
    DataGridHeaderCell,
    DataGridRow,
    makeStyles,
    TableColumnDefinition,
    tokens,
    Tooltip
} from "@fluentui/react-components";
import { EyeOffRegular, EyeRegular } from "@fluentui/react-icons";
import { useNavigate } from 'react-router-dom';

import { UiHelper } from '../../Helpers/UIHelper';
import { Zone } from '../../Types/Zone';

const useStyles = makeStyles({
    fqdnColumn: {
        minWidth: "250px",
        maxWidth: "250px",
        wordWrap: "break-word"
    },
    domainColumn: {
        minWidth: "100px",
        maxWidth: "100px",
        wordWrap: "break-word"
    },
    actionsColumn: {
        minWidth: "90px",
        maxWidth: "90px"
    }
});

interface ZonesTableProps {
    refreshZones: () => void,
    zones: Zone[]
}

export const ZonesTable = ({ refreshZones, zones }: ZonesTableProps) => {

    const styles = useStyles();
    const navigate = useNavigate();

    const columns: TableColumnDefinition<Zone>[] = [
        createTableColumn<Zone>({
            columnId: "fqdnColumn",
            compare: (zoneA, zoneB) => {
                return zoneA.fqdn.localeCompare(zoneB.fqdn);
            },
            renderHeaderCell: () => {
                return (
                    <Body1Strong className={styles.fqdnColumn}>
                        FQDN
                    </Body1Strong>
                );
            },
            renderCell: (zone) => {
                return (
                    <DataGridCell className={styles.fqdnColumn}>
                        <Caption1>
                            {zone.fqdn.replace("." + zone.domain, "")}
                        </Caption1>
                        <Caption1 style={{ color: tokens.colorNeutralForeground4 }}>
                            .{zone.domain}
                        </Caption1>
                    </DataGridCell>
                );
            }
        }),
        createTableColumn<Zone>({
            columnId: "domainColumn",
            compare: (zoneA, zoneB) => {
                return zoneA.domain.localeCompare(zoneB.domain);
            },
            renderHeaderCell: () => {
                return (
                    <Body1Strong className={styles.domainColumn}>
                        Domain
                    </Body1Strong>
                );
            },
            renderCell: (zone) => {
                return (
                    <DataGridCell className={styles.domainColumn}>
                        <Caption1>
                            {zone.domain}
                        </Caption1>
                    </DataGridCell>
                );
            }
        }),
        createTableColumn<Zone>({
            columnId: "actionsColumn",
            renderHeaderCell: () => {
                return (
                    <Body1Strong className={styles.actionsColumn}>
                        Actions
                    </Body1Strong>
                );
            },
            renderCell: (zone) => {
                return (
                    <DataGridCell style={{ paddingLeft: 5, paddingRight: 5 }}>
                        <Button onClick={() => {
                            navigate(zone.fqdn);
                        }}>
                            Details &raquo;
                        </Button>
                    </DataGridCell>
                );
            }
        }),
        createTableColumn<Zone>({
            columnId: "hideColumn",
            compare: (zoneA, zoneB) => {
                const hiddenA = UiHelper.IsZoneHidden(zoneA.fqdn);
                const hiddenB = UiHelper.IsZoneHidden(zoneB.fqdn);
                if (hiddenA && hiddenB) {
                    return 0;
                } else if (hiddenB) {
                    return -1;
                } else {
                    return 1;
                }
            },
            renderHeaderCell: () => {
                return <Body1Strong>Hide</Body1Strong>;
            },
            renderCell: (zone) => {
                const hidden = UiHelper.IsZoneHidden(zone.fqdn);
                return (
                    <DataGridCell style={{ paddingLeft: 5, paddingRight: 5 }}>
                        <Tooltip content={`Hide/unhide ${zone.fqdn}`} relationship="label">
                            <Button
                                appearance="transparent"
                                icon={hidden ? <EyeOffRegular /> : <EyeRegular />}
                                onClick={() => {
                                    UiHelper.ToggleZone(zone.fqdn);
                                    refreshZones();
                                }}
                            />
                        </Tooltip>
                    </DataGridCell>
                );
            }
        })
    ];

    return (
        <DataGrid
            items={zones}
            columns={columns}
            sortable
            noNativeElements={false}
            style={{ tableLayout: "auto" }}
        >
            <DataGridHeader>
                <DataGridRow>
                    {({ renderHeaderCell }) => (
                        <DataGridHeaderCell>{renderHeaderCell()}</DataGridHeaderCell>
                    )}
                </DataGridRow>
            </DataGridHeader>
            <DataGridBody<Zone>>
                {({ item }) => (
                    <DataGridRow<Zone>>
                        {({ renderCell }) => (
                            renderCell(item)
                        )}
                    </DataGridRow>
                )}
            </DataGridBody>
        </DataGrid>
    );
} 
