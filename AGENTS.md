##  Mission Profile
- **Project Name:** doppler-colab
- **Core Stack:** Python
- **Constraint:** Prioritize lightweight, ephemeral execution specifically targeting Notebooks. No CLI or background path hook dependencies.

##  Agent Roles & Permissions
### Lead Architect
- **Domain:** Project Root (`pyproject.toml`) & CI/CD.
- **Responsibility:** Reviewing all code artifacts and managing the `Implementation Plan`.
- **Permissions:** Full terminal access for builds and dependency management.

### Feature Specialist
- **Domain:** `/src/doppler_colab` and scripts.
- **Responsibility:** Writing modular, testable logic targeting `httpx` and Google Colab native behavior.
- **Constraint:** Must provide a `Unit Test` artifact for every change.

##  Operating Procedures
- **Pre-Flight:** Every session begins with a `git pull` and dependency sync.
- **Workflow:** **Plan** (Artifact) → **Execute** (Terminal) → **Verify** (Browser/Test).
- **Hard Rule:** Never expose or print secret payloads inside Notebook cells. Keep runtime output clean and secure by default.
- **Success Criteria:** A task is only "Done" after a `Walkthrough` artifact is attached.
