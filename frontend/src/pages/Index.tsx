
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import FileUpload from '@/components/FileUpload';
import JobCard from '@/components/JobCard';
import SkillTag from '@/components/SkillTag';
import LoadingSpinner from '@/components/LoadingSpinner';
import { toast } from "@/hooks/use-toast";

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const mockJobRecommendations = [
    {
      title: "Senior Frontend Developer",
      company: "TechCorp Inc.",
      description: "Build modern web applications using React, TypeScript, and Node.js. Perfect match for your current skill set.",
      matchScore: 95
    },
    {
      title: "Full Stack Engineer",
      company: "StartupXYZ",
      description: "Work on both frontend and backend systems. Your React experience would be valuable here.",
      matchScore: 87
    },
    {
      title: "UI/UX Developer",
      company: "Design Studios",
      description: "Combine your technical skills with design principles to create beautiful user interfaces.",
      matchScore: 82
    }
  ];

  const mockMissingSkills = [
    "Docker", "Kubernetes", "AWS", "GraphQL", "Next.js", "Python", "Machine Learning"
  ];

  const handleScanResume = async () => {
    if (!selectedFile) {
      toast({
        title: "No file selected",
        description: "Please upload a resume file first.",
        variant: "destructive"
      });
      return;
    }

    setIsAnalyzing(true);
    setShowResults(false);

    // Simulate API call
    setTimeout(() => {
      setIsAnalyzing(false);
      setShowResults(true);
      toast({
        title: "Analysis complete!",
        description: "Your resume has been successfully analyzed.",
      });
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-4">
            AI Resume Scanner
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Upload your resume to get personalized job recommendations and skill insights powered by AI
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <Card className="p-8 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            {!isAnalyzing && !showResults && (
              <div className="space-y-8 animate-fade-in">
                <FileUpload 
                  onFileSelect={setSelectedFile}
                  selectedFile={selectedFile}
                />
                
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

            {showResults && (
              <div className="space-y-8 animate-fade-in">
                {/* Results Header */}
                <div className="text-center pb-6 border-b">
                  <h2 className="text-3xl font-bold text-gray-800 mb-2">Analysis Results</h2>
                  <p className="text-gray-600">Based on your resume, here are your personalized insights</p>
                </div>

                {/* Job Recommendations */}
                <div>
                  <h3 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                    🎯 Recommended Jobs
                  </h3>
                  <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-1">
                    {mockJobRecommendations.map((job, index) => (
                      <JobCard
                        key={index}
                        title={job.title}
                        company={job.company}
                        description={job.description}
                        matchScore={job.matchScore}
                      />
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                <div>
                  <h3 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                    📈 Skills to Develop
                  </h3>
                  <div className="bg-gray-50 rounded-xl p-6">
                    <p className="text-gray-600 mb-4">
                      Consider learning these skills to increase your job market competitiveness:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {mockMissingSkills.map((skill, index) => (
                        <SkillTag key={index} skill={skill} type="missing" />
                      ))}
                    </div>
                  </div>
                </div>

                {/* Action Button */}
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

        {/* Footer */}
        <footer className="text-center mt-16 pb-8">
          <p className="text-gray-500">
            Built with ❤️ @syed fahed
          </p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
