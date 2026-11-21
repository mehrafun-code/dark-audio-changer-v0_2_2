import json
import re
from . import config


def _claude(texts: list[str]) -> list[str]:
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    prompt = (
        "Translate these English dialogue lines into natural, spoken Hindi (Devanagari), "
        "like in a movie dub. Keep each line short and conversational. "
        "Return ONLY a JSON array of strings, same order and same length.\n\n"
        + json.dumps(texts, ensure_ascii=False)
    )
    msg = client.messages.create(
        model=config.CLAUDE_MODEL, max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    out = "".join(b.text for b in msg.content if b.type == "text")
    m = re.search(r"\[.*\]", out, re.S)
    result = json.loads(m.group(0))
    if len(result) != len(texts):
        raise ValueError("Translation length mismatch")
    return result


def _google(texts: list[str]) -> list[str]:
    from deep_translator import GoogleTranslator
    tr = GoogleTranslator(source="auto", target=config.TARGET_LANG)
    return [tr.translate(t) for t in texts]


def translate_all(texts: list[str]) -> list[str]:
    if config.ANTHROPIC_API_KEY:
        try:
            out = []
            for i in range(0, len(texts), 40):  # batches
                out += _claude(texts[i:i + 40])
            return out
        except Exception as e:
            print("Claude translate failed, fallback to Google:", e)
    return _google(texts)
