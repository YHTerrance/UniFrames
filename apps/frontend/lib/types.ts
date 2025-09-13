export interface Frame {
  id: string;
  universityId: string;
  name: string;
  url: string;
}

export interface PhotoState {
  originalFile: File | null;
  croppedImage: string | null;
  selectedUniversity: string | null;
  selectedFrame: Frame | null;
  finalImage: string | null;
}

export interface CropArea {
  x: number;
  y: number;
  width: number;
  height: number;
}
