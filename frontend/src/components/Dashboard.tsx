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
  required_skills: {
    programming_languages?: string[];
    web_frameworks?: string[];
    databases?: string[];
    cloud_platforms?: string[];
    devops_tools?: string[];
    data_tools?: string[];
    frontend_tools?: string[];
    mobile_development?: string[];
    testing_tools?: string[];
    version_control?: string[];
    project_management?: string[];
    other_technical?: string[];
    soft_skills?: string[];
  };
  preferred_skills?: {
    programming_languages?: string[];
    web_frameworks?: string[];
    databases?: string[];
    cloud_platforms?: string[];
    devops_tools?: string[];
    data_tools?: string[];
    other_technical?: string[];
    soft_skills?: string[];
  };
  minimum_experience?: number;
  preferred_experience?: number;
  education_requirements?: {
    required_degree?: string;
    preferred_degree?: string;
    field_of_study?: string[];
    certifications?: string[];
  };
  seniority_level?: string;
  summary?: string;
  industry?: string;
  remote_work?: string;
  key_responsibilities?: string[];
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

  // Helper function to get all required skills as a flat array
  const getAllRequiredSkills = (requiredSkills: JobAnalysis['required_skills']) => {
    if (!requiredSkills) return [];
    
    const allSkills: string[] = [];
    Object.values(requiredSkills).forEach(skillArray => {
      if (Array.isArray(skillArray)) {
        allSkills.push(...skillArray);
      }
    });
    return allSkills;
  };

  // Helper function to get key technical skills for display
  const getKeyTechnicalSkills = (requiredSkills: JobAnalysis['required_skills']) => {
    if (!requiredSkills) return [];
    
    const keySkills: string[] = [];
    
    // Prioritize most important categories
    const priorityCategories = [
      'programming_languages',
      'web_frameworks', 
      'databases',
      'cloud_platforms',
      'devops_tools'
    ];
    
    priorityCategories.forEach(category => {
      const skills = requiredSkills[category as keyof typeof requiredSkills];
      if (Array.isArray(skills)) {
        keySkills.push(...skills.slice(0, 3)); // Take first 3 from each category
      }
    });
    
    return keySkills.slice(0, 8); // Show max 8 key skills
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
              
              {/* Show enhanced job summary */}
              {jobAnalysis && (
                <div className="mt-8">
                  <div className="card max-w-4xl mx-auto">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Enhanced Job Requirements Summary
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
                        <h4 className="font-medium text-gray-900 mb-2">Key Technical Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {getKeyTechnicalSkills(jobAnalysis.required_skills).map((skill, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                        {jobAnalysis.required_skills?.soft_skills && jobAnalysis.required_skills.soft_skills.length > 0 && (
                          <div className="mt-4">
                            <h4 className="font-medium text-gray-900 mb-2">Soft Skills</h4>
                            <div className="flex flex-wrap gap-2">
                              {jobAnalysis.required_skills.soft_skills.slice(0, 4).map((skill, index) => (
                                <span
                                  key={index}
                                  className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Experience & Requirements</h4>
                        <div className="space-y-2">
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Experience:</span> {jobAnalysis.minimum_experience || 'Not specified'} years minimum
                            {jobAnalysis.preferred_experience && jobAnalysis.preferred_experience !== jobAnalysis.minimum_experience && 
                              `, ${jobAnalysis.preferred_experience} preferred`}
                          </p>
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Level:</span> {jobAnalysis.seniority_level || 'Not specified'}
                          </p>
                          {jobAnalysis.education_requirements?.required_degree && (
                            <p className="text-sm text-gray-600">
                              <span className="font-medium">Education:</span> {jobAnalysis.education_requirements.required_degree}
                              {jobAnalysis.education_requirements.field_of_study && jobAnalysis.education_requirements.field_of_study.length > 0 && 
                                ` in ${jobAnalysis.education_requirements.field_of_study.join(', ')}`}
                            </p>
                          )}
                          {jobAnalysis.remote_work && (
                            <p className="text-sm text-gray-600">
                              <span className="font-medium">Work Style:</span> {jobAnalysis.remote_work}
                            </p>
                          )}
                          {jobAnalysis.industry && (
                            <p className="text-sm text-gray-600">
                              <span className="font-medium">Industry:</span> {jobAnalysis.industry}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Show total skills count */}
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>Total Required Skills: {getAllRequiredSkills(jobAnalysis.required_skills).length}</span>
                        <span>Enhanced Analysis ✨</span>
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

        {/* Enhanced Features Section (shown on job step) */}
        {step === 'job' && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="mt-16"
          >
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Enhanced AI-Powered Resume Screening
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Advanced skill categorization, career analysis, and intelligent matching with detailed insights
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: Brain,
                  title: 'Smart Skill Analysis',
                  description: 'Categorizes skills by type (languages, frameworks, databases) with proficiency levels',
                  color: 'primary'
                },
                {
                  icon: TrendingUp,
                  title: 'Career Intelligence',
                  description: 'Analyzes career progression, leadership experience, and growth trajectory',
                  color: 'success'
                },
                {
                  icon: Zap,
                  title: 'Enhanced Scoring',
                  description: 'Intelligent matching with skill relationships, resume quality, and detailed justifications',
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