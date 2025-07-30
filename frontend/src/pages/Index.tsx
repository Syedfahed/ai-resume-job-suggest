import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import FileUpload from '@/components/FileUpload';
import JobCard from '@/components/JobCard';
import SkillTag from '@/components/SkillTag';
import LoadingSpinner from '@/components/LoadingSpinner';
import { toast } from '@/hooks/use-toast';
import axios from 'axios';

interface Job {
  title: string;
  company: string;
  description: string;
  matchScore: number;
}

interface ResumeData {
  contact_info: {
    email: string;
    phone: string;
  };
  skills: string[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  experience: any[];
  metrics: {
    word_count: number;
    skill_count: number;
    experience_years: number;
    overall_score: number;
  };
  recommendations: {
    recommended_jobs: string[];
    skills_to_develop: string[];
  };
  raw_text: string;
}

const Index: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);

  const handleScanResume = async () => {
    if (!selectedFile) {
      toast({
        title: 'No file selected',
        description: 'Please upload a resume file first.',
        variant: 'destructive',
      });
      return;
    }

    setIsAnalyzing(true);
    setShowResults(false);
    const formData = new FormData();
    formData.append('resume', selectedFile);
    try {
      const response = await axios.post<ResumeData>('http://localhost:8000/api/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResumeData(response.data);
    } catch (error) {
      console.error(error);
    }
    setTimeout(() => {
      setIsAnalyzing(false);
      setShowResults(true);
      toast({
        title: 'Analysis complete!',
        description: 'Your resume has been successfully analyzed.',
      });
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-4">
            AI Resume Scanner
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Upload your resume to get personalized job recommendations and skill insights powered by AI
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="p-8 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            {!isAnalyzing && !showResults && (
              <div className="space-y-8 animate-fade-in">
                <FileUpload onFileSelect={setSelectedFile} selectedFile={selectedFile} />

                <div className="text-center">
                  <Button
                    onClick={handleScanResume}
                    size="lg"
                    className="px-8 py-3 text-lg font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200"
                    disabled={!selectedFile}
                  >
                    Scan My Resume
                  </Button>
                </div>
              </div>
            )}

            {isAnalyzing && <LoadingSpinner />}

            {showResults && resumeData && (
              <div className="space-y-8 animate-fade-in">
                <div className="text-center pb-6 border-b">
                  <h2 className="text-3xl font-bold text-gray-800 mb-2">Analysis Results</h2>
                  <p className="text-gray-600">Based on your resume, here are your personalized insights</p>
                </div>

                <div>
                  <h3 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                    🎯 Recommended Jobs
                  </h3>
                  <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-1">
                    <span className='bg-green-500 w-[20%] text-center rounded-md text-white font-bold p-2'>Socre: {resumeData.metrics.overall_score} %</span>
                    {resumeData.recommendations.recommended_jobs.map((job, idx) => (
                      <p key={idx} className='p-2 rounded-md shadow-md'>{job}</p>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                    📈 Skills to Develop
                  </h3>
                  <div className="bg-gray-50 rounded-xl p-6">
                    <p className="text-gray-600 mb-4">
                      Consider learning these skills to increase your job market competitiveness:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {resumeData.recommendations.skills_to_develop.map((skill, idx) => (
                        <SkillTag key={idx} skill={skill} />
                      ))}
                    </div>
                  </div>
                </div>

                <div className="text-center pt-6">
                  <Button
                    onClick={() => {
                      setShowResults(false);
                      setSelectedFile(null);
                    }}
                    variant="outline"
                    size="lg"
                    className="px-8 py-3 text-lg"
                  >
                    Scan Another Resume
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </div>

        <footer className="text-center mt-16 pb-8">
          <p className="text-gray-500">Built with ❤️ @syed fahed</p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
