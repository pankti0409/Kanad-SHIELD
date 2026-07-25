STOP PATCHING THE EXISTING SYSTEM.

Do not attempt to fix individual bugs one by one.

Instead, perform a complete engineering audit of the entire TraceVault project and rebuild any subsystem that prevents the platform from reaching production quality.

The current implementation is NOT acceptable.

Current issues include (but are not limited to):

• Audio upload workflow is broken.
• Upload does not properly accept or validate supported audio formats.
• Backend processing fails after upload.
• Transcript generation is unreliable or incomplete.
• The entire transcript is not being processed as a single coherent document.
• Multiple file upload workflow is not production ready.
• Error handling is insufficient.
• The UI and UX are incomplete and do not feel like a finished enterprise application.

Do not preserve existing architecture simply because it already exists.

If a subsystem is poorly designed, replace it.

If an algorithm is not appropriate, replace it.

If a workflow is broken, redesign it.

Always choose the architecture that best satisfies the project requirements.

================================================================================

TARGET WORKFLOW

The complete workflow must be:

1.

User creates or opens an Investigation Case.

↓

2.

User uploads one or more supported audio recordings.

Supported formats include at least:

WAV
MP3
M4A
AAC
FLAC
OGG
OPUS
AMR
WMA
3GP
MP4 (audio extraction)
MKV (audio extraction)
WEBM (audio extraction)

The upload component must:

• support drag-and-drop
• support multiple files
• show upload progress
• validate files
• display meaningful errors
• allow retry
• queue multiple uploads

↓

3.

Backend validates every uploaded file.

↓

4.

Generate SHA-256 hash immediately.

↓

5.

Perform audio preprocessing:

• format normalization
• sample rate normalization
• channel normalization
• silence trimming where appropriate
• noise reduction
• voice activity detection

↓

6.

Run multilingual Speech-to-Text using Faster-Whisper Large-v3 (or another high-quality open-source model if demonstrably better for the project requirements).

Requirements:

• Hindi
• Gujarati
• English
• mixed-language conversations

The transcript must be generated for the ENTIRE conversation.

Do not split the transcript into unrelated fragments.

Preserve timestamps.

Preserve ordering.

↓

7.

Run speaker diarization.

The output must clearly indicate:

Speaker 1

Speaker 2

Speaker 3

...

Every transcript segment must identify the speaker and timestamps.

↓

8.

Run transcript intelligence extraction.

Extract at minimum:

• people
• aliases
• organisations
• locations
• phone numbers
• account numbers
• monetary values
• dates
• times
• addresses
• vehicles (if mentioned)
• weapons (if mentioned)
• case-relevant identifiers

Use evidence-backed extraction only.

Do not fabricate entities.

↓

9.

Run threat analysis.

Identify evidence of:

• extortion
• fraud
• scam
• kidnapping
• violence
• bribery
• blackmail
• coercion
• illegal transactions
• suspicious coordination

Every finding must include supporting transcript evidence.

↓

10.

Run emotion and conversation analysis.

Where supported by the chosen models:

• anger
• fear
• stress
• urgency
• neutral
• calm

Do not invent emotions.

Only report confidence-supported results.

↓

11.

Generate a structured investigation report.

The report should include:

Executive Summary

Languages

Speakers

Conversation Summary

Named Entities

Threat Indicators

Emotion Timeline

Important Quotes

Timeline of Important Events

Evidence References

Confidence Information

Evidence Integrity

Recommendations

Chain of Custody Information

Audit Metadata

↓

12.

Store every result in the database.

↓

13.

Update dashboard analytics.

↓

14.

Allow investigators to:

search

filter

sort

bookmark

annotate

export

generate PDF

generate CSV

generate JSON

================================================================================

QUALITY REQUIREMENTS

This is NOT a hackathon prototype.

Build it like enterprise software.

The application must feel complete.

Every page must have:

loading states

empty states

error states

success states

responsive layouts

consistent typography

consistent spacing

proper accessibility

light theme

dark theme

================================================================================

AI REQUIREMENTS

The system should prioritise accuracy over creativity.

Never hallucinate.

Never invent entities.

Never invent threats.

Never invent people.

Never invent locations.

If confidence is insufficient, explicitly state that evidence is insufficient.

Every AI conclusion should reference supporting transcript segments whenever applicable.

================================================================================

ENGINEERING REQUIREMENTS

Review the entire backend.

Review the entire frontend.

Review the database.

Review APIs.

Review AI pipeline.

Review routing.

Review authentication.

Review uploads.

Review storage.

Review background processing.

Review state management.

Review security.

Replace weak implementations where necessary.

Do not preserve bad architecture.

================================================================================

BUG FIXING

Do not only fix the reported upload issue.

Search for every bug in the application.

Resolve runtime errors.

Resolve logic errors.

Resolve UI issues.

Resolve API issues.

Resolve state management issues.

Resolve database issues.

Resolve concurrency issues.

Resolve upload issues.

Resolve processing issues.

Resolve report generation issues.

Resolve export issues.

Verify every complete workflow from upload to report generation.

================================================================================

FINAL VALIDATION

Do not stop because the project compiles.

Do not stop because the UI loads.

Do not stop because the backend starts.

The implementation is complete only when:

• audio upload works reliably
• multiple uploads work reliably
• transcription works end-to-end
• diarization works
• transcript intelligence works
• threat analysis works
• reports are generated
• exports function
• dashboard updates correctly
• no critical runtime errors remain
• the entire upload → analysis → report workflow has been verified successfully.

If rebuilding a subsystem results in a cleaner, more reliable architecture, prefer rebuilding over patching.