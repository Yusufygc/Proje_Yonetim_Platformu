import React from "react";
import {AbsoluteFill, Composition, registerRoot, Series} from "remotion";
import {AppScene} from "./AppScene";
import {HookCard} from "./HookCard";
import {OutroCard} from "./OutroCard";
import {Background, Subtitle, useFonts} from "./theme";
import type {Timeline} from "./types";

const Video: React.FC<Timeline> = ({scenes, subtitles, link, aiNote}) => {
  useFonts();
  return (
    <AbsoluteFill>
      <Background />
      <Series>
        {scenes.map((scene) => (
          <Series.Sequence key={scene.id} durationInFrames={scene.duration}>
            {scene.capture ? (
              <AppScene scene={scene} capture={scene.capture} />
            ) : scene.id === "kapanis" ? (
              <OutroCard scene={scene} link={link} aiNote={aiNote} />
            ) : (
              <HookCard scene={scene} />
            )}
            {/* Giriş kartında metin zaten büyük puntoyla ekranda. */}
            {subtitles && scene.id !== "kanca" ? <Subtitle cues={scene.cues} /> : null}
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};

const EMPTY: Timeline = {fps: 30, width: 1920, height: 1080, subtitles: true, link: "", aiNote: "", scenes: []};

const Root: React.FC = () => (
  <Composition
    id="Tanitim"
    component={Video}
    defaultProps={EMPTY}
    fps={30}
    width={1920}
    height={1080}
    durationInFrames={1}
    calculateMetadata={({props}) => ({
      fps: props.fps,
      width: props.width,
      height: props.height,
      durationInFrames: Math.max(1, props.scenes.reduce((sum, s) => sum + s.duration, 0)),
    })}
  />
);

registerRoot(Root);
