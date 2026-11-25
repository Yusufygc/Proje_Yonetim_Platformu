import React from "react";
import {AbsoluteFill, Freeze, interpolate, OffthreadVideo, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {cameraAt} from "./camera";
import {Keys} from "./Keys";
import {color, FONT} from "./theme";
import type {Capture, Scene} from "./types";

// Pencerenin sahnedeki yeri: üstte başlık, altta altyazı için boşluk kalır.
const FRAME = {width: 1472, height: 828, left: 224, top: 128};
// Yakınlaşan pencere bu şeridin altına inmez; altyazı arayüz metnini örtmez.
const SUBTITLE_BAND = 116;

const Cursor: React.FC<{capture: Capture; frame: number; scale: number}> = ({capture, frame, scale}) => {
  const [x, y] = capture.cursor[Math.min(frame, capture.cursor.length - 1)];
  return (
    <>
      {capture.clicks
        .filter((at) => frame >= at && frame < at + 18)
        .map((at) => {
          const t = (frame - at) / 18;
          const size = 18 + t * 70;
          return (
            <div
              key={at}
              style={{
                position: "absolute",
                left: x * scale - size / 2,
                top: y * scale - size / 2,
                width: size,
                height: size,
                borderRadius: "50%",
                border: `3px solid ${color.accent}`,
                background: "rgba(59,130,246,0.18)",
                opacity: 1 - t,
              }}
            />
          );
        })}
      <svg
        width={30}
        height={30}
        viewBox="0 0 24 24"
        style={{
          position: "absolute",
          left: x * scale - 5,
          top: y * scale - 3,
          scale: capture.clicks.some((at) => frame >= at && frame < at + 5) ? "0.85" : "1",
          filter: "drop-shadow(0 3px 6px rgba(0,0,0,0.55))",
        }}
      >
        <path d="M4 2.5v17l4.6-4.4 2.9 6.4 3.1-1.4-2.9-6.3h6.4z" fill="#fff" stroke="#111827" strokeWidth={1.4} />
      </svg>
    </>
  );
};

export const AppScene: React.FC<{scene: Scene; capture: Capture}> = ({scene, capture}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 18, mass: 0.9}});
  const leave = interpolate(frame, [scene.duration - 10, scene.duration], [1, 0], {extrapolateLeft: "clamp"});
  const view = cameraAt(capture, frame);
  const scale = FRAME.width / capture.window[0];
  const shiftX = (capture.window[0] / 2 - view.x) * scale * view.scale;
  const shiftY = (capture.window[1] / 2 - view.y) * scale * view.scale;
  // Uygulama dururken görüntü donmuş gibi görünmesin diye çok yavaş yaklaşma.
  const drift = 1 + 0.025 * (frame / scene.duration);
  const titleOpacity =interpolate(view.scale, [1, 1.12], [1, 0], {extrapolateRight: "clamp"});
  const video = <OffthreadVideo muted src={staticFile(capture.video)} style={{width: "100%", height: "100%"}} />;

  return (
    <AbsoluteFill style={{opacity: leave}}>
      <div
        style={{
          position: "absolute",
          top: 34,
          left: 0,
          right: 0,
          textAlign: "center",
          color: color.text,
          font: `800 54px ${FONT}`,
          letterSpacing: -1,
          opacity: titleOpacity * enter,
          transform: `translateY(${(1 - enter) * 30}px)`,
        }}
      >
        {scene.title}
      </div>
      <AbsoluteFill style={{clipPath: `inset(0 0 ${SUBTITLE_BAND}px 0)`}}>
      <div style={{position: "absolute", ...FRAME, perspective: 2200}}>
        <div
          style={{
            position: "absolute",
            inset: 0,
            transform: `translate(${shiftX}px, ${shiftY + (1 - enter) * 160}px) scale(${view.scale * drift * (0.92 + enter * 0.08)}) rotateX(${(1 - enter) * 14}deg)`,
            borderRadius: 18,
            overflow: "hidden",
            border: `1px solid ${color.border}`,
            boxShadow: "0 40px 120px rgba(0,0,0,0.65), 0 0 90px rgba(59,130,246,0.18)",
            opacity: Math.min(1, enter * 1.4),
          }}
        >
          {/* Kayıt sahneden kısaysa son kare tutulur. */}
          {frame < capture.frames ? video : <Freeze frame={capture.frames - 1}>{video}</Freeze>}
          <Cursor capture={capture} frame={frame} scale={scale} />
        </div>
      </div>
      </AbsoluteFill>
      <Keys capture={capture} />
    </AbsoluteFill>
  );
};
