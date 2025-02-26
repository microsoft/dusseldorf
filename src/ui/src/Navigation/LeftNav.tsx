// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Tooltip, Body1Stronger, Text } from "@fluentui/react-components";
import {
    HomeRegular,
    TargetEditRegular,
    TargetRegular,
    WindowBulletListRegular,
    WindowEditRegular
} from "@fluentui/react-icons";
import {
    Hamburger,
    NavCategory,
    NavCategoryItem,
    NavDrawer,
    NavDrawerBody,
    NavDrawerHeader,
    NavItem,
    NavItemValue,
    NavSectionHeader,
    NavSubItem,
    NavSubItemGroup,
    OnNavItemSelectData
} from "@fluentui/react-nav-preview";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { DusseldorfAPI } from "../DusseldorfApi";
import { CacheHelper } from "../Helpers/CacheHelper";
import { Logger } from "../Helpers/Logger";
import { UiHelper } from "../Helpers/UIHelper";

interface ILeftNavProps {
    refreshToken: () => void;
}

export const LeftNav = ({ refreshToken }: ILeftNavProps) => {
    const navigate = useNavigate();

    // Control nav panel
    const [open, setOpen] = useState<boolean>(true);
    const [openCategories, setOpenCategories] = useState<NavItemValue[]>(["zones"]);
    const [selectedCategoryValue, setSelectedCategoryValue] = useState<string | undefined>();
    const [selectedValue, setSelectedValue] = useState<string>("home");

    // Control zones
    const [zoneLinks, setZoneLinks] = useState<JSX.Element[]>([]);

    // set an interval to check for new zones every 7 seconds
    useEffect(() => {
        refreshZones();
        const interval = setInterval(() => {
            refreshZones();
        }, 7000);
        return () => {
            clearInterval(interval);
        };
    }, []);

    // Fetches an updated list of zones
    const refreshZones = () => {
        DusseldorfAPI.GetZones()
            .then((zones) => {
                CacheHelper.SetZones(zones);
                setZoneLinks(
                    zones
                        .filter((zone) => !UiHelper.IsZoneHidden(zone.fqdn))
                        .slice(0, 13)
                        .map((zone) => (
                            <NavSubItem key={zone.fqdn} value={zone.fqdn}>
                                <Text truncate wrap={false} style={{ overflow: "hidden", width: 200, display: "block" }}>
                                    {zone.fqdn}
                                </Text>
                            </NavSubItem>
                        ))
                        .concat(<NavSubItem key={" "} value=" ">...</NavSubItem>)
                );
            })
            .catch((err) => {
                Logger.Error(err);
                CacheHelper.SetZones([]);
                refreshToken();
            });
    };

    const handleCategoryToggle = (_: Event | React.SyntheticEvent<Element, Event>, data: OnNavItemSelectData) => {
        if (openCategories.includes(data.categoryValue as string)) {
            setOpenCategories([]);
        } else {
            setOpenCategories([data.categoryValue as string]);
        }
    };

    const handleItemSelect = (ev: Event | React.SyntheticEvent<Element, Event>, data: OnNavItemSelectData) => {
        setSelectedCategoryValue(data.categoryValue as string);
        setSelectedValue(data.value as string);
        if (data.value && data.categoryValue) {
            navigate("/" + data.categoryValue + "/" + data.value);
        } else if (data.value) {
            navigate("/" + data.value);
        }
    };

    return (
        <>
            <NavDrawer
                style={{ minWidth: 30, maxWidth: 30, height: "100%" }}
                type={"inline"}
                open={!open}
            >
                <Tooltip
                    content="Navigation"
                    relationship="label"
                >
                    <Hamburger onClick={() => setOpen(!open)} />
                </Tooltip>
            </NavDrawer>
            <NavDrawer
                style={{ minWidth: 200, maxWidth: 200, height: "100%" }}
                onNavCategoryItemToggle={handleCategoryToggle}
                onNavItemSelect={handleItemSelect}
                tabbable={true} // enables keyboard tabbing
                openCategories={openCategories}
                selectedValue={selectedValue}
                selectedCategoryValue={selectedCategoryValue}
                type={"inline"}
                open={open}
                density="small"
            >
                <NavDrawerHeader>
                    <Tooltip
                        content="Navigation"
                        relationship="label"
                    >
                        <Hamburger onClick={() => setOpen(!open)} />
                    </Tooltip>
                </NavDrawerHeader>
                <NavDrawerBody>
                    <NavItem
                        icon={<HomeRegular fontSize={20} />}
                        value="home"
                    >
                        Home
                    </NavItem>
                    <NavSectionHeader>
                        <Body1Stronger>Rule Templates</Body1Stronger>
                    </NavSectionHeader>
                    <NavItem
                        value="templates"
                        icon={<WindowBulletListRegular fontSize={20} />}
                    >
                        About
                    </NavItem>
                    <NavCategory value="templates">
                        <NavCategoryItem icon={<WindowEditRegular fontSize={20} />}>Templates</NavCategoryItem>
                        <NavSubItemGroup>
                            <NavSubItem value="jsalertdom">XSS alert(domain)</NavSubItem>
                            <NavSubItem value="cors">CORS options call</NavSubItem>
                            <NavSubItem value="exfiljs">Exfil DOM using JS</NavSubItem>
                            <NavSubItem value="psimdskeyvault">Powershell IMDS AKV Exfil</NavSubItem>
                            <NavSubItem value="xxeoob">XXE Out of band exfil</NavSubItem>
                            <NavSubItem value="localhost">DNS set to localhost</NavSubItem>
                        </NavSubItemGroup>
                    </NavCategory>
                    <NavSectionHeader>
                        <Body1Stronger>DNS Zones</Body1Stronger>
                    </NavSectionHeader>
                    <NavItem
                        value="zones"
                        icon={<TargetRegular fontSize={20} />}
                    >
                        All Zones
                    </NavItem>
                    <NavCategory value="zones">
                        <NavCategoryItem icon={<TargetEditRegular fontSize={20} />}>Zones</NavCategoryItem>
                        <NavSubItemGroup>{zoneLinks}</NavSubItemGroup>
                    </NavCategory>
                </NavDrawerBody>
            </NavDrawer>
        </>
    );
};
