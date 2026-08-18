import json
import re
from openai import OpenAI
from ..config import Settings


class QuestionGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def question(self, role: str, summary: str, skills: list[str], context: list[dict], ordinal: int, previous_answer: str | None = None) -> dict:
        passages = "\n\n".join(f"[{i+1}] {c['source']}: {c['text']}" for i, c in enumerate(context))
        if self.client:
            prompt = f"""You are conducting a rigorous {role} interview. Generate exactly one original question grounded in the retrieved passages and tailored to the candidate. Do not copy a passage or use generic trivia. Increase depth for question {ordinal}.

Candidate summary: {summary}
Candidate skills: {', '.join(skills) or 'not confidently extracted'}
Previous answer: {previous_answer or 'none'}
Retrieved passages:\n{passages}

Return JSON only: {{"prompt":"...","topic":"...","difficulty":"foundation|applied|advanced"}}"""
            response = self.client.responses.create(model=self.settings.openai_model, input=prompt, temperature=0.35)
            return self._json(response.output_text)
        return self._grounded_fallback(role, skills, context, ordinal, previous_answer)

    def report(self, role: str, questions: list[dict]) -> dict:
        transcript = "\n\n".join(f"Q: {q['prompt']}\nA: {q.get('answer') or ''}" for q in questions)
        if self.client:
            prompt = f"""Evaluate this {role} interview. Score 0-100 using conceptual accuracy, applied reasoning, tradeoff awareness, and clarity. Return JSON only with keys score (integer), summary (string), strongest_area (string), depth (string), strengths (array of 2 strings), improvements (array of 2 strings). Do not invent evidence.\n\n{transcript}"""
            response = self.client.responses.create(model=self.settings.openai_model, input=prompt, temperature=0.2)
            return self._json(response.output_text)
        answers = [q.get("answer", "") for q in questions]
        detailed = sum(len(answer.split()) >= 45 for answer in answers)
        tradeoffs = sum(bool(re.search(r"trade.?off|however|depends|constraint|risk", answer, re.I)) for answer in answers)
        score = min(88, 50 + detailed * 6 + tradeoffs * 4)
        return {"score": score, "summary": "The candidate showed structured reasoning and connected technical choices to practical outcomes.", "strongest_area": questions[0]["topic"] if questions else role, "depth": "Applied", "strengths": ["Structured problem decomposition", "Practical implementation awareness"], "improvements": ["Use concrete metrics and validation criteria", "State failure modes and operational tradeoffs"]}

    @staticmethod
    def _json(text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise ValueError("Model did not return a JSON object")
        return json.loads(match.group(0))

    @staticmethod
    def _grounded_fallback(role: str, skills: list[str], context: list[dict], ordinal: int, previous_answer: str | None) -> dict:
        if not context:
            raise RuntimeError("No role knowledge has been ingested")
        excerpt = context[0]["text"].split(". ")[0].strip()
        signal = skills[0] if skills else role
        followup = " Building on your previous answer, identify the weakest assumption and how you would test it." if previous_answer else ""
        return {"prompt": f"The knowledge source states: ‘{excerpt[:240]}.’ Relate this concept to your experience with {signal}, then design a practical approach and defend its tradeoffs.{followup}", "topic": context[0]["source"].rsplit(".", 1)[0], "difficulty": "foundation" if ordinal == 1 else "applied" if ordinal < 4 else "advanced"}
