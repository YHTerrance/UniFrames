'use client';

import { useState, useRef, ChangeEvent, FormEvent } from 'react';
import Image from 'next/image';

export default function FrameGenerator() {
  const [universityName, setUniversityName] = useState('');
  const [mascot, setMascot] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSelectedFile(file);
    
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setPreviewUrl(null);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!universityName) {
      setError('Please enter a university name');
      return;
    }
    
    if (!mascot) {
      setError('Please enter a mascot name');
      return;
    }
    
    if (!selectedFile) {
      setError('Please select an image');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('university_name', universityName);
    formData.append('university_mascot', mascot);
    formData.append('image', selectedFile);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/gemini-frames/', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        // Try to surface backend error details
        let detailMsg = `Error: ${response.status}`;
        try {
          const errJson = await response.json();
          if (errJson && errJson.detail) {
            detailMsg = errJson.detail;
          }
        } catch (_) {
          // Fall back to text if JSON parsing fails
          try {
            const text = await response.text();
            if (text) detailMsg = text;
          } catch {}
        }

        throw new Error(detailMsg);
      }
      
      const data = await response.json();
      setGeneratedImageUrl(data.data.image_base64);
    } catch (err) {
      setError(`Failed to generate frame: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadImage = () => {
    if (generatedImageUrl) {
      const link = document.createElement('a');
      link.href = generatedImageUrl;
      link.download = `${universityName.replace(/\s+/g, '-').toLowerCase()}-frame.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6 text-center">University Frame Generator</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="universityName" className="block text-sm font-medium text-gray-700 mb-1">
              University Name *
            </label>
            <input
              type="text"
              id="universityName"
              value={universityName}
              onChange={(e) => setUniversityName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter university name"
            />
          </div>
          
          <div>
            <label htmlFor="mascot" className="block text-sm font-medium text-gray-700 mb-1">
              Mascot *
            </label>
            <input
              type="text"
              id="mascot"
              value={mascot}
              onChange={(e) => setMascot(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter mascot name"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Profile Image *
            </label>
            <div className="flex items-center justify-center w-full">
              <label
                htmlFor="dropzone-file"
                className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
              >
                {previewUrl ? (
                  <div className="relative w-full h-full">
                    <Image
                      src={previewUrl}
                      alt="Preview"
                      fill
                      style={{ objectFit: 'contain' }}
                    />
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <svg
                      className="w-10 h-10 mb-3 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      ></path>
                    </svg>
                    <p className="mb-2 text-sm text-gray-500">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-gray-500">PNG, JPG or JPEG (MAX. 5MB)</p>
                  </div>
                )}
                <input
                  id="dropzone-file"
                  type="file"
                  className="hidden"
                  accept="image/*"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                />
              </label>
            </div>
          </div>
          
          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}
          
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {isLoading ? 'Generating...' : 'Generate Frame'}
          </button>
        </form>
      </div>
      
      {generatedImageUrl && (
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-center">Your Generated Frame</h2>
          <div className="relative w-full h-96 mb-4">
            <Image
              src={generatedImageUrl}
              alt="Generated Frame"
              fill
              style={{ objectFit: 'contain' }}
            />
          </div>
          <button
            onClick={downloadImage}
            className="w-full py-3 px-4 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            Download Frame
          </button>
        </div>
      )}
    </div>
  );
}
