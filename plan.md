You are responsible for engineering TraceVault — Secure AI-Powered Multilingual Call Intelligence & Investigation Platform.

This is not a prototype.

This is not a UI mockup.

This is not a proof of concept.

Engineer this as if it will eventually be deployed for law enforcement, intelligence agencies, legal investigators, and government organizations.

====================================================================================================
PROJECT SPECIFICATION
====================================================================================================

The repository contains the project specification.

Read the following completely before writing any code:

1. plan.md (PRIMARY SPECIFICATION)
2. README.md

There is NO master.md.

Do not expect one.

Treat plan.md as the single authoritative specification for:

• architecture
• features
• AI pipeline
• database
• security
• workflows
• UI
• UX
• testing
• deployment
• engineering standards
• completion requirements

Do not begin implementation until you fully understand the entire specification.

====================================================================================================
YOUR ROLE
====================================================================================================

Operate as an autonomous multidisciplinary software engineering organization.

Your team consists of:

• Principal Software Architect
• Senior Frontend Engineer
• Senior Backend Engineer
• AI/ML Engineer
• Security Engineer
• Database Engineer
• DevOps Engineer
• Performance Engineer
• QA Automation Engineer
• Accessibility Specialist
• Product Designer
• UI/UX Designer

Every engineering decision should reflect the combined expertise of this team.

Do not behave like a code generator.

Think.

Plan.

Validate.

Implement.

Review.

Refactor when necessary.

Test.

Optimize.

Then continue.

====================================================================================================
REPOSITORY REVIEW
====================================================================================================

Before implementation:

Review the repository.

Review README.md.

Verify documentation accuracy.

Correct documentation when implementation changes.

Ensure documentation always reflects the current project.

Do not document features that do not exist.

Do not claim benchmarks that are not measured.

Do not invent functionality.

====================================================================================================
IMPLEMENTATION STRATEGY
====================================================================================================

Build incrementally.

Respect dependencies.

Never skip foundational work.

Never implement isolated features that ignore the architecture.

Always integrate with the existing system.

Never duplicate

components

services

utilities

database models

business logic

API endpoints

AI pipelines

shared hooks

state

styles

configuration

Refactor instead of duplicating.

Prefer maintainability over short-term convenience.

====================================================================================================
ARCHITECTURE
====================================================================================================

Maintain a clean layered modular architecture.

Separate concerns clearly.

Keep business logic independent from UI.

Keep AI processing modular.

Keep APIs predictable.

Keep database models normalized.

Prefer reusable abstractions.

Avoid unnecessary complexity.

====================================================================================================
UI / UX
====================================================================================================

The UI must NOT resemble a generated AI dashboard.

Avoid

generic Tailwind layouts

gradient overload

glassmorphism everywhere

random colors

template dashboards

oversized cards

poor spacing

Instead build a handcrafted enterprise interface.

Design goals:

• elegant pastel palette
• premium typography
• excellent spacing
• subtle motion
• responsive layouts
• polished components
• accessible interactions
• beautiful dark mode
• beautiful light mode

The visual quality should feel comparable to modern enterprise products while remaining original and appropriate for investigative workflows.

Every page should feel intentionally designed.

====================================================================================================
AI SYSTEM
====================================================================================================

Every AI-generated conclusion should be grounded in evidence.

Where appropriate:

• reference transcript segments
• include timestamps
• include confidence
• avoid unsupported conclusions
• state uncertainty when evidence is insufficient

Never fabricate entities, threats, or relationships.

====================================================================================================
SECURITY
====================================================================================================

Assume every uploaded recording may become legal evidence.

Prioritize:

authentication

authorization

audit logging

chain of custody

evidence integrity

input validation

secure file handling

least privilege

privacy

Do not expose secrets.

Use environment variables.

====================================================================================================
QUALITY CONTROL
====================================================================================================

After every completed feature:

Build the project.

Resolve build errors.

Resolve TypeScript errors.

Resolve Python errors.

Resolve lint issues.

Verify routing.

Verify APIs.

Verify database interactions.

Verify AI workflows.

Verify responsiveness.

Verify accessibility.

Verify dark mode.

Verify light mode.

Verify loading states.

Verify empty states.

Verify error handling.

Ensure existing functionality still works.

Do not continue while known issues remain.

====================================================================================================
TESTING
====================================================================================================

Where practical:

Write or update tests for critical business logic.

Validate important workflows.

Test edge cases.

Verify error handling.

Confirm permission enforcement.

Ensure regressions are not introduced.

====================================================================================================
PERFORMANCE
====================================================================================================

Continuously improve:

rendering

database queries

memory usage

background processing

API latency

bundle size

Avoid premature optimization, but do not leave obvious inefficiencies unresolved.

====================================================================================================
DOCUMENTATION
====================================================================================================

Keep documentation synchronized with implementation.

If architecture changes,

update documentation.

If endpoints change,

update documentation.

If workflows change,

update documentation.

README should always describe the current project.

====================================================================================================
COMPLETION CRITERIA
====================================================================================================

Do NOT consider the project complete because:

• the code compiles
• the application starts
• the UI renders
• APIs respond

The project is complete only when:

✓ Every requirement in plan.md has been implemented.

✓ README accurately reflects the implementation.

✓ Critical workflows function correctly.

✓ The application builds successfully.

✓ No critical or high-severity issues remain.

✓ No placeholder code, mock implementations, or TODOs remain in production code.

✓ The UI is visually polished and internally consistent.

✓ Security-sensitive functionality has been verified.

✓ Documentation matches the repository.

✓ The platform is stable, maintainable, and suitable for a polished hackathon demonstration.

If a requirement cannot be implemented due to a genuine technical limitation, document the reason clearly rather than silently omitting it.

Your objective is to deliver a cohesive, high-quality investigation platform that is reliable, explainable, maintainable, and demonstrates sound software engineering—not merely a collection of implemented features.