import React from "react";
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {color, FONT} from "./theme";
import type {Scene} from "./types";

type Chip = {text: string; tag: string; tone: string; x: number; y: number; angle: number};

// Dağınıklığı anlatan kartlar; metinler örnek verideki başlıklardır.
const CHIPS: Chip[] = [
  {text: "Tablet görünümü", tag: "Fikir", tone: color.amber, x: -690, y: -330, angle: -9},
  {text: "Beta kullanıcı testleri", tag: "Görev", tone: color.accent, x: 560, y: -360, angle: 7},
  {text: "Sürüm planı", tag: "Not", tone: color.green, x: -760, y: 40, angle: 6},
  {text: "Bildirim izin akışı", tag: "Engellendi", tone: color.red, x: 690, y: 20, angle: -6},
  {text: "Harcama kategorisi tahmini", tag: "Fikir", tone: color.amber, x: -520, y: 340, angle: -5},
  {text: "Hesap özeti ekranı", tag: "Görev", tone: color.accent, x: 540, y: 330, angle: 9},
];

const Chips: React.FC<{gatherAt: number}> = ({gatherAt}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <>
      {CHIPS.map((chip, index) => {
        const drop = spring({frame: frame - index * 5, fps, config: {damping: 14}});
        const gather = spring({frame: frame - gatherAt - index * 2, fps, config: {damping: 20}});
        const float = Math.sin(frame / 18 + index) * 8;
        return (
          <div
            key={chip.text}
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              transform: `translate(-50%, -50%) translate(${chip.x * (1 - gather)}px, ${(chip.y + float - (1 - drop) * 220) * (1 - gather)}px) rotate(${chip.angle * (1 - gather)}deg) scale(${1 - gather * 0.7})`,
              opacity: drop * (1 - gather),
              padding: "18px 26px",
              borderRadius: 16,
              background: color.surface,
              border: `1px solid ${color.border}`,
              boxShadow: "0 24px 60px rgba(0,0,0,0.5)",
              whiteSpace: "nowrap",
            }}
          >
            <div style={{color: chip.tone, font: `600 20px ${FONT}`, marginBottom: 6}}>● {chip.tag}</div>
            <div style={{color: color.text, font: `600 30px ${FONT}`}}>{chip.text}</div>
          </div>
        );
      })}
    </>
  );
};

const Words: React.FC<{text: string; start: number; size: number; tone: string}> = ({text, start, size, tone}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div style={{display: "flex", gap: size * 0.28, justifyContent: "center"}}>
      {text.split(" ").map((word, index) => {
        const pop = spring({frame: frame - start - index * 3, fps, config: {damping: 16}});
        return (
          <span key={index} style={{color: tone, font: `800 ${size}px ${FONT}`, letterSpacing: -2, opacity: pop, transform: `translateY(${(1 - pop) * 50}px)`}}>
            {word}
          </span>
        );
      })}
    </div>
  );
};

export const HookCard: React.FC<{scene: Scene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // Kartlar ikinci cümle başlarken toplanır; zamanlama seslendirmeden gelir.
  const gatherAt = scene.cues[1]?.from ?? 100;
  const questionOpacity = interpolate(frame, [gatherAt - 12, gatherAt], [1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const logo = spring({frame: frame - gatherAt - 14, fps, config: {damping: 12}});
  const leave = interpolate(frame, [scene.duration - 10, scene.duration], [1, 0], {extrapolateLeft: "clamp"});

  return (
    <AbsoluteFill style={{opacity: leave}}>
      <Chips gatherAt={gatherAt} />
      <AbsoluteFill style={{justifyContent: "center", gap: 6, opacity: questionOpacity}}>
        <Words text="Fikirler bir yerde," start={8} size={86} tone={color.text} />
        <Words text="görevler başka yerde mi?" start={36} size={86} tone={color.accent} />
      </AbsoluteFill>
      {frame >= gatherAt && (
        <AbsoluteFill style={{alignItems: "center", justifyContent: "center", gap: 30}}>
          <Img src={staticFile("generated/logo.png")} style={{width: 170, height: 170, transform: `scale(${logo})`, filter: "drop-shadow(0 20px 50px rgba(59,130,246,0.5))"}} />
          <Words text="Proje Takip Platformu" start={gatherAt + 20} size={88} tone={color.text} />
          <Words text={scene.title} start={gatherAt + 32} size={42} tone={color.muted} />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
