const { useState, useEffect, useRef } = React;

// Company Logo Icons generator with vibrant colors
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
    const [modalTab, setModalTab] = useState("upload"); // 'upload' | 'paste' | 'personas'
    
    const fileInputRef = useRef(null);

    // Search & Filter State
    const [searchQuery, setSearchQuery] = useState("AI Engineer");
    const [searchLocation, setSearchLocation] = useState("Pakistan");
    const [activeFilter, setActiveFilter] = useState("all");
    
    // Jobs & Matches State
    const [jobsList, setJobsList] = useState([]);
    const [selectedJob, setSelectedJob] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const [savedJobs, setSavedJobs] = useState(new Set());

    // Load initial personas and run initial match
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

    // Core Matching Fetcher
    const fetchJobsAndMatch = async (currResume, query, loc) => {
        if (!currResume || !currResume.trim()) return;
        setLoading(true);
        setErrorMsg("");
        try {
            const res = await fetch("/api/v1/search-and-match-jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_text: currResume,
                    query: query || "Software Engineer",
                    location: loc || "Pakistan",
                    limit: 15
                })
            });
            const data = await res.json();
            if (res.ok && data.ranked_jobs) {
                setJobsList(data.ranked_jobs);
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
                // Immediately trigger matching with newly uploaded resume!
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

    const handleClearSearch = () => {
        setSearchQuery("");
        setSearchLocation("");
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
            {/* 1. TOP PROFILE NAVBAR */}
            <nav className="top-profile-bar">
                <div className="profile-info">
                    <div className="profile-avatar">
                        {userName.split(' ').map(n => n[0]).join('').substring(0, 2)}
                    </div>
                    <div className="profile-text">
                        <div className="profile-name-row">
                            <span className="profile-name">{userName}</span>
                            <span className="profile-badge-icon">✓</span>
                            <span style={{ color: '#cbd5e1' }}>|</span>
                            <span className="profile-title">{userRole}</span>
                        </div>
                        <div className="profile-status">
                            Available for work • <span style={{ color: '#0284c7', cursor: 'pointer', textDecoration: 'underline' }} onClick={() => setShowResumeModal(true)}>
                                {uploadedFileName ? `📄 ${uploadedFileName} Active` : "Upload / Update CV"}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="profile-actions">
                    <button className="resume-trigger-btn" onClick={() => setShowResumeModal(true)}>
                        <span>📁 {uploadedFileName ? `Replace ${uploadedFileName}` : "Upload / Edit Resume"}</span>
                    </button>
                    <button className="icon-btn" title="Saved candidates">
                        <span>♡</span>
                    </button>
                    <button className="icon-btn" title="Bookmarks">
                        <span>🔖</span>
                    </button>
                    <button className="get-in-touch-btn" onClick={() => alert(`Alture AI Intelligent Job Matcher\nCandidate: ${userName}\nReady for global hiring.`)}>
                        Get in touch
                    </button>
                </div>
            </nav>

            {/* 2. HERO SEARCH BANNER */}
            <section className="hero-search-section">
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
                            placeholder="Country, city (e.g. Pakistan, Lahore, Remote)"
                            value={searchLocation}
                            onChange={(e) => setSearchLocation(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
                        />
                    </div>

                    {(searchQuery || searchLocation) && (
                        <button className="search-clear-btn" onClick={handleClearSearch}>
                            Clear
                        </button>
                    )}

                    <button className="search-submit-btn" onClick={handleSearchSubmit} disabled={loading}>
                        {loading ? "Searching..." : "Search"}
                    </button>
                </div>
            </section>

            {/* 3. FILTER PILLS BAR */}
            <div className="filter-bar-container">
                <button className={`filter-pill ${activeFilter === 'all' ? 'active' : ''}`} onClick={() => { setSearchLocation("Pakistan"); handleSearchSubmit(); }}>
                    🇵🇰 Pakistan (Lahore, Karachi) ⌵
                </button>
                <button className="filter-pill" onClick={() => { setSearchLocation("Remote"); handleSearchSubmit(); }}>
                    🌍 Remote Worldwide ⌵
                </button>
                <button className="filter-pill" onClick={() => { setSearchQuery("AI / Machine Learning"); handleSearchSubmit(); }}>
                    🧠 AI / ML Roles ⌵
                </button>
                <button className="filter-pill" onClick={() => { setSearchQuery("Full Stack Python"); handleSearchSubmit(); }}>
                    💻 Full-Stack & Backend ⌵
                </button>
                <button className="filter-pill" onClick={() => { setSearchQuery("DevOps Kubernetes"); handleSearchSubmit(); }}>
                    ☁️ Cloud & DevOps ⌵
                </button>
                {uploadedFileName && (
                    <span style={{ marginLeft: 'auto', fontSize: '0.78rem', fontFamily: 'var(--font-mono)', padding: '4px 10px', background: '#ecfdf5', color: '#047857', border: '1px solid #a7f3d0', borderRadius: '999px', fontWeight: 'bold' }}>
                        ✓ {uploadedFileName} ({uploadedWordCount} words)
                    </span>
                )}
            </div>

            {errorMsg && (
                <div style={{ maxWidth: '1240px', margin: '0 auto 1.5rem', padding: '0 1.5rem' }}>
                    <div style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#991b1b', fontSize: '0.9rem' }}>
                        ⚠️ {errorMsg}
                    </div>
                </div>
            )}

            {/* 4. MAIN SPLIT MASTER-DETAIL LAYOUT */}
            <main className="main-layout">
                {/* Left Column: Recommended Jobs Feed */}
                <div className="jobs-feed-column">
                    <div className="feed-header">
                        <span className="recommended-title">
                            Recommended jobs <span className="recommended-count">{jobsList.length.toLocaleString()}</span>
                        </span>
                        <div className="sort-by-text">
                            Sort by: <span className="sort-by-val">Best ATS Match ⌵</span>
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
                                            {isSaved ? "Saved 🔖" : "Save job 🔖"}
                                        </button>
                                    </div>

                                    {/* Profile Match Pill */}
                                    <div className="profile-match-pill">
                                        <div className="match-avatar-mini">✓</div>
                                        <span>Your profile matches this job ({job.ats_score}% Fit)</span>
                                    </div>

                                    {/* Tags Row */}
                                    <div className="card-tags-row">
                                        <span className="tag-badge fulltime">Full Time</span>
                                        <span className="tag-badge remote">{job.type || "Remote"}</span>
                                        <span className="tag-badge senior">{job.fit_tier}</span>
                                        <span className="tag-badge ats-score">{job.ats_score}% ATS Match</span>
                                        <span className="card-post-time">Active posting</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Right Column: Sticky Job Detail Inspector */}
                {selectedJob ? (
                    <div className="detail-pane">
                        <div className="detail-header">
                            <div>
                                <h2 className="detail-job-title">{selectedJob.title}</h2>
                                <div className="detail-subhead">
                                    <strong>{selectedJob.company}</strong> • {selectedJob.location} • <span style={{ color: '#0284c7' }}>Verified Tech Partner</span>
                                </div>
                            </div>
                            <span style={{ fontSize: '1.25rem', color: '#94a3b8', cursor: 'pointer' }}>⋮</span>
                        </div>

                        {/* Metadata Row */}
                        <div className="detail-meta-list">
                            <div className="detail-meta-item">
                                <span className="detail-meta-icon">💼</span>
                                <span><strong>Full-time</strong> · Senior / Lead Level</span>
                            </div>
                            <div className="detail-meta-item">
                                <span className="detail-meta-icon">🏢</span>
                                <span>Enterprise Technology · High Growth</span>
                            </div>
                            <div className="detail-meta-item">
                                <span className="detail-meta-icon">💰</span>
                                <span>{selectedJob.salary_range || "Market Competitive Compensation"}</span>
                            </div>
                            <div className="detail-meta-item">
                                <span className="detail-meta-icon">📋</span>
                                <span>Skills: {selectedJob.matched_skills_sample.concat(selectedJob.missing_skills_sample).slice(0, 5).join(', ')}</span>
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
                                Apply now ↗
                            </a>
                            <button 
                                className="save-detail-btn"
                                onClick={() => toggleSaveJob(selectedJob.job_id)}
                            >
                                {savedJobs.has(selectedJob.job_id) ? "Saved 🔖" : "Save job 🔖"}
                            </button>
                        </div>

                        {/* ATS Deep Analytics & Match Breakdown */}
                        <div className="ats-deep-card">
                            <div className="ats-deep-header">
                                <span className="ats-deep-title">🎯 Alture AI Compatibility Index</span>
                                <span className="ats-score-highlight">{selectedJob.ats_score}%</span>
                            </div>

                            <div style={{ marginBottom: '0.75rem' }}>
                                <div style={{ fontSize: '0.78rem', fontWeight: '700', color: '#15803d', marginBottom: '4px' }}>
                                    ✓ MATCHED TECHNICAL COMPETENCIES ({selectedJob.matched_skills_count}):
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
                                    <div style={{ fontSize: '0.78rem', fontWeight: '700', color: '#991b1b', marginBottom: '4px' }}>
                                        + RECOMMENDED SKILLS TO BOOST SCORE ({selectedJob.missing_skills_count}):
                                    </div>
                                    <div className="skill-pill-container">
                                        {selectedJob.missing_skills_sample.map(s => (
                                            <span key={s} className="spill missing">+ {s}</span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Job Description Body */}
                        <div className="job-body-section">
                            <h3 className="job-body-title">About the job</h3>
                            <p className="job-body-text">
                                We are seeking a high-performing professional to lead and accelerate engineering solutions. You will collaborate directly with top engineering teams to build scalable systems, deploy high-performance microservices, and optimize technical outcomes.
                            </p>
                        </div>

                        <div className="job-body-section">
                            <h3 className="job-body-title">The Role & Requirements</h3>
                            <div className="job-body-text">
                                • Proven hands-on experience in building and architecting scalable production software.<br/>
                                • Strong mastery of core technologies: {selectedJob.matched_skills_sample.join(', ')}.<br/>
                                • Excellent problem-solving, team collaboration, and communication skills.<br/>
                                • Demonstrated ownership of distributed systems and end-to-end deliverables.
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="detail-pane" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                        <p style={{ color: '#94a3b8' }}>Select a job from the list to view full ATS match breakdown.</p>
                    </div>
                )}
            </main>

            {/* 5. RESUME UPLOAD & EDIT MODAL */}
            {showResumeModal && (
                <div className="modal-backdrop" onClick={() => setShowResumeModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">Candidate CV & Resume Upload</h2>
                            <button className="close-btn" onClick={() => setShowResumeModal(false)}>✕</button>
                        </div>

                        {/* Tabs in Modal */}
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

                        {/* TAB A: FILE UPLOAD DROPZONE */}
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
                                        <span style={{ fontSize: '0.78rem', color: '#047857' }}>All matches calculated live</span>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* TAB B: RAW TEXT EDITOR */}
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
                                Calculate Matches for All Jobs
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
