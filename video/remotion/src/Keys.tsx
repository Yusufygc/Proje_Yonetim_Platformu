import React from "react";
import {interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {color, FONT} from "./theme";
import type {Capture} from "./types";

const SHOWN_FRAMES = 40;

// Kısayol ekranda görünmez; izleyici hangi tuşlara basıldığını buradan anlar.
export const Keys: React.FC<{capture: Capture}> = ({capture}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const mark = capture.marks.find((m) => m.kind === "shortcut" && frame >= m.frame - 8 && frame < m.frame + SHOWN_FRAMES);
  if (!mark || mark.kind !== "shortcut") return null;
  const pop = spring({frame: frame - mark.frame + 8, fps, config: {damping: 12}});
  const fade = interpolate(frame, [mark.frame + SHOWN_FRAMES - 10, mark.frame + SHOWN_FRAMES], [1, 0], {extrapolateLeft: "clamp"});

  return (
    <div style={{position: "absolute", left: 0, right: 0, bottom: 150, display: "flex", justifyContent: "center", alignItems: "center", gap: 18, opacity: fade}}>
      {mark.label.split(" + ").map((key) => (
        <div
          key={key}
          style={{
            minWidth: 130,
            padding: "26px 34px",
            textAlign: "center",
            borderRadius: 22,
            background: "linear-gradient(#26324a, #141b2a)",
            border: `2px solid ${color.accent}`,
            borderBottomWidth: 8,
            color: color.text,
            font: `800 56px ${FONT}`,
            boxShadow: "0 30px 80px rgba(0,0,0,0.6)",
            transform: `scale(${pop})`,
          }}
        >
          {key}
        </div>
      ))}
    </div>
  );
};
