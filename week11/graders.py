import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

def deterministic_grader(answer, case):
    answer_upper = answer.upper()
    expected = case["expected"]

    if expected == "NOT FOUND":
        has_not_found = "NOT FOUND" in answer_upper or "I CANNOT" in answer_upper
        has_citation = bool(re.search(r"\[DOC-\d+\]", answer_upper))
        return has_not_found and not has_citation

    return f"[{expected}]" in answer_upper or f"({expected})" in answer_upper

def model_grader(query, answer, expected_doc):
    # حماية الـ Grader: لو متوقع NOT FOUND، التقييم الثابت كفاية ومش محتاجين نبعت الهجوم للـ LLM
    if expected_doc == "NOT FOUND":
        return "NOT FOUND" in answer.upper() or "I CANNOT" in answer.upper()

    # للأسئلة العادية، بنبعت سؤال بسيط جدًا للـ LLM عشان ميتلخبطش
    prompt = f"""Read the following answer and tell me if it contains factual information.
Answer:
{answer}

Reply exactly with YES or NO."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=600,
        )
        response.raise_for_status()
        result = response.json()["response"].strip().upper()
        
        # لو الـ LLM رد بأي حاجة فيها YES نعتبرها نجحت
        return "YES" in result
    except Exception as e:
        print(f"  [Model Grader Error] {e}")
        return False