import regex as re


def preprocessing(text):
    text = text.lower()
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (ios)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    url_pattern = re.compile(r"https?://\S+|www\.\S+")
    html_pattern = re.compile("<.*?>")
    text = emoji_pattern.sub(r"", text)
    text = url_pattern.sub(r"", text)
    text = html_pattern.sub(r"", text)
    text = re.sub(r"[^\w\d'\s]+]", "", text)

    # Remove punctuations
    punctuations: str = r"""!()-[]{};:'"\,<>./?@#$%^&*_~"""
    for ele in text:
        if ele in punctuations:
            text = text.replace(ele, "")

    return text


def sentiment(n):
    return 1 if n >= 4 else 0


def filter_txt(txt):
    return isinstance(txt, str)
