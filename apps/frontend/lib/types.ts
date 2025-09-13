export interface PhotoState {
  originalFile: File | null;
  croppedImage: string | null;
  selectedUniversity: string | null;
  selectedFrame: string | null;
  finalImage: string | null;
}

export interface CropArea {
  x: number;
  y: number;
  width: number;
  height: number;
}
