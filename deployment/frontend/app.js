const { useState, useEffect } = React;

function App() {
    const [activeTab, setActiveTab] = useState("analyzer"); // 'analyzer' | 'global_jobs'
    const [sampleData, setSampleData] = useState({ personas: [], jobs: [] });
    
    // Editor State
    const [resumeText, setResumeText] = useState("");
    const [jdText, setJdText] = useState("");
    const [jobTitle, setJobTitle] = useState("Senior AI / ML Research Engineer");
    
    // Result State
    const [matchResult, setMatchResult] = useState(null);
    const [globalMatches, setGlobalMatches] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    // Load initial sample data on mount
    useEffect(() => {
        fetch("/api/v1/sample-data")
            .then(res => res.json())
            .then(data => {
                setSampleData(data);
                if (data.personas && data.personas.length > 0) {
                    setResumeText(data.personas[0].resume_text);
                }
                if (data.jobs && data.jobs.length > 0) {
                    setJdText(data.jobs[0].jd_text);
                    setJobTitle(data.jobs[0].title);
                }
            })
            .catch(err => console.log("Failed loading sample data:", err));
    }, []);

    // Trigger Single Match Analysis
    const handleAnalyze = async () => {
        if (!resumeText.trim() || !jdText.trim()) {
            setErrorMsg("Please enter both resume text and job description.");
            return;
        }
        setErrorMsg("");
        setLoading(true);
        try {
            const res = await fetch("/api/v1/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_text: resumeText,
                    jd_text: jdText,
                    job_title: jobTitle
                })
            });
            const data = await res.json();
            if (res.ok) {
                setMatchResult(data.match_result);
            } else {
                setErrorMsg(data.detail || "Analysis failed.");
            }
        } catch (err) {
            setErrorMsg("Network error communicating with Alture AI API.");
        } finally {
            setLoading(false);
        }
    };

    // Trigger Batch Global Jobs Match
    const handleMatchGlobalJobs = async () => {
        if (!resumeText.trim()) {
            setErrorMsg("Please provide a resume to match against global job feeds.");
            return;
        }
        setErrorMsg("");
        setLoading(true);
        try {
            const res = await fetch("/api/v1/match-jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_text: resumeText
                })
            });
            const data = await res.json();
            if (res.ok) {
                setGlobalMatches(data.ranked_jobs);
                setActiveTab("global_jobs");
            } else {
                setErrorMsg(data.detail || "Global matching failed.");
            }
        } catch (err) {
            setErrorMsg("Network error connecting to API.");
        } finally {
            setLoading(false);
        }
    };

    const handleSelectPersona = (persona) => {
        setResumeText(persona.resume_text);
        setErrorMsg("");
    };

    const handleSelectJob = (job) => {
        setJdText(job.jd_text);
        setJobTitle(job.title);
        setErrorMsg("");
    };

    return (
        <div className="app-container">
            {/* Navbar */}
            <nav className="navbar">
                <div className="brand-container">
                    <div className="brand-logo">A</div>
                    <div>
                        <span className="brand-title">Alture</span>
                        <span className="brand-badge">RESEARCH & SAAS</span>
                    </div>
                </div>

                <div className="nav-links">
                    <div className="nav-tabs">
                        <button 
                            className={`nav-tab ${activeTab === 'analyzer' ? 'active' : ''}`}
                            onClick={() => setActiveTab('analyzer')}
                        >
                            Compatibility Analyzer
                        </button>
                        <button 
                            className={`nav-tab ${activeTab === 'global_jobs' ? 'active' : ''}`}
                            onClick={() => {
                                setActiveTab('global_jobs');
                                if (globalMatches.length === 0 && resumeText) {
                                    handleMatchGlobalJobs();
                                }
                            }}
                        >
                            Global Opportunity Feed
                        </button>
                    </div>

                    <a href="/docs" target="_blank" rel="noreferrer" className="api-docs-link">
                        <span>API Reference</span>
                        <span>↗</span>
                    </a>
                </div>
            </nav>

            {/* Main Content Area */}
            <main className="main-content">
                {/* Header */}
                <header className="page-header">
                    <h1 className="page-title">
                        {activeTab === 'analyzer' ? "Candidate–Job Semantic Compatibility" : "Multi-Source Opportunity Feed"}
                    </h1>
                    <p className="page-subtitle">
                        {activeTab === 'analyzer' 
                            ? "A multi-modal intelligence engine fusing dense Transformer embeddings, 500+ technical skill ontology overlap, and multi-task calibrated scoring."
                            : "Explore and rank candidate fit across international technology openings in real time."
                        }
                    </p>
                </header>

                {/* Persona Quick Fill Bar */}
                <div className="persona-selector">
                    <span className="persona-label">✦ Curated Candidate Profiles:</span>
                    {sampleData.personas.map(p => (
                        <button key={p.id} className="persona-btn" onClick={() => handleSelectPersona(p)}>
                            {p.name} — {p.title.split(' ')[0]} {p.title.split(' ')[1] || ''}
                        </button>
                    ))}
                </div>

                {errorMsg && (
                    <div style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#991b1b', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                        ⚠️ {errorMsg}
                    </div>
                )}

                {/* TAB 1: ATS MATCH ANALYZER */}
                {activeTab === 'analyzer' && (
                    <>
                        <div className="editor-grid">
                            {/* Resume Input */}
                            <div className="editor-card">
                                <div className="editor-header">
                                    <span className="editor-title">Curriculum Vitae / Resume</span>
                                    <span className="editor-meta">{resumeText.split(/\s+/).filter(Boolean).length} words</span>
                                </div>
                                <textarea 
                                    className="editor-textarea"
                                    placeholder="Paste candidate resume text..."
                                    value={resumeText}
                                    onChange={(e) => setResumeText(e.target.value)}
                                />
                            </div>

                            {/* Job Description Input */}
                            <div className="editor-card">
                                <div className="editor-header">
                                    <span className="editor-title">Job Specification & Requirements</span>
                                    <div style={{ display: 'flex', gap: '6px' }}>
                                        {sampleData.jobs.map(j => (
                                            <button 
                                                key={j.id} 
                                                style={{ fontSize: '0.74rem', fontWeight: '600', background: '#ffffff', color: '#57534e', border: '1px solid #d6cbba', borderRadius: '4px', padding: '3px 8px', cursor: 'pointer' }}
                                                onClick={() => handleSelectJob(j)}
                                            >
                                                {j.title.split(' ')[0]} {j.title.split(' ')[1]}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <textarea 
                                    className="editor-textarea"
                                    placeholder="Paste target position description..."
                                    value={jdText}
                                    onChange={(e) => setJdText(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="action-bar">
                            <button 
                                className="secondary-btn"
                                onClick={handleMatchGlobalJobs}
                                disabled={loading}
                            >
                                Rank Across Global Feed
                            </button>
                            <button 
                                className="primary-btn"
                                onClick={handleAnalyze}
                                disabled={loading}
                            >
                                {loading ? "Computing NLP Signals..." : "Evaluate Compatibility"}
                            </button>
                        </div>

                        {/* Analysis Results View */}
                        {matchResult && (
                            <section className="results-container">
                                <div className="results-header">
                                    <div>
                                        <h2 style={{ fontSize: '1.35rem', fontFamily: 'var(--font-serif)', fontWeight: '600', color: 'var(--text-heading)' }}>
                                            Compatibility & Qualification Report
                                        </h2>
                                        <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                                            Benchmarked against <strong style={{ color: 'var(--mustard-dark)' }}>{jobTitle}</strong>
                                        </p>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase' }}>Classification Confidence:</span>
                                        <span style={{ fontSize: '0.9rem', fontFamily: 'var(--font-mono)', color: 'var(--text-heading)', fontWeight: '700' }}>
                                            {(matchResult.fit_confidence * 100).toFixed(0)}%
                                        </span>
                                    </div>
                                </div>

                                {/* Score Hero & Key Metrics */}
                                <div className="score-hero">
                                    <div className="gauge-box">
                                        <div className={`gauge-score ${matchResult.fit_tier === 'Good Fit' ? 'good' : matchResult.fit_tier === 'Potential Fit' ? 'potential' : 'poor'}`}>
                                            {matchResult.ats_score.toFixed(1)}%
                                        </div>
                                        <span className="gauge-label">ATS Compatibility Index</span>
                                        <span className={`fit-badge ${matchResult.fit_tier === 'Good Fit' ? 'good' : matchResult.fit_tier === 'Potential Fit' ? 'potential' : 'poor'}`}>
                                            {matchResult.fit_tier}
                                        </span>
                                    </div>

                                    <div className="metrics-grid">
                                        <div className="metric-card">
                                            <div className="metric-card-title">Semantic Context Match</div>
                                            <div className="metric-card-val" style={{ color: '#0f766e' }}>
                                                {(matchResult.semantic_similarity * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-card-title">Skill Recall Ratio</div>
                                            <div className="metric-card-val" style={{ color: '#15803d' }}>
                                                {(matchResult.skill_analysis.skill_recall_score * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-card-title">Skill Jaccard Overlap</div>
                                            <div className="metric-card-val" style={{ color: '#4338ca' }}>
                                                {(matchResult.skill_analysis.skill_jaccard_score * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-card-title">Length Ratio</div>
                                            <div className="metric-card-val" style={{ color: 'var(--mustard-dark)' }}>
                                                {matchResult.word_count_ratio}x
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Skill Breakdown Badges */}
                                <div className="skills-section">
                                    <div className="skills-box">
                                        <div className="skills-box-header">
                                            <span className="skills-box-title" style={{ color: 'var(--match-green-text)' }}>
                                                ✓ Matched Competencies ({matchResult.skill_analysis.matched_skills.length})
                                            </span>
                                        </div>
                                        <div className="pill-container">
                                            {matchResult.skill_analysis.matched_skills.length > 0 ? (
                                                matchResult.skill_analysis.matched_skills.map(s => (
                                                    <span key={s} className="skill-pill matched">✓ {s}</span>
                                                ))
                                            ) : (
                                                <span className="skill-pill empty">No exact skill matches identified.</span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="skills-box">
                                        <div className="skills-box-header">
                                            <span className="skills-box-title" style={{ color: 'var(--missing-rose-text)' }}>
                                                ✦ Missing Required Skills ({matchResult.skill_analysis.missing_skills.length})
                                            </span>
                                        </div>
                                        <div className="pill-container">
                                            {matchResult.skill_analysis.missing_skills.length > 0 ? (
                                                matchResult.skill_analysis.missing_skills.map(s => (
                                                    <span key={s} className="skill-pill missing">+ {s}</span>
                                                ))
                                            ) : (
                                                <span className="skill-pill empty">All mandatory skills matched!</span>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Actionable Recommendations */}
                                <div className="recommendations-box">
                                    <div className="rec-title">
                                        Strategic Resume Optimization Guidance
                                    </div>
                                    <ul className="rec-list">
                                        {matchResult.recommendations.map((rec, idx) => (
                                            <li key={idx} className="rec-item">{rec}</li>
                                        ))}
                                    </ul>
                                </div>
                            </section>
                        )}
                    </>
                )}

                {/* TAB 2: GLOBAL JOB DISCOVERY & RANKING */}
                {activeTab === 'global_jobs' && (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.75rem' }}>
                            <span style={{ fontSize: '0.98rem', color: 'var(--text-muted)' }}>
                                Showing {globalMatches.length} openings ranked by suitability for the current candidate profile.
                            </span>
                            <button className="primary-btn" style={{ padding: '7px 18px', fontSize: '0.88rem' }} onClick={handleMatchGlobalJobs} disabled={loading}>
                                {loading ? "Scoring..." : "Refresh Rankings"}
                            </button>
                        </div>

                        {globalMatches.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '4rem 2rem', background: '#ffffff', borderRadius: '16px', border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-card)' }}>
                                <p style={{ color: 'var(--text-muted)', marginBottom: '1.25rem', fontSize: '1.05rem' }}>No global openings evaluated yet.</p>
                                <button className="primary-btn" onClick={handleMatchGlobalJobs} disabled={loading}>
                                    Evaluate Against Global Feed
                                </button>
                            </div>
                        ) : (
                            <div className="jobs-grid">
                                {globalMatches.map(job => (
                                    <div key={job.job_id} className="job-card">
                                        <div>
                                            <div className="job-card-header">
                                                <div>
                                                    <h3 className="job-title">{job.title}</h3>
                                                    <div className="job-company">{job.company} • {job.location}</div>
                                                </div>
                                                <div className="job-score-badge" style={{ color: job.fit_tier === 'Good Fit' ? '#15803d' : job.fit_tier === 'Potential Fit' ? 'var(--mustard-dark)' : '#b91c1c' }}>
                                                    {job.ats_score}%
                                                </div>
                                            </div>

                                            <div className="job-details">
                                                <span>✦ {job.type}</span>
                                                {job.salary_range && <span>💰 {job.salary_range}</span>}
                                            </div>

                                            <div style={{ marginBottom: '1.2rem' }}>
                                                <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>MATCHED COMPETENCIES:</div>
                                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                                    {job.matched_skills_sample.map(s => (
                                                        <span key={s} className="skill-pill matched" style={{ fontSize: '0.74rem', padding: '2px 8px' }}>{s}</span>
                                                    ))}
                                                    {job.matched_skills_count > 4 && (
                                                        <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', alignSelf: 'center' }}>+{job.matched_skills_count - 4} more</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="job-footer">
                                            <span className={`fit-badge ${job.fit_tier === 'Good Fit' ? 'good' : job.fit_tier === 'Potential Fit' ? 'potential' : 'poor'}`} style={{ margin: 0 }}>
                                                {job.fit_tier}
                                            </span>
                                            <button 
                                                style={{ padding: '6px 14px', fontSize: '0.84rem', fontWeight: '600', background: 'var(--bg-surface-soft)', color: 'var(--mustard-dark)', border: '1px solid var(--mustard-border)', borderRadius: '6px', cursor: 'pointer' }}
                                                onClick={() => {
                                                    const selected = sampleData.jobs.find(j => j.id === job.job_id);
                                                    if (selected) {
                                                        handleSelectJob(selected);
                                                        setActiveTab('analyzer');
                                                    }
                                                }}
                                            >
                                                Inspect ➔
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="footer">
                <div>
                    <strong>Alture</strong> — Research Architecture for Bilateral Talent Matching & ATS Optimization
                </div>
                <div style={{ marginTop: '4px', color: 'var(--text-muted)' }}>
                    Authored by <strong>Ahmad Mustafa Iqbal</strong> • Built with FastAPI, Sentence-BERT & React
                </div>
            </footer>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
