import re

def clean_text(text):
    if not text or not isinstance(text, str):
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Skip very short texts
    if len(text) < 10:
        return ""
    
    return text

if __name__ == "__main__":
    sample = "Nvidia crushes earnings! check this out https://t.co/abc123 !!!"
    print(clean_text(sample))