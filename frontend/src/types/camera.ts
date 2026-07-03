/** Camera preview + upload telemetry overlaid on the Camera screen. */
export type UploadStatus = 'idle' | 'uploading' | 'ok' | 'error';

export interface BoundingBox {
  id: string;
  label: string;
  confidence: number; // 0..1
  /** Normalized [0..1] coordinates relative to the preview. */
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface CameraOverlayInfo {
  fps: number;
  resolution: string; // e.g. "1280x720"
  uploadStatus: UploadStatus;
  detectionCount: number;
  boxes: BoundingBox[];
}
