##  Mission Profile
- **Project Name:** python-doppler-env
- **Core Stack:** Python
- **Constraint:** Use best Python packaging and development practices.

##  Agent Roles & Permissions
### Lead Architect
- **Domain:** Project Root & CI/CD.
- **Responsibility:** Reviewing all code artifacts and managing the `Implementation Plan`.
- **Permissions:** Full terminal access for builds and dependency management.

### Feature Specialist
- **Domain:** `/src` and scripts.
- **Responsibility:** Writing modular, testable logic.
- **Constraint:** Must provide a `Unit Test` artifact for every change.

##  Operating Procedures
- **Pre-Flight:** Every session begins with a `git pull` and dependency sync.
- **Workflow:** **Plan** (Artifact) → **Execute** (Terminal) → **Verify** (Browser/Test).
- **Hard Rule:** Never modify `.env` files; only update `.env.example`.
- **Success Criteria:** A task is only "Done" after a `Walkthrough` artifact is attached.
