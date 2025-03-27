from transformers import BertTokenizer, BertForSequenceClassification
import torch
import spacy
from spacy.matcher import Matcher
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
# Reload the saved model and tokenizer
saved_model_path = "./model"
model = BertForSequenceClassification.from_pretrained(saved_model_path)
tokenizer = BertTokenizer.from_pretrained(saved_model_path)
nlp = spacy.load("en_core_web_sm")
label_encoder = LabelEncoder()
label_encoder.fit(["Breaking_News", "Non_Breaking_News"])


def preprocess_text(text):
    doc = nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha
    ]
    return " ".join(tokens)


def predict_news_category(news_text):
    # Preprocess the input text
    preprocessed_text = preprocess_text(news_text)  # Use the same preprocess_text function

    # Tokenize the text
    encoding = tokenizer(
        preprocessed_text,
        max_length=128,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )

    # Move tensors to the appropriate device
    input_ids = encoding["input_ids"]
    attention_mask = encoding["attention_mask"]

    # Perform inference
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=-1).item()  # Get the predicted label

    # Decode the label
    predicted_label = label_encoder.inverse_transform([prediction])[0]
    return predicted_label
