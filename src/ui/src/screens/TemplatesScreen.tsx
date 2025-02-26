// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { MessageBar, Text, Title2 } from "@fluentui/react-components";
import { load } from "js-yaml";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { TemplateDetails } from "../Components/Templates/TemplateDetails";
import {
    CORSOptionsCall,
    DNSSetToLocalhost,
    JSAlertDomain,
    KeyVaultTokenExfil,
    XssExfilCall,
    XXEOOBCall
} from "../Components/Templates/TemplateStrings";
import { Template } from "../Helpers/Types";

const templateDictionary: Record<string, string> = {
    jsalertdom: JSAlertDomain,
    cors: CORSOptionsCall,
    exfiljs: XssExfilCall,
    psimdskeyvault: KeyVaultTokenExfil,
    xxeoob: XXEOOBCall,
    localhost: DNSSetToLocalhost
};

export const TemplatesScreen = () => {
    const { template } = useParams();

    const [templateKey, setTemplateKey] = useState<string>();
    const [activeTemplate, setActiveTemplate] = useState<Template | undefined>();

    useEffect(() => {
        if (template) {
            const templateString = templateDictionary[template];
            if (templateString) {
                setTemplateKey(template);
                setActiveTemplate(load(templateString) as Template);
                return;
            }
        }
        setTemplateKey("all");
        setActiveTemplate(undefined);
    }, [template]);

    useEffect(() => {
        if (templateKey) {
            const templateString = templateDictionary[templateKey];
            if (templateString) {
                setActiveTemplate(load(templateString) as Template);
                return;
            }
        }
        setActiveTemplate(undefined);
    }, [templateKey]);

    return (
        <div className="stack stack-screen vstack-gap" style={{ marginLeft: 20 }}>
            <Title2>Templates</Title2>

            <Text>
                Dusseldorf comes with several pre-installed internal and community-driven security payloads to aid in
                making customized responses. These templates can be used to craft a better response and allow an
                operator to chain several attack payloads, providing a better exploitation chain.
            </Text>

            <MessageBar>Templates are still experimental and may not work as expected.</MessageBar>

            <TemplateDetails template={activeTemplate} />
        </div>
    );
};
