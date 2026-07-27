================================================================================
AI INVESTIGATION COPILOT – PRODUCTION-GRADE RAG AGENT
================================================================================

The current chatbot is not sufficient.

Redesign it into a production-grade AI Investigation Copilot.

The Copilot should not behave like a generic chatbot.

It should function as an intelligent investigative assistant with complete knowledge of the TraceVault system.

================================================================================
KNOWLEDGE SOURCES
================================================================================

The Copilot must continuously retrieve information from the system instead of relying on static prompts.

It should automatically use the following knowledge sources whenever answering questions:

• Investigation Cases
• Audio Recordings
• Generated Transcripts
• Transcript Segments
• Speaker Diarization Results
• Extracted Entities
• Threat Detection Results
• Emotion Analysis
• Timeline Events
• Investigation Reports
• Audit Logs
• User Notes
• Bookmarks
• Metadata
• Database Records
• Future uploaded investigations

Whenever new investigations are analysed, they must automatically become available to the Copilot without requiring manual intervention.

================================================================================
AUTOMATIC KNOWLEDGE UPDATES
================================================================================

The Copilot must always work with the latest available data.

Whenever:

• a new audio file is uploaded
• transcription completes
• diarization completes
• entity extraction completes
• threat analysis completes
• a report is generated
• an investigator adds notes
• metadata changes

the knowledge base must automatically update.

The AI should never require manual retraining.

The retrieval index must stay synchronized with the database.

================================================================================
RAG ARCHITECTURE
================================================================================

Implement Retrieval-Augmented Generation (RAG).

Every query should follow this pipeline:

1. Understand the user's intent.
2. Retrieve the most relevant information from the vector database and relational database.
3. Retrieve supporting transcript segments, timestamps, speakers, entities, reports, and metadata.
4. Build grounded context.
5. Send only the relevant context to the LLM.
6. Generate an evidence-backed answer.

Do not answer case-specific questions from the LLM's general knowledge.

Always retrieve evidence first.

================================================================================
DATABASE AWARENESS
================================================================================

The Copilot should understand relationships across the entire system.

For example it should be able to answer:

• Which cases mention this person?
• Which recordings contain this phone number?
• Which threats were detected last month?
• Show every conversation involving Mumbai.
• Which speaker discussed account number XXXXX?
• Which investigations mention extortion?
• Which calls contain high stress?
• Which reports contain financial fraud?
• Which conversations reference the same organisation?
• Compare Case A and Case B.
• Summarise every investigation related to cybercrime.
• Show all evidence connected to this entity.

It should understand relationships rather than searching raw text only.

================================================================================
INTELLIGENT MEMORY
================================================================================

The Copilot should maintain conversational context during the current chat session.

Users should be able to ask follow-up questions naturally.

Example:

User:
Summarise Case 21.

↓

User:
Who issued the threats?

↓

User:
What evidence supports that?

↓

User:
Show me the transcript.

↓

User:
Which locations were mentioned?

The Copilot should understand these follow-up questions without requiring the user to repeat the case name.

================================================================================
ANSWER QUALITY
================================================================================

Responses should resemble a professional intelligence analyst.

They should be:

• well structured
• concise when appropriate
• detailed when requested
• evidence based
• easy to understand
• free from hallucinations

Where applicable include:

• investigation summary
• supporting transcript excerpts
• timestamps
• speaker references
• extracted entities
• threat indicators
• confidence information

If evidence is insufficient, explicitly state that there is insufficient evidence rather than guessing.

================================================================================
GENERAL KNOWLEDGE
================================================================================

If the user asks a general question that is unrelated to stored investigations (for example, "What is speaker diarization?" or "How does SHA-256 work?"), the Copilot may answer using the configured LLM's general knowledge.

Clearly distinguish between:

• information retrieved from TraceVault data
• general knowledge provided by the language model

================================================================================
CONTINUOUS SYNCHRONIZATION
================================================================================

The Copilot must always reflect the current state of the platform.

Any newly analysed recording, transcript, report, entity, or investigation should immediately become searchable and retrievable through the Copilot.

No manual indexing or intervention should be required.

================================================================================
GOAL
================================================================================

The AI Investigation Copilot should feel like a senior digital investigator with complete access to the authorised evidence stored in TraceVault.

It should not merely generate responses—it should retrieve, reason over, correlate, and explain information from the system while remaining fully grounded in the underlying evidence.