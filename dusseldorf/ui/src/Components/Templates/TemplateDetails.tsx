// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { Link, makeStyles, MessageBar, Subtitle1, Text, Textarea } from "@fluentui/react-components";
import { dump, YAMLException } from "js-yaml";
import { useEffect, useState } from "react";

import { CreateAsRuleDialog } from "./CreateAsRuleDialog";
import { YamlHelper } from "../../Helpers/YamlHelper";
import { NewRule } from "../../Types/Rule";
import { Template } from "../../Types/Template";

const useStyles = makeStyles({
    textarea: {
        minHeight: "250px"
    }
});

interface ITemplateDetailsProps {
    template?: Template;
}

export const TemplateDetails = ({ template }: ITemplateDetailsProps): JSX.Element => {
    const styles = useStyles();

    const [activeTemplate, setActiveTemplate] = useState<Template | undefined>(template);
    const [payload, setPayload] = useState<string>(template ? dump(template.rules) : "");
    const [payloadErrorMsg, setPayloadErrorMsg] = useState<string>("");
    const [payloadRules, setPayloadRules] = useState<NewRule[]>([]);

    const parseTemplateRules = (newPayload: string): void => {
        try {
            const rules = YamlHelper.ParseToRules(newPayload);

            if (rules.length === 0) {
                setPayloadRules([]);
                setPayloadErrorMsg("No rules found in payload");
            } else {
                setPayloadRules(rules);
                setPayloadErrorMsg("");
            }
        } catch (ex) {
            setPayloadRules([]);
            if (ex instanceof YAMLException) {
                setPayloadErrorMsg(`Parsing Error on (${ex.mark.line}:${ex.mark.column}): ${ex.reason}`);
            } else if (ex instanceof Error) {
                setPayloadErrorMsg(ex.message);
            } else {
                setPayloadErrorMsg("Parsing Error");
            }
        }
    };

    useEffect(() => {
        setActiveTemplate(template);
        const newPayload = template ? dump(template.rules) : "";
        setPayload(newPayload);
        parseTemplateRules(newPayload);
    }, [template]);

    if (activeTemplate) {
        return (
            <div className="stack vstack-gap">
                <Subtitle1>{activeTemplate.title}</Subtitle1>

                <Text>{activeTemplate.description}</Text>

                <Textarea
                    className={styles.textarea}
                    textarea={{ style: { fontFamily: "monospace" } }}
                    onChange={(_, data) => {
                        setPayload(data.value);
                        parseTemplateRules(data.value);
                    }}
                    spellCheck={false}
                    value={payload}
                />

                {payloadErrorMsg && <MessageBar intent="error">{payloadErrorMsg}</MessageBar>}

                <CreateAsRuleDialog rules={payloadRules} />
            </div>
        );
    } else {
        return (
            <div className="stack vstack-gap">
                <Text>Templates make up one or more rules that can be applied to a zone.</Text>

                <Text>
                    For more information on how to use templates, please see the documentation on{" "}
                    <Link
                        href="https://github.com/microsoft/dusseldorf"
                        inline
                    >
                        https://github.com/microsoft/dusseldorf
                    </Link>
                    .
                </Text>
            </div>
        );
    }
};
