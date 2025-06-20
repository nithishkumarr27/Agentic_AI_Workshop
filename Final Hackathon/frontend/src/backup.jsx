

// import React, { useState, useEffect } from 'react';

// function App() {
//   // State for all agents
//   const [learnerId, setLearnerId] = useState('');
//   const [codeInput, setCodeInput] = useState('');
//   const [quizLogs, setQuizLogs] = useState('');
//   const [detectionResults, setDetectionResults] = useState(null);
//   const [classificationResults, setClassificationResults] = useState(null);
//   const [interventionResults, setInterventionResults] = useState(null);
// // Add to your existing state
// const [quizData, setQuizData] = useState(null);
// const [userAnswers, setUserAnswers] = useState([]);
// const [quizResults, setQuizResults] = useState(null);
// const [isPreTest, setIsPreTest] = useState(true);
// const [currentIntervention, setCurrentIntervention] = useState(null);
//   const [roadmapResults, setRoadmapResults] = useState(null);
//   const [recoveryResults, setRecoveryResults] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState('');

//   // API call handler
//   const callAgent = async (endpoint, data) => {
//     setLoading(true);
//     setError('');
//     try {
//       const response = await fetch(`http://localhost:5000/api/${endpoint}`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(data),
//       });
      
//       if (!response.ok) throw new Error('Agent processing failed');
//       return await response.json();
//     } catch (err) {
//       setError(err.message || 'API connection error');
//       return null;
//     } finally {
//       setLoading(false);
//     }
//   };
// const startQuiz = (intervention, preTest = true) => {
//   setCurrentIntervention(intervention);
//   setIsPreTest(preTest);
//   setQuizData(intervention.assessment[preTest ? 'pre_test' : 'post_test']);
//   setUserAnswers(Array(intervention.assessment[preTest ? 'pre_test' : 'post_test'].length).fill(null));
//   setQuizResults(null);
// };
// // Add to your state
// const [quiz, setQuiz] = useState({
//   questions: [],
//   answers: [],
//   results: null
// });

// // Modified startQuiz function


// // New validateQuiz function
// const validateQuiz = () => {
//   const { questions, answers } = quiz;
//   let correct = 0;
  
//   const results = questions.map((question, index) => {
//     const isCorrect = answers[index] === question.answer;
//     if (isCorrect) correct++;
//     return {
//       question: question.question,
//       userAnswer: answers[index],
//       correctAnswer: question.answer,
//       isCorrect
//     };
//   });

//   const score = Math.round((correct / questions.length) * 100);
//   const passed = score >= currentIntervention.assessment.success_threshold;

//   setQuiz(prev => ({ ...prev, results: { score, passed, details: results } }));
  
//   // Automatically proceed if post-test passed
//   if (!isPreTest && passed) {
//     proceedToRoadmap(score);
//   }
// };

// // New proceedToRoadmap function
// const proceedToRoadmap = async (score) => {
//   setLoading(true);
//   try {
//     // Store results and get interventions
//     const response = await callAgent('store-results', {
//       learnerId,
//       interventionId: currentIntervention.concept,
//       score,
//       isPreTest
//     });

//     // Then proceed to roadmap adjustment
//     if (response) {
//       await runRoadmapAdjustment();
//     }
//   } catch (err) {
//     setError(err.message);
//   } finally {
//     setLoading(false);
//   }
// };

// // Update your answer selection handler


// // const submitQuiz = async () => {
// //   setLoading(true);
// //   try {
// //     const response = await fetch('http://localhost:5000/api/validate-quiz', {
// //       method: 'POST',
// //       headers: { 'Content-Type': 'application/json' },
// //       body: JSON.stringify({
// //         learnerId,
// //         interventionId: currentIntervention.concept,
// //         answers: userAnswers,
// //         isPreTest
// //       })
// //     });

// //     if (!response.ok) throw new Error('Quiz validation failed');
// //     const result = await response.json();
// //     setQuizResults(result);

