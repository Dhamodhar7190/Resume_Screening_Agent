import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Brain, 
  Trophy, 
  Users, 
  Zap,
  CheckCircle,
  Upload,
  Sparkles,
  TrendingUp,
  Clock
} from 'lucide-react';
import JobInput from './JobInput';
import FileUpload from './FileUpload';
import ScoringResults from './ScoringResults';
import ProcessingStatus from './ProcessingStatus';

interface JobAnalysis {
  required_skills: string[];
  preferred_skills: string[];
  minimum_experience: number;
  seniority_level: string;
  summary: string;
}

interface ResumeFile {
  file: File;
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  score?: number;
  results?: any;
}

const Dashboard: React.FC = () => {
  const [step, setStep] = useState<'job' | 'upload' | 'results'>('job');
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(null);
  const [resumes, setResumes] = useState<ResumeFile[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleJobAnalyzed = (analysis: JobAnalysis) => {
    setJobAnalysis(analysis);
    setStep('upload');
  };

  const handleFilesUploaded = (files: ResumeFile[]) => {
    setResumes(files);
  };

  const handleProcessingComplete = (scoringResults: any) => {
    setResults(scoringResults);
    setStep('results');
    setIsProcessing(false);
  };

  const startOver = () => {
    setStep('job');
    setJobDescription('');
    setJobTitle('');
    setJobAnalysis(null);
    setResumes([]);
    setResults(null);
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-center space-x-8">
            {[
              { id: 'job', label: 'Job Description', icon: FileText },
              { id: 'upload', label: 'Upload Resumes', icon: Upload },
              { id: 'results', label: 'View Results', icon: Trophy }
            ].map((stepItem, index) => {
              const Icon = stepItem.icon;
              const isActive = step === stepItem.id;
              const isCompleted = 
                (stepItem.id === 'job' && jobAnalysis) ||
                (stepItem.id === 'upload' && resumes.length > 0) ||
                (stepItem.id === 'results' && results);

              return (
                <div key={stepItem.id} className="flex items-center">
                  <motion.div
                    className={`flex items-center space-x-3 ${
                      isActive 
                        ? 'text-primary-600' 
                        : isCompleted 
                          ? 'text-success-600' 
                          : 'text-gray-400'
                    }`}
                    animate={{ scale: isActive ? 1.05 : 1 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className={`
                      w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300
                      ${isActive 
                        ? 'bg-primary-600 border-primary-600 text-white animate-glow' 
                        : isCompleted 
                          ? 'bg-success-600 border-success-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-400'
                      }
                    `}>
                      {isCompleted && !isActive ? (
                        <CheckCircle className="w-6 h-6" />
                      ) : (
                        <Icon className="w-6 h-6" />
                      )}
                    </div>
                    <span className="font-medium hidden sm:block">{stepItem.label}</span>
                  </motion.div>
                  {index < 2 && (
                    <div className={`w-16 h-0.5 mx-4 ${
                      (stepItem.id === 'job' && jobAnalysis) || 
                      (stepItem.id === 'upload' && results)
                        ? 'bg-success-600' 
                        : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Step Content */}
        <AnimatePresence mode="wait">
          {step === 'job' && (
            <motion.div
              key="job-step"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <JobInput
                jobDescription={jobDescription}
                setJobDescription={setJobDescription}
                jobTitle={jobTitle}
                setJobTitle={setJobTitle}
                onJobAnalyzed={handleJobAnalyzed}
              />
            </motion.div>
          )}

          {step === 'upload' && (
            <motion.div
              key="upload-step"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <FileUpload
                jobAnalysis={jobAnalysis}
                jobTitle={jobTitle}
                resumes={resumes}
                onFilesUploaded={handleFilesUploaded}
                onProcessingComplete={handleProcessingComplete}
                isProcessing={isProcessing}
                setIsProcessing={setIsProcessing}
              />
              
              {/* Show job summary */}
              {jobAnalysis && (
                <div className="mt-8">
                  <div className="card max-w-4xl mx-auto">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Job Requirements Summary
                      </h3>
                      <button
                        onClick={() => setStep('job')}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        Edit Job
                      </button>
                    </div>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Required Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {jobAnalysis.required_skills?.map((skill, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Experience & Level</h4>
                        <div className="space-y-2">
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Minimum Experience:</span> {jobAnalysis.minimum_experience || 'Not specified'} years
                          </p>
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Seniority:</span> {jobAnalysis.seniority_level || 'Not specified'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {step === 'results' && (
            <motion.div
              key="results-step"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <ScoringResults
                results={results}
                jobTitle={jobTitle}
                onStartOver={startOver}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Processing Status Overlay */}
        {isProcessing && (
          <ProcessingStatus
            resumes={resumes}
            currentStep="processing"
          />
        )}

        {/* Features Section (shown on job step) */}
        {step === 'job' && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="mt-16"
          >
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                AI-Powered Resume Screening
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Upload job requirements and let our AI analyze, score, and rank candidates automatically
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: Brain,
                  title: 'Smart Analysis',
                  description: 'AI extracts skills, experience, and qualifications from resumes with high accuracy',
                  color: 'primary'
                },
                {
                  icon: Zap,
                  title: 'Fast Processing',
                  description: 'Process hundreds of resumes in minutes, not hours or days',
                  color: 'success'
                },
                {
                  icon: TrendingUp,
                  title: 'Intelligent Scoring',
                  description: 'Weighted scoring system ensures the best candidates rise to the top',
                  color: 'warning'
                }
              ].map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 + index * 0.1, duration: 0.5 }}
                    className="card text-center group hover:shadow-lg transition-all duration-300"
                  >
                    <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-${feature.color}-100 flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className={`w-8 h-8 text-${feature.color}-600`} />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600">
                      {feature.description}
                    </p>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;