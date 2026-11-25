// timeline.json sözleşmesi; üreten taraf video/timeline.py.
export type Mark =
  | {frame: number; kind: "focus"; rect: [number, number, number, number] | null}
  | {frame: number; kind: "shortcut"; label: string}
  | {frame: number; kind: "say"};

export type Capture = {
  video: string;
  frames: number;
  window: [number, number];
  cursor: [number, number][];
  clicks: number[];
  marks: Mark[];
};

export type Cue = {from: number; to: number; text: string};

export type Scene = {
  id: string;
  kind: "kart" | "uygulama";
  title: string;
  duration: number;
  cues: Cue[];
  capture: Capture | null;
};

export type Timeline = {
  fps: number;
  width: number;
  height: number;
  subtitles: boolean;
  link: string;
  aiNote: string;
  scenes: Scene[];
};
