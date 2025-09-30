import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy,
  User,
  Mail,
  Phone,
  Download,
  RefreshCw,
  Eye,
  Target,
  Clock,
  CheckCircle,
  AlertCircle,
  Users,
} from "lucide-react";
import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from "chart.js";
import CandidateComparison from "./CandidateComparison";

// Register ChartJS components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
);

interface ScoringResultsProps {
  results: any;
  jobTitle: string;
  onStartOver: () => void;
}

const ScoringResults: React.FC<ScoringResultsProps> = ({
  results,
  jobTitle,
  onStartOver,
}) => {
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [showComparison, setShowComparison] = useState(false);

  if (!results || !results.batch_results) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No results available</p>
      </div>
    );
  }

  const { batch_results, summary } = results;
  const candidates = batch_results.results || [];
  const topCandidates = candidates.slice(0, 5);

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-green-600 bg-green-50 border-green-200";
    if (score >= 70) return "text-blue-600 bg-blue-50 border-blue-200";
    if (score >= 55) return "text-yellow-600 bg-yellow-50 border-yellow-200";
    return "text-red-600 bg-red-50 border-red-200";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 85) return "Excellent Match";
    if (score >= 70) return "Good Match";
    if (score >= 55) return "Moderate Match";
    return "Weak Match";
  };

  const exportResults = () => {
    const csvContent = [
      ["Rank", "Name", "Score", "Email", "Phone", "Recommendation"].join(","),
      ...candidates.map((candidate: any, index: number) =>
        [
          index + 1,
          candidate.candidate_info?.name || candidate.filename,
          candidate.overall_score,
          candidate.candidate_info?.email || "",
          candidate.candidate_info?.phone || "",
          candidate.recommendation,
        ].join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `resume_screening_results_${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Chart data for score distribution
  const scoreDistribution = {
    labels: [
      "Excellent (85+)",
      "Good (70-84)",
      "Moderate (55-69)",
      "Weak (<55)",
    ],
    datasets: [
      {
        data: [
          candidates.filter((c: any) => c.overall_score >= 85).length,
          candidates.filter(
            (c: any) => c.overall_score >= 70 && c.overall_score < 85
          ).length,
          candidates.filter(
            (c: any) => c.overall_score >= 55 && c.overall_score < 70
          ).length,
          candidates.filter((c: any) => c.overall_score < 55).length,
        ],
        backgroundColor: ["#10B981", "#3B82F6", "#F59E0B", "#EF4444"],
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom" as const,
        labels: {
          padding: 20,
          usePointStyle: true,
        },
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const total = context.dataset.data.reduce(
              (a: number, b: number) => a + b,
              0
            );
            const percentage = ((context.parsed / total) * 100).toFixed(1);
            return `${context.label}: ${context.parsed} candidates (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-2xl flex items-center justify-center animate-float">
          <Trophy className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Screening Results
        </h2>
        <p className="text-lg text-gray-600">
          {jobTitle && `Results for ${jobTitle} position`}
        </p>
      </motion.div>

      {/* Summary Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8"
      >
        {[
          {
            label: "Total Resumes",
            value: summary.total_files,
            icon: User,
            color: "blue",
          },
          {
            label: "Successfully Processed",
            value: summary.successfully_processed,
            icon: CheckCircle,
            color: "green",
          },
          {
            label: "Average Score",
            value: `${summary.average_score}/100`,
            icon: Target,
            color: "purple",
          },
          {
            label: "Processing Time",
            value: `${Math.round(summary.processing_time)}s`,
            icon: Clock,
            color: "orange",
          },
        ].map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              className="card text-center"
            >
              <div
                className={`w-12 h-12 mx-auto mb-3 bg-${stat.color}-100 rounded-xl flex items-center justify-center`}
              >
                <Icon className={`w-6 h-6 text-${stat.color}-600`} />
              </div>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-sm text-gray-600">{stat.label}</p>
            </motion.div>
          );
        })}
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-8 mb-8">
        {/* Score Distribution Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Score Distribution
          </h3>
          <div className="h-64">
            <Doughnut data={scoreDistribution} options={chartOptions} />
          </div>
        </motion.div>

        {/* Top Candidates */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2 card"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Top 5 Candidates
            </h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={exportResults}
                className="btn-secondary text-sm py-2 px-4 flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              <button
                onClick={onStartOver}
                className="btn-secondary text-sm py-2 px-4 flex items-center space-x-2"
              >
                <RefreshCw className="w-4 h-4" />
                <span>New Analysis</span>
              </button>
            </div>
            <button
              onClick={() => setShowComparison(true)}
              className="btn-primary text-sm py-2 px-4 flex items-center space-x-2"
              disabled={candidates.length < 2}
            >
              <Users className="w-4 h-4" />
              <span>Compare Top Candidates</span>
            </button>
          </div>

          <div className="space-y-4">
            {topCandidates.map((candidate: any, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors cursor-pointer"
                onClick={() => setSelectedCandidate(candidate)}
              >
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                        index < 3
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {index + 1}
                    </div>
                    {index === 0 && (
                      <Trophy className="w-5 h-5 text-yellow-500" />
                    )}
                  </div>

                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">
                      {candidate.candidate_info?.name || candidate.filename}
                    </h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                      {candidate.candidate_info?.email && (
                        <div className="flex items-center space-x-1">
                          <Mail className="w-4 h-4" />
                          <span>{candidate.candidate_info.email}</span>
                        </div>
                      )}
                      {candidate.candidate_info?.years_experience && (
                        <span>
                          {candidate.candidate_info.years_experience} years exp.
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div
                    className={`px-3 py-1 rounded-full border text-sm font-medium ${getScoreColor(
                      candidate.overall_score
                    )}`}
                  >
                    {candidate.overall_score}/100
                  </div>
                  <Eye className="w-5 h-5 text-gray-400" />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* All Candidates Grid/List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            All Candidates ({candidates.length})
          </h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode("grid")}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === "grid"
                  ? "bg-primary-100 text-primary-700"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === "list"
                  ? "bg-primary-100 text-primary-700"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              List
            </button>
          </div>
        </div>

        <div
          className={
            viewMode === "grid"
              ? "grid md:grid-cols-2 lg:grid-cols-3 gap-6"
              : "space-y-4"
          }
        >
          {candidates.map((candidate: any, index: number) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.7 + index * 0.05 }}
              className={`border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-all cursor-pointer hover:shadow-md ${
                viewMode === "list" ? "flex items-center justify-between" : ""
              }`}
              onClick={() => setSelectedCandidate(candidate)}
            >
              <div
                className={
                  viewMode === "list"
                    ? "flex items-center space-x-4 flex-1"
                    : ""
                }
              >
                <div className={viewMode === "grid" ? "mb-4" : ""}>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 truncate">
                      {candidate.candidate_info?.name || candidate.filename}
                    </h4>
                    <span className="text-xs text-gray-500">#{index + 1}</span>
                  </div>

                  {viewMode === "grid" && (
                    <div className="space-y-2 text-sm text-gray-600">
                      {candidate.candidate_info?.email && (
                        <div className="flex items-center space-x-1">
                          <Mail className="w-3 h-3" />
                          <span className="truncate">
                            {candidate.candidate_info.email}
                          </span>
                        </div>
                      )}
                      {candidate.candidate_info?.years_experience && (
                        <p>
                          Experience:{" "}
                          {candidate.candidate_info.years_experience} years
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div
                className={
                  viewMode === "list"
                    ? "flex items-center space-x-4"
                    : "space-y-2"
                }
              >
                <div
                  className={`px-3 py-1 rounded-full border text-sm font-medium text-center ${getScoreColor(
                    candidate.overall_score
                  )}`}
                >
                  {candidate.overall_score}/100
                </div>
                <div
                  className={`text-xs ${
                    getScoreColor(candidate.overall_score).split(" ")[0]
                  } font-medium`}
                >
                  {getScoreLabel(candidate.overall_score)}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Detailed Candidate Modal */}
      <AnimatePresence>
        {selectedCandidate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedCandidate(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">
                  {selectedCandidate.candidate_info?.name ||
                    selectedCandidate.filename}
                </h3>
                <button
                  onClick={() => setSelectedCandidate(null)}
                  className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center"
                >
                  ×
                </button>
              </div>

              {/* Score Overview */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="text-center">
                  <div
                    className={`text-4xl font-bold ${
                      getScoreColor(selectedCandidate.overall_score).split(
                        " "
                      )[0]
                    } mb-2`}
                  >
                    {selectedCandidate.overall_score}
                  </div>
                  <p className="text-sm text-gray-600">Overall Score</p>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900 mb-2">
                    {selectedCandidate.recommendation}
                  </div>
                  <p className="text-sm text-gray-600">Recommendation</p>
                </div>
              </div>

              {/* Score Breakdown */}
              {selectedCandidate.score_breakdown && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">
                    Score Breakdown
                  </h4>
                  <div className="space-y-3">
                    {Object.entries(selectedCandidate.score_breakdown).map(
                      ([category, score]: [string, any]) => (
                        <div
                          key={category}
                          className="flex items-center justify-between"
                        >
                          <span className="text-sm capitalize text-gray-600">
                            {category.replace("_", " ")}
                          </span>
                          <div className="flex items-center space-x-2">
                            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary-500 transition-all duration-500"
                                style={{ width: `${score}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium text-gray-900 w-12">
                              {score}/100
                            </span>
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}

              {/* Contact Info */}
              {selectedCandidate.candidate_info && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">
                    Contact Information
                  </h4>
                  <div className="space-y-2 text-sm">
                    {selectedCandidate.candidate_info.email && (
                      <div className="flex items-center space-x-2">
                        <Mail className="w-4 h-4 text-gray-400" />
                        <span>{selectedCandidate.candidate_info.email}</span>
                      </div>
                    )}
                    {selectedCandidate.candidate_info.phone && (
                      <div className="flex items-center space-x-2">
                        <Phone className="w-4 h-4 text-gray-400" />
                        <span>{selectedCandidate.candidate_info.phone}</span>
                      </div>
                    )}
                    {selectedCandidate.candidate_info.years_experience && (
                      <p>
                        Experience:{" "}
                        {selectedCandidate.candidate_info.years_experience}{" "}
                        years
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Enhanced AI Analysis */}
              {selectedCandidate.justification && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <Target className="w-5 h-5 text-blue-500 mr-2" />
                    Enhanced AI Analysis
                  </h4>
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    {(() => {
                      const analysis = selectedCandidate.justification;

                      // Try to parse structured analysis or fall back to formatted text
                      const sections = [
                        { title: "Technical Competency", pattern: /Technical Competency[:\s]*(.*?)(?=Experience Quality|Role Alignment|Overall Assessment|$)/s },
                        { title: "Experience Quality", pattern: /Experience Quality[:\s]*(.*?)(?=Technical Competency|Role Alignment|Overall Assessment|$)/s },
                        { title: "Role Alignment", pattern: /Role Alignment[:\s]*(.*?)(?=Technical Competency|Experience Quality|Overall Assessment|$)/s },
                        { title: "Overall Assessment", pattern: /Overall Assessment[:\s]*(.*?)(?=Technical Competency|Experience Quality|Role Alignment|$)/s }
                      ];

                      const parsedSections = sections.map(section => {
                        const match = analysis.match(section.pattern);
                        return match ? { title: section.title, content: match[1].trim() } : null;
                      }).filter((section): section is { title: string; content: string } => section !== null);

                      if (parsedSections.length > 0) {
                        return (
                          <div className="space-y-4">
                            {parsedSections.map((section, index) => (
                              <div key={index} className={index > 0 ? "border-t border-gray-200 pt-3" : ""}>
                                <h5 className="text-sm font-semibold text-gray-800 mb-2 flex items-center">
                                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                  {section.title}
                                </h5>
                                <p className="text-sm text-gray-600 leading-relaxed pl-4">
                                  {section.content}
                                </p>
                              </div>
                            ))}
                          </div>
                        );
                      } else {
                        // Fallback: show original justification if no structured format detected
                        return (
                          <div>
                            <h5 className="text-sm font-semibold text-gray-800 mb-2">Analysis Summary</h5>
                            <p className="text-sm text-gray-600 leading-relaxed">
                              {analysis}
                            </p>
                          </div>
                        );
                      }
                    })()}
                  </div>
                </div>
              )}

              {/* Strengths & Concerns */}
              <div className="grid md:grid-cols-2 gap-6">
                {selectedCandidate.key_strengths &&
                  selectedCandidate.key_strengths.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                        Key Strengths
                      </h4>
                      <ul className="space-y-2">
                        {selectedCandidate.key_strengths.map(
                          (strength: string, index: number) => (
                            <li
                              key={index}
                              className="text-sm text-gray-600 flex items-start"
                            >
                              <span className="w-2 h-2 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0" />
                              {strength}
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}

                {selectedCandidate.areas_of_concern &&
                  selectedCandidate.areas_of_concern.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <AlertCircle className="w-5 h-5 text-orange-500 mr-2" />
                        Areas of Concern
                      </h4>
                      <ul className="space-y-2">
                        {selectedCandidate.areas_of_concern.map(
                          (concern: string, index: number) => (
                            <li
                              key={index}
                              className="text-sm text-gray-600 flex items-start"
                            >
                              <span className="w-2 h-2 bg-orange-500 rounded-full mt-1.5 mr-2 flex-shrink-0" />
                              {concern}
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      {showComparison && (
        <CandidateComparison
          candidates={candidates}
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  );
};

export default ScoringResults;
