import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "pub-ee8f31fc638a430ba19e1dc299a82447.r2.dev",
      },
    ],
  },
};

export default nextConfig;
