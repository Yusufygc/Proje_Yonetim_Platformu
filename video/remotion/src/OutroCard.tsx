import React from "react";
import {AbsoluteFill, Img, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {color, FONT} from "./theme";
import type {Scene} from "./types";

export const OutroCard: React.FC<{scene: Scene; link: string; aiNote: string}> = ({scene, link, aiNote}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const rise = (delay: number) => {
    const t = spring({frame: frame - delay, fps, config: {damping: 15}});
    return {opacity: t, transform: `translateY(${(1 - t) * 40}px)`};
  };
  const linkAt = scene.cues[scene.cues.length - 1]?.from ?? 40;

  return (
    <AbsoluteFill style={{alignItems: "center", justifyContent: "center", gap: 28, paddingBottom: 90}}>
      <Img src={staticFile("generated/logo.png")} style={{width: 160, height: 160, filter: "drop-shadow(0 20px 50px rgba(59,130,246,0.5))", ...rise(0)}} />
      <div style={{color: color.text, font: `800 88px ${FONT}`, letterSpacing: -2, ...rise(6)}}>Proje Takip Platformu</div>
      <div style={{color: color.muted, font: `600 42px ${FONT}`, ...rise(12)}}>{scene.title}</div>
      <div
        style={{
          marginTop: 18,
          padding: "22px 44px",
          borderRadius: 18,
          background: color.accent,
          color: "#fff",
          font: `600 36px ${FONT}`,
          boxShadow: "0 24px 70px rgba(59,130,246,0.45)",
          ...rise(linkAt),
        }}
      >
        {link}
      </div>
      <div style={{position: "absolute", right: 36, top: 28, color: color.muted, font: `500 22px ${FONT}`}}>{aiNote}</div>
    </AbsoluteFill>
  );
};
