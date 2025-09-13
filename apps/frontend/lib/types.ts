export interface University {
  id: string
  name: string
  logo: string
  primaryColor: string
  secondaryColor: string
}

export interface Frame {
  id: string
  universityId: string
  name: string
  url: string
}

export interface PhotoState {
  originalFile: File | null
  croppedImage: string | null
  selectedUniversity: University | null
  selectedFrame: Frame | null
  finalImage: string | null
}

export interface CropArea {
  x: number
  y: number
  width: number
  height: number
}
