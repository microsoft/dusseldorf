// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Caption1, Button, Divider, Link, Title2, Text } from "@fluentui/react-components";
import { AddRegular } from "@fluentui/react-icons";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { AddZoneDialog } from "../Components/AddZoneDialog";
import { CacheHelper } from "../Helpers/CacheHelper";
import { HomepageCards } from "../Components/HomepageCards";
import { SuccesBanner } from "../Components/SuccesBanner";
import { Logger } from "../Helpers/Logger";
import { Zone } from "../Types/Zone";
import { DusseldorfAPI } from "../DusseldorfApi";

import "../Styles/Stack.css";

export const HomePage = () => {
    const navigate = useNavigate();

    Logger.PageView("Homepage");

    const [recentZones, setRecentZones] = useState<Zone[]>(CacheHelper.GetZones());

    const [showAddZone, setShowAddZone] = useState<boolean>(false);

    useEffect(() => {
        // get zones, maybe even from cache
        if (recentZones.length > 0) return;

        // setNudge(nudge + 1);
        DusseldorfAPI.GetZones()
            .then((zones) => {
                setRecentZones(zones);
                CacheHelper.SetZones(zones);
            })
            .catch((err) => {
                Logger.Error(err);
                setRecentZones([]);
                CacheHelper.SetZones([]);
            });
    }, []);

    return (
        <div style={{ overflow: "auto", width: "100%", height: "100%", marginRight: 20, marginLeft: 20 }}>
            <div
                className="stack hstack-spread"
                style={{ paddingBottom: "30px" }}
            >
                <div className="stack vstack-gap">
                    <Title2>Project Dusseldorf</Title2>

                    {recentZones.length > 0 ? (
                        <Text>Create a new DNS zone, or open a recent one to pick up where you left off.</Text>
                    ) : (
                        // or
                        <Text>Create a new DNS zone to get started.</Text>
                    )}
                </div>

                <Button
                    icon={<AddRegular />}
                    style={{ maxWidth: 200 }}
                    onClick={() => {
                        setShowAddZone(true);
                    }}
                >
                    Create zone
                </Button>
            </div>

            <HomepageCards
                zones={recentZones}
                onNewClick={() => {
                    setShowAddZone(true);
                }}
                onClick={(zone) => {
                    navigate(`/zones/${zone.fqdn}/requests`);
                }}
            />

            <Divider style={{ paddingTop: 20, paddingBottom: 20 }} />

            <div className="stack vstack-gap">
                <Text>
                    Dusseldorf is a platform for analyzing out-of-band network requests to detect security
                    vulnerabilities at scale. It is intented to help with application security research. 
                    If you are unsure if you should be using this software,
                    please contact your security team or contact us on:{" "}
                    <Link
                        inline
                        href="mailto:dusseldorf@microsoft.com"
                    >
                        dusseldorf@microsoft.com
                    </Link>
                    .
                </Text>

                <Text>
                    This platform is used to automatically detcet and dissect network traffic and iteratively manipulate
                    its responses with custom payloads to ease further analysis and exploitation. This process helps in
                    exploring, researching and exploiting cloud vulnerabilities such as{" "}
                    <abbr title="Server Side Request Forgery">SSRF</abbr>, <abbr title="Cross Site Scripting">XSS</abbr>
                    , <abbr title="eXternal Xml Entities">XXE</abbr> ,{" "}
                    <abbr title="Server Side Template Injection">SSTI</abbr>,{" "}
                    <abbr title="Remote Code Execution">RCE</abbr> etc.
                </Text>

                <div style={{ paddingTop: "10px", paddingBottom: "10px" }}>
                    <SuccesBanner />
                </div>

                <Text>
                    Dusseldorf uses unique <em>zones</em> (in the form of{" "}
                    <abbr title="Fully Qualified Domain Name">FQDN</abbr> subdomains) to determine the routing of
                    network requests. This way, only you can see what's sent to your zones, or you can setup strong{" "}
                    <abbr title="Role Based Access Control">RBAC</abbr> rules to provide granular access to other to
                    collaborate.
                </Text>

                <Text>
                    For more information and information on how to get started, go to{" "}
                    <Link
                        href="https://aka.ms/dusseldorf/docs"
                        inline
                    >
                        https://aka.ms/dusseldorf/docs
                    </Link>
                    .
                </Text>
            </div>

            <Divider style={{ paddingTop: 20, paddingBottom: 20 }} />

            <Caption1>
                <Link
                    inline
                    href="https://go.microsoft.com/fwlink/?LinkId=518021"
                >
                    Privacy notification
                </Link>
            </Caption1>

            <AddZoneDialog
                open={showAddZone}
                onDismiss={() => {
                    // no zones added, stay on home page
                    setShowAddZone(false);
                }}
                onSuccess={(fqdn?: string) => {
                    if (fqdn) {
                        // single zone added, redirect to that zone
                        navigate(`/zones/${fqdn}/requests`);
                    } else {
                        // bulk zones added, redirect to zones page
                        navigate(`/zones`);
                    }
                }}
            />
        </div>
    );
};
