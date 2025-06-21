
import React from 'react';
import { Card } from '@/components/ui/card';

interface JobCardProps {
  title: string;
  company: string;
  description: string;
  matchScore: number;
}

const JobCard: React.FC<JobCardProps> = ({ title, company, description, matchScore }) => {
  return (
    <Card className="p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 animate-fade-in">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-gray-800 mb-1">{title}</h3>
          <p className="text-primary font-medium">{company}</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            {matchScore}% match
          </div>
        </div>
      </div>
      <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
    </Card>
  );
};

export default JobCard;
