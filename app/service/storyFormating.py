def splitParagraphs(text):
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    for s in paragraphs:
        print(s+"\n")
    return paragraphs

def formatStory(text):
    numberedList = []

    for i,s in enumerate(text):
        numberedList.append(f"{i+1}. {s}")
    return "\n\n".join(numberedList)