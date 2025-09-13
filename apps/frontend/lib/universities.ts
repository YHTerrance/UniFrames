import type { University, Frame } from "./types"

export const universities: University[] = [
  {
    id: "harvard",
    name: "Harvard University",
    logo: "/harvard-university-logo.png",
    primaryColor: "#A41E22",
    secondaryColor: "#FFFFFF",
  },
  {
    id: "stanford",
    name: "Stanford University",
    logo: "/stanford-university-logo.png",
    primaryColor: "#8C1515",
    secondaryColor: "#FFFFFF",
  },
  {
    id: "mit",
    name: "MIT",
    logo: "/mit-logo-generic.png",
    primaryColor: "#A31F34",
    secondaryColor: "#FFFFFF",
  },
  {
    id: "yale",
    name: "Yale University",
    logo: "/yale-university-logo.png",
    primaryColor: "#00356B",
    secondaryColor: "#FFFFFF",
  },
  {
    id: "princeton",
    name: "Princeton University",
    logo: "/princeton-university-logo.png",
    primaryColor: "#E87722",
    secondaryColor: "#FFFFFF",
  },
  {
    id: "columbia",
    name: "Columbia University",
    logo: "/columbia-university-logo.png",
    primaryColor: "#B9D9EB",
    secondaryColor: "#FFFFFF",
  },
]

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


