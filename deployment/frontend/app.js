const { useState, useEffect, useRef } = React;

// Company Logo Badges
const COMPANY_LOGOS = {
    "Slack": { bg: "#4a154b", icon: "💬", color: "#ffffff" },
    "Figma": { bg: "#1abcfe", icon: "🎨", color: "#ffffff" },
    "Telegram": { bg: "#24A1DE", icon: "✈️", color: "#ffffff" },
    "Systems Limited": { bg: "#0047ba", icon: "🏢", color: "#ffffff" },
    "Arbisoft": { bg: "#e11d48", icon: "⚡", color: "#ffffff" },
    "10Pearls": { bg: "#0f766e", icon: "💎", color: "#ffffff" },
    "VentureDive": { bg: "#6366f1", icon: "🚀", color: "#ffffff" },
    "Lemon.io": { bg: "#eab308", icon: "🍋", color: "#000000" },
    "A.Team": { bg: "#000000", icon: "▲", color: "#ffffff" },
    "Shatterproof": { bg: "#0284c7", icon: "🛡️", color: "#ffffff" }
};

function getCompanyBadge(name = "") {
    for (let key in COMPANY_LOGOS) {
        if (name.toLowerCase().includes(key.toLowerCase())) {
            return COMPANY_LOGOS[key];
        }
    }
    return { bg: "#2563eb", icon: name.charAt(0).toUpperCase() || "💼", color: "#ffffff" };
}

