# translator.py
# Final production-grade translator module for FYP
# Model: Meta AI NLLB 200 distilled 600M (best stable model for Indian languages)

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------- MODEL CONFIG ----------
MODEL_ID = "facebook/nllb-200-distilled-600M"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Language → NLLB code mapping
LANG_CODES = {
    "english": "eng_Latn",
    "hindi": "hin_Deva",
    "telugu": "tel_Telu",
    "tamil": "tam_Taml",
    "malayalam": "mal_Mlym",
    "marathi": "mar_Deva",
    "bengali": "ben_Beng",
    "kannada": "kan_Knda",
    "gujarati": "guj_Gujr",
    "punjabi": "pan_Guru",
    "odia": "ory_Orya",
    "assamese": "asm_Beng",
    "urdu": "urd_Arab",
}

# ---------- LOAD MODEL ----------
print(f"[Translator] Loading {MODEL_ID} on {DEVICE} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID).to(DEVICE)
model.eval()
print("[Translator] Ready!")

# ---------- TRANSLATION FUNCTION ----------
def translate(text: str, target_lang: str = "hindi") -> str:
    """
    Clean + safe translation to avoid Indic corruption.
    """
    target_lang = target_lang.lower()

    if target_lang not in LANG_CODES:
        raise ValueError(f"Language '{target_lang}' is not supported.")

    tgt_code = LANG_CODES[target_lang]

    # --- CLEAN INPUT (very important) ---
    clean = (
        text.replace("•", "-")
            .replace("|", " ")
            .replace("→", " ")
            .replace("⇒", " ")
            .replace("►", " ")
            .replace("✔", " ")
            .replace("✖", " ")
            .replace("★", " ")
            .replace("✦", " ")
            .replace("👌", " ")
            .replace("👉", " ")
    )

    clean = " ".join(clean.split())  # collapse spacing

    try:
        inputs = tokenizer(clean, return_tensors="pt").to(DEVICE)

        with torch.no_grad():
            output = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_code),
                num_beams=4,
                max_new_tokens=256,
                no_repeat_ngram_size=4,
                repetition_penalty=1.1,
                early_stopping=True,
            )

        translated = tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        return translated.strip()

    except Exception as e:
        return f"[Translation Error] {str(e)}"



# ---------- QUICK TEST ----------
if __name__ == "__main__":
    sample = "The lungs appear clear and well expanded. No nodules or infiltrates are seen."

    for lang in ["hindi", "telugu", "tamil", "malayalam", "marathi"]:
        print(f"\n{lang.upper()} →", translate(sample, lang))