// //     // Update local intervention data with new metrics
// //     if (interventionResults) {
// //       const updatedInterventions = [...interventionResults.interventions];
// //       const interventionIndex = updatedInterventions.findIndex(
// //         i => i.concept === currentIntervention.concept
// //       );
      
// //       if (interventionIndex >= 0) {
// //         updatedInterventions[interventionIndex].metrics = result.metrics;
// //         setInterventionResults({ interventions: updatedInterventions });
// //       }
// //     }
// //   } catch (err) {
// //     setError(err.message);
// //   } finally {
// //     setLoading(false);
// //   }
// // };
//   // Agent 1: Misconception Detection
//   const runDetection = async () => {
//     const data = { learnerId, code: codeInput, quizLogs };
//     const result = await callAgent('detect', data);
//     if (result) setDetectionResults(result);
//   };

//   // Agent 2: Misconception Classification
//   const runClassification = async () => {
//     if (!detectionResults) return;
//     const data = { 
//       learnerId,
//       candidates: detectionResults.candidates 
//     };
//     const result = await callAgent('classify', data);
//     if (result) setClassificationResults(result);
//   };

//   // Agent 3: Correction Intervention
//   const runIntervention = async () => {
//     if (!classificationResults) return;
//     const data = { 
//       learnerId,
//       misconceptions: classificationResults.misconceptions 
//     };
//     const result = await callAgent('correct', data);
//     if (result) setInterventionResults(result);
//   };

//   // Agent 4: Roadmap Adjustment
//   const runRoadmapAdjustment = async () => {
//     if (!interventionResults) return;
//     const data = { 
//       learnerId,
//       interventions: interventionResults.interventions 
//     };
//     const result = await callAgent('adjust-roadmap', data);
//     if (result) setRoadmapResults(result);
//   };

//   // Agent 5: Confidence Recovery Tracker
//   const runRecoveryTracker = async () => {
//     if (!roadmapResults) return;
//     const data = { 
//       learnerId,
//       roadmap: roadmapResults.roadmap 
//     };
//     const result = await callAgent('track-recovery', data);
//     if (result) setRecoveryResults(result);
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 p-6">
//       <header className="max-w-6xl mx-auto mb-12 text-center">
//         <h1 className="text-4xl font-bold text-indigo-800 mb-2">
//           Misconception-Driven Learning Path Correction
//         </h1>
//         <p className="text-lg text-indigo-600">
//           Detect, classify, and correct learning misconceptions
//         </p>
//       </header>

//       <main className="max-w-6xl mx-auto space-y-12">
//         {/* Learner Identification */}
//         <section className="bg-white rounded-xl shadow-lg p-6">
//           <h2 className="text-2xl font-semibold text-gray-800 mb-4">Learner Profile</h2>
//           <div className="flex flex-col md:flex-row gap-4">
//             <input
//               type="text"
//               value={learnerId}
//               onChange={(e) => setLearnerId(e.target.value)}
//               placeholder="Enter Learner ID"
//               className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
//             />
//             <button
//               onClick={() => {
//                 setDetectionResults(null);
//                 setClassificationResults(null);
//                 setInterventionResults(null);
//                 setRoadmapResults(null);
//                 setRecoveryResults(null);
//               }}
//               className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
//             >
//               Reset Session
//             </button>
//           </div>
//         </section>

//         {/* Agent 1: Misconception Detection */}
//         <section className="bg-white rounded-xl shadow-lg p-6">
//           <div className="flex items-center justify-between mb-4">
//             <h2 className="text-2xl font-semibold text-gray-800">
//               <span className="inline-block w-8 h-8 bg-indigo-600 text-white rounded-full text-center mr-2">1</span>
//               Misconception Detection
//             </h2>
//             <button
//               onClick={runDetection}
//               disabled={loading || !learnerId}
//               className={`px-6 py-2 rounded-lg transition-colors ${
//                 loading || !learnerId
//                   ? 'bg-gray-300 cursor-not-allowed'
//                   : 'bg-indigo-600 text-white hover:bg-indigo-700'
//               }`}
//             >
//               Detect Errors
//             </button>
//           </div>

//           <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
//             <div>
//               <label className="block text-gray-700 mb-2">Code Input</label>
//               <textarea
//                 value={codeInput}
//                 onChange={(e) => setCodeInput(e.target.value)}
//                 rows={8}
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none font-mono text-sm"
//                 placeholder="Paste learner's code here..."
//               />
//             </div>
//             <div>
//               <label className="block text-gray-700 mb-2">Quiz Logs</label>
//               <textarea
//                 value={quizLogs}
//                 onChange={(e) => setQuizLogs(e.target.value)}
//                 rows={8}
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none font-mono text-sm"
//                 placeholder="Enter quiz logs or behavioral patterns..."
//               />
//             </div>
//           </div>

//           {detectionResults && (
//             <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
//               <h3 className="text-lg font-medium text-blue-800 mb-2">Detection Results</h3>
//               <div className="space-y-3">
//                  {Array.isArray(detectionResults.candidates)
//         ? detectionResults.candidates.map((candidate, idx) => (
//              <div key={idx} className="p-3 bg-white rounded-lg border border-blue-100">
//                     <div className="flex justify-between">
//                       <span className="font-medium">{candidate.tag}</span>
//                       <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
//                         Confidence: {candidate.confidence}%
//                       </span>
//                     </div>
//                     <p className="mt-1 text-sm text-gray-600">{candidate.description}</p>
//                   </div>
//           ))
//         : (
//           <div className="p-3 bg-white rounded-lg border border-red-100">
           
//             <p className="mt-1 text-sm text-gray-600">
//               {detectionResults.candidates}
//             </p>
//           </div>
//         )
//       }
                
//               </div>
//             </div>
//           )}
//         </section>

//         {/* Agent 2: Misconception Classification */}
//         <section className="bg-white rounded-xl shadow-lg p-6">
//           <div className="flex items-center justify-between mb-4">
//             <h2 className="text-2xl font-semibold text-gray-800">
//               <span className="inline-block w-8 h-8 bg-indigo-600 text-white rounded-full text-center mr-2">2</span>
//               Misconception Classification
//             </h2>
//             <button
//               onClick={runClassification}
//               disabled={loading || !detectionResults}
//               className={`px-6 py-2 rounded-lg transition-colors ${
//                 loading || !detectionResults
//                   ? 'bg-gray-300 cursor-not-allowed'
//                   : 'bg-indigo-600 text-white hover:bg-indigo-700'
//               }`}
//             >
//               Classify Errors
//             </button>
//           </div>

//           {classificationResults && (
//             <div className="mt-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
//               <h3 className="text-lg font-medium text-purple-800 mb-2">Classification Results</h3>
//               <div className="space-y-4">
//                 {classificationResults.misconceptions.map((misconception, idx) => (
//                   <div key={idx} className="p-4 bg-white rounded-lg border border-purple-100">
//                     <div className="flex justify-between items-start">
//                       <div>
//                         <h4 className="font-semibold text-lg">{misconception.concept}</h4>
//                         <span className="inline-block mt-1 px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
//                           {misconception.category}
//                         </span>
//                       </div>
//                       <div className="flex items-center space-x-2">
//                         <span className="text-sm font-medium">Confidence: {misconception.confidence}%</span>
//                         <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
//                           <div 
//                             className={`h-full ${
//                               misconception.confidence > 75 ? 'bg-green-500' : 
//                               misconception.confidence > 50 ? 'bg-yellow-500' : 'bg-red-500'
//                             }`}
//                             style={{ width: `${misconception.confidence}%` }}
//                           ></div>
//                         </div>
//                       </div>
//                     </div>
//                     <div className="mt-3">
//                       <h5 className="font-medium text-gray-700">Explanation:</h5>
//                       <p className="text-gray-600">{misconception.explanation}</p>
//                     </div>
//                     <div className="mt-3">
//                       <h5 className="font-medium text-gray-700">RAG Sources:</h5>
//                       <ul className="list-disc pl-5 text-sm text-gray-600">
//                         {misconception.rag_sources.map((source, sIdx) => (
//                           <li key={sIdx}>{source}</li>
//                         ))}
//                       </ul>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           )}
//         </section>

//         {/* Agent 3: Correction Intervention */}
//         <section className="bg-white rounded-xl shadow-lg p-6">
//           <div className="flex items-center justify-between mb-4">
//             <h2 className="text-2xl font-semibold text-gray-800">
//               <span className="inline-block w-8 h-8 bg-indigo-600 text-white rounded-full text-center mr-2">3</span>
//               Correction Intervention
//             </h2>
//             <button
//               onClick={runIntervention}
//               disabled={loading || !classificationResults}
//               className={`px-6 py-2 rounded-lg transition-colors ${
//                 loading || !classificationResults
//                   ? 'bg-gray-300 cursor-not-allowed'
//                   : 'bg-indigo-600 text-white hover:bg-indigo-700'
//               }`}
//             >
//               Generate Interventions
//             </button>
//           </div>

// {interventionResults && (
//   <div className="mt-4 p-4 bg-teal-50 rounded-lg border border-teal-200">
//     <h3 className="text-lg font-medium text-teal-800 mb-2">Intervention Plan</h3>
    
//     {/* Concept Header */}
//     <div className="mb-4 p-3 bg-teal-100 rounded-lg">
//       <h4 className="font-bold text-teal-800">{interventionResults.interventions[0]?.concept}</h4>
//     </div>
    
//     {/* Analogy & Explanation */}
//     <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
//       <div className="p-4 bg-white rounded-lg border border-teal-100">
//         <h4 className="font-semibold text-lg text-teal-700">Analogy</h4>
//         <p className="mt-2 text-gray-600">{interventionResults.interventions[0]?.analogy}</p>
//       </div>
//       <div className="p-4 bg-white rounded-lg border border-teal-100">
//         <h4 className="font-semibold text-lg text-teal-700">Technical Explanation</h4>
//         <p className="mt-2 text-gray-600">{interventionResults.interventions[0]?.explanation}</p>
//       </div>
//     </div>
    
//     {/* Interactive Content */}
//     <h4 className="font-semibold text-lg text-teal-700 mb-3">Interactive Content</h4>
//     <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
//       {interventionResults.interventions[0]?.interactive_content?.map((item, idx) => (
//         <div key={idx} className="p-4 bg-white rounded-lg border border-teal-100">
//           <div className="flex items-start mb-2">
//             <span className="px-2 py-1 bg-teal-100 text-teal-800 text-xs rounded-full mr-2">
//               {item.type.replace('_', ' ')}
//             </span>
//             <h5 className="font-medium">{item.title}</h5>
//           </div>
//           <p className="text-sm text-gray-600 mb-3">{item.description}</p>
//           <button className="px-3 py-1 bg-teal-600 text-white text-sm rounded hover:bg-teal-700">
//             Launch Activity
//           </button>
//         </div>
//       ))}
//     </div>
//     {quiz.questions.length > 0 && (
//   <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
//     <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
//       <h2 className="text-xl font-bold mb-4">
//         {isPreTest ? 'Pre-Test' : 'Post-Test'}: {currentIntervention.concept}
//       </h2>

