from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "ealvaradob/bert-finetuned-phishing"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def predict_url(url):

    inputs = tokenizer(url, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    prediction = torch.argmax(probs).item()

    if prediction == 1:
        return ["unsafe", "Phishing URL detected"]
    else:
        return ["safe", "Legitimate URL"]