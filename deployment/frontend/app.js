const { useState, useEffect } = React;

function App() {
    const [activeTab, setActiveTab] = useState("analyzer"); // 'analyzer' | 'global_jobs'
    const [sampleData, setSampleData] = useState({ personas: [], jobs: [] });
    
    // Editor State
    const [resumeText, setResumeText] = useState("");
    const [jdText, setJdText] = useState("");
    const [jobTitle, setJobTitle] = useState("Senior AI / ML Research Engineer");
    
    // Global Multi-Source Search State
    const [searchQuery, setSearchQuery] = useState("AI Engineer");
    const [searchLocation, setSearchLocation] = useState("Pakistan");
    const [rapidApiKey, setRapidApiKey] = useState("");
    const [providerUsed, setProviderUsed] = useState("Pakistan Enterprise Tech Feed");
    const [showKeyModal, setShowKeyModal] = useState(false);

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

    // Trigger Multi-Source Search & Match (Pakistan + Worldwide + LinkedIn/Indeed)
    const handleSearchAndMatch = async (customQuery = null, customLoc = null) => {
        if (!resumeText.trim()) {
            setErrorMsg("Please provide a candidate resume to match against job opportunities.");
            return;
        }
        setErrorMsg("");
        setLoading(true);
        
        const q = customQuery !== null ? customQuery : searchQuery;
        const loc = customLoc !== null ? customLoc : searchLocation;
        
        try {
            const res = await fetch("/api/v1/search-and-match-jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_text: resumeText,
                    query: q || "Software Engineer",
                    location: loc || "Pakistan",
                    provider: "auto",
                    rapidapi_key: rapidApiKey.trim() || null,
                    limit: 15
                })
            });
            const data = await res.json();
            if (res.ok) {
                setGlobalMatches(data.ranked_jobs);
                setProviderUsed(data.provider_used || "Multi-Source Engine");
                setActiveTab("global_jobs");
            } else {
                setErrorMsg(data.detail || "Multi-source matching failed.");
            }
        } catch (err) {
            setErrorMsg("Network error connecting to Job Search API.");
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
                                    handleSearchAndMatch();
                                }
                            }}
                        >
                            Opportunity Search & Feed
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
                        {activeTab === 'analyzer' ? "Candidate–Job Semantic Compatibility" : "Multi-Source Opportunity Search & Ranking"}
                    </h1>
                    <p className="page-subtitle">
                        {activeTab === 'analyzer' 
                            ? "A multi-modal intelligence engine fusing dense Transformer embeddings, 500+ technical skill ontology overlap, and multi-task calibrated scoring."
                            : "Search and rank opportunities across Pakistan (Lahore, Karachi, Islamabad) and Worldwide Remote tech openings in real time."
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
                                onClick={() => handleSearchAndMatch()}
                                disabled={loading}
                            >
                                Search Pakistan & Global Openings
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

                {/* TAB 2: GLOBAL & PAKISTAN MULTI-SOURCE SEARCH & RANKING */}
                {activeTab === 'global_jobs' && (
                    <div>
                        {/* Search Filter Bar */}
                        <div style={{ background: '#ffffff', border: '1px solid var(--border-subtle)', borderRadius: '16px', padding: '1.5rem', marginBottom: '2rem', boxShadow: 'var(--shadow-card)' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr auto', gap: '1rem', alignItems: 'flex-end' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>
                                        🎯 Target Role / Skill Keyword:
                                    </label>
                                    <input 
                                        type="text"
                                        style={{ width: '100%', padding: '10px 14px', border: '1px solid var(--border-medium)', borderRadius: '8px', fontSize: '0.92rem', outline: 'none', background: 'var(--bg-surface-soft)' }}
                                        placeholder="e.g. AI Engineer, Python Developer, Data Scientist..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                    />
                                </div>

                                <div>
                                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>
                                        📍 Target Location:
                                    </label>
                                    <input 
                                        type="text"
                                        style={{ width: '100%', padding: '10px 14px', border: '1px solid var(--border-medium)', borderRadius: '8px', fontSize: '0.92rem', outline: 'none', background: 'var(--bg-surface-soft)' }}
                                        placeholder="e.g. Pakistan, Lahore, Karachi, Remote, USA..."
                                        value={searchLocation}
                                        onChange={(e) => setSearchLocation(e.target.value)}
                                    />
                                </div>

                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button 
                                        className="primary-btn" 
                                        style={{ padding: '10px 22px', fontSize: '0.92rem' }}
                                        onClick={() => handleSearchAndMatch()}
                                        disabled={loading}
                                    >
                                        {loading ? "Searching & Ranking..." : "🔍 Search & Match"}
                                    </button>
                                </div>
                            </div>

                            {/* Quick Location Pills */}
                            <div style={{ display: 'flex', gap: '8px', marginTop: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                                <span style={{ fontSize: '0.78rem', fontWeight: '700', color: 'var(--mustard-dark)', textTransform: 'uppercase' }}>Quick Locations:</span>
                                {[
                                    { label: "🇵🇰 Pakistan (All)", loc: "Pakistan" },
                                    { label: "📍 Lahore", loc: "Lahore" },
                                    { label: "📍 Karachi", loc: "Karachi" },
                                    { label: "📍 Islamabad", loc: "Islamabad" },
                                    { label: "🌍 Worldwide Remote", loc: "Remote" },
                                    { label: "🇺🇸 United States", loc: "USA" }
                                ].map(p => (
                                    <button 
                                        key={p.loc}
                                        style={{ fontSize: '0.78rem', fontWeight: '600', padding: '4px 10px', background: searchLocation === p.loc ? 'var(--mustard-subtle)' : 'var(--bg-surface-soft)', border: searchLocation === p.loc ? '1px solid var(--mustard-border)' : '1px solid var(--border-subtle)', borderRadius: '6px', color: searchLocation === p.loc ? 'var(--mustard-dark)' : 'var(--text-body)', cursor: 'pointer' }}
                                        onClick={() => {
                                            setSearchLocation(p.loc);
                                            handleSearchAndMatch(searchQuery, p.loc);
                                        }}
                                    >
                                        {p.label}
                                    </button>
                                ))}

                                <button 
                                    style={{ marginLeft: 'auto', fontSize: '0.78rem', color: 'var(--text-muted)', background: 'transparent', border: 'none', textDecoration: 'underline', cursor: 'pointer' }}
                                    onClick={() => setShowKeyModal(!showKeyModal)}
                                >
                                    ⚙️ {rapidApiKey ? "Custom RapidAPI Key Set ✓" : "Enter Free RapidAPI Key (Optional for unlimited live queries)"}
                                </button>
                            </div>

                            {showKeyModal && (
                                <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--bg-surface-soft)', border: '1px solid var(--mustard-border)', borderRadius: '8px' }}>
                                    <div style={{ fontSize: '0.82rem', fontWeight: '700', color: 'var(--mustard-dark)', marginBottom: '4px' }}>
                                        🔑 Optional RapidAPI JSearch Key for Direct LinkedIn & Indeed Aggregation:
                                    </div>
                                    <div style={{ display: 'flex', gap: '8px' }}>
                                        <input 
                                            type="password"
                                            placeholder="Paste your RapidAPI key here..."
                                            value={rapidApiKey}
                                            onChange={(e) => setRapidApiKey(e.target.value)}
                                            style={{ flex: 1, padding: '6px 10px', fontSize: '0.85rem', border: '1px solid var(--border-medium)', borderRadius: '4px' }}
                                        />
                                        <button 
                                            className="secondary-btn" 
                                            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
                                            onClick={() => setShowKeyModal(false)}
                                        >
                                            Save Key
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Stream Provider Status */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                            <span style={{ fontSize: '0.95rem', color: 'var(--text-muted)' }}>
                                Showing <strong>{globalMatches.length}</strong> matching positions ranked by compatibility for current candidate resume.
                            </span>
                            <span style={{ fontSize: '0.76rem', fontFamily: 'var(--font-mono)', padding: '3px 10px', background: 'var(--mustard-subtle)', color: 'var(--mustard-dark)', border: '1px solid var(--mustard-border)', borderRadius: '4px', fontWeight: '700' }}>
                                📡 ACTIVE FEED: {providerUsed}
                            </span>
                        </div>

                        {/* Jobs Grid */}
                        {globalMatches.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '4rem 2rem', background: '#ffffff', borderRadius: '16px', border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-card)' }}>
                                <p style={{ color: 'var(--text-muted)', marginBottom: '1.25rem', fontSize: '1.05rem' }}>No positions matching query currently loaded.</p>
                                <button className="primary-btn" onClick={() => handleSearchAndMatch()} disabled={loading}>
                                    Run Search & Rank Opportunities
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
                                            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                                <span className={`fit-badge ${job.fit_tier === 'Good Fit' ? 'good' : job.fit_tier === 'Potential Fit' ? 'potential' : 'poor'}`} style={{ margin: 0 }}>
                                                    {job.fit_tier}
                                                </span>
                                                {job.apply_url && (
                                                    <a 
                                                        href={job.apply_url} 
                                                        target="_blank" 
                                                        rel="noreferrer" 
                                                        style={{ fontSize: '0.78rem', fontWeight: '700', color: 'var(--mustard-dark)', textDecoration: 'none', padding: '4px 8px', background: 'var(--mustard-subtle)', borderRadius: '4px', border: '1px solid var(--mustard-border)' }}
                                                    >
                                                        Apply Direct ↗
                                                    </a>
                                                )}
                                            </div>
                                            <button 
                                                style={{ padding: '6px 14px', fontSize: '0.84rem', fontWeight: '600', background: 'var(--bg-surface-soft)', color: 'var(--text-heading)', border: '1px solid var(--border-medium)', borderRadius: '6px', cursor: 'pointer' }}
                                                onClick={() => {
                                                    const selected = sampleData.jobs.find(j => j.id === job.job_id);
                                                    if (selected) {
                                                        handleSelectJob(selected);
                                                    } else {
                                                        setJobTitle(job.title);
                                                    }
                                                    setActiveTab('analyzer');
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