//       {!quiz.results ? (
//         <>
//           {quiz.questions.map((question, index) => (
//             <div key={index} className="mb-6 p-4 border rounded-lg">
//               <p className="font-medium mb-3">{question.question}</p>
//               <div className="space-y-2">
//                 {question.options.map((option, optIndex) => (
//                   <label key={optIndex} className="flex items-center space-x-2 cursor-pointer">
//                     <input
//                       type="radio"
//                       name={`q-${index}`}
//                       checked={quiz.answers[index] === option}
//                       onChange={() => handleAnswerSelect(index, option)}
//                       className="h-4 w-4 text-indigo-600"
//                     />
//                     <span>{option}</span>
//                   </label>
//                 ))}
//               </div>
//             </div>
//           ))}

//           <div className="flex justify-between mt-6">
//             <button
//               onClick={() => setQuiz({ questions: [], answers: [], results: null })}
//               className="px-4 py-2 border rounded-lg hover:bg-gray-100"
//             >
//               Cancel
//             </button>
//             <button
//               onClick={validateQuiz}
//               disabled={quiz.answers.length !== quiz.questions.length}
//               className={`px-4 py-2 rounded-lg text-white ${
//                 quiz.answers.length !== quiz.questions.length
//                   ? 'bg-gray-400 cursor-not-allowed'
//                   : 'bg-indigo-600 hover:bg-indigo-700'
//               }`}
//             >
//               Submit Quiz
//             </button>
//           </div>
//         </>
//       ) : (
//         <div>
//           <div className={`p-4 rounded-lg mb-6 text-center ${
//             quiz.results.passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
//           }`}>
//             <h3 className="font-bold text-lg">
//               {quiz.results.passed ? 'Passed!' : 'Needs Improvement'}
//             </h3>
//             <p>Score: {quiz.results.score}%</p>
//             <p>Passing Threshold: {currentIntervention.assessment.success_threshold}%</p>
//           </div>

//           {quiz.results.details.map((result, index) => (
//             <div key={index} className={`mb-4 p-3 rounded-lg ${
//               result.isCorrect ? 'bg-green-50' : 'bg-red-50'
//             }`}>
//               <p className="font-medium">{result.question}</p>
//               <p>Your answer: {result.userAnswer || 'Not answered'}</p>
//               {!result.isCorrect && (
//                 <p>Correct answer: {result.correctAnswer}</p>
//               )}
//             </div>
//           ))}

//           <button
//             onClick={() => {
//               setQuiz({ questions: [], answers: [], results: null });
//               if (!isPreTest && quiz.results.passed) {
//                 proceedToRoadmap(quiz.results.score);
//               }
//             }}
//             className="w-full mt-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
//           >
//             {isPreTest ? 'Start Learning' : 'Continue to Roadmap'}
//           </button>
//         </div>
//       )}
//     </div>
//   </div>
// )}
//     {/* Micro Challenges */}
//     <h4 className="font-semibold text-lg text-teal-700 mb-3">Micro Challenges</h4>
//     <div className="space-y-3 mb-6">
//       {interventionResults.interventions[0]?.micro_challenges?.map((challenge, idx) => (
//         <div key={idx} className="p-3 bg-white rounded-lg border border-teal-100">
//           <div className="font-medium">{challenge.title}</div>
//           <p className="text-sm text-gray-600 mt-1">{challenge.description}</p>
//           {challenge.code && (
//             <pre className="bg-gray-100 p-2 rounded mt-2 overflow-x-auto text-xs">
//               {challenge.code}
//             </pre>
//           )}
//           <details className="mt-2">
//             <summary className="text-teal-600 cursor-pointer text-sm">Show Solution</summary>
//             <pre className="bg-gray-100 p-2 rounded mt-1 overflow-x-auto text-xs">
//               {challenge.solution}
//             </pre>
//           </details>
//         </div>
//       ))}
//     </div>
    
