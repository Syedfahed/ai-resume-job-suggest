
import React from 'react';
import { Badge } from '@/components/ui/badge';

interface SkillTagProps {
  skill: string;
  type?: 'missing' | 'recommended';
}

const SkillTag: React.FC<SkillTagProps> = ({ skill, type = 'missing' }) => {
  const variants = {
    missing: 'bg-red-100 text-red-700 hover:bg-red-200',
    recommended: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
  };

  return (
    <Badge 
      variant="secondary" 
      className={`px-3 py-1 text-sm font-medium transition-colors duration-200 ${variants[type]}`}
    >
      {skill}
    </Badge>
  );
};

export default SkillTag;
