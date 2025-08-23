import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Sparkles, ChevronRight, AlertCircle } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface JobInputProps {
  jobDescription: string;
  setJobDescription: (value: string) => void;
  jobTitle: string;
  setJobTitle: (value: string) => void;
  onJobAnalyzed: (analysis: any) => void;
}

const JobInput: React.FC<JobInputProps> = ({
  jobDescription,
  setJobDescription,
  jobTitle,
  setJobTitle,
  onJobAnalyzed
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyzeJob = async () => {
    if (!jobDescription.trim()) {
      toast.error('Please enter a job description');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/analysis/analyze-job', {
        description: jobDescription,
        title: jobTitle || 'Untitled Position',
        company: null
      });

      if (response.data.status === 'success') {
        toast.success('Job description analyzed successfully!');
        onJobAnalyzed(response.data.analysis);
      } else {
        throw new Error('Analysis failed');
      }
    } catch (error: any) {
      console.error('Job analysis error:', error);
      toast.error(
        error.response?.data?.detail || 
        'Failed to analyze job description. Please try again.'
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const sampleJobs = [
    {
      title: 'Senior Python Developer',
      description: 'We are looking for a Senior Python Developer with 3+ years experience in Django, React, PostgreSQL, and AWS. Bachelor\'s degree in Computer Science required. Experience with Docker, CI/CD, and Agile methodologies preferred.'
    },
    {
      title: 'Data Scientist',
      description: 'Seeking a Data Scientist with 2+ years experience in Python, R, Machine Learning, and SQL. Master\'s degree in Data Science, Statistics, or related field preferred. Experience with TensorFlow, Pandas, and data visualization tools required.'
    },
    {
      title: 'Frontend Developer',
      description: 'Looking for a Frontend Developer with 2+ years experience in React, TypeScript, and modern CSS frameworks. Experience with Redux, Jest, and responsive design essential. Knowledge of Node.js and GraphQL a plus.'
    }
  ];

  const loadSampleJob = (sample: typeof sampleJobs[0]) => {
    setJobTitle(sample.title);
    setJobDescription(sample.description);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-8"
      >
        <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-primary-600 to-purple-600 rounded-2xl flex items-center justify-center animate-float">
          <Brain className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Describe Your Perfect Candidate
        </h2>
        <p className="text-lg text-gray-600">
          Enter the job description and let our AI extract the key requirements
        </p>
      </motion.div>

      <div className="card">
        <div className="space-y-6">
          {/* Job Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Title (Optional)
            </label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g. Senior Python Developer"
              className="input-field"
            />
          </div>

          {/* Job Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Description *
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste your complete job description here. Include required skills, experience level, education requirements, and any preferred qualifications..."
              rows={8}
              className="input-field resize-none"
            />
            <p className="text-sm text-gray-500 mt-2">
              Include details about required skills, experience level, education, and responsibilities
            </p>
          </div>

          {/* Sample Jobs */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">
              Try a sample job description:
            </h3>
            <div className="grid gap-3">
              {sampleJobs.map((sample, index) => (
                <button
                  key={index}
                  onClick={() => loadSampleJob(sample)}
                  className="text-left p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all duration-200 group"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900 group-hover:text-primary-700">
                        {sample.title}
                      </h4>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {sample.description.substring(0, 100)}...
                      </p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600" />
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Analyze Button */}
          <div className="flex items-center justify-center pt-4">
            <motion.button
              onClick={handleAnalyzeJob}
              disabled={isAnalyzing || !jobDescription.trim()}
              className="btn-primary flex items-center space-x-3 text-lg px-8 py-4 min-w-[240px]"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isAnalyzing ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Analyzing with AI...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-6 h-6" />
                  <span>Analyze Job Description</span>
                </>
              )}
            </motion.button>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">What happens next?</p>
              <p>Our AI will analyze your job description and extract:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Required vs preferred skills</li>
                <li>Experience and education requirements</li>
                <li>Key responsibilities and seniority level</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobInput;