# fixed_translate_test.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "ai4bharat/IndicTrans3-beta"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory>6000) else torch.float32

print(f"Loading {MODEL_ID} on {DEVICE} dtype={DTYPE}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    torch_dtype=DTYPE,
    device_map="auto" if DEVICE.startswith("cuda") else None,
    low_cpu_mem_usage=True,
)
model.eval()

def clean_generated(full_text: str, prompt: str) -> str:
    """Remove prompt echo and trimming repeated tails."""
    # Remove prompt echo if present at beginning
    if full_text.startswith(prompt):
        out = full_text[len(prompt):].strip()
    else:
        out = full_text
    # Collapse excessive repeated tokens (simple heuristic)
    tokens = out.split()
    if len(tokens) > 80:
        # detect long repeated token sequences — remove runs longer than 12
        cleaned = []
        last = None
        run = 0
        for t in tokens:
            if t == last:
                run += 1
            else:
                run = 1
            if run <= 12:  # allow short repetition but stop runaway
                cleaned.append(t)
            last = t
        out = " ".join(cleaned)
    # final whitespace fix
    return out.strip()

def translate(text: str, target_language: str = "Hindi") -> str:
    prompt = f"Translate the following text to {target_language}:\n{text}\n\nTranslation:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(model.device)

    gen_kwargs = {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs.get("attention_mask", None),
        # Beam search (deterministic) — better for translation
        "num_beams": 4,
        "do_sample": False,
        "max_new_tokens": 128,
        "early_stopping": True,
        "no_repeat_ngram_size": 3,
        "repetition_penalty": 1.2,
        "length_penalty": 1.0,
    }

    with torch.no_grad():
        outputs = model.generate(**{k:v for k,v in gen_kwargs.items() if v is not None})
    text_out = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Postprocess: remove prompt echo and collapse extremes
    cleaned = clean_generated(text_out, prompt)
    return cleaned

if __name__ == "__main__":
    text = "The lungs appear clear and well expanded. No nodules or infiltrates are seen."
    languages = ["Hindi", "Telugu", "Tamil", "Malayalam", "Marathi"]
    for lang in languages:
        print(f"\n=== {lang} ===")
        out = translate(text, lang)
        print(out)
