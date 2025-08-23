import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  File, 
  X, 
  CheckCircle, 
  AlertTriangle, 
  Zap,
  Users,
  Clock,
  FileText
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface ResumeFile {
  file: File;
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  score?: number;
  results?: any;
}

interface FileUploadProps {
  jobAnalysis: any;
  jobTitle: string;
  resumes: ResumeFile[];
  onFilesUploaded: (files: ResumeFile[]) => void;
  onProcessingComplete: (results: any) => void;
  isProcessing: boolean;
  setIsProcessing: (processing: boolean) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  jobAnalysis,
  jobTitle,
  resumes,
  onFilesUploaded,
  onProcessingComplete,
  isProcessing,
  setIsProcessing
}) => {
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newResumes: ResumeFile[] = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substring(7),
      status: 'pending'
    }));

    const allResumes = [...resumes, ...newResumes];
    onFilesUploaded(allResumes);
    
    toast.success(`${acceptedFiles.length} resume(s) added successfully!`);
  }, [resumes, onFilesUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10MB
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    onDropAccepted: () => setDragActive(false),
    onDropRejected: (rejectedFiles) => {
      setDragActive(false);
      rejectedFiles.forEach(rejection => {
        toast.error(`${rejection.file.name}: ${rejection.errors[0].message}`);
      });
    }
  });

  const removeFile = (id: string) => {
    const updatedResumes = resumes.filter(resume => resume.id !== id);
    onFilesUploaded(updatedResumes);
  };

  const startProcessing = async () => {
    if (resumes.length === 0) {
      toast.error('Please upload at least one resume');
      return;
    }

    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      
      // Add job description
      formData.append('job_description', jobAnalysis ? 
        `${jobTitle}\n\nRequired Skills: ${jobAnalysis.required_skills?.join(', ')}\n\nDescription: ${jobAnalysis.summary}` 
        : 'General position'
      );
      
      if (jobTitle) {
        formData.append('job_title', jobTitle);
      }

      // Add all resume files
      resumes.forEach(resume => {
        formData.append('files', resume.file);
      });

      const response = await axios.post(
        'http://localhost:8000/api/v1/scoring/batch-score-resumes',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 300000, // 5 minutes timeout
        }
      );

      if (response.data.status === 'success') {
        toast.success(`Successfully processed ${response.data.batch_results.processed_successfully} resumes!`);
        onProcessingComplete(response.data);
      } else {
        throw new Error('Processing failed');
      }
    } catch (error: any) {
      console.error('Batch processing error:', error);
      toast.error(
        error.response?.data?.detail || 
        'Failed to process resumes. Please try again.'
      );
      setIsProcessing(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-8"
      >
        <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-green-500 to-blue-600 rounded-2xl flex items-center justify-center animate-float">
          <Upload className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Candidate Resumes
        </h2>
        <p className="text-lg text-gray-600">
          Drag & drop resume files or click to browse. We'll analyze them against your job requirements.
        </p>
      </motion.div>

      {/* Upload Area */}
      <div className="mb-8">
        <motion.div
          {...(getRootProps() as any)}
          className={`
            relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300
            ${isDragActive || dragActive 
              ? 'border-primary-500 bg-primary-50 scale-[1.02]' 
              : 'border-gray-300 bg-gray-50 hover:border-primary-400 hover:bg-primary-50'
            }
          `}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          <input {...getInputProps()} />
          
          <motion.div
            animate={{ 
              y: isDragActive || dragActive ? -10 : 0,
              scale: isDragActive || dragActive ? 1.1 : 1 
            }}
            transition={{ duration: 0.2 }}
          >
            <Upload className={`w-16 h-16 mx-auto mb-4 ${
              isDragActive || dragActive ? 'text-primary-600' : 'text-gray-400'
            }`} />
          </motion.div>
          
          {isDragActive || dragActive ? (
            <div className="text-primary-600">
              <p className="text-xl font-semibold mb-2">Drop the files here!</p>
              <p className="text-sm">We'll process them automatically</p>
            </div>
          ) : (
            <div>
              <p className="text-xl font-semibold text-gray-900 mb-2">
                Drop resume files here, or click to browse
              </p>
              <p className="text-gray-600 mb-4">
                Supports PDF, DOC, and DOCX files up to 10MB each
              </p>
              <motion.button
                className="btn-primary inline-flex items-center space-x-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Upload className="w-5 h-5" />
                <span>Choose Files</span>
              </motion.button>
            </div>
          )}

          {/* Quick stats */}
          {resumes.length > 0 && (
            <div className="absolute top-4 right-4">
              <div className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium">
                {resumes.length} files ready
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Uploaded Files List */}
      <AnimatePresence>
        {resumes.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-8"
          >
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Uploaded Resumes ({resumes.length})
                </h3>
                {resumes.length > 1 && (
                  <button
                    onClick={() => onFilesUploaded([])}
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Clear All
                  </button>
                )}
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {resumes.map((resume, index) => (
                  <motion.div
                    key={resume.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                  >
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div className="flex-shrink-0">
                        <File className="w-8 h-8 text-primary-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {resume.file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(resume.file.size)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      {resume.status === 'completed' && resume.score && (
                        <div className={`px-2 py-1 rounded text-xs font-medium ${
                          resume.score >= 80 ? 'bg-success-100 text-success-800' :
                          resume.score >= 60 ? 'bg-warning-100 text-warning-800' :
                          'bg-danger-100 text-danger-800'
                        }`}>
                          {resume.score}/100
                        </div>
                      )}
                      
                      {resume.status === 'pending' && (
                        <CheckCircle className="w-5 h-5 text-success-500" />
                      )}
                      
                      {resume.status === 'error' && (
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                      )}

                      <button
                        onClick={() => removeFile(resume.id)}
                        className="p-1 hover:bg-red-100 rounded-full transition-colors"
                        disabled={isProcessing}
                      >
                        <X className="w-4 h-4 text-gray-400 hover:text-red-600" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Processing Button */}
      {resumes.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <motion.button
            onClick={startProcessing}
            disabled={isProcessing || resumes.length === 0}
            className="btn-primary flex items-center space-x-3 text-lg px-8 py-4 mx-auto min-w-[280px]"
            whileHover={{ scale: isProcessing ? 1 : 1.02 }}
            whileTap={{ scale: isProcessing ? 1 : 0.98 }}
          >
            {isProcessing ? (
              <>
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Processing Resumes...</span>
              </>
            ) : (
              <>
                <Zap className="w-6 h-6" />
                <span>Start AI Analysis ({resumes.length} resumes)</span>
              </>
            )}
          </motion.button>

          <p className="text-sm text-gray-600 mt-3">
            This may take a few minutes depending on the number of resumes
          </p>
        </motion.div>
      )}

      {/* Info Cards */}
      {resumes.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid md:grid-cols-3 gap-6 mt-12"
        >
          {[
            {
              icon: Users,
              title: 'Batch Processing',
              description: 'Upload multiple resumes at once for efficient screening'
            },
            {
              icon: Clock,
              title: 'Fast Analysis',
              description: 'Each resume is analyzed in seconds using advanced AI'
            },
            {
              icon: Zap,
              title: 'Smart Ranking',
              description: 'Automatically ranked by job fit with detailed explanations'
            }
          ].map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="card text-center">
                <div className="w-12 h-12 mx-auto mb-4 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </motion.div>
      )}
    </div>
  );
};

export default FileUpload;