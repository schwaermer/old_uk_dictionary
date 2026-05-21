import json
from pathlib import Path
import pandas as pd

def normalize_word(word):
    word = word.lower()
    replacements = {
        "ѣ": "е", "ѳ": "ф", "ѵ": "и", "i": "и", "ꙋ": "у", "оу": "у",
        "і": "и", "ѡ": "о", "ѧ": "я", "ї": "и", "ꙗ": "я",
        "ѩ": "я", "ѫ": "у", "ѭ": "ю", "ь": "", "ъ": "", "ѯ": "кс",
        "с̑": "с", "м̑": "м", "є": "е", "̃": "", "̑": "", "ε": "е",
        "҃": "", "ꙑ": "ы"
    }
    for old, new in replacements.items():
        word = word.replace(old, new)
    return word

def get_stems(word, endings_set):
    stems = {word}
    for i in range(1, min(len(word), 8)):         
        suffix = word[len(word) - i:]
        if suffix in endings_set:
            stem = word[:len(word) - i]
            stems.add(stem)
            stems.add(normalize_word(stem))
    return stems

def load_endings(file_path):
    endings = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                ending = line.strip()
                if ending:
                    endings.add(ending)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found.")
    return endings

def process_data(word_upos_df, endings_dir="."):
    
    ns_endings = load_endings(f"{endings_dir}/ns_dict_keys.txt")
    adj_endings = load_endings(f"{endings_dir}/adj_dict_keys.txt")
    vs_endings = load_endings(f"{endings_dir}/vs_dict_keys.txt")
    
    output_dictionary = {}
    
    for row in word_upos_df.itertuples(index=False):
        original_word = row[0]
        pos = row[1]
        
        if not original_word:
            continue
        
        if pos in ["NOUN", "PROPN", "NUM"]:
            current_endings_set = ns_endings
        elif pos == "ADJ":
            current_endings_set = adj_endings
        elif pos in ["VERB", "AUX"]:
            current_endings_set = vs_endings
        else:
            current_endings_set = set()
        
        raw_stems = get_stems(original_word, current_endings_set)
        output_dictionary[original_word] = sorted(list(raw_stems))
    
    return output_dictionary

if __name__ == "__main__":
    csv_path = Path("timchenko_with_upos.csv")

    if csv_path.exists():
        tagged_data = pd.read_csv(csv_path)
        print(f"Файл загружен.")
    else:
        print(f"Файл не найден: {csv_path.absolute()}")
        print("Доступные CSV файлы:", list(Path(".").glob("*.csv")))
        tagged_data = None
    
    result = process_data(
        word_upos_df=tagged_data,
        endings_dir="."
    )
    
    with open("dict_stems.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
