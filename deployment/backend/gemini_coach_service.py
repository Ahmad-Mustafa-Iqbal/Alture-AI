"""
Alture AI — Gemini-Powered Career Coach Service
================================================
Provides three AI-powered features using Google Gemini 2.0 Flash (free tier):
  1. Resume Improvement Tips — actionable suggestions based on skill gaps
  2. Tailored Cover Letter — auto-generated for a specific job
  3. Interview Prep Questions — based on job requirements and missing skills

Usage:
    from deployment.backend.gemini_coach_service import GeminiCoachService
    coach = GeminiCoachService()
    tips = coach.get_resume_tips(resume, job_title, job_desc, matched, missing)
"""

import os
import json
import re

# ─── Try importing Gemini SDK ───
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiCoachService:
    """Modular AI Coach powered by Google Gemini 2.0 Flash."""

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = None
        self._initialize()

    def _initialize(self):
        """Initialize Gemini model if API key and SDK are available."""
        if not GEMINI_AVAILABLE:
            print("  [WARN] google-generativeai not installed. AI Coach disabled.")
            return
        if not self.api_key:
            print("  [WARN] GEMINI_API_KEY not set. AI Coach will use fallback tips.")
            return
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            print("  [OK] Gemini AI Coach initialized (gemini-2.0-flash)")
        except Exception as e:
            print(f"  [WARN] Gemini initialization failed: {e}")
            self.model = None

    @property
    def is_available(self) -> bool:
        """Check if Gemini is properly configured and ready."""
        return self.model is not None

    # ─────────────────────────────────────────────
    # 1. RESUME IMPROVEMENT TIPS
    # ─────────────────────────────────────────────
    def get_resume_tips(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        matched_skills: list,
        missing_skills: list,
        ats_score: float = 0.0
    ) -> dict:
        """
        Generate actionable resume improvement tips.
        Falls back to rule-based tips if Gemini is unavailable.
        """
        if not self.is_available:
            return self._fallback_resume_tips(matched_skills, missing_skills, ats_score)

        prompt = f"""You are an expert AI Career Coach helping job seekers optimize their resumes for ATS (Applicant Tracking Systems).

CANDIDATE'S RESUME (excerpt):
{resume_text[:3000]}

TARGET JOB: {job_title}
JOB DESCRIPTION (excerpt):
{job_description[:2000]}

CURRENT ATS COMPATIBILITY SCORE: {ats_score:.1f}/100

SKILLS ALREADY MATCHED: {', '.join(matched_skills[:15]) if matched_skills else 'None'}
SKILLS MISSING FROM RESUME: {', '.join(missing_skills[:15]) if missing_skills else 'None'}

Based on this analysis, provide exactly 5 specific, actionable resume improvement tips.

IMPORTANT RULES:
- Each tip must be concrete and specific (not generic advice)
- For missing skills: suggest HOW to add them if the candidate has any related experience
- Focus on ATS optimization (keyword placement, formatting, quantifiable achievements)
- Use simple, clear language

Respond in this exact JSON format:
{{
  "tips": [
    {{"title": "Short title", "detail": "Specific actionable advice", "priority": "high/medium/low"}},
    {{"title": "Short title", "detail": "Specific actionable advice", "priority": "high/medium/low"}},
    {{"title": "Short title", "detail": "Specific actionable advice", "priority": "high/medium/low"}},
    {{"title": "Short title", "detail": "Specific actionable advice", "priority": "high/medium/low"}},
    {{"title": "Short title", "detail": "Specific actionable advice", "priority": "high/medium/low"}}
  ],
  "overall_assessment": "1-2 sentence summary of the resume's fit for this role",
  "estimated_score_after_fixes": {min(ats_score + 15, 95)}
}}

Return ONLY valid JSON. No markdown, no code blocks, no extra text."""

        return self._call_gemini(prompt, fallback=self._fallback_resume_tips(matched_skills, missing_skills, ats_score))

    # ─────────────────────────────────────────────
    # 2. COVER LETTER GENERATION
    # ─────────────────────────────────────────────
    def generate_cover_letter(
        self,
        resume_text: str,
        job_title: str,
        company: str,
        job_description: str
    ) -> dict:
        """Generate a tailored cover letter for a specific job."""
        if not self.is_available:
            return {"cover_letter": self._fallback_cover_letter(job_title, company), "powered_by": "template"}

        prompt = f"""You are an expert career coach. Write a professional, compelling cover letter.

CANDIDATE'S RESUME:
{resume_text[:3000]}

TARGET POSITION: {job_title} at {company}
JOB DESCRIPTION:
{job_description[:2000]}

Write a 3-paragraph cover letter that:
1. Opens with a compelling hook mentioning the specific role and company
2. Highlights 2-3 specific experiences from the resume that match the job requirements
3. Closes with enthusiasm and a call to action

Keep it under 300 words. Be specific, not generic.

Respond in this exact JSON format:
{{
  "cover_letter": "The full cover letter text here",
  "key_highlights": ["highlight 1", "highlight 2", "highlight 3"]
}}

Return ONLY valid JSON."""

        return self._call_gemini(prompt, fallback={"cover_letter": self._fallback_cover_letter(job_title, company), "powered_by": "template"})

    # ─────────────────────────────────────────────
    # 3. INTERVIEW PREP QUESTIONS
    # ─────────────────────────────────────────────
    def generate_interview_questions(
        self,
        job_title: str,
        job_description: str,
        missing_skills: list,
        matched_skills: list
    ) -> dict:
        """Generate interview prep questions based on the job and skill gaps."""
        if not self.is_available:
            return self._fallback_interview_questions(job_title, missing_skills)

        prompt = f"""You are a senior technical interviewer for a {job_title} position.

JOB DESCRIPTION:
{job_description[:2000]}

CANDIDATE'S MATCHED SKILLS: {', '.join(matched_skills[:10])}
CANDIDATE'S SKILL GAPS: {', '.join(missing_skills[:10])}

Generate 5 likely interview questions for this role. Include:
- 2 technical questions about the candidate's strong skills (to help them prepare confident answers)
- 2 questions about the skill gaps (to help them prepare for tough questions)
- 1 behavioral/situational question

Respond in this exact JSON format:
{{
  "questions": [
    {{"question": "...", "category": "strength/gap/behavioral", "tip": "Brief preparation tip"}},
    {{"question": "...", "category": "strength/gap/behavioral", "tip": "Brief preparation tip"}},
    {{"question": "...", "category": "strength/gap/behavioral", "tip": "Brief preparation tip"}},
    {{"question": "...", "category": "strength/gap/behavioral", "tip": "Brief preparation tip"}},
    {{"question": "...", "category": "strength/gap/behavioral", "tip": "Brief preparation tip"}}
  ]
}}

Return ONLY valid JSON."""

        return self._call_gemini(prompt, fallback=self._fallback_interview_questions(job_title, missing_skills))

    # ─────────────────────────────────────────────
    # INTERNAL: Call Gemini API
    # ─────────────────────────────────────────────
    def _call_gemini(self, prompt: str, fallback: dict) -> dict:
        """Send prompt to Gemini and parse JSON response."""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Strip markdown code fences if present
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            text = text.strip()

            parsed = json.loads(text)
            parsed["powered_by"] = "gemini-2.0-flash"
            return parsed

        except json.JSONDecodeError as e:
            print(f"  [WARN] Gemini returned non-JSON: {e}")
            try:
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    parsed["powered_by"] = "gemini-2.0-flash"
                    return parsed
            except Exception:
                pass
            fallback["powered_by"] = "fallback (parse error)"
            return fallback

        except Exception as e:
            print(f"  [WARN] Gemini API call failed: {e}")
            fallback["powered_by"] = "fallback (api error)"
            return fallback

    # ─────────────────────────────────────────────
    # FALLBACK: Rule-Based Tips (no API needed)
    # ─────────────────────────────────────────────
    def _fallback_resume_tips(self, matched: list, missing: list, score: float) -> dict:
        """Generate rule-based tips when Gemini is unavailable."""
        tips = []

        if missing:
            top_missing = missing[:3]
            tips.append({
                "title": f"Add Missing Skills: {', '.join(top_missing)}",
                "detail": f"These skills are required by the job but not found in your resume. If you have any experience with {top_missing[0]}, add it to your skills section and mention it in your work experience.",
                "priority": "high"
            })

        if score < 40:
            tips.append({
                "title": "Increase Keyword Density",
                "detail": "Your resume has low keyword overlap with this job description. Mirror the exact terminology used in the job posting within your experience bullets.",
                "priority": "high"
            })

        tips.append({
            "title": "Quantify Your Achievements",
            "detail": "Replace vague statements like 'improved performance' with specific metrics like 'reduced latency by 40%%' or 'processed 10K+ requests/day'.",
            "priority": "medium"
        })

        tips.append({
            "title": "Tailor Your Summary Section",
            "detail": "Customize your professional summary for each application. Include the job title and 2-3 key requirements from the posting.",
            "priority": "medium"
        })

        if matched:
            tips.append({
                "title": f"Strengthen Matched Skills: {', '.join(matched[:3])}",
                "detail": f"You already have {', '.join(matched[:3])} — make them more prominent by adding project outcomes and metrics for each.",
                "priority": "low"
            })
        else:
            tips.append({
                "title": "Consider Role Alignment",
                "detail": "Very few skills match this role. Consider whether this position aligns with your background, or highlight transferable skills.",
                "priority": "high"
            })

        return {
            "tips": tips[:5],
            "overall_assessment": f"Current ATS score is {score:.1f}/100. {'Strong foundation — optimize keywords to boost score.' if score > 30 else 'Significant skill gaps detected. Focus on adding missing technical skills.'}",
            "estimated_score_after_fixes": min(score + 12, 95),
            "powered_by": "rule-based fallback"
        }

    def _fallback_cover_letter(self, job_title: str, company: str) -> str:
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. With my background in technology and passion for innovation, I believe I would be a valuable addition to your team.

Throughout my career, I have developed strong technical skills and a proven track record of delivering results. I am particularly drawn to {company}'s mission and would welcome the opportunity to contribute to your continued success.

I look forward to discussing how my experience and skills can benefit your team. Thank you for considering my application.

Best regards,
[Your Name]"""

    def _fallback_interview_questions(self, job_title: str, missing: list) -> dict:
        questions = [
            {"question": f"Tell me about your experience relevant to the {job_title} role.", "category": "behavioral", "tip": "Prepare 2-3 specific projects that demonstrate your qualifications."},
            {"question": "Describe a challenging technical problem you solved recently.", "category": "strength", "tip": "Use the STAR method: Situation, Task, Action, Result."},
            {"question": "How do you stay updated with the latest developments in your field?", "category": "behavioral", "tip": "Mention specific resources, communities, or recent papers you've read."},
        ]
        if missing:
            questions.append({"question": f"What is your experience with {missing[0]}?", "category": "gap", "tip": f"Be honest about your level, but mention related skills or your learning plan for {missing[0]}."})
            if len(missing) > 1:
                questions.append({"question": f"How would you approach learning {missing[1]} for this role?", "category": "gap", "tip": "Show enthusiasm and a concrete learning plan with timeline."})
        return {"questions": questions[:5], "powered_by": "rule-based fallback"}


# ─── Module-level singleton ───
coach_service = GeminiCoachService()
