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
    const [showTextPaste, setShowTextPaste] = useState(false);
    
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

    // AI Coach State
    const [coachData, setCoachData] = useState(null);
    const [coachLoading, setCoachLoading] = useState(false);
    const [coachTab, setCoachTab] = useState("tips"); // 'tips' | 'cover_letter' | 'interview_prep'
    const [coachError, setCoachError] = useState("");

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
                    setUploadedWordCount(defaultPersona.resume_text.split(/\s+/).filter(Boolean).length);
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
                setShowTextPaste(false);
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
        setUploadedWordCount(persona.resume_text.split(/\s+/).filter(Boolean).length);
        setCoachData(null);
        fetchJobsAndMatch(persona.resume_text, searchQuery, searchLocation);
    };

    // AI Coach Handler
    const fetchAICoach = async (action) => {
        if (!selectedJob || !resumeText) return;
        setCoachLoading(true);
        setCoachError("");
        setCoachTab(action);
        try {
            const res = await fetch("/api/v1/ai-coach", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_text: resumeText,
                    job_title: selectedJob.title,
                    job_description: `${selectedJob.title} at ${selectedJob.company}. Location: ${selectedJob.location}. Type: ${selectedJob.type}. Required skills include expertise in software engineering and technical development.`,
                    company: selectedJob.company,
                    matched_skills: selectedJob.matched_skills_sample || [],
                    missing_skills: selectedJob.missing_skills_sample || [],
                    ats_score: selectedJob.ats_score || 0,
                    action: action
                })
            });
            const data = await res.json();
            if (res.ok) {
                setCoachData({ action, ...data.data });
            } else {
                setCoachError(data.detail || "AI Coach request failed.");
            }
        } catch (err) {
            setCoachError("Failed to connect to AI Coach.");
        } finally {
            setCoachLoading(false);
        }
    };

    return (
        <div className="app-container">
            {/* 1. TOP MAIN NAVBAR (CLEAN & NON-REDUNDANT) */}
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

                    {/* Main 2-Column Job Split Board */}
                    <main className="main-layout" style={{ marginTop: '2.5rem' }}>
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
                    {/* Embedded Single Resume Upload & Personas Section */}
                    <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '1.75rem', marginBottom: '2rem', boxShadow: '0 4px 14px rgba(0,0,0,0.04)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                            <div>
                                <span style={{ fontSize: '0.78rem', fontWeight: '800', textTransform: 'uppercase', color: '#0284c7', letterSpacing: '0.05em' }}>
                                    🧠 Multi-Modal NLP Intelligence Engine
                                </span>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: '800', color: '#0f172a', margin: '2px 0' }}>
                                    Resume Compatibility & ATS Screening
                                </h2>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <button 
                                    style={{ padding: '6px 12px', fontSize: '0.8rem', fontWeight: '700', background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '6px', cursor: 'pointer', color: '#475569' }}
                                    onClick={() => setShowTextPaste(!showTextPaste)}
                                >
                                    {showTextPaste ? "Hide Text Editor" : "✍️ Paste Resume Text"}
                                </button>
                            </div>
                        </div>

                        {/* Drag & Drop File Upload Box */}
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
                            style={{ padding: '1.25rem', marginBottom: '1rem', border: '2px dashed #94a3b8', background: '#f8fafc' }}
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
                            <div className="upload-icon-circle" style={{ width: '40px', height: '40px', fontSize: '1.2rem', marginBottom: '2px' }}>
                                {isUploading ? "⏳" : "📁"}
                            </div>
                            <div className="upload-prompt-text" style={{ fontSize: '0.92rem' }}>
                                {isUploading ? "Parsing & Extracting Text from Resume..." : "Drop your Resume here (PDF, DOCX, TXT) or Click to Browse"}
                            </div>
                            <div className="upload-prompt-sub" style={{ fontSize: '0.78rem' }}>
                                Automatically calculates ATS Compatibility scores across all live jobs
                            </div>
                        </div>

                        {/* Active Resume Status Banner */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: '8px', marginBottom: '1rem', flexWrap: 'wrap', gap: '6px' }}>
                            <span style={{ fontSize: '0.85rem', color: '#065f46', fontWeight: '600' }}>
                                ✓ Active Candidate: <strong>{userName}</strong> • Document: <strong>{uploadedFileName || "Default Candidate Profile"}</strong> ({uploadedWordCount} words parsed)
                            </span>
                            <button 
                                style={{ padding: '4px 10px', fontSize: '0.76rem', fontWeight: '700', background: '#047857', color: '#ffffff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                                onClick={() => fileInputRef.current && fileInputRef.current.click()}
                            >
                                ↻ Upload Different Resume
                            </button>
                        </div>

                        {/* Raw Text Paste Drawer */}
                        {showTextPaste && (
                            <div style={{ marginBottom: '1rem', padding: '1rem', background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '8px' }}>
                                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: '#64748b', marginBottom: '6px' }}>
                                    Paste Plain Resume Text:
                                </label>
                                <textarea 
                                    style={{ width: '100%', height: '140px', padding: '10px', border: '1px solid #cbd5e1', borderRadius: '6px', fontFamily: 'monospace', fontSize: '0.82rem', outline: 'none' }}
                                    value={resumeText}
                                    onChange={(e) => setResumeText(e.target.value)}
                                    placeholder="Paste raw CV text..."
                                />
                                <button 
                                    className="search-submit-btn" 
                                    style={{ marginTop: '8px', padding: '6px 14px', fontSize: '0.82rem' }}
                                    onClick={() => {
                                        setUploadedWordCount(resumeText.split(/\s+/).filter(Boolean).length);
                                        setShowTextPaste(false);
                                        fetchJobsAndMatch(resumeText, searchQuery, searchLocation);
                                    }}
                                >
                                    Re-Analyze Matched Jobs
                                </button>
                            </div>
                        )}

                        {/* Sample Candidate Personas Row */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', paddingTop: '0.25rem' }}>
                            <span style={{ fontSize: '0.78rem', fontWeight: '800', textTransform: 'uppercase', color: '#64748b' }}>
                                ⚡ Or Test with Sample Profiles:
                            </span>
                            {sampleData.personas.map(p => (
                                <button 
                                    key={p.id}
                                    style={{ padding: '4px 10px', fontSize: '0.78rem', fontWeight: '600', background: userName === p.name ? '#e0f2fe' : '#f1f5f9', border: userName === p.name ? '1px solid #0284c7' : '1px solid #cbd5e1', borderRadius: '6px', color: userName === p.name ? '#0369a1' : '#334155', cursor: 'pointer' }}
                                    onClick={() => handleSelectPersona(p)}
                                >
                                    👤 {p.name} ({p.title.split(' ')[0]} {p.title.split(' ')[1] || ''})
                                </button>
                            ))}
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

                                {/* ═══ GEMINI AI CAREER COACH PANEL ═══ */}
                                <div className="coach-panel">
                                    <div className="coach-header">
                                        <div>
                                            <span className="coach-badge">✨ Powered by Google Gemini</span>
                                            <h3 className="coach-title">AI Career Coach</h3>
                                        </div>
                                    </div>

                                    {/* Coach Action Tabs */}
                                    <div className="coach-tabs">
                                        <button 
                                            className={`coach-tab ${coachTab === 'tips' ? 'active' : ''}`}
                                            onClick={() => fetchAICoach('tips')}
                                            disabled={coachLoading}
                                        >
                                            💡 Resume Tips
                                        </button>
                                        <button 
                                            className={`coach-tab ${coachTab === 'cover_letter' ? 'active' : ''}`}
                                            onClick={() => fetchAICoach('cover_letter')}
                                            disabled={coachLoading}
                                        >
                                            ✉️ Cover Letter
                                        </button>
                                        <button 
                                            className={`coach-tab ${coachTab === 'interview_prep' ? 'active' : ''}`}
                                            onClick={() => fetchAICoach('interview_prep')}
                                            disabled={coachLoading}
                                        >
                                            🎤 Interview Prep
                                        </button>
                                    </div>

                                    {/* Loading State */}
                                    {coachLoading && (
                                        <div className="coach-loading">
                                            <div className="coach-spinner"></div>
                                            <span>AI is analyzing your resume against this job...</span>
                                        </div>
                                    )}

                                    {/* Error */}
                                    {coachError && <div className="coach-error">{coachError}</div>}

                                    {/* Coach Results */}
                                    {coachData && !coachLoading && (
                                        <div className="coach-results">
                                            <div className="coach-powered-by">
                                                🤖 {coachData.powered_by || 'AI Engine'}
                                            </div>

                                            {/* TIPS VIEW */}
                                            {coachData.action === 'tips' && coachData.tips && (
                                                <div>
                                                    {coachData.overall_assessment && (
                                                        <div className="coach-assessment">
                                                            {coachData.overall_assessment}
                                                        </div>
                                                    )}
                                                    <div className="coach-tips-list">
                                                        {coachData.tips.map((tip, i) => (
                                                            <div key={i} className={`coach-tip-card priority-${tip.priority || 'medium'}`}>
                                                                <div className="tip-header">
                                                                    <span className={`tip-priority ${tip.priority || 'medium'}`}>
                                                                        {tip.priority === 'high' ? '🔴' : tip.priority === 'low' ? '🟢' : '🟡'} {(tip.priority || 'medium').toUpperCase()}
                                                                    </span>
                                                                    <strong>{tip.title}</strong>
                                                                </div>
                                                                <p className="tip-detail">{tip.detail}</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                    {coachData.estimated_score_after_fixes && (
                                                        <div className="coach-score-boost">
                                                            📈 Estimated score after fixes: <strong>{coachData.estimated_score_after_fixes}/100</strong>
                                                        </div>
                                                    )}
                                                </div>
                                            )}

                                            {/* COVER LETTER VIEW */}
                                            {coachData.action === 'cover_letter' && coachData.cover_letter && (
                                                <div>
                                                    <div className="coach-cover-letter">
                                                        {coachData.cover_letter.split('\n').map((line, i) => (
                                                            <p key={i}>{line}</p>
                                                        ))}
                                                    </div>
                                                    {coachData.key_highlights && (
                                                        <div className="coach-highlights">
                                                            <strong>Key Highlights Used:</strong>
                                                            <ul>
                                                                {coachData.key_highlights.map((h, i) => <li key={i}>{h}</li>)}
                                                            </ul>
                                                        </div>
                                                    )}
                                                    <button 
                                                        className="coach-copy-btn"
                                                        onClick={() => {
                                                            navigator.clipboard.writeText(coachData.cover_letter);
                                                            alert('Cover letter copied to clipboard!');
                                                        }}
                                                    >
                                                        📋 Copy to Clipboard
                                                    </button>
                                                </div>
                                            )}

                                            {/* INTERVIEW PREP VIEW */}
                                            {coachData.action === 'interview_prep' && coachData.questions && (
                                                <div className="coach-interview-list">
                                                    {coachData.questions.map((q, i) => (
                                                        <div key={i} className={`coach-question-card category-${q.category || 'behavioral'}`}>
                                                            <div className="question-category">
                                                                {q.category === 'strength' ? '💪' : q.category === 'gap' ? '⚠️' : '🧠'} {(q.category || 'general').toUpperCase()}
                                                            </div>
                                                            <div className="question-text">{q.question}</div>
                                                            <div className="question-tip">💡 Tip: {q.tip}</div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Initial State (no data yet) */}
                                    {!coachData && !coachLoading && !coachError && (
                                        <div className="coach-empty">
                                            Click any tab above to get AI-powered career coaching for this job.
                                        </div>
                                    )}
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
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
