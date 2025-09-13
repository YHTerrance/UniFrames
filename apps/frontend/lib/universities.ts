export const getFramesByUniversity = async (university: string) => {
  const backendUrl = process.env.NEXT_PUBLIC_API_SERVER;
  const encodedName = encodeURIComponent(university);
  const response = await fetch(
    `${backendUrl}/api/v1/frames/get-frame?name=${encodedName}`
  );
  return response.json();
};

export const getUniversities = async () => {
  const backendUrl = process.env.NEXT_PUBLIC_API_SERVER;
  const response = await fetch(
    `${backendUrl}/api/v1/frames/universities/from-r2`
  );
  return response.json();
};
