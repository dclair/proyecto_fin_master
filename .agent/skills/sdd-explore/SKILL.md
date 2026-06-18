---
name: sdd-explore
description: "Executes the exploration phase of Spec-Driven Development (SDD). Analyzes project readiness, architecture, and identifies gaps before proposing changes. Specially focused on production readiness."
---

# SDD Explore Skill

You are executing the `sdd-explore` phase of the Spec-Driven Development (SDD) workflow. 

## Goal
Perform a deep architectural and production-readiness exploration of the current codebase without making any modifications.

## Execution Steps
1. **Analyze the Project Structure**: Look at the root directory, identify the framework (e.g., Django, React, etc.), and the database configuration.
2. **Production Readiness Audit**: 
   - Check for hardcoded secrets or misconfigured environment variables.
   - Check the database (e.g., using SQLite in production is an anti-pattern).
   - Check static files serving strategies.
   - Check security settings (e.g., in Django, `DEBUG = True`, `ALLOWED_HOSTS`, CORS, etc.).
3. **Review Documentation**: Read `README.md`, architecture docs, etc., to see if they match the current state.
4. **Generate Report**: Produce an exploration report summarizing your findings, risks, and next recommended steps.

## Output Contract
You MUST write your findings into a local file (following the `openspec` convention).
- Save the report to: `.sdd/changes/auditoria-produccion/explore.md`
- The report must include sections: `Status`, `Executive Summary`, `Key Findings`, `Risks`, and `Next Recommended`.

Execute these steps meticulously.
