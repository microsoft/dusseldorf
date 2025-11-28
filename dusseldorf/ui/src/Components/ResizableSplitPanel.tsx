// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { makeStyles } from "@fluentui/react-components";
import { useCallback, useEffect, useRef, useState } from "react";

const useStyles = makeStyles({
    container: {
        display: "flex",
        flexDirection: "row",
        width: "100%",
        height: "100%",
        overflow: "hidden"
    },
    leftPanel: {
        overflow: "auto",
        display: "flex",
        flexDirection: "column"
    },
    rightPanel: {
        overflow: "auto",
        display: "flex",
        flexDirection: "column"
    },
    divider: {
        width: "19px",
        cursor: "col-resize",
        backgroundColor: "transparent",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        userSelect: "none",
        "&:hover": {
            backgroundColor: "var(--colorNeutralBackground1Hover)"
        },
        "&:active": {
            backgroundColor: "var(--colorNeutralBackground1Pressed)"
        }
    },
    dividerLine: {
        width: "1px",
        height: "100%",
        backgroundColor: "var(--colorNeutralStroke2)"
    },
    dragging: {
        cursor: "col-resize",
        userSelect: "none"
    }
});

interface ResizableSplitPanelProps {
    leftPanel: React.ReactNode;
    rightPanel: React.ReactNode;
    initialLeftWidth?: number; // percentage (0-100)
    minLeftWidth?: number; // percentage
    maxLeftWidth?: number; // percentage
}

export const ResizableSplitPanel = ({
    leftPanel,
    rightPanel,
    initialLeftWidth = 48,
    minLeftWidth = 20,
    maxLeftWidth = 80
}: ResizableSplitPanelProps) => {
    const styles = useStyles();
    const containerRef = useRef<HTMLDivElement>(null);
    const [leftWidth, setLeftWidth] = useState(initialLeftWidth);
    const [isDragging, setIsDragging] = useState(false);

    const handleMouseDown = useCallback((e: React.MouseEvent) => {
        e.preventDefault();
        setIsDragging(true);
        document.body.style.cursor = "col-resize";
        document.body.style.userSelect = "none";
    }, []);

    const handleMouseMove = useCallback(
        (e: MouseEvent) => {
            if (!isDragging || !containerRef.current) return;

            const containerRect = containerRef.current.getBoundingClientRect();
            const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
            
            // Constrain within min/max bounds
            const constrainedWidth = Math.min(Math.max(newLeftWidth, minLeftWidth), maxLeftWidth);
            setLeftWidth(constrainedWidth);
        },
        [isDragging, minLeftWidth, maxLeftWidth]
    );

    const handleMouseUp = useCallback(() => {
        setIsDragging(false);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
    }, []);

    useEffect(() => {
        if (isDragging) {
            document.addEventListener("mousemove", handleMouseMove);
            document.addEventListener("mouseup", handleMouseUp);
            
            return () => {
                document.removeEventListener("mousemove", handleMouseMove);
                document.removeEventListener("mouseup", handleMouseUp);
            };
        }
    }, [isDragging, handleMouseMove, handleMouseUp]);

    return (
        <div ref={containerRef} className={styles.container}>
            <div className={styles.leftPanel} style={{ width: `${leftWidth}%` }}>
                {leftPanel}
            </div>
            
            <div className={styles.divider} onMouseDown={handleMouseDown}>
                <div className={styles.dividerLine} />
            </div>
            
            <div 
                className={styles.rightPanel} 
                style={{ width: `${100 - leftWidth}%` }}
            >
                {rightPanel}
            </div>
        </div>
    );
};
