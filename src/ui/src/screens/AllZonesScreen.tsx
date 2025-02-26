// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.


import { Body1Strong, Input, Title2, Toolbar, ToolbarButton } from "@fluentui/react-components";
import { AddRegular, ArrowCounterclockwiseRegular } from "@fluentui/react-icons";
import { useEffect, useState } from 'react';

import { ZonesTable } from '../Components/Zones/ZonesTable';
import { DusseldorfAPI } from '../DusseldorfApi';
import { CacheHelper } from '../Helpers/CacheHelper';
import { Logger } from '../Helpers/Logger';
import { Zone } from '../Types/Zone';
import { AddZoneDialog } from "../Components/AddZoneDialog";

export const AllZonesScreen = () => {

    Logger.PageView("AllZones");

    const [allZones, setAllZones] = useState<Zone[]>(CacheHelper.GetZones()); // full set
    const [zones, setZones] = useState<Zone[]>(allZones);
    const [filter, setFilter] = useState<string>("");

    const [showAddZone, setShowAddZone] = useState<boolean>(false);

    const refreshZones = () => {
        DusseldorfAPI.GetZones().then(zones => {
            setAllZones(zones);
            CacheHelper.SetZones(zones);
        }).catch(err => {
            Logger.Error(err);
            setAllZones([]);
            CacheHelper.SetZones([]);
        });
    };

    useEffect(() => {
        refreshZones();
    }, []);

    // when filter or zones change, update the list of zones
    useEffect(() => {
        if (filter === "") {
            setZones(allZones);
        } else {
            setZones(allZones.filter(z => z.fqdn.includes(filter)));
        }
    }, [filter, allZones]);

    return (
        <div className='stack vstack-gap' style={{ overflow: "auto", width: "100%", height: "100%", marginRight: 20, marginLeft: 20 }}>
            <div className='stack hstack' style={{ marginBottom: '10px' }}>
                <Title2>Zones</Title2>

                <Toolbar style={{ marginLeft: 20 }}>
                    <ToolbarButton
                        icon={<ArrowCounterclockwiseRegular />}
                        onClick={refreshZones}
                    >
                        Refresh
                    </ToolbarButton>
                    <ToolbarButton
                        icon={<AddRegular />}
                        onClick={() => {
                            setShowAddZone(true);
                        }}
                    >
                        Create zone(s)
                    </ToolbarButton>
                </Toolbar>
            </div>

            <div className="stack vstack">
                <Body1Strong>Filter by FQDN</Body1Strong>
                <Input
                    value={filter}
                    onChange={(_, data) => {
                        setFilter(data.value);
                    }}
                    style={{width: 300}}
                />
            </div>

            <ZonesTable refreshZones={refreshZones} zones={zones}/>

            <AddZoneDialog
                    open={showAddZone}
                    onDismiss={() => {
                        // no zones added, stay on home page
                        setShowAddZone(false);
                    }}
                    onSuccess={(_?: string) => {
                        // don't redirect, we are intentionally editing zones
                        setShowAddZone(false);
                    }}
                />
        </div>
    );
}  