function App() {
    const [currentPage, setCurrentPage] = useState("search"); // 'search' (Page 1) | 'matcher' (Page 2)
    const [sampleData, setSampleData] = useState({ personas: [], jobs: [] });
    
    // User Profile & Resume State
    const [userName, setUserName] = useState("Ahmad Mustafa Iqbal");
    const [userRole, setUserRole] = useState("AI & Machine Learning Engineer");
    const [resumeText, setResumeText] = useState("");
    const [uploadedFileName, setUploadedFileName] = useState("");
    const [uploadedWordCount, setUploadedWordCount] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [showResumeModal, setShowResumeModal] = useState(false);
    const [modalTab, setModalTab] = useState("upload");
    
    const fileInputRef = useRef(null);

    // Search & Filter State (Page 1)
    const [searchQuery, setSearchQuery] = useState("AI Engineer");
    const [searchLocation, setSearchLocation] = useState("Pakistan");
    const [activeFilter, setActiveFilter] = useState("pk");
    
    // Jobs & Matches State
    const [jobsList, setJobsList] = useState([]);
    const [selectedJob, setSelectedJob] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const [savedJobs, setSavedJobs] = useState(new Set());
    const [providerUsed, setProviderUsed] = useState("Pakistan Enterprise Tech Feed");

    // Load initial data
    useEffect(() => {
        fetch("/api/v1/sample-data")
            .then(res => res.json())
            .then(data => {
                setSampleData(data);
                if (data.personas && data.personas.length > 0) {
                    const defaultPersona = data.personas[0];
                    setResumeText(defaultPersona.resume_text);
                    setUserName("Ahmad Mustafa Iqbal");
                    setUserRole("AI & Machine Learning Engineer");
                    fetchJobsAndMatch(defaultPersona.resume_text, "AI Engineer", "Pakistan");
                }
            })
            .catch(err => console.log("Failed loading sample data:", err));
    }, []);

    // Core Matching & Search Fetcher
    const fetchJobsAndMatch = async (currResume, query, loc) => {
        setLoading(true);
        setErrorMsg("");
        try {
            const res = await fetch("/api/v1/search-and-match-jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_text: currResume || "Experienced Software and AI Engineer with Python, FastAPI, and Machine Learning expertise.",
                    query: query || "Software Engineer",
                    location: loc || "Pakistan",
                    limit: 15
                })
            });
            const data = await res.json();
            if (res.ok && data.ranked_jobs) {
                setJobsList(data.ranked_jobs);
                setProviderUsed(data.provider_used || "Multi-Source Engine");
                if (data.ranked_jobs.length > 0) {
                    setSelectedJob(data.ranked_jobs[0]);
                }
            } else {
                setErrorMsg(data.detail || "Failed to search jobs.");
            }
        } catch (err) {
            setErrorMsg("Network error connecting to Alture AI backend.");
        } finally {
            setLoading(false);
        }
    };

    // File Upload Handler (PDF, DOCX, TXT)
    const handleFileUpload = async (file) => {
        if (!file) return;
        setIsUploading(true);
        setErrorMsg("");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/api/v1/upload-resume", {
                method: "POST",
                body: formData
            });
            const data = await res.json();

            if (res.ok && data.extracted_text) {
                setResumeText(data.extracted_text);
                setUploadedFileName(data.filename);
                setUploadedWordCount(data.word_count);
                if (data.candidate_name && data.candidate_name !== "Candidate") {
                    setUserName(data.candidate_name);
                }
                setShowResumeModal(false);
                setCurrentPage("matcher");
                // Immediately calculate ATS matches for all jobs
                fetchJobsAndMatch(data.extracted_text, searchQuery, searchLocation);
            } else {
                setErrorMsg(data.detail || "Failed to parse uploaded resume document.");
            }
        } catch (err) {
            setErrorMsg("Upload failed. Please check network connection.");
        } finally {
            setIsUploading(false);
        }
    };

    const handleSearchSubmit = (e) => {
        if (e) e.preventDefault();
        fetchJobsAndMatch(resumeText, searchQuery, searchLocation);
    };

    const toggleSaveJob = (jobId) => {
        const next = new Set(savedJobs);
        if (next.has(jobId)) next.delete(jobId);
        else next.add(jobId);
        setSavedJobs(next);
    };

    const handleSelectPersona = (persona) => {
        setResumeText(persona.resume_text);
        setUserName(persona.name);
        setUserRole(persona.title);
        setUploadedFileName("");
        setShowResumeModal(false);
        fetchJobsAndMatch(persona.resume_text, searchQuery, searchLocation);
    };

    return (
        <div className="app-container">
            {/* 1. TOP MAIN HEADER WITH CLEAN 2-PAGE NAVIGATION */}
            <header className="top-profile-bar">
                <div className="profile-info">
                    <div className="brand-logo-wrapper">
                        <img src="/static/logo.png" alt="Alture AI" className="header-brand-logo" onError={(e) => { e.target.style.display = 'none'; }} />
                        <span className="brand-name-tag">Alture AI</span>
                    </div>

                    {/* TWO PRIMARY PAGES TABS */}
                    <div className="main-nav-tabs">
                        <button 
                            className={`main-nav-tab ${currentPage === 'search' ? 'active' : ''}`}
                            onClick={() => setCurrentPage('search')}
                        >
                            🔍 1. Live Job Discovery
                        </button>
                        <button 
                            className={`main-nav-tab ${currentPage === 'matcher' ? 'active' : ''}`}
                            onClick={() => setCurrentPage('matcher')}
                        >
                            🧠 2. AI Resume Matcher & Score
                        </button>
                    </div>
                </div>

                <div className="profile-actions">
                    <button className="resume-trigger-btn" onClick={() => setShowResumeModal(true)}>
                        <span>📁 {uploadedFileName ? `📄 ${uploadedFileName}` : "Upload My Resume (PDF)"}</span>
                    </button>
                    <div className="profile-user-pill">
                        <div className="profile-avatar">
                            {userName.split(' ').map(n => n[0]).join('').substring(0, 2)}
                        </div>
                        <span style={{ fontSize: '0.85rem', fontWeight: '700' }}>{userName}</span>
                    </div>
                </div>
            </header>

            {/* -------------------------------------------------------------
               PAGE 1: LIVE JOB DISCOVERY PORTAL (Search & Direct Apply)
            -------------------------------------------------------------- */}
            {currentPage === 'search' && (
                <div>
                    {/* Hero Search Section */}
                    <section className="hero-search-section">
                        <div style={{ textAlign: 'center', marginBottom: '1.25rem', color: '#ffffff' }}>
                            <h1 style={{ fontSize: '1.85rem', fontWeight: '800', letterSpacing: '-0.02em', marginBottom: '4px' }}>
                                Find & Apply to Tech Jobs in Pakistan & Worldwide
                            </h1>
                            <p style={{ fontSize: '0.95rem', color: '#bae6fd' }}>
                                Search real-time open positions across LinkedIn, Indeed, Systems Ltd, Arbisoft & Global Remote feeds.
                            </p>
                        </div>

                        <div className="search-box-container">
                            <div className="search-input-group">
                                <span className="search-icon">🔍</span>
                                <input 
                                    type="text" 
                                    className="search-input" 
                                    placeholder="Job title, technical skill, or keyword"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
                                />
                            </div>

                            <div className="search-divider"></div>

                            <div className="search-input-group">
                                <span className="search-icon">📍</span>
                                <input 
                                    type="text" 
                                    className="search-input" 
                                    placeholder="City or Country (e.g. Lahore, Karachi, Pakistan, Remote)"
                                    value={searchLocation}
                                    onChange={(e) => setSearchLocation(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
                                />
                            </div>

                            {(searchQuery || searchLocation) && (
                                <button className="search-clear-btn" onClick={() => { setSearchQuery(""); setSearchLocation(""); }}>
                                    Clear
                                </button>
                            )}

                            <button className="search-submit-btn" onClick={handleSearchSubmit} disabled={loading}>
                                {loading ? "Searching..." : "Search Jobs"}
                            </button>
                        </div>
                    </section>

                    {/* Quick Filter Pills Bar */}
                    <div className="filter-bar-container">
                        <button className={`filter-pill ${activeFilter === 'pk' ? 'active' : ''}`} onClick={() => { setActiveFilter('pk'); setSearchLocation("Pakistan"); fetchJobsAndMatch(resumeText, searchQuery, "Pakistan"); }}>
                            🇵🇰 All Pakistan (Lahore, Karachi, Islamabad)
                        </button>
                        <button className={`filter-pill ${activeFilter === 'lahore' ? 'active' : ''}`} onClick={() => { setActiveFilter('lahore'); setSearchLocation("Lahore"); fetchJobsAndMatch(resumeText, searchQuery, "Lahore"); }}>
                            📍 Lahore Tech Hub
                        </button>
                        <button className={`filter-pill ${activeFilter === 'karachi' ? 'active' : ''}`} onClick={() => { setActiveFilter('karachi'); setSearchLocation("Karachi"); fetchJobsAndMatch(resumeText, searchQuery, "Karachi"); }}>
                            📍 Karachi Tech Hub
                        </button>
                        <button className={`filter-pill ${activeFilter === 'remote' ? 'active' : ''}`} onClick={() => { setActiveFilter('remote'); setSearchLocation("Remote"); fetchJobsAndMatch(resumeText, searchQuery, "Remote"); }}>
                            🌍 Worldwide Remote
                        </button>
                        <span style={{ marginLeft: 'auto', fontSize: '0.78rem', fontFamily: 'var(--font-mono)', padding: '4px 10px', background: '#e0f2fe', color: '#0369a1', border: '1px solid #bae6fd', borderRadius: '6px', fontWeight: 'bold' }}>
                            📡 {providerUsed}
                        </span>
                    </div>

                    {/* Main 2-Column Job Split Board */}
                    <main className="main-layout">
                        {/* Left Feed */}
                        <div className="jobs-feed-column">
                            <div className="feed-header">
                                <span className="recommended-title">
                                    Available Openings <span className="recommended-count">({jobsList.length})</span>
                                </span>
                                <div className="sort-by-text">
                                    Location: <span className="sort-by-val">{searchLocation || "All"}</span>
                                </div>
                            </div>

                            <div className="jobs-list-container">
                                {jobsList.map(job => {
                                    const isSelected = selectedJob && selectedJob.job_id === job.job_id;
                                    const isSaved = savedJobs.has(job.job_id);
                                    const badge = getCompanyBadge(job.company);

                                    return (
                                        <div 
                                            key={job.job_id} 
                                            className={`job-feed-card ${isSelected ? 'active' : ''}`}
                                            onClick={() => setSelectedJob(job)}
                                        >
                                            <div className="card-top-row">
                                                <div className="company-logo-badge" style={{ backgroundColor: badge.bg, color: badge.color }}>
                                                    {badge.icon}
                                                </div>
                                                <div className="card-title-group">
                                                    <h3 className="card-job-title">{job.title}</h3>
                                                    <div className="card-company-name">{job.company} • {job.location}</div>
                                                </div>
                                                <button 
                                                    className="save-job-icon" 
                                                    onClick={(e) => { e.stopPropagation(); toggleSaveJob(job.job_id); }}
                                                >
                                                    {isSaved ? "Saved 🔖" : "Save 🔖"}
                                                </button>
                                            </div>

                                            {/* Tags Row */}
                                            <div className="card-tags-row">
                                                <span className="tag-badge fulltime">Full Time</span>
                                                <span className="tag-badge remote">{job.type || "Remote"}</span>
                                                {job.salary_range && <span className="tag-badge senior">{job.salary_range}</span>}
                                                <span className="card-post-time">Active opening</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Right Detail Pane */}
                        {selectedJob ? (
                            <div className="detail-pane">
                                <div className="detail-header">
                                    <div>
                                        <h2 className="detail-job-title">{selectedJob.title}</h2>
                                        <div className="detail-subhead">
                                            <strong>{selectedJob.company}</strong> • {selectedJob.location}
                                        </div>
                                    </div>
                                    <span style={{ fontSize: '1.25rem', color: '#94a3b8' }}>⋮</span>
                                </div>

                                <div className="detail-meta-list">
                                    <div className="detail-meta-item">
                                        <span className="detail-meta-icon">💼</span>
                                        <span><strong>Full-time</strong> · Professional Tech Opening</span>
                                    </div>
                                    <div className="detail-meta-item">
                                        <span className="detail-meta-icon">💰</span>
                                        <span>{selectedJob.salary_range || "Market Competitive Compensation"}</span>
                                    </div>
                                    <div className="detail-meta-item">
                                        <span className="detail-meta-icon">📋</span>
                                        <span>Required Skills: {selectedJob.matched_skills_sample.concat(selectedJob.missing_skills_sample).slice(0, 6).join(', ') || "Python, React, Software Engineering"}</span>
                                    </div>
                                </div>

                                {/* Action Buttons */}
                                <div className="detail-action-row">
                                    <a 
                                        href={selectedJob.apply_url || "https://www.linkedin.com/jobs"} 
                                        target="_blank" 
                                        rel="noreferrer" 
                                        className="apply-btn"
                                    >
                                        Apply Direct on Official Site ↗
                                    </a>
                                    <button 
                                        className="save-detail-btn"
                                        onClick={() => {
                                            setCurrentPage('matcher');
                                        }}
                                    >
                                        🧠 Match My Resume Against This Job
                                    </button>
                                </div>

                                <div className="job-body-section">
                                    <h3 className="job-body-title">Job Overview & Requirements</h3>
                                    <p className="job-body-text">
                                        {selectedJob.title} position at {selectedJob.company}. You will participate in architecture, development, code optimization, and delivery of production systems.
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div className="detail-pane" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                                <p style={{ color: '#94a3b8' }}>Select a job from the list to view details.</p>
                            </div>
                        )}
                    </main>
                </div>
            )}

            {/* -------------------------------------------------------------
               PAGE 2: AI RESUME-TO-JOB MATCHER & SCREENING ENGINE
            -------------------------------------------------------------- */}
            {currentPage === 'matcher' && (
                <div style={{ maxWidth: '1240px', margin: '2rem auto', padding: '0 1.5rem' }}>
                    {/* Header Banner */}
                    <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '2rem', marginBottom: '2rem', boxShadow: '0 4px 14px rgba(0,0,0,0.04)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.5rem' }}>
                        <div>
                            <span style={{ fontSize: '0.78rem', fontWeight: '800', textTransform: 'uppercase', color: '#0284c7', letterSpacing: '0.05em' }}>
                                🧠 Multi-Modal NLP Intelligence Engine
                            </span>
                            <h2 style={{ fontSize: '1.75rem', fontWeight: '800', color: '#0f172a', margin: '4px 0' }}>
                                Resume Compatibility & ATS Screening
                            </h2>
                            <p style={{ color: '#64748b', fontSize: '0.92rem' }}>
                                Candidate: <strong style={{ color: '#0f172a' }}>{userName}</strong> • Document: <strong style={{ color: '#0284c7' }}>{uploadedFileName || "Active Profile Resume"}</strong> ({resumeText.split(/\s+/).filter(Boolean).length} words)
                            </p>
                        </div>

                        <div style={{ display: 'flex', gap: '10px' }}>
                            <button className="primary-btn" style={{ padding: '10px 20px', fontSize: '0.9rem' }} onClick={() => setShowResumeModal(true)}>
                                📁 Upload / Change Resume (PDF)
                            </button>
                        </div>
                    </div>

                    {/* 2-Column Split: Ranked Matches vs Deep Match Inspector */}
                    <div className="main-layout" style={{ margin: 0, padding: 0 }}>
                        {/* Left Feed: Ranked by ATS % */}
                        <div className="jobs-feed-column">
                            <div className="feed-header">
                                <span className="recommended-title">
                                    🏆 Ranked Job Matches <span className="recommended-count">({jobsList.length})</span>
                                </span>
                                <div className="sort-by-text">
                                    Ranked by: <span className="sort-by-val" style={{ color: '#15803d' }}>Highest ATS Match % ⌵</span>
                                </div>
                            </div>

                            <div className="jobs-list-container">
                                {jobsList.map(job => {
                                    const isSelected = selectedJob && selectedJob.job_id === job.job_id;
                                    const badge = getCompanyBadge(job.company);

                                    return (
                                        <div 
                                            key={job.job_id} 
                                            className={`job-feed-card ${isSelected ? 'active' : ''}`}
                                            onClick={() => setSelectedJob(job)}
                                        >
                                            <div className="card-top-row">
                                                <div className="company-logo-badge" style={{ backgroundColor: badge.bg, color: badge.color }}>
                                                    {badge.icon}
                                                </div>
                                                <div className="card-title-group">
                                                    <h3 className="card-job-title">{job.title}</h3>
                                                    <div className="card-company-name">{job.company} • {job.location}</div>
                                                </div>
                                                <div style={{ fontSize: '1.25rem', fontFamily: 'monospace', fontWeight: '800', color: job.fit_tier === 'Good Fit' ? '#15803d' : job.fit_tier === 'Potential Fit' ? '#b45309' : '#b91c1c' }}>
                                                    {job.ats_score}%
                                                </div>
                                            </div>

                                            <div className="profile-match-pill">
                                                <div className="match-avatar-mini">✓</div>
                                                <span>{job.fit_tier} Compatibility ({job.matched_skills_count} Skills Matched)</span>
                                            </div>

                                            <div className="card-tags-row">
                                                <span className={`tag-badge ${job.fit_tier === 'Good Fit' ? 'senior' : 'fulltime'}`}>{job.fit_tier}</span>
                                                <span className="tag-badge ats-score">{job.ats_score}% ATS Score</span>
                                                <span className="card-post-time">Ranked</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Right Deep ATS Inspector */}
                        {selectedJob ? (
                            <div className="detail-pane">
                                <div className="detail-header">
                                    <div>
                                        <h2 className="detail-job-title">{selectedJob.title}</h2>
                                        <div className="detail-subhead">
                                            <strong>{selectedJob.company}</strong> • {selectedJob.location}
                                        </div>
                                    </div>
                                    <div className="gauge-score good" style={{ fontSize: '2.5rem', lineHeight: '1' }}>
                                        {selectedJob.ats_score}%
                                    </div>
                                </div>

                                {/* ATS Score Gauge Card */}
                                <div className="ats-deep-card">
                                    <div className="ats-deep-header">
                                        <span className="ats-deep-title">🎯 Model Compatibility Breakdown</span>
                                        <span className="ats-score-highlight">{selectedJob.fit_tier}</span>
                                    </div>

                                    <div style={{ marginBottom: '1rem' }}>
                                        <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#15803d', marginBottom: '6px' }}>
                                            ✓ MATCHED SKILLS IN YOUR RESUME ({selectedJob.matched_skills_count}):
                                        </div>
                                        <div className="skill-pill-container">
                                            {selectedJob.matched_skills_sample.map(s => (
                                                <span key={s} className="spill matched">✓ {s}</span>
                                            ))}
                                            {selectedJob.matched_skills_sample.length === 0 && <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>General contextual match</span>}
                                        </div>
                                    </div>

                                    {selectedJob.missing_skills_sample.length > 0 && (
                                        <div>
                                            <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#991b1b', marginBottom: '6px' }}>
                                                + RECOMMENDED SKILLS TO BOOST SCORE ({selectedJob.missing_skills_count}):
                                            </div>
                                            <div className="skill-pill-container">
                                                {selectedJob.missing_skills_sample.map(s => (
                                                    <span key={s} className="spill missing">+ Add {s}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Action Buttons */}
                                <div className="detail-action-row">
                                    <a 
                                        href={selectedJob.apply_url || "https://www.linkedin.com/jobs"} 
                                        target="_blank" 
                                        rel="noreferrer" 
                                        className="apply-btn"
                                    >
                                        Apply with this Resume ↗
                                    </a>
                                    <button 
                                        className="save-detail-btn" 
                                        onClick={() => toggleSaveJob(selectedJob.job_id)}
                                    >
                                        {savedJobs.has(selectedJob.job_id) ? "Saved 🔖" : "Save Job 🔖"}
                                    </button>
                                </div>

                                <div className="job-body-section">
                                    <h3 className="job-body-title">Strategic Resume Recommendations</h3>
                                    <div className="job-body-text">
                                        • Emphasize your hands-on achievements with {selectedJob.matched_skills_sample.slice(0, 3).join(', ')} in your Experience bullet points.<br/>
                                        • Quantify your impact with measurable metrics (e.g. latency reduction, scale, throughput).<br/>
                                        • Ensure standard single-column ATS formatting for maximum readability.
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="detail-pane" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                                <p style={{ color: '#94a3b8' }}>Select a job from the list to view full ATS score analysis.</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* -------------------------------------------------------------
               RESUME UPLOAD MODAL (PDF / DOCX / TEXT)
            -------------------------------------------------------------- */}
            {showResumeModal && (
                <div className="modal-backdrop" onClick={() => setShowResumeModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">Upload or Edit Candidate CV</h2>
                            <button className="close-btn" onClick={() => setShowResumeModal(false)}>✕</button>
                        </div>

                        {/* Tabs */}
                        <div style={{ display: 'flex', gap: '8px', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
                            <button 
                                style={{ padding: '6px 14px', fontSize: '0.85rem', fontWeight: '700', background: modalTab === 'upload' ? '#0284c7' : '#f1f5f9', color: modalTab === 'upload' ? '#ffffff' : '#475569', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                                onClick={() => setModalTab('upload')}
                            >
                                📁 Upload Document (PDF / DOCX)
                            </button>
                            <button 
                                style={{ padding: '6px 14px', fontSize: '0.85rem', fontWeight: '700', background: modalTab === 'paste' ? '#0284c7' : '#f1f5f9', color: modalTab === 'paste' ? '#ffffff' : '#475569', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                                onClick={() => setModalTab('paste')}
                            >
                                ✍️ Paste Resume Text
                            </button>
                            <button 
                                style={{ padding: '6px 14px', fontSize: '0.85rem', fontWeight: '700', background: modalTab === 'personas' ? '#0284c7' : '#f1f5f9', color: modalTab === 'personas' ? '#ffffff' : '#475569', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                                onClick={() => setModalTab('personas')}
                            >
                                ⚡ Sample Personas
                            </button>
                        </div>

                        {/* TAB A: FILE DROPZONE */}
                        {modalTab === 'upload' && (
                            <div>
                                <input 
                                    type="file" 
                                    ref={fileInputRef}
                                    style={{ display: 'none' }}
                                    accept=".pdf,.docx,.doc,.txt"
                                    onChange={(e) => {
                                        if (e.target.files && e.target.files[0]) {
                                            handleFileUpload(e.target.files[0]);
                                        }
                                    }}
                                />

                                <div 
                                    className={`upload-dropzone ${isDragging ? 'dragging' : ''}`}
                                    onClick={() => fileInputRef.current && fileInputRef.current.click()}
                                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                                    onDragLeave={() => setIsDragging(false)}
                                    onDrop={(e) => {
                                        e.preventDefault();
                                        setIsDragging(false);
                                        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                                            handleFileUpload(e.dataTransfer.files[0]);
                                        }
                                    }}
                                >
                                    <div className="upload-icon-circle">
                                        {isUploading ? "⏳" : "📁"}
                                    </div>
                                    <div className="upload-prompt-text">
                                        {isUploading ? "Parsing & Extracting Text from Resume..." : "Click to browse or drop your resume here"}
                                    </div>
                                    <div className="upload-prompt-sub">
                                        Supports PDF, Word (.DOCX), and Plain Text (.TXT)
                                    </div>
                                </div>

                                {uploadedFileName && (
                                    <div className="upload-success-banner">
                                        <span>✓ Currently Active Document: <strong>{uploadedFileName}</strong> ({uploadedWordCount} words parsed)</span>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* TAB B: TEXT EDITOR */}
                        {modalTab === 'paste' && (
                            <div style={{ marginBottom: '1.25rem' }}>
                                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: '#64748b', marginBottom: '6px' }}>
                                    📄 Paste Full Candidate Resume Text:
                                </label>
                                <textarea 
                                    style={{ width: '100%', height: '240px', padding: '1rem', border: '1px solid #cbd5e1', borderRadius: '8px', fontFamily: 'monospace', fontSize: '0.85rem', outline: 'none' }}
                                    value={resumeText}
                                    onChange={(e) => setResumeText(e.target.value)}
                                    placeholder="Paste entire CV/Resume text here..."
                                />
                            </div>
                        )}

                        {/* TAB C: PRELOADED PERSONAS */}
                        {modalTab === 'personas' && (
                            <div style={{ marginBottom: '1.25rem' }}>
                                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: '#64748b', marginBottom: '6px' }}>
                                    ⚡ 1-Click Candidate Profiles:
                                </label>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    {sampleData.personas.map(p => (
                                        <div 
                                            key={p.id}
                                            style={{ padding: '10px 14px', background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '8px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                                            onClick={() => handleSelectPersona(p)}
                                        >
                                            <div>
                                                <div style={{ fontWeight: '700', fontSize: '0.92rem' }}>{p.name}</div>
                                                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{p.title}</div>
                                            </div>
                                            <button style={{ padding: '4px 10px', fontSize: '0.78rem', background: '#0284c7', color: '#ffffff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                                                Select ➔
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '1rem' }}>
                            <button 
                                style={{ padding: '8px 16px', background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: '600', cursor: 'pointer' }}
                                onClick={() => setShowResumeModal(false)}
                            >
                                Close
                            </button>
                            <button 
                                className="search-submit-btn"
                                onClick={() => {
                                    setShowResumeModal(false);
                                    fetchJobsAndMatch(resumeText, searchQuery, searchLocation);
                                }}
                            >
                                Save & Re-Calculate All Matches
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