//     {/* Assessment & Metrics */}
//     <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//       <div className="p-4 bg-white rounded-lg border border-teal-100">
//         <h4 className="font-semibold text-lg text-teal-700 mb-2">Assessment</h4>
//         <div className="flex justify-between mb-2">
//           <span>Pre-test:</span>
//           <span>{interventionResults.interventions[0]?.assessment?.pre_test?.length || 0} questions</span>
//         </div>
//         <div className="flex justify-between">
//           <span>Post-test:</span>
//           <span>{interventionResults.interventions[0]?.assessment?.post_test?.length || 0} questions</span>
//         </div>
//         <button   onClick={() => startQuiz(interventionResults.interventions[0], true)} className="mt-3 w-full py-2 bg-teal-600 text-white rounded hover:bg-teal-700">
//           Start Assessment
//         </button>
//       </div>
      
//       <div className="p-4 bg-white rounded-lg border border-teal-100">
//         <h4 className="font-semibold text-lg text-teal-700 mb-2">Progress Tracking</h4>
//         <div className="flex justify-between mb-1">
//           <span>Time Spent:</span>
//           <span>{interventionResults.interventions[0]?.metrics?.time_spent || 0} mins</span>
//         </div>
//         <div className="flex justify-between mb-1">
//           <span>Success Rate:</span>
//           <span>{interventionResults.interventions[0]?.metrics?.success_rate || 0}%</span>
//         </div>
//         <div className="flex justify-between">
//           <span>Completed:</span>
//           <span>{interventionResults.interventions[0]?.metrics?.completion_count || 0} times</span>
//         </div>
//       </div>
//     </div>
//   </div>
// )}
//         </section>

//         {/* Agent 4: Roadmap Adjustment */}
//         <section className="bg-white rounded-xl shadow-lg p-6">
//           <div className="flex items-center justify-between mb-4">
//             <h2 className="text-2xl font-semibold text-gray-800">
//               <span className="inline-block w-8 h-8 bg-indigo-600 text-white rounded-full text-center mr-2">4</span>
//               Roadmap Adjustment
//             </h2>
//             <button
//               onClick={runRoadmapAdjustment}
//               disabled={loading || !interventionResults}
//               className={`px-6 py-2 rounded-lg transition-colors ${
//                 loading || !interventionResults
//                   ? 'bg-gray-300 cursor-not-allowed'
//                   : 'bg-indigo-600 text-white hover:bg-indigo-700'
//               }`}
//             >
//               Adjust Learning Path
//             </button>
//           </div>

//           {roadmapResults && (
//             <div className="mt-4 p-4 bg-amber-50 rounded-lg border border-amber-200">
//               <h3 className="text-lg font-medium text-amber-800 mb-4">Adjusted Learning Roadmap</h3>
//               <div className="relative">
//                 {/* Roadmap timeline */}
//                 <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-amber-300"></div>
                
//                 <div className="space-y-6 pl-10">
//                   {roadmapResults.roadmap.modules.map((module, idx) => (
//                     <div key={idx} className="relative">
//                       <div className="absolute -left-7 top-4 w-6 h-6 rounded-full bg-amber-500 flex items-center justify-center text-white font-bold">
//                         {idx + 1}
//                       </div>
                      
//                       <div className={`p-4 rounded-lg border ${
//                         module.status === 'completed' 
//                           ? 'bg-green-50 border-green-200' 
//                           : module.status === 'current'
//                           ? 'bg-blue-50 border-blue-200 shadow-sm'
//                           : module.status === 'adjusted'
//                           ? 'bg-amber-100 border-amber-300'
//                           : 'bg-white border-gray-200'
//                       }`}>
//                         <div className="flex justify-between">
//                           <h4 className="font-semibold">{module.title}</h4>
//                           {module.status === 'adjusted' && (
//                             <span className="px-2 py-1 bg-amber-500 text-white text-xs rounded-full">
//                               Adjusted
//                             </span>
//                           )}
//                         </div>
//                         <p className="mt-1 text-sm text-gray-600">{module.description}</p>
//                         <div className="mt-3 flex flex-wrap gap-2">
//                           {module.tags.map((tag, tagIdx) => (
//                             <span 
//                               key={tagIdx} 
//                               className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full"
//                             >
//                               {tag}
//                             </span>
//                           ))}
//                         </div>
//                       </div>
//                     </div>
//                   ))}
//                 </div>
//               </div>
//             </div>
//           )}
//         </section>

//         {/* Agent 5: Confidence Recovery Tracker */}
//         <section className="bg-white rounded-xl shadow-lg p-6">
//           <div className="flex items-center justify-between mb-4">
//             <h2 className="text-2xl font-semibold text-gray-800">
//               <span className="inline-block w-8 h-8 bg-indigo-600 text-white rounded-full text-center mr-2">5</span>
//               Confidence Recovery Tracker
//             </h2>
//             <button
//               onClick={runRecoveryTracker}
//               disabled={loading || !roadmapResults}
//               className={`px-6 py-2 rounded-lg transition-colors ${
//                 loading || !roadmapResults
//                   ? 'bg-gray-300 cursor-not-allowed'
//                   : 'bg-indigo-600 text-white hover:bg-indigo-700'
//               }`}
//             >
//               Track Recovery Progress
//             </button>
//           </div>

//           {recoveryResults && (
//             <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
//               <h3 className="text-lg font-medium text-green-800 mb-4">Recovery Progress</h3>
              
//               <div className="mb-6">
//                 <div className="flex justify-between mb-2">
//                   <span className="font-medium">Confidence Index</span>
//                   <span className="font-bold text-green-700">{recoveryResults.confidence_index}%</span>
//                 </div>
//                 <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
//                   <div 
//                     className="h-full bg-green-500 transition-all duration-1000 ease-out"
//                     style={{ width: `${recoveryResults.confidence_index}%` }}
//                   ></div>
//                 </div>
//               </div>
              
//               <h4 className="font-medium text-gray-700 mb-3">Recovery Timeline</h4>
//               <div className="space-y-4">
//                 {recoveryResults.timeline.map((event, idx) => (
//                   <div key={idx} className="flex">
//                     <div className="flex flex-col items-center mr-4">
//                       <div className={`w-3 h-3 rounded-full ${
//                         event.status === 'recovered' ? 'bg-green-500' : 
//                         event.status === 'in-progress' ? 'bg-yellow-500' : 'bg-red-500'
//                       }`}></div>
//                       {idx < recoveryResults.timeline.length - 1 && (
//                         <div className="w-0.5 h-full bg-gray-300"></div>
//                       )}
//                     </div>
//                     <div className="pb-4">
//                       <p className="font-medium">{event.date}</p>
//                       <p className="text-gray-600">{event.description}</p>
//                       <div className="mt-2 flex flex-wrap gap-1">
//                         {event.flags?.map((flag, flagIdx) => (
//                           <span 
//                             key={flagIdx} 
//                             className={`px-2 py-1 text-xs rounded-full ${
//                               flag.type === 'critical' 
//                                 ? 'bg-red-100 text-red-800' 
//                                 : 'bg-yellow-100 text-yellow-800'
//                             }`}
//                           >
//                             {flag.message}
//                           </span>
//                         ))}
//                       </div>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           )}
//         </section>
//       </main>

//       {/* Loading and Error Indicators */}
//       {loading && (
//         <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
//           <div className="bg-white p-6 rounded-xl shadow-xl flex flex-col items-center">
//             <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
//             <p className="text-lg font-medium text-gray-800">Processing with AI agents...</p>
//           </div>
//         </div>
//       )}

//       {error && (
//         <div className="fixed bottom-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg max-w-md z-50">
//           <div className="flex justify-between items-start">
//             <p>{error}</p>
//             <button 
//               onClick={() => setError('')}
//               className="ml-4 text-white hover:text-gray-200"
//             >
//               <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
//                 <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
//               </svg>
//             </button>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }

// export default App;
