// Odak işaretlerinden kamera dönüşümü üretir.
import {Easing, interpolate} from "remotion";
import type {Capture} from "./types";

export type View = {scale: number; x: number; y: number};

const MOVE_FRAMES = 22;
const MAX_ZOOM = 1.75;

// x, y: pencere içinde ekran merkezine alınacak nokta (mantıksal piksel).
const viewFor = (rect: [number, number, number, number] | null, [w, h]: [number, number]): View => {
  if (!rect) return {scale: 1, x: w / 2, y: h / 2};
  const [left, top, width, height] = rect;
  const scale = Math.min(MAX_ZOOM, Math.max(1.2, Math.min((w * 0.5) / width, (h * 0.5) / height)));
  // Pencerenin dışı görünmesin diye merkez kenarlardan içeride tutulur.
  const clamp = (v: number, size: number) => Math.min(size - size / (2 * scale), Math.max(size / (2 * scale), v));
  return {scale, x: clamp(left + width / 2, w), y: clamp(top + height / 2, h)};
};

export const cameraAt = (capture: Capture, frame: number): View => {
  let view = viewFor(null, capture.window);
  for (const mark of capture.marks) {
    if (mark.kind !== "focus" || mark.frame > frame) continue;
    const next = viewFor(mark.rect, capture.window);
    const t = interpolate(frame, [mark.frame, mark.frame + MOVE_FRAMES], [0, 1], {
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    });
    const mix = (a: number, b: number) => a + (b - a) * t;
    view = {scale: mix(view.scale, next.scale), x: mix(view.x, next.x), y: mix(view.y, next.y)};
  }
  return view;
};
