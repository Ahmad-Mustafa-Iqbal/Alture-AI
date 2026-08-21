from typing import List
from .schemas import JobPosting, SamplePersona

SAMPLE_PERSONAS: List[SamplePersona] = [
    SamplePersona(
        id="persona-ai-eng",
        name="Alex Chen",
        title="Senior AI & Machine Learning Engineer",
        summary="5+ years experience building LLM pipelines, PyTorch models, and high-scale FastAPI microservices.",
        resume_text="""Alex Chen | Senior AI / ML Engineer
Contact: alex.chen@example.com | San Francisco, CA | github.com/alexchen | linkedin.com/in/alexchen-ai

Summary:
Results-driven AI & Machine Learning Engineer with 5+ years of experience designing, training, and deploying large-scale NLP, Deep Learning, and Computer Vision architectures into production. Expert in PyTorch, Hugging Face Transformers, Sentence-BERT, LangChain, RAG pipelines, FastAPI, and Dockerized microservices. Experienced in building real-time semantic search, recommendation engines, and ML training pipelines on AWS and GCP.

Technical Skills:
• Programming & Core: Python (Advanced), C++, SQL, Bash, Git, Linux
• Machine Learning & NLP: PyTorch, TensorFlow, Scikit-Learn, XGBoost, LightGBM, Hugging Face, Transformers, Sentence-BERT, spaCy, NLTK, OpenCV
• LLM & GenAI: LangChain, LlamaIndex, RAG, Vector Databases (Pinecone, ChromaDB, Weaviate), OpenAI API, Prompt Engineering
• Cloud & MLOps: AWS (EC2, S3, SageMaker), GCP, Docker, Kubernetes, CI/CD (GitHub Actions), MLflow, DVC, Airflow
• Backend & Systems: FastAPI, Flask, REST API, gRPC, PostgreSQL, Redis, Microservices, Distributed Systems

Professional Experience:
Senior AI Engineer | NeuralScale AI (2022 - Present) | San Francisco, CA
• Designed and deployed a multi-tenant LLM RAG platform serving 2M+ monthly queries using LangChain, Pinecone, and FastAPI, cutting latency by 45%.
• Fine-tuned open-source Transformer models (Llama 3, Mistral) using LoRA and PyTorch, achieving 94.2% domain intent accuracy.
• Engineered distributed feature extraction and embedding pipelines processing 50M+ documents using Sentence-BERT, Redis, and Celery.
• Mentored 4 junior ML engineers and established MLOps practices with automated CI/CD and MLflow tracking.

Machine Learning Engineer | Cortex Dynamics (2019 - 2022) | Seattle, WA
• Developed real-time recommendation algorithms and semantic matching pipelines using XGBoost, Scikit-Learn, and Word2Vec, increasing user engagement by 28%.
• Built high-throughput asynchronous REST APIs using FastAPI and Docker, containerized on AWS ECS.
• Integrated PostgreSQL and Redis caching layers to reduce average response time from 350ms to 48ms.

Education:
• Master of Science in Computer Science (AI Track) | Stanford University
• Bachelor of Science in Software Engineering | University of Washington
"""
    ),
    SamplePersona(
        id="persona-fullstack",
        name="Sarah Jenkins",
        title="Full-Stack Web Developer (React + Python/Node)",
        summary="4+ years developing scalable SaaS web applications with React, Next.js, FastAPI, Node.js, and PostgreSQL.",
        resume_text="""Sarah Jenkins | Full-Stack Software Engineer
Contact: sarah.jenkins@example.com | London, UK | github.com/sjenkins-dev | linkedin.com/in/sarah-jenkins-dev

Summary:
Dynamic Full-Stack Software Engineer with 4+ years of hands-on experience building modern, accessible, and high-performance web applications. Proficient across the entire software development lifecycle, from designing intuitive React/Next.js frontends to architecting robust backend APIs using FastAPI, Node.js, Express, and PostgreSQL. Passionate about clean code, component-driven design, and CI/CD automation.

Technical Skills:
• Frontend: JavaScript (ES6+), TypeScript, React, Next.js, Vue.js, HTML5, CSS3, Tailwind CSS, Redux, Webpack, Vite
• Backend: Python, FastAPI, Django, Node.js, Express, REST API, GraphQL, Microservices
• Databases: PostgreSQL, MySQL, MongoDB, Redis, SQLite, Prisma ORM, SQLAlchemy
• DevOps & Tools: Docker, Git, GitHub Actions, AWS (S3, CloudFront), Linux, Agile, Scrum, Unit Testing (Jest, Pytest)

Professional Experience:
Full-Stack Engineer | FinTech Horizon (2021 - Present) | London, UK
• Engineered core customer dashboard in Next.js, React, and Tailwind CSS, improving core web vitals and reducing page load times by 35%.
• Architected asynchronous REST APIs in FastAPI with Pydantic validation and JWT authentication, supporting 100k+ daily transactions.
• Designed PostgreSQL schema and query optimizations with Redis caching, decreasing database query latency by 40%.
• Built automated CI/CD deployment workflows using GitHub Actions and Docker.

Junior Software Developer | CloudBase Digital (2019 - 2021) | Manchester, UK
• Built responsive frontend components using React and styled-components for an enterprise analytics SaaS.
• Developed RESTful endpoints using Node.js, Express, and MongoDB.
• Implemented unit and integration tests using Jest and Supertest, achieving 85%+ test coverage.

Education:
• B.Sc. in Computer Science | University of Manchester
"""
    ),
    SamplePersona(
        id="persona-devops",
        name="Marcus Vance",
        title="Lead Cloud & DevOps Engineer",
        summary="6+ years specializing in Kubernetes, Terraform, AWS multi-region architectures, and automated CI/CD pipelines.",
        resume_text="""Marcus Vance | Lead DevOps & Cloud Infrastructure Engineer
Contact: marcus.vance@example.com | Austin, TX | github.com/marcus-vance | linkedin.com/in/marcus-vance-cloud

Summary:
Accomplished Cloud & DevOps Engineer with 6+ years of expertise designing, scaling, and automating resilient multi-cloud infrastructures. Proven track record implementing Infrastructure as Code (Terraform), Kubernetes cluster orchestration, zero-downtime CI/CD pipelines, and proactive observability platforms on AWS and GCP.

Technical Skills:
• Cloud Platforms: AWS (EKS, EC2, S3, RDS, IAM, VPC), GCP, Microsoft Azure
• Containerization & Orchestration: Kubernetes, Docker, Helm, Docker Swarm, OpenShift
• Infrastructure as Code (IaC): Terraform, Ansible, CloudFormation
• CI/CD & Automation: GitHub Actions, GitLab CI, Jenkins, ArgoCD, Bash, Python
• Monitoring & Observability: Prometheus, Grafana, Datadog, ELK Stack (Elasticsearch, Logstash, Kibana)
• Networking & Security: Linux (RHEL, Ubuntu), Nginx, Istio Service Mesh, OAuth, SSL/TLS, Vault

Professional Experience:
Lead DevOps Engineer | ScaleForge Systems (2021 - Present) | Austin, TX
• Architected multi-region AWS EKS Kubernetes clusters handling 50M+ requests daily with 99.99% uptime.
• Reduced infrastructure provisioning time from 2 weeks to 20 minutes by authoring modular Terraform code.
• Implemented GitOps deployment workflows using ArgoCD and GitHub Actions, cutting production deployment failures by 60%.
• Configured Prometheus, Grafana, and Datadog alerts for real-time anomaly detection and SLO tracking.

Cloud Operations Engineer | DataStream Enterprise (2018 - 2021) | Denver, CO
• Managed Docker containerization of 40+ legacy services and migrated infrastructure to AWS.
• Built automated CI/CD pipelines with Jenkins and GitLab CI.
• Enforced security compliance, automated backup routines, and IAM least-privilege policies.

Education:
• B.S. in Information Technology & Network Security | University of Colorado
• Certified Kubernetes Administrator (CKA) | AWS Certified Solutions Architect - Professional
"""
    )
]

SAMPLE_JOBS: List[JobPosting] = [
    JobPosting(
        id="job-ai-lead",
        title="Senior AI / ML Research Engineer",
        company="Anthropic-Style AI Labs",
        location="San Francisco, CA / Remote",
        type="Remote",
        salary_range="$180,000 - $240,000",
        required_skills=["python", "pytorch", "transformers", "sentence-bert", "nlp", "fastapi", "docker", "aws", "rag", "scikit-learn"],
        jd_text="""Job Title: Senior AI / ML Research Engineer
Location: San Francisco, CA (Remote Friendly)
Company: NextGen Intelligence Labs
Salary: $180,000 - $240,000 + Equity

About the Role:
We are seeking an exceptional Senior AI/ML Engineer to lead the design and deployment of cutting-edge NLP, Transformer embeddings, and RAG architectures. You will collaborate directly with our founding research team to turn state-of-the-art AI into ultra-fast, production-grade microservices.

Key Responsibilities:
• Build and fine-tune large-scale Transformer models, Sentence-BERT semantic matching pipelines, and LLM inference workflows.
• Design scalable, low-latency REST APIs in Python using FastAPI, Docker, and Redis caching.
• Build automated MLOps pipelines on AWS/GCP for continuous evaluation, benchmarking, and deployment.
• Optimize model inference latency and vector search across millions of embeddings.

Mandatory Requirements:
• 4+ years of professional AI/ML engineering experience in Python.
• Strong mastery of PyTorch, Scikit-Learn, XGBoost, and Hugging Face Transformers.
• Production experience with Sentence-BERT, spaCy, and NLP semantic similarity.
• Proven track record building and deploying production APIs using FastAPI, Docker, and AWS.
• Solid background in vector databases (Pinecone, ChromaDB) and RAG architectures.
"""
    ),
    JobPosting(
        id="job-fullstack-dev",
        title="Senior Full-Stack Engineer (React + Python/FastAPI)",
        company="VentureFlow SaaS",
        location="London, UK / Hybrid",
        type="Hybrid",
        salary_range="£85,000 - £110,000",
        required_skills=["react", "nextjs", "typescript", "python", "fastapi", "postgresql", "docker", "tailwind", "rest api"],
        jd_text="""Job Title: Senior Full-Stack Engineer
Location: London, UK (Hybrid - 2 days/week in office)
Company: VentureFlow Technologies
Salary: £85,000 - £110,000 + Benefits

About the Role:
VentureFlow is looking for a talented Senior Full-Stack Software Engineer to build our next-generation enterprise investment platform. You will have full ownership across the modern React/Next.js frontend and high-throughput Python/FastAPI microservices.

Key Responsibilities:
• Architect clean, modern, and accessible user interfaces in React, Next.js, TypeScript, and Tailwind CSS.
• Develop high-performance, asynchronous RESTful APIs using Python, FastAPI, and SQLAlchemy.
• Design and optimize PostgreSQL database schemas, indexing, and Redis caching.
• Write comprehensive unit and integration tests, participating in code reviews and agile sprints.

Requirements:
• 4+ years experience in Full-Stack web development.
• Deep proficiency with React, TypeScript, and modern CSS frameworks (Tailwind).
• Strong backend experience with Python (FastAPI or Django) or Node.js.
• Strong relational database design skills with PostgreSQL.
• Experience with Docker, Git, and automated CI/CD pipelines.
"""
    ),
    JobPosting(
        id="job-devops-lead",
        title="Lead Cloud & Kubernetes Architect",
        company="Apex Global Cloud",
        location="New York, NY / Remote",
        type="Remote",
        salary_range="$170,000 - $215,000",
        required_skills=["kubernetes", "docker", "terraform", "aws", "ci/cd", "prometheus", "grafana", "linux", "python", "ansible"],
        jd_text="""Job Title: Lead Cloud & Kubernetes Architect
Location: New York, NY (100% Remote)
Company: Apex Cloud Infrastructure
Salary: $170,000 - $215,000 + Bonus

About the Role:
We are hiring a Lead DevOps / Cloud Infrastructure Architect to scale our globally distributed cloud footprint. You will lead Kubernetes orchestration, Infrastructure as Code, and automated multi-region deployments on AWS.

Key Responsibilities:
• Architect, operate, and scale production Kubernetes (EKS) clusters handling high-traffic enterprise workloads.
• Author, modularize, and maintain infrastructure using Terraform and Ansible.
• Design zero-downtime CI/CD pipelines using GitHub Actions and ArgoCD.
• Maintain end-to-end observability using Prometheus, Grafana, and Datadog.

Requirements:
• 5+ years experience in DevOps, Site Reliability, or Cloud Engineering.
• Expert-level knowledge of Kubernetes (EKS, GKE) and Docker containerization.
• Extensive hands-on experience with Terraform and AWS multi-account architectures.
• Strong scripting abilities in Python or Bash for operational automation.
• Solid background in Linux internals, networking, and SSL/TLS security.
"""
    ),
    JobPosting(
        id="job-data-platform",
        title="Data Platform & Analytics Engineer",
        company="InsightData Corp",
        location="Berlin, Germany / Remote",
        type="Remote",
        salary_range="€75,000 - €95,000",
        required_skills=["python", "sql", "spark", "kafka", "postgresql", "airflow", "docker", "aws", "pandas", "data engineering"],
        jd_text="""Job Title: Data Platform & Analytics Engineer
Location: Berlin, Germany (Remote across EU)
Company: InsightData Analytics
Salary: €75,000 - €95,000

About the Role:
InsightData is seeking a Data Platform Engineer to design and optimize our batch and real-time data pipelines. You will work with petabyte-scale data lakes and power analytics dashboards for Fortune 500 customers.

Key Responsibilities:
• Build distributed data ingestion pipelines using Apache Spark, Kafka, and Python.
• Orchestrate complex data workflows and ETL transformations using Apache Airflow.
• Optimize SQL queries, data warehousing in Snowflake/BigQuery, and PostgreSQL storage.
• Collaborate with ML engineers to build reliable feature stores and data APIs.

Requirements:
• 3+ years experience in Data Engineering or Backend Data Platform development.
• Strong proficiency in Python, Advanced SQL, and PySpark.
• Experience with streaming and batch systems (Kafka, Spark, Airflow).
• Familiarity with Docker, cloud storage (AWS S3), and data quality validation.
"""
    )
]
