import React, {useEffect, useState} from "react";
import {AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame} from "remotion";
import type {Cue} from "./types";

// Uygulamanın koyu slate temasıyla uyumlu renkler.
export const color = {
  bg: "#070A11",
  surface: "#161C29",
  border: "#283247",
  text: "#F4F7FB",
  muted: "#9AA6BA",
  accent: "#3B82F6",
  green: "#10B981",
  amber: "#F59E0B",
  red: "#EF4444",
};

export const FONT = "Jakarta";

const FACES: [string, string][] = [
  ["PlusJakartaSans-Medium.ttf", "500"],
  ["PlusJakartaSans-SemiBold.ttf", "600"],
  ["PlusJakartaSans-ExtraBold.ttf", "800"],
];

export const useFonts = (): void => {
  const [handle] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all(
      FACES.map(async ([file, weight]) => {
        const face = new FontFace(FONT, `url(${staticFile(`generated/${file}`)})`, {weight});
        document.fonts.add(await face.load());
      }),
    ).then(() => continueRender(handle));
  }, [handle]);
};

export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame / 90) * 6;
  return (
    <AbsoluteFill style={{background: color.bg}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(900px 600px at ${22 + drift}% 12%, rgba(59,130,246,0.30), transparent 70%),
            radial-gradient(800px 600px at ${82 - drift}% 90%, rgba(99,102,241,0.22), transparent 70%)`,
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: "radial-gradient(rgba(255,255,255,0.06) 1px, transparent 1px)",
          backgroundSize: "36px 36px",
        }}
      />
    </AbsoluteFill>
  );
};

export const Subtitle: React.FC<{cues: Cue[]}> = ({cues}) => {
  const frame = useCurrentFrame();
  const cue = cues.find((c) => frame >= c.from && frame < c.to);
  if (!cue) return null;
  return (
    <div style={{position: "absolute", left: 0, right: 0, bottom: 30, display: "flex", justifyContent: "center"}}>
      <span
        style={{
          maxWidth: 1500,
          padding: "12px 28px",
          borderRadius: 14,
          background: "rgba(7,10,17,0.82)",
          border: `1px solid ${color.border}`,
          color: color.text,
          font: `500 34px/1.35 ${FONT}`,
          textAlign: "center",
        }}
      >
        {cue.text}
      </span>
    </div>
  );
};
