import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import {
  Upload,
  FileText,
  X,
  CheckCircle,
  AlertTriangle,
  Brain,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Eye,
  EyeOff,
  Download,
  File,
  Wand2
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface JobDescriptionUploadProps {
  onJobAnalyzed: (analysis: any) => void;
  onJobDescriptionExtracted: (description: string, title: string) => void;
  className?: string;
}

interface UploadedJobFile {
  file: File;
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  extractedText?: string;
  extractedTitle?: string;
  analysis?: any;
  preview?: string;
}

const JobDescriptionUpload: React.FC<JobDescriptionUploadProps> = ({
  onJobAnalyzed,
  onJobDescriptionExtracted,
  className = ''
}) => {
  const [uploadedFile, setUploadedFile] = useState<UploadedJobFile | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [enhanceWithAI, setEnhanceWithAI] = useState(true);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0]; // Only take the first file for job descriptions

    const newJobFile: UploadedJobFile = {
      file,
      id: Math.random().toString(36).substring(7),
      status: 'pending'
    };

    setUploadedFile(newJobFile);

    // Auto-process the file
    await processJobFile(newJobFile);

    toast.success('Job description file uploaded successfully!', {
      icon: '📄',
      duration: 3000,
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: false, // Only one job description at a time
    maxSize: 20 * 1024 * 1024, // 20MB for job descriptions
    onDropRejected: (rejectedFiles) => {
      rejectedFiles.forEach((rejection) => {
        toast.error(`${rejection.file.name}: ${rejection.errors[0].message}`, {
          duration: 5000,
        });
      });
    },
  });

  const processJobFile = async (jobFile: UploadedJobFile) => {
    setIsProcessing(true);

    try {
      // Update status to processing
      setUploadedFile(prev => prev ? { ...prev, status: 'processing' } : null);

      const formData = new FormData();
      formData.append('file', jobFile.file);
      formData.append('enhance_with_ai', enhanceWithAI.toString());

      const response = await axios.post(
        'http://localhost:8000/api/v1/analysis/analyze-job-file',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // 1 minute timeout
        }
      );

      if (response.data.status === 'success') {
        const updatedFile: UploadedJobFile = {
          ...jobFile,
          status: 'completed',
          extractedText: response.data.analysis.summary || 'Job description extracted',
          extractedTitle: response.data.extracted_job_title,
          analysis: response.data.analysis,
          preview: response.data.analysis.summary?.substring(0, 200) + '...'
        };

        setUploadedFile(updatedFile);

        // Notify parent components
        onJobAnalyzed(response.data.analysis);
        onJobDescriptionExtracted(
          response.data.analysis.summary || '',
          response.data.extracted_job_title || ''
        );

        toast.success(
          `Job description analyzed successfully! ${enhanceWithAI ? '✨ Enhanced with AI' : ''}`,
          {
            icon: '🎯',
            duration: 4000,
          }
        );
      } else {
        throw new Error('Analysis failed');
      }
    } catch (error: any) {
      console.error('Job file processing error:', error);

      setUploadedFile(prev => prev ? { ...prev, status: 'error' } : null);

      toast.error(
        error.response?.data?.detail ||
        'Failed to process job description file. Please try again.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setShowPreview(false);
    toast.success('File removed');
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const reprocessWithToggle = async () => {
    if (!uploadedFile) return;
    setEnhanceWithAI(!enhanceWithAI);
    await processJobFile(uploadedFile);
  };

  return (
    <div className={`w-full ${className}`}>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <motion.div
            className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-purple-500 to-blue-600 rounded-2xl flex items-center justify-center"
            animate={{
              rotate: isDragActive ? 5 : 0,
              scale: isDragActive ? 1.1 : 1,
            }}
            transition={{ duration: 0.3 }}
          >
            <FileText className="w-8 h-8 text-white" />
          </motion.div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Upload Job Description
          </h3>
          <p className="text-gray-600 text-sm">
            Upload a PDF, DOC, or DOCX file containing the job description
          </p>
        </motion.div>

        {/* AI Enhancement Toggle */}
        <div className="flex items-center justify-center space-x-3">
          <span className="text-sm text-gray-600">AI Enhancement:</span>
          <button
            onClick={() => setEnhanceWithAI(!enhanceWithAI)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              enhanceWithAI ? 'bg-purple-600' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                enhanceWithAI ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
          <span className="text-xs text-purple-600 font-medium">
            {enhanceWithAI ? 'ON' : 'OFF'}
          </span>
        </div>

        {/* Upload Area */}
        {!uploadedFile && (
          <motion.div
            {...(getRootProps() as any)}
            className={`
              relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300
              ${
                isDragActive
                  ? 'border-purple-500 bg-gradient-to-br from-purple-50 to-blue-50 scale-[1.02] shadow-lg'
                  : 'border-gray-300 bg-gradient-to-br from-gray-50 to-white hover:border-purple-400 hover:bg-gradient-to-br hover:from-purple-50 hover:to-blue-50 hover:shadow-md'
              }
            `}
            animate={{
              scale: isDragActive ? 1.02 : 1,
            }}
            transition={{ duration: 0.3 }}
          >
            <input {...getInputProps()} />

            {/* Upload Icon */}
            <motion.div
              animate={{
                y: isDragActive ? [-10, 5] : [0, -5],
                rotate: isDragActive ? [0, 5, -5, 0] : 0,
              }}
              transition={{
                duration: 0.6,
                repeat: isDragActive ? Infinity : 0,
                repeatType: 'reverse',
              }}
            >
              <Upload
                className={`w-12 h-12 mx-auto mb-4 transition-colors duration-300 ${
                  isDragActive ? 'text-purple-600' : 'text-gray-400'
                }`}
              />
            </motion.div>

            {/* Dynamic Content */}
            {isDragActive ? (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-purple-600"
              >
                <p className="text-lg font-semibold mb-2">
                  ✨ Drop the job description file here!
                </p>
                <p className="text-sm">We'll extract and analyze it automatically</p>
              </motion.div>
            ) : (
              <div>
                <p className="text-lg font-semibold text-gray-900 mb-2">
                  Drop job description file here, or click to browse
                </p>
                <p className="text-gray-600 mb-4">
                  Supports PDF, DOC, and DOCX files up to 20MB
                </p>
                <motion.button
                  className="btn-primary inline-flex items-center space-x-2"
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <FileText className="w-5 h-5" />
                  <span>Choose File</span>
                </motion.button>
              </div>
            )}
          </motion.div>
        )}

        {/* Uploaded File Display */}
        <AnimatePresence>
          {uploadedFile && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-purple-600" />
                  Uploaded Job Description
                </h4>
                <div className="flex items-center space-x-2">
                  {uploadedFile.status === 'completed' && (
                    <button
                      onClick={() => setShowPreview(!showPreview)}
                      className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                      title={showPreview ? 'Hide preview' : 'Show preview'}
                    >
                      {showPreview ?
                        <EyeOff className="w-4 h-4 text-gray-600" /> :
                        <Eye className="w-4 h-4 text-gray-600" />
                      }
                    </button>
                  )}
                  {!isProcessing && (
                    <button
                      onClick={removeFile}
                      className="p-2 hover:bg-red-100 rounded-full transition-colors"
                    >
                      <X className="w-4 h-4 text-gray-400 hover:text-red-600" />
                    </button>
                  )}
                </div>
              </div>

              {/* File Info */}
              <div className="flex items-center space-x-4 mb-4">
                <div className="flex-shrink-0 relative">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg">
                    <File className="w-6 h-6 text-white" />
                  </div>

                  {/* Status Indicator */}
                  <div className="absolute -top-1 -right-1">
                    {uploadedFile.status === 'completed' && (
                      <CheckCircle className="w-5 h-5 text-green-500 bg-white rounded-full" />
                    )}
                    {uploadedFile.status === 'processing' && (
                      <div className="w-5 h-5 border-2 border-purple-500 border-t-transparent rounded-full animate-spin bg-white" />
                    )}
                    {uploadedFile.status === 'error' && (
                      <AlertTriangle className="w-5 h-5 text-red-500 bg-white rounded-full" />
                    )}
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate mb-1">
                    {uploadedFile.file.name}
                  </p>
                  <div className="flex items-center space-x-3 text-xs text-gray-500">
                    <span>{formatFileSize(uploadedFile.file.size)}</span>
                    <span>•</span>
                    <span className="capitalize">{uploadedFile.status}</span>
                    {uploadedFile.extractedTitle && (
                      <>
                        <span>•</span>
                        <span className="text-purple-600 font-medium">
                          {uploadedFile.extractedTitle}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Processing Status */}
              {isProcessing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4 mb-4"
                >
                  <div className="flex items-center space-x-3">
                    <RefreshCw className="w-5 h-5 text-purple-600 animate-spin" />
                    <div>
                      <p className="text-sm font-medium text-purple-900">
                        Processing job description...
                      </p>
                      <p className="text-xs text-purple-700">
                        Extracting text and analyzing with {enhanceWithAI ? 'AI enhancement' : 'standard processing'}
                      </p>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Preview */}
              {showPreview && uploadedFile.status === 'completed' && uploadedFile.preview && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="bg-gray-50 rounded-lg p-4 mb-4"
                >
                  <h5 className="text-sm font-medium text-gray-900 mb-2">
                    Extracted Content Preview:
                  </h5>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {uploadedFile.preview}
                  </p>
                </motion.div>
              )}

              {/* Actions */}
              {uploadedFile.status === 'completed' && (
                <div className="flex items-center space-x-3">
                  <motion.button
                    onClick={reprocessWithToggle}
                    className="btn-secondary text-sm px-4 py-2 flex items-center space-x-2"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Wand2 className="w-4 h-4" />
                    <span>Reprocess with {enhanceWithAI ? 'Standard' : 'AI Enhancement'}</span>
                  </motion.button>

                  <button
                    onClick={() => setShowPreview(!showPreview)}
                    className="text-gray-600 hover:text-gray-800 text-sm px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    {showPreview ? 'Hide' : 'Show'} Preview
                  </button>
                </div>
              )}

              {/* Error State */}
              {uploadedFile.status === 'error' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="bg-red-50 border border-red-200 rounded-lg p-4"
                >
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                    <div>
                      <p className="text-sm font-medium text-red-900">
                        Failed to process file
                      </p>
                      <p className="text-xs text-red-700">
                        Please try uploading the file again or check if it's a valid job description document.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => processJobFile(uploadedFile)}
                    className="mt-3 btn-primary text-sm px-4 py-2"
                  >
                    Retry Processing
                  </button>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Info Box */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <Brain className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-purple-800">
              <p className="font-medium mb-1">📄 Smart Job Description Processing</p>
              <p>Our AI will:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Extract text from PDF, DOC, and DOCX files</li>
                <li>Automatically detect the job title</li>
                <li>Clean and optimize the description for analysis</li>
                <li>Extract and categorize all requirements</li>
              </ul>
              <div className="mt-2 text-xs text-purple-600">
                💡 Enable AI Enhancement for optimized requirement extraction
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDescriptionUpload;