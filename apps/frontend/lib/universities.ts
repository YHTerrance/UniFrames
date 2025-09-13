import type { Frame } from "./types";

export const frames: Frame[] = [
  {
    id: "classic-1",
    universityId: "harvard",
    name: "Classic Border",
    url: "/ucla.webp",
  },
];

export const getFramesByUniversity = (universityId: string): Frame[] => {
  return frames.filter((frame) => frame.universityId === universityId);
};

export const getUniversities = async () => {
  const backendUrl = process.env.NEXT_PUBLIC_API_SERVER;
  const response = await fetch(
    `${backendUrl}/api/v1/frames/universities/from-r2`
  );
  return response.json();
};
