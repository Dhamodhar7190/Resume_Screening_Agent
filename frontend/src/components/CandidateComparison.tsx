import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Star, 
  CheckCircle, 
  XCircle,
  Eye,
  Download,
  Mail,
  Phone,
  Calendar,
  Trophy,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Plus,
  X
} from 'lucide-react';

interface Candidate {
  filename: string;
  overall_score: number;
  score_breakdown: {
    required_skills: number;
    experience_level: number;
    education: number;
    additional_qualifications: number;
  };
  key_strengths: string[];
  areas_of_concern: string[];
  candidate_info: {
    name?: string;
    email?: string;
    phone?: string;
    years_experience?: number;
    education_level?: string;
  };
  recommendation: string;
  justification: string;
}

interface CandidateComparisonProps {
  candidates: Candidate[];
  onClose: () => void;
}

const CandidateComparison: React.FC<CandidateComparisonProps> = ({
  candidates,
  onClose
}) => {
  const [selectedCandidates, setSelectedCandidates] = useState<Candidate[]>(
    candidates.slice(0, 3) // Top 3 by default
  );
  
  const [compareMode, setCompareMode] = useState<'overview' | 'detailed'>('overview');

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 55) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 85) return 'bg-green-50 border-green-200';
    if (score >= 70) return 'bg-blue-50 border-blue-200';
    if (score >= 55) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getScoreDifference = (score1: number, score2: number) => {
    const diff = score1 - score2;
    if (Math.abs(diff) < 2) return { text: 'Similar', icon: Minus, color: 'gray' };
    if (diff > 0) return { text: `+${diff.toFixed(1)}`, icon: ArrowUpRight, color: 'green' };
    return { text: `${diff.toFixed(1)}`, icon: ArrowDownRight, color: 'red' };
  };

  const addCandidate = (candidate: Candidate) => {
    if (selectedCandidates.length < 4 && !selectedCandidates.find(c => c.filename === candidate.filename)) {
      setSelectedCandidates([...selectedCandidates, candidate]);
    }
  };

  const removeCandidate = (filename: string) => {
    if (selectedCandidates.length > 2) {
      setSelectedCandidates(selectedCandidates.filter(c => c.filename !== filename));
    }
  };

  const exportComparison = () => {
    const csvContent = [
      ['Metric', ...selectedCandidates.map(c => c.candidate_info?.name || c.filename)].join(','),
      ['Overall Score', ...selectedCandidates.map(c => c.overall_score)].join(','),
      ['Required Skills', ...selectedCandidates.map(c => c.score_breakdown.required_skills)].join(','),
      ['Experience', ...selectedCandidates.map(c => c.score_breakdown.experience_level)].join(','),
      ['Education', ...selectedCandidates.map(c => c.score_breakdown.education)].join(','),
      ['Additional Qualifications', ...selectedCandidates.map(c => c.score_breakdown.additional_qualifications)].join(','),
      ['Recommendation', ...selectedCandidates.map(c => `"${c.recommendation}"`)].join(','),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `candidate_comparison_${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 overflow-y-auto"
    >
      <div className="min-h-screen p-4">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="max-w-7xl mx-auto bg-white rounded-2xl shadow-2xl"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Candidate Comparison
                </h2>
                <p className="text-sm text-gray-600">
                  Side-by-side analysis of top candidates
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCompareMode('overview')}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    compareMode === 'overview' ? 'bg-primary-100 text-primary-700' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setCompareMode('detailed')}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    compareMode === 'detailed' ? 'bg-primary-100 text-primary-700' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Detailed
                </button>
              </div>
              
              <button
                onClick={exportComparison}
                className="btn-secondary flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
              >
                ×
              </button>
            </div>
          </div>

          {/* Candidate Selection */}
          <div className="p-6 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">
                Select Candidates to Compare ({selectedCandidates.length}/4)
              </h3>
              <div className="text-sm text-gray-600">
                Choose 2-4 candidates for comparison
              </div>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {candidates.slice(0, 8).map((candidate, index) => {
                const isSelected = selectedCandidates.find(c => c.filename === candidate.filename);
                const canAdd = selectedCandidates.length < 4;
                
                return (
                  <motion.button
                    key={candidate.filename}
                    onClick={() => isSelected ? removeCandidate(candidate.filename) : addCandidate(candidate)}
                    disabled={!isSelected && !canAdd}
                    className={`
                      flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
                      ${isSelected 
                        ? 'bg-primary-100 text-primary-800 border border-primary-300' 
                        : canAdd 
                          ? 'bg-white text-gray-700 border border-gray-300 hover:border-primary-300 hover:bg-primary-50' 
                          : 'bg-gray-100 text-gray-400 border border-gray-200 cursor-not-allowed'
                      }
                    `}
                    whileHover={{ scale: isSelected || canAdd ? 1.02 : 1 }}
                    whileTap={{ scale: isSelected || canAdd ? 0.98 : 1 }}
                  >
                    <span className={`w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center ${
                      index < 3 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {index + 1}
                    </span>
                    <span className="truncate max-w-32">
                      {candidate.candidate_info?.name || candidate.filename.replace('.pdf', '')}
                    </span>
                    <span className={`text-xs ${getScoreColor(candidate.overall_score)}`}>
                      {candidate.overall_score}
                    </span>
                    {isSelected ? (
                      <X className="w-4 h-4" />
                    ) : canAdd ? (
                      <Plus className="w-4 h-4" />
                    ) : null}
                  </motion.button>
                );
              })}
            </div>
          </div>

          {/* Comparison Content */}
          <div className="p-6">
            {compareMode === 'overview' ? (
              /* Overview Mode - Card Layout */
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {selectedCandidates.map((candidate, index) => (
                  <motion.div
                    key={candidate.filename}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`relative bg-white rounded-xl border-2 p-6 ${
                      index === 0 ? 'border-yellow-300 bg-gradient-to-br from-yellow-50 to-white shadow-lg' : 'border-gray-200 hover:border-gray-300'
                    } transition-all duration-300`}
                  >
                    {/* Winner Badge */}
                    {index === 0 && (
                      <motion.div
                        initial={{ scale: 0, rotate: -10 }}
                        animate={{ scale: 1, rotate: 0 }}
                        className="absolute -top-3 -right-3 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center shadow-lg"
                      >
                        <Trophy className="w-5 h-5 text-yellow-800" />
                      </motion.div>
                    )}

                    {/* Rank Badge */}
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                        index === 0 ? 'bg-yellow-100 text-yellow-800' : 
                        index === 1 ? 'bg-gray-100 text-gray-600' :
                        'bg-bronze-100 text-bronze-600'
                      }`}>
                        #{index + 1}
                      </div>
                      {index < 3 && <Star className="w-5 h-5 text-yellow-500 fill-current" />}
                    </div>

                    {/* Candidate Avatar */}
                    <div className="text-center mb-6">
                      <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg mb-3 mx-auto shadow-lg">
                        {(candidate.candidate_info?.name || candidate.filename)
                          .split(' ')
                          .map(n => n[0])
                          .join('')
                          .substring(0, 2)
                          .toUpperCase()}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">
                        {candidate.candidate_info?.name || candidate.filename.replace('.pdf', '')}
                      </h3>
                      <div className="flex items-center justify-center space-x-3 text-xs text-gray-500">
                        {candidate.candidate_info?.years_experience && (
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{candidate.candidate_info.years_experience}y exp</span>
                          </span>
                        )}
                        {candidate.candidate_info?.education_level && (
                          <span className="truncate max-w-20">{candidate.candidate_info.education_level}</span>
                        )}
                      </div>
                    </div>

                    {/* Overall Score */}
                    <div className="text-center mb-6">
                      <motion.div 
                        className={`text-4xl font-bold mb-2 ${getScoreColor(candidate.overall_score)}`}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.3 + index * 0.1, type: 'spring' }}
                      >
                        {candidate.overall_score}
                      </motion.div>
                      <div className={`inline-block px-3 py-1 rounded-full border text-xs font-medium ${getScoreBg(candidate.overall_score)} ${getScoreColor(candidate.overall_score)}`}>
                        {candidate.overall_score >= 85 ? 'Excellent Match' :
                         candidate.overall_score >= 70 ? 'Good Match' :
                         candidate.overall_score >= 55 ? 'Moderate Match' : 'Weak Match'}
                      </div>
                    </div>

                    {/* Score Breakdown */}
                    <div className="space-y-3 mb-6">
                      <h4 className="font-medium text-gray-900 text-sm">Score Breakdown</h4>
                      {Object.entries(candidate.score_breakdown).map(([category, score]) => (
                        <div key={category} className="flex items-center justify-between">
                          <span className="text-xs text-gray-600 capitalize">
                            {category.replace('_', ' ')}
                          </span>
                          <div className="flex items-center space-x-2">
                            <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                              <motion.div 
                                className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
                                initial={{ width: 0 }}
                                animate={{ width: `${score}%` }}
                                transition={{ delay: 0.5 + index * 0.1, duration: 0.8 }}
                              />
                            </div>
                            <span className="text-xs font-medium text-gray-900 w-8">
                              {score}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Contact Info */}
                    <div className="space-y-2 mb-6 text-xs">
                      {candidate.candidate_info?.email && (
                        <div className="flex items-center space-x-2 text-gray-600">
                          <Mail className="w-3 h-3" />
                          <span className="truncate">{candidate.candidate_info.email}</span>
                        </div>
                      )}
                      {candidate.candidate_info?.phone && (
                        <div className="flex items-center space-x-2 text-gray-600">
                          <Phone className="w-3 h-3" />
                          <span>{candidate.candidate_info.phone}</span>
                        </div>
                      )}
                    </div>

                    {/* Quick Strengths */}
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 text-sm mb-2 flex items-center">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                        Top Strengths
                      </h4>
                      <div className="space-y-1">
                        {candidate.key_strengths?.slice(0, 3).map((strength, idx) => (
                          <div key={idx} className="text-xs text-gray-600 flex items-start">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0" />
                            <span className="line-clamp-2">{strength}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Concerns */}
                    <div>
                      <h4 className="font-medium text-gray-900 text-sm mb-2 flex items-center">
                        <XCircle className="w-4 h-4 text-orange-500 mr-1" />
                        Areas to Review
                      </h4>
                      <div className="space-y-1">
                        {candidate.areas_of_concern?.slice(0, 2).map((concern, idx) => (
                          <div key={idx} className="text-xs text-gray-600 flex items-start">
                            <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 mr-2 flex-shrink-0" />
                            <span className="line-clamp-2">{concern}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Remove Button */}
                    {selectedCandidates.length > 2 && (
                      <button
                        onClick={() => removeCandidate(candidate.filename)}
                        className="absolute top-2 right-2 w-6 h-6 bg-red-100 hover:bg-red-200 rounded-full flex items-center justify-center transition-colors"
                      >
                        <X className="w-4 h-4 text-red-600" />
                      </button>
                    )}
                  </motion.div>
                ))}

                {/* Add More Candidates Card */}
                {selectedCandidates.length < 4 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: selectedCandidates.length * 0.1 }}
                    className="border-2 border-dashed border-gray-300 rounded-xl p-6 flex flex-col items-center justify-center text-center hover:border-primary-400 hover:bg-primary-50 transition-all duration-300 cursor-pointer min-h-[400px]"
                  >
                    <Plus className="w-12 h-12 text-gray-400 mb-4" />
                    <p className="text-gray-600 font-medium mb-2">Add Another Candidate</p>
                    <p className="text-sm text-gray-500">
                      Select from remaining candidates to compare
                    </p>
                    
                    <div className="mt-4 space-y-2 w-full">
                      {candidates
                        .filter(c => !selectedCandidates.find(sc => sc.filename === c.filename))
                        .slice(0, 3)
                        .map((candidate, idx) => (
                          <button
                            key={candidate.filename}
                            onClick={() => addCandidate(candidate)}
                            className="w-full text-left p-2 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors text-xs"
                          >
                            <div className="flex items-center justify-between">
                              <span className="truncate">
                                {candidate.candidate_info?.name || candidate.filename.replace('.pdf', '')}
                              </span>
                              <span className={`font-medium ${getScoreColor(candidate.overall_score)}`}>
                                {candidate.overall_score}
                              </span>
                            </div>
                          </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            ) : (
              /* Detailed Mode - Table Layout */
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">
                        Criteria
                      </th>
                      {selectedCandidates.map((candidate, index) => (
                        <th key={candidate.filename} className="px-6 py-4 text-center">
                          <div className="flex flex-col items-center space-y-2">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                              index === 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-600'
                            }`}>
                              #{index + 1}
                            </div>
                            <div className="text-sm font-medium text-gray-900 truncate max-w-32">
                              {candidate.candidate_info?.name || candidate.filename.replace('.pdf', '')}
                            </div>
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {[
                      { 
                        key: 'overall_score', 
                        label: 'Overall Score', 
                        format: (val: number) => val,
                        showComparison: true
                      },
                      { 
                        key: 'required_skills', 
                        label: 'Required Skills Match', 
                        format: (val: number, candidate: Candidate) => candidate.score_breakdown.required_skills,
                        showComparison: true
                      },
                      { 
                        key: 'experience_level', 
                        label: 'Experience Level', 
                        format: (val: number, candidate: Candidate) => candidate.score_breakdown.experience_level,
                        showComparison: true
                      },
                      { 
                        key: 'education', 
                        label: 'Education Match', 
                        format: (val: number, candidate: Candidate) => candidate.score_breakdown.education,
                        showComparison: true
                      },
                      { 
                        key: 'years_experience', 
                        label: 'Years of Experience', 
                        format: (val: any, candidate: Candidate) => `${candidate.candidate_info?.years_experience || 'N/A'} years`,
                        showComparison: false
                      },
                      { 
                        key: 'education_level', 
                        label: 'Education Level', 
                        format: (val: any, candidate: Candidate) => candidate.candidate_info?.education_level || 'N/A',
                        showComparison: false
                      },
                      { 
                        key: 'recommendation', 
                        label: 'Recommendation', 
                        format: (val: any, candidate: Candidate) => candidate.recommendation,
                        showComparison: false
                      }
                    ].map((row) => (
                      <tr key={row.key} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {row.label}
                        </td>
                        {selectedCandidates.map((candidate, candidateIndex) => {
                          const value = row.format(candidate[row.key as keyof Candidate] as any, candidate);
                          const isNumeric = typeof value === 'number';
                          
                          return (
                            <td key={candidate.filename} className="px-6 py-4 whitespace-nowrap text-sm text-center">
                              <div className="flex flex-col items-center space-y-1">
                                <span className={`font-medium ${isNumeric ? getScoreColor(value) : 'text-gray-900'}`}>
                                  {isNumeric ? `${value}/100` : value}
                                </span>
                                
                                {/* Score Comparison */}
                                {row.showComparison && candidateIndex > 0 && typeof value === 'number' && (
                                  <div className="flex items-center space-x-1">
                                    {(() => {
                                      const firstScore = row.format(selectedCandidates[0][row.key as keyof Candidate] as any, selectedCandidates[0]);
                                      const diff = getScoreDifference(value, firstScore as number);
                                      const Icon = diff.icon;
                                      return (
                                        <div className={`flex items-center space-x-1 text-${diff.color}-600`}>
                                          <Icon className="w-3 h-3" />
                                          <span className="text-xs font-medium">{diff.text}</span>
                                        </div>
                                      );
                                    })()}
                                  </div>
                                )}
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Quick Actions */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  Comparing {selectedCandidates.length} candidates • 
                  Top score: {Math.max(...selectedCandidates.map(c => c.overall_score))}/100
                </div>
                
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default CandidateComparison;