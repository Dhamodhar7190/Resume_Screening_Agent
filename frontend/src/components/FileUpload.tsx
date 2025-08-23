import React, { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  File,
  X,
  CheckCircle,
  AlertTriangle,
  Zap,
  Users,
  Clock,
  FileText,
  Plus,
  Eye,
  Download,
} from "lucide-react";
import toast from "react-hot-toast";
import axios from "axios";
// Note: In your actual project, you'll import:
// import axios from 'axios';
// import toast from 'react-hot-toast';

interface ResumeFile {
  file: File;
  id: string;
  status: "pending" | "processing" | "completed" | "error";
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
  setIsProcessing,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [draggedFiles, setDraggedFiles] = useState<File[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const newResumes: ResumeFile[] = acceptedFiles.map((file) => ({
        file,
        id: Math.random().toString(36).substring(7),
        status: "pending",
      }));

      const allResumes = [...resumes, ...newResumes];
      onFilesUploaded(allResumes);

      // Clear dragged files
      setDraggedFiles([]);

      toast.success(`${acceptedFiles.length} resume(s) added successfully!`, {
        icon: "🎉",
        duration: 3000,
      });
    },
    [resumes, onFilesUploaded]
  );

  const onDragEnter = useCallback((files: File[]) => {
    setDragActive(true);
    setDraggedFiles(files);
  }, []);

  const onDragLeave = useCallback(() => {
    setDragActive(false);
    setDraggedFiles([]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10MB
    onDragEnter: () => onDragEnter([]),
    onDragLeave: onDragLeave,
    onDropAccepted: () => {
      setDragActive(false);
      setDraggedFiles([]);
    },
    onDropRejected: (rejectedFiles) => {
      setDragActive(false);
      setDraggedFiles([]);
      rejectedFiles.forEach((rejection) => {
        toast.error(`${rejection.file.name}: ${rejection.errors[0].message}`, {
          duration: 5000,
        });
      });
    },
  });

  const removeFile = (id: string) => {
    const updatedResumes = resumes.filter((resume) => resume.id !== id);
    onFilesUploaded(updatedResumes);
    toast.success("File removed");
  };

  // Update the startProcessing function in FileUpload.tsx

  const startProcessing = async () => {
    if (resumes.length === 0) {
      toast.error("Please upload at least one resume");
      return;
    }

    setIsProcessing(true);

    try {
      const formData = new FormData();

      // Enhanced job description formatting for the new structure
      let jobDescriptionText = jobTitle ? `${jobTitle}\n\n` : "Position\n\n";

      if (jobAnalysis) {
        // Add required skills by category
        if (jobAnalysis.required_skills) {
          jobDescriptionText += "REQUIRED SKILLS:\n";

          Object.entries(jobAnalysis.required_skills).forEach(
            ([category, skills]) => {
              if (Array.isArray(skills) && skills.length > 0) {
                const categoryName = category.replace(/_/g, " ").toUpperCase();
                jobDescriptionText += `${categoryName}: ${skills.join(", ")}\n`;
              }
            }
          );
        }

        // Add experience requirements
        if (jobAnalysis.minimum_experience) {
          jobDescriptionText += `\nMINIMUM EXPERIENCE: ${jobAnalysis.minimum_experience} years\n`;
        }

        // Add education requirements
        if (jobAnalysis.education_requirements?.required_degree) {
          jobDescriptionText += `EDUCATION: ${jobAnalysis.education_requirements.required_degree}\n`;
        }

        // Add seniority level
        if (jobAnalysis.seniority_level) {
          jobDescriptionText += `LEVEL: ${jobAnalysis.seniority_level}\n`;
        }

        // Add summary
        if (jobAnalysis.summary) {
          jobDescriptionText += `\nSUMMARY: ${jobAnalysis.summary}\n`;
        }
      } else {
        jobDescriptionText +=
          "General position - no specific requirements analyzed";
      }

      formData.append("job_description", jobDescriptionText);

      if (jobTitle) {
        formData.append("job_title", jobTitle);
      }

      // Add all resume files
      resumes.forEach((resume) => {
        formData.append("files", resume.file);
      });

      const response = await axios.post(
        "http://localhost:8000/api/v1/scoring/batch-score-resumes",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 300000, // 5 minutes timeout
        }
      );

      if (response.data.status === "success") {
        toast.success(
          `Successfully processed ${response.data.batch_results.processed_successfully} resumes!`,
          {
            icon: "🚀",
          }
        );
        onProcessingComplete(response.data);
      } else {
        throw new Error("Processing failed");
      }
    } catch (error: any) {
      console.error("Batch processing error:", error);
      toast.error(
        error.response?.data?.detail ||
          "Failed to process resumes. Please try again."
      );
      setIsProcessing(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-8"
      >
        <motion.div
          className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-green-500 to-blue-600 rounded-2xl flex items-center justify-center"
          animate={{
            rotate: dragActive ? 5 : 0,
            scale: dragActive ? 1.1 : 1,
          }}
          transition={{ duration: 0.3 }}
        >
          <Upload className="w-10 h-10 text-white" />
        </motion.div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Candidate Resumes
        </h2>
        <p className="text-lg text-gray-600">
          Drag & drop resume files or click to browse. We'll analyze them
          against your job requirements.
        </p>
      </motion.div>

      {/* Enhanced Upload Area */}
      <div className="mb-8">
        <motion.div
          {...(getRootProps() as any)}
          className={`
            relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 overflow-hidden
            ${
              isDragActive || dragActive
                ? "border-primary-500 bg-gradient-to-br from-primary-50 to-blue-50 scale-[1.02] shadow-xl"
                : "border-gray-300 bg-gradient-to-br from-gray-50 to-white hover:border-primary-400 hover:bg-gradient-to-br hover:from-primary-50 hover:to-blue-50 hover:shadow-lg"
            }
          `}
          animate={{
            scale: dragActive ? 1.02 : 1,
            boxShadow: dragActive
              ? "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
              : "0 0px 0px 0px rgba(0, 0, 0, 0)",
          }}
          transition={{ duration: 0.3 }}
        >
          <input {...getInputProps()} />

          {/* Floating background elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-32 h-32 bg-gradient-to-r from-primary-200/20 to-blue-200/20 rounded-full"
                style={{
                  left: `${20 + i * 15}%`,
                  top: `${10 + i * 20}%`,
                }}
                animate={{
                  y: dragActive ? [-10, 10] : [0, -20],
                  x: dragActive ? [-5, 5] : [0, 10],
                  rotate: dragActive ? [0, 360] : [0, 180],
                }}
                transition={{
                  duration: 3 + i,
                  repeat: Infinity,
                  repeatType: "reverse",
                  ease: "easeInOut",
                }}
              />
            ))}
          </div>

          {/* Upload Icon with Animation */}
          <motion.div
            animate={{
              y: isDragActive || dragActive ? [-15, 5] : [0, -10],
              rotate: isDragActive || dragActive ? [0, 10, -10, 0] : 0,
              scale: isDragActive || dragActive ? [1, 1.2, 1] : 1,
            }}
            transition={{
              duration: 0.6,
              repeat: dragActive ? Infinity : 0,
              repeatType: "reverse",
            }}
            className="relative z-10"
          >
            <Upload
              className={`w-16 h-16 mx-auto mb-4 transition-colors duration-300 ${
                isDragActive || dragActive
                  ? "text-primary-600"
                  : "text-gray-400"
              }`}
            />
          </motion.div>

          {/* Dynamic Content */}
          <motion.div
            className="relative z-10"
            animate={{ scale: dragActive ? 1.05 : 1 }}
            transition={{ duration: 0.2 }}
          >
            {isDragActive || dragActive ? (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-primary-600"
              >
                <p className="text-xl font-semibold mb-2">
                  ✨ Drop the files here!
                </p>
                <p className="text-sm">We'll process them automatically</p>

                {/* Animated file count preview */}
                {draggedFiles.length > 0 && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="mt-4 inline-block bg-primary-100 text-primary-800 px-4 py-2 rounded-full text-sm font-medium"
                  >
                    {draggedFiles.length} file
                    {draggedFiles.length > 1 ? "s" : ""} ready to upload
                  </motion.div>
                )}
              </motion.div>
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
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Plus className="w-5 h-5" />
                  <span>Choose Files</span>
                </motion.button>
              </div>
            )}
          </motion.div>

          {/* File Counter Badge */}
          {resumes.length > 0 && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute top-4 right-4 z-20"
            >
              <div className="bg-gradient-to-r from-primary-600 to-blue-600 text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg">
                {resumes.length} files ready 🚀
              </div>
            </motion.div>
          )}

          {/* Success Indicator */}
          {dragActive && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-20"
            >
              <div className="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center shadow-2xl">
                <CheckCircle className="w-12 h-12 text-white" />
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>

      {/* Enhanced Uploaded Files List */}
      <AnimatePresence>
        {resumes.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-8"
          >
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-primary-600" />
                  Uploaded Resumes ({resumes.length})
                </h3>
                <div className="flex space-x-2">
                  {resumes.length > 1 && (
                    <button
                      onClick={() => onFilesUploaded([])}
                      className="text-red-600 hover:text-red-700 text-sm font-medium px-3 py-1 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      Clear All
                    </button>
                  )}
                  <button className="text-gray-600 hover:text-gray-700 text-sm font-medium px-3 py-1 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-1">
                    <Download className="w-4 h-4" />
                    <span>Download List</span>
                  </button>
                </div>
              </div>

              <div className="grid gap-3 max-h-96 overflow-y-auto">
                {resumes.map((resume, index) => (
                  <motion.div
                    key={resume.id}
                    initial={{ opacity: 0, x: -20, scale: 0.95 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    exit={{ opacity: 0, x: 20, scale: 0.95 }}
                    transition={{ delay: index * 0.05, duration: 0.3 }}
                    className="group relative flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all duration-300"
                  >
                    {/* File Icon with Animation */}
                    <div className="flex items-center space-x-4 flex-1 min-w-0">
                      <motion.div
                        className="flex-shrink-0 relative"
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg">
                          <File className="w-6 h-6 text-white" />
                        </div>

                        {/* Status Indicator */}
                        <div className="absolute -top-1 -right-1">
                          {resume.status === "completed" && (
                            <CheckCircle className="w-5 h-5 text-green-500 bg-white rounded-full" />
                          )}
                          {resume.status === "processing" && (
                            <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin bg-white" />
                          )}
                          {resume.status === "error" && (
                            <AlertTriangle className="w-5 h-5 text-red-500 bg-white rounded-full" />
                          )}
                          {resume.status === "pending" && (
                            <motion.div
                              animate={{ scale: [1, 1.2, 1] }}
                              transition={{ duration: 2, repeat: Infinity }}
                              className="w-5 h-5 bg-yellow-400 rounded-full border-2 border-white"
                            />
                          )}
                        </div>
                      </motion.div>

                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate mb-1">
                          {resume.file.name}
                        </p>
                        <div className="flex items-center space-x-3 text-xs text-gray-500">
                          <span>{formatFileSize(resume.file.size)}</span>
                          <span>•</span>
                          <span className="capitalize">{resume.status}</span>
                          {resume.file.type.includes("pdf") && (
                            <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded-full">
                              PDF
                            </span>
                          )}
                          {resume.file.type.includes("word") && (
                            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                              DOC
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Score and Actions */}
                    <div className="flex items-center space-x-3">
                      {resume.status === "completed" && resume.score && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className={`px-3 py-1 rounded-full text-sm font-medium border ${
                            resume.score >= 80
                              ? "bg-green-50 text-green-800 border-green-200"
                              : resume.score >= 60
                              ? "bg-blue-50 text-blue-800 border-blue-200"
                              : resume.score >= 40
                              ? "bg-yellow-50 text-yellow-800 border-yellow-200"
                              : "bg-red-50 text-red-800 border-red-200"
                          }`}
                        >
                          {resume.score}/100
                        </motion.div>
                      )}

                      {resume.status === "completed" && (
                        <button className="p-2 hover:bg-primary-100 rounded-full transition-colors group-hover:scale-110">
                          <Eye className="w-4 h-4 text-primary-600" />
                        </button>
                      )}

                      <motion.button
                        onClick={() => removeFile(resume.id)}
                        className="p-2 hover:bg-red-100 rounded-full transition-colors"
                        disabled={isProcessing}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                      >
                        <X className="w-4 h-4 text-gray-400 hover:text-red-600" />
                      </motion.button>
                    </div>

                    {/* Hover Effect Overlay */}
                    <motion.div className="absolute inset-0 bg-gradient-to-r from-primary-500/5 to-blue-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Enhanced Processing Button */}
      {resumes.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <motion.button
            onClick={startProcessing}
            disabled={isProcessing || resumes.length === 0}
            className={`
              relative overflow-hidden flex items-center space-x-3 text-lg px-8 py-4 mx-auto min-w-[320px] rounded-xl font-semibold transition-all duration-300
              ${
                isProcessing
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl"
              }
            `}
            whileHover={{
              scale: isProcessing ? 1 : 1.02,
              y: isProcessing ? 0 : -2,
            }}
            whileTap={{ scale: isProcessing ? 1 : 0.98 }}
          >
            {/* Animated Background */}
            {!isProcessing && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent"
                animate={{ x: [-100, 100] }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              />
            )}

            {isProcessing ? (
              <>
                <motion.div
                  className="w-6 h-6 border-2 border-white border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
                <span>Processing {resumes.length} Resumes...</span>
              </>
            ) : (
              <>
                <motion.div
                  animate={{ rotate: [0, 15, -15, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Zap className="w-6 h-6" />
                </motion.div>
                <span>Start AI Analysis ({resumes.length} resumes)</span>
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="text-xl"
                >
                  🚀
                </motion.div>
              </>
            )}
          </motion.button>

          <motion.p
            className="text-sm text-gray-600 mt-3"
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            This may take a few minutes depending on the number of resumes
          </motion.p>
        </motion.div>
      )}

      {/* Info Cards for Empty State */}
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
              title: "Batch Processing",
              description:
                "Upload multiple resumes at once for efficient screening",
              color: "blue",
            },
            {
              icon: Clock,
              title: "Lightning Fast",
              description:
                "Each resume analyzed in under 2 seconds using advanced AI",
              color: "green",
            },
            {
              icon: Zap,
              title: "Smart Ranking",
              description:
                "Automatically ranked by job fit with detailed explanations",
              color: "purple",
            },
          ].map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="bg-white rounded-xl p-6 border border-gray-200 text-center hover:shadow-lg transition-all duration-300 group"
              >
                <motion.div
                  className={`w-14 h-14 mx-auto mb-4 bg-${feature.color}-100 rounded-xl flex items-center justify-center`}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  transition={{ duration: 0.2 }}
                >
                  <Icon className={`w-7 h-7 text-${feature.color}-600`} />
                </motion.div>
                <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </motion.div>
            );
          })}
        </motion.div>
      )}
    </div>
  );
};

export default FileUpload;
