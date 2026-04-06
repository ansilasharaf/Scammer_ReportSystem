from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
from sklearn.metrics import accuracy_score

# Load model and tokenizer
model_name = "ealvaradob/bert-finetuned-phishing"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Create pipeline
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Sample test data (you can replace with your dataset)
texts = [
    "Your account has been suspended, click here to verify",
    "Meeting is scheduled at 10 AM tomorrow",
    "Update your bank details immediately",
    "Lunch at 1 pm?"
]

# True labels (example: 1 = phishing, 0 = safe)
true_labels = [1, 0, 1, 0]

# Get predictions
pred_labels = []
for text in texts:
    result = classifier(text)[0]
    label = result['label']

    # Convert label to numeric
    if label == "LABEL_1":
        pred_labels.append(1)
    else:
        pred_labels.append(0)

# Calculate accuracy
accuracy = accuracy_score(true_labels, pred_labels)

print("Predictions:", pred_labels)
print("Actual:", true_labels)
print("Model Accuracy:", accuracy)