import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Sparkles,
  ChevronRight,
  AlertCircle,
  Wand2,
  CheckCircle2,
  ArrowRight,
  RefreshCw,
  Eye,
  EyeOff,
  FileText,
  Type,
  Upload
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import JobDescriptionUpload from './JobDescriptionUpload';

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
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancementResult, setEnhancementResult] = useState<any>(null);
  const [showEnhancementPreview, setShowEnhancementPreview] = useState(false);
  const [useAIEnhancement, setUseAIEnhancement] = useState(true);

  // 🌟 NEW: Input method selection
  const [inputMethod, setInputMethod] = useState<'manual' | 'file'>('manual');

  // 🌟 NEW: AI Enhancement Function
  const handleEnhanceJobDescription = async () => {
    if (!jobDescription.trim()) {
      toast.error('Please enter a job description first');
      return;
    }

    setIsEnhancing(true);
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/analysis/enhance-job-description', {
        description: jobDescription,
        title: jobTitle || null
      });

      if (response.data.status === 'success') {
        const enhancement = response.data.enhancement;
        setEnhancementResult(enhancement);
        
        // Show preview
        setShowEnhancementPreview(true);
        
        toast.success('Job description enhanced successfully! 🚀', {
          duration: 4000,
          icon: '✨'
        });
      } else {
        throw new Error('Enhancement failed');
      }
    } catch (error: any) {
      console.error('Job enhancement error:', error);
      toast.error(
        error.response?.data?.detail || 
        'Failed to enhance job description. Please try again.'
      );
    } finally {
      setIsEnhancing(false);
    }
  };

  // 🌟 NEW: Apply Enhancement
  const applyEnhancement = () => {
    if (enhancementResult) {
      setJobDescription(enhancementResult.enhanced_description);
      setJobTitle(enhancementResult.enhanced_title);
      setShowEnhancementPreview(false);
      
      toast.success('Enhanced job description applied!', {
        icon: '🎯'
      });
    }
  };

  // 🌟 NEW: Handle job description from file upload
  const handleJobDescriptionFromFile = (description: string, title: string) => {
    setJobDescription(description);
    setJobTitle(title);
    // Clear any existing enhancement results since we have new content
    setEnhancementResult(null);
    setShowEnhancementPreview(false);
  };

  // Enhanced Analysis Function
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
        company: null,
        enhance_with_ai: useAIEnhancement // 🌟 NEW: Enable AI enhancement during analysis
      });

      if (response.data.status === 'success') {
        // Show enhancement info if used
        if (response.data.enhancement_info?.was_enhanced) {
          toast.success('Job analyzed with AI enhancement! ✨', {
            duration: 4000
          });
        } else {
          toast.success('Job description analyzed successfully!');
        }
        
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
    setEnhancementResult(null);
    setShowEnhancementPreview(false);
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
          Enter the job description manually or upload a file and let our enhanced AI extract and optimize the requirements
        </p>
      </motion.div>

      <div className="card">
        <div className="space-y-6">
          {/* 🌟 NEW: Input Method Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              How would you like to provide the job description?
            </label>
            <div className="grid grid-cols-2 gap-3">
              <motion.button
                onClick={() => setInputMethod('manual')}
                className={`p-4 rounded-xl border-2 transition-all duration-200 flex items-center space-x-3 ${
                  inputMethod === 'manual'
                    ? 'border-primary-500 bg-primary-50 text-primary-900'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-primary-300 hover:bg-primary-50'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Type className="w-6 h-6" />
                <div className="text-left">
                  <p className="font-medium">Type Manually</p>
                  <p className="text-sm opacity-75">Enter or paste job description text</p>
                </div>
              </motion.button>

              <motion.button
                onClick={() => setInputMethod('file')}
                className={`p-4 rounded-xl border-2 transition-all duration-200 flex items-center space-x-3 ${
                  inputMethod === 'file'
                    ? 'border-purple-500 bg-purple-50 text-purple-900'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-purple-300 hover:bg-purple-50'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Upload className="w-6 h-6" />
                <div className="text-left">
                  <p className="font-medium">Upload File</p>
                  <p className="text-sm opacity-75">PDF, DOC, or DOCX file</p>
                </div>
              </motion.button>
            </div>
          </div>
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

          {/* 🌟 NEW: Conditional content based on input method */}
          {inputMethod === 'file' ? (
            <JobDescriptionUpload
              onJobAnalyzed={onJobAnalyzed}
              onJobDescriptionExtracted={handleJobDescriptionFromFile}
              className="my-6"
            />
          ) : (
            <>
              {/* Job Description with Enhancement */}
              <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Job Description *
              </label>
              
              {/* 🌟 NEW: AI Enhancement Toggle */}
              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-600">AI Enhancement:</label>
                <button
                  onClick={() => setUseAIEnhancement(!useAIEnhancement)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    useAIEnhancement ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      useAIEnhancement ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className="text-xs text-primary-600 font-medium">
                  {useAIEnhancement ? 'ON' : 'OFF'}
                </span>
              </div>
            </div>

            <div className="relative">
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste your job description here. Our AI will clean it up and extract requirements automatically..."
                rows={8}
                className="input-field resize-none pr-12"
              />
              
              {/* 🌟 NEW: Quick Enhancement Button */}
              {jobDescription.trim() && (
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  onClick={handleEnhanceJobDescription}
                  disabled={isEnhancing}
                  className="absolute top-3 right-3 p-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:from-purple-600 hover:to-blue-600 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50"
                  title="Enhance with AI"
                >
                  {isEnhancing ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Wand2 className="w-4 h-4" />
                  )}
                </motion.button>
              )}
            </div>

            <div className="flex items-center justify-between mt-2">
              <p className="text-sm text-gray-500">
                Include details about required skills, experience level, education, and responsibilities
              </p>
              
              {jobDescription.length > 0 && (
                <span className="text-xs text-gray-400">
                  {jobDescription.length} characters
                </span>
              )}
            </div>
          </div>

          {/* 🌟 NEW: Enhancement Preview Modal */}
          <AnimatePresence>
            {showEnhancementPreview && enhancementResult && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="border border-green-200 rounded-lg p-4 bg-green-50"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <h3 className="font-medium text-green-900">
                      AI Enhancement Ready ✨
                    </h3>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setShowEnhancementPreview(!showEnhancementPreview)}
                      className="p-1 hover:bg-green-100 rounded"
                    >
                      {showEnhancementPreview ? 
                        <EyeOff className="w-4 h-4 text-green-600" /> : 
                        <Eye className="w-4 h-4 text-green-600" />
                      }
                    </button>
                  </div>
                </div>

                {/* Enhancement Metrics */}
                {enhancementResult.quality_score && (
                  <div className="mb-3 p-3 bg-white rounded-lg border border-green-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Quality Improvement</span>
                      <span className="text-sm font-bold text-green-600">
                        {enhancementResult.quality_score}/100
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${enhancementResult.quality_score}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Enhanced Content Preview */}
                <div className="mb-3 p-3 bg-white rounded-lg border border-green-200 max-h-40 overflow-y-auto">
                  <h4 className="font-medium text-gray-900 mb-1">
                    {enhancementResult.enhanced_title}
                  </h4>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {enhancementResult.enhanced_description?.substring(0, 300)}
                    {enhancementResult.enhanced_description?.length > 300 && '...'}
                  </p>
                </div>

                {/* Optimization Notes */}
                {enhancementResult.optimization_notes && (
                  <div className="mb-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="text-sm font-medium text-blue-900 mb-1">
                      What was improved:
                    </h4>
                    <p className="text-sm text-blue-700">
                      {enhancementResult.optimization_notes}
                    </p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center space-x-3">
                  <motion.button
                    onClick={applyEnhancement}
                    className="btn-primary text-sm px-4 py-2 flex items-center space-x-2"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Apply Enhancement</span>
                  </motion.button>
                  
                  <button
                    onClick={() => setShowEnhancementPreview(false)}
                    className="btn-secondary text-sm px-4 py-2"
                  >
                    Keep Original
                  </button>
                </div>
              </motion.div>
              )}
            </AnimatePresence>

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
            </>
          )}

          {/* Enhanced Analyze Button - Only show in manual mode */}
          {inputMethod === 'manual' && (
            <div className="flex items-center justify-center pt-4">
            <motion.button
              onClick={handleAnalyzeJob}
              disabled={isAnalyzing || !jobDescription.trim()}
              className="btn-primary flex items-center space-x-3 text-lg px-8 py-4 min-w-[280px] relative overflow-hidden"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Animated Background */}
              {!isAnalyzing && (
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent"
                  animate={{ x: [-100, 100] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />
              )}

              {isAnalyzing ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Analyzing with AI...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-6 h-6" />
                  <span>
                    {useAIEnhancement ? 'Analyze with AI Enhancement' : 'Analyze Job Description'}
                  </span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </motion.button>
            </div>
          )}

          {/* 🌟 NEW: Enhancement Info Box - Show for both modes */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">
                {inputMethod === 'file' ? '📄 Smart File Processing' : '🚀 Enhanced AI Analysis'}
              </p>
              <p>Our advanced AI will:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                {inputMethod === 'file' ? (
                  <>
                    <li>Extract text from PDF, DOC, and DOCX files automatically</li>
                    <li>Detect job titles and clean formatting</li>
                    <li>Extract and categorize all requirements intelligently</li>
                    <li>Optimize the content for accurate candidate matching</li>
                  </>
                ) : (
                  <>
                    <li>Clean and optimize your job description for better results</li>
                    <li>Extract and categorize required vs preferred skills</li>
                    <li>Standardize skill terminology and experience requirements</li>
                    <li>Identify missing requirements and suggest improvements</li>
                  </>
                )}
              </ul>
              <div className="mt-2 text-xs text-blue-600">
                {inputMethod === 'file'
                  ? '💡 Tip: Enable AI Enhancement for optimized requirement extraction'
                  : '💡 Tip: Turn off AI Enhancement if you prefer to use your exact wording'
                }
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobInput;