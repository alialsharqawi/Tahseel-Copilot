# LMS Requirements, Deadlines, and Grading

Transcribed from the notices and screenshots we received, so the whole team can read them. The original screenshots are kept privately and are not part of the repository. Open questions and to-dos are tracked in `PROJECT_STATUS.md`; this file holds the facts as announced.

---

## 1. Notice from CLS Learning Solutions (Digital Egypt Pioneers, Phase 5)

Final graduation-project teams are approved, according to the division in the Google Drive file.

### First: complete the project data
- Choose a **Project Name**. (Chosen: Tahseel AI, Decision Log D26.)
- Create a **GitHub repository** for the project. Each team must have **exactly one** GitHub link. (Name: `Tahseel-Copilot`, D26 as amended 4 Nov 2026.)
- Record the project name and GitHub link in the designated columns of the projects sheet on Google Drive.

### Second: Project Documentation requirements (the first three parts)
1. **Project Planning & Management:** clarify the idea, goals, and scope; set a timeline; distribute tasks and responsibilities among team members; identify potential risks and how to handle them; define success metrics.
2. **Literature Review:** research similar projects or solutions; identify their strengths and weaknesses; compare them with our project to show the differences and what we can learn; document the sources used.
3. **Requirements Gathering:** identify the beneficiaries and stakeholders and their needs; the functions and features the project will provide; quality requirements such as performance, security, and ease of use, matching the nature and track of the project.

### Delivery method & Submission Status
- Combine the required parts of the Project Documentation into **one PDF** and upload it to the team's GitHub repository root (`Tahseel_Project_Documentation_v1.pdf`).
- **Submission Status:** The Team Leader (Ali Al-Sharqawi) **already submitted** all required links on the LMS portal on time. Because formal grading is deferred to the final capstone evaluation, the submitted links act as dynamic live references:
  1. **Documentation link:** Direct URL to `Tahseel_Project_Documentation_v1.pdf` in the repository root. *(The PDF remains permanently located at the root directory so the submitted link never breaks; once Stage 3 is complete, the newly compiled documentation replaces this file in-place).*
  2. **GitHub link:** The team repository URL (`https://github.com/alialsharqawi/Tahseel-Copilot`).
  3. **Presentation link:** Live Canva presentation link (submitted as a placeholder deck, to be populated with final slides and benchmark numbers in Stage 7).

### Dates and Milestones
- **Initial Submission Deadline:** Successfully satisfied via dynamic submission links.
- **Final Evaluation / Grading:** Conducted at the graduation project defense based on the active repository, live documentation PDF, and presentation deck.

### Other
- The notice refers to a **Project Documentation Guidelines** file sent earlier to the groups (full details, deadlines, and the track-specific rules). We do not have a copy.
- Questions go to the Technical Instructor.

---

## 2. LMS assignment: "DEPI GradProject" (course R5_CLS)

- **Opened:** Thursday, 22 October 2026, 12:00 AM
- **Due:** **Saturday, 31 October 2026, 12:00 AM** (that is, the end of Friday 30 October)
- **Submission type:** online text (a rich-text box where we paste links)

**What to submit**
1. **Documentation link:** Project Planning, Stakeholder Analysis, Database Design, UI/UX Design
2. **GitHub link:** source code
3. **Presentation link:** video demonstration and PDF

---

## 3. Documentation structure (a working assumption)

The two notices list different parts. The notice names Project Planning & Management, Literature Review, and Requirements Gathering. The LMS page names Project Planning, Stakeholder Analysis, Database Design, and UI/UX Design. We read them as stages of the same documentation: the notice describes the first three parts, and the LMS page adds the design parts. Stakeholder Analysis belongs inside Requirements Gathering, since the notice asks for the beneficiaries and stakeholders and their needs.

Until we get the Documentation Guidelines, we use the union as the working structure (**an assumption**):

1. Project Planning & Management
2. Literature Review
3. Requirements Gathering, including the Stakeholder Analysis
4. System Architecture
5. Database Design
6. UI/UX Design

The documentation language is English (D24). If the guidelines require Arabic, the decision is revisited.

The notice asks for one PDF uploaded to the repository, and the LMS asks for a "Documentation link". We assume the link points to that PDF in the repository. This is **an assumption** to confirm.

---

## 4. Grading rubric (same seven criteria for any project)

| Criterion | Weight |
|---|---:|
| System Architecture | 20% |
| UI & Dashboard | 15% |
| RAG & Memory | 15% |
| Code Quality | 15% |
| Presentation | 15% |
| Real-World Value | 10% |
| Team Collaboration | 10% |

---

## 5. What we will produce for each requirement

References are by file and section name, not by number.

| Required item | Source material we already have | Status |
|---|---|---|
| Project Planning & Management | `Final_Concept` (goals, scope, tiers), `Decision_Log` (decisions, cut order), `Business_Strength` (business risks), `PRD` (KPIs; its 8-week plan is only a proposal) | Needs a real project plan: milestones, owners, dates |
| Literature Review | `Business_Strength` (problem evidence, competitive landscape, sources) | Needs expanding: more solutions, strengths and weaknesses, a comparison, and the sources |
| Requirements Gathering and Stakeholder Analysis | `Business_Strength` (stakeholder analysis), `PRD` (user stories, acceptance criteria, API), `Final_Concept` (scope tiers) | The material exists; it needs formatting as functional and quality requirements |
| System Architecture | `Final_Concept` (architecture), `Technical_Strength` (pipeline vs agent, ADRs, security), `Adaptability_Strategy` | Needs a drawn diagram |
| Database Design | `PRD` (data model, field level) and `Final_Concept` (data model) | Needs an ERD |
| UI/UX Design | `Final_Concept` (demo flow), `Decision_Log` (D14) | Needs wireframes in Arabic and English |
| GitHub (source code) | none | No code yet; the repository is `Tahseel-Copilot` (D26 as amended) |
| Presentation PDF and demo video | `Final_Pitch` | Skeleton ready; needs real numbers and screenshots |
| Project name and repository link | `Decision_Log` (D26) | Tahseel AI, `Tahseel-Copilot` (D26 amended 4 Nov 2026) |