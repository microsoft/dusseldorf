// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
    Button,
    Checkbox,
    Dialog,
    DialogActions,
    DialogBody,
    DialogContent,
    DialogSurface,
    DialogTitle,
    DialogTrigger,
    makeStyles,
    Text,
    Tooltip
} from "@fluentui/react-components";
import { SettingsRegular } from "@fluentui/react-icons";
import { useState } from "react";

const useStyles = makeStyles({
    columnList: {
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        marginTop: "12px"
    },
    columnItem: {
        display: "flex",
        alignItems: "center",
        gap: "8px"
    }
});

export interface ColumnConfig {
    id: string;
    label: string;
    visible: boolean;
    required?: boolean; // Some columns shouldn't be hideable
}

interface ColumnManagerProps {
    columns: ColumnConfig[];
    onColumnsChange: (columns: ColumnConfig[]) => void;
}

export const ColumnManager = ({ columns, onColumnsChange }: ColumnManagerProps) => {
    const styles = useStyles();
    const [open, setOpen] = useState(false);
    const [localColumns, setLocalColumns] = useState<ColumnConfig[]>(columns);

    const handleColumnToggle = (columnId: string, checked: boolean) => {
        const updatedColumns = localColumns.map(col => 
            col.id === columnId ? { ...col, visible: checked } : col
        );
        setLocalColumns(updatedColumns);
    };

    const handleApply = () => {
        onColumnsChange(localColumns);
        setOpen(false);
    };

    const handleCancel = () => {
        setLocalColumns(columns); // Reset to original state
        setOpen(false);
    };

    const handleReset = () => {
        const resetColumns = columns.map(col => ({ ...col, visible: true }));
        setLocalColumns(resetColumns);
    };

    return (
        <Dialog open={open} onOpenChange={(_, data) => setOpen(data.open)}>
            <DialogTrigger disableButtonEnhancement>
                <Tooltip content="Manage Columns" relationship="label">
                    <Button
                        appearance="subtle"
                        icon={<SettingsRegular />}
                        onClick={() => setOpen(true)}
                    />
                </Tooltip>
            </DialogTrigger>
            
            <DialogSurface>
                <DialogBody>
                    <DialogTitle>Manage Table Columns</DialogTitle>
                    <DialogContent>
                        <Text>Choose which columns to show or hide:</Text>
                        <div className={styles.columnList}>
                            {localColumns.map((column) => (
                                <div key={column.id} className={styles.columnItem}>
                                    <Checkbox
                                        checked={column.visible}
                                        disabled={column.required}
                                        onChange={(_, data) => handleColumnToggle(column.id, data.checked === true)}
                                        label={column.label}
                                    />
                                    {column.required && (
                                        <Text size={200} style={{ fontStyle: "italic", color: "var(--colorNeutralForeground3)" }}>
                                            (required)
                                        </Text>
                                    )}
                                </div>
                            ))}
                        </div>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleReset}>Reset All</Button>
                        <Button onClick={handleCancel}>Cancel</Button>
                        <Button appearance="primary" onClick={handleApply}>Apply</Button>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
};
