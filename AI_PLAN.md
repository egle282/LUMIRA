# AI PLAN

## 1. Provider Strategy
- **Primary LLM:** Gemini Pro (for complex astrological reasoning and long context memory).
- **Fallback LLM:** OpenRouter (e.g., Claude or GPT-4o) if Gemini rate limits or fails.
- **Provider Abstraction:** `LLMProvider` interface to easily switch models.

## 2. Data Flow (Strict Separation)
The AI **never** calculates planetary positions or scores.
1. User asks a question.
2. System retrieves deterministic data (Natal Chart, current Transits, Panchanga) from Astrology Engine.
3. System fetches User Memory (past readings, corrections, facts).
4. System constructs prompt: `[Astrology Data] + [User Question] + [Rules] + [Memory]`.
5. LLM interprets the deterministic data and provides structured output.

## 3. Structured Outputs
LLM responses will be forced into JSON schemas using Function Calling / Structured Outputs.
Example Schema:
```json
{
  "summary": "string",
  "factors": ["string"],
  "risks": ["string"],
  "recommendations": ["string"],
  "disclaimer": "string"
}
```

## 4. Daily Briefing Pipeline
A cron job runs at midnight (user's timezone):
1. Calculates Panchanga and transits for the day.
2. Identifies affected Life Areas.
3. Asks AI to generate a personalized briefing.
4. Sends via Telegram.
