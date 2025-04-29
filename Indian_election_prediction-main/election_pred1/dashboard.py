# election_sentiment_dashboard.py
import pandas as pd
import re
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments, pipeline
import streamlit as st

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_data(file_path):
    df = pd.read_excel(file_path, sheet_name="Combined")
    df['text'] = df['text'].apply(clean_text)
    df['label'] = np.random.randint(0, 2, size=len(df))  # Dummy labels for training
    return df

def train_model(df):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    class NewsDataset(torch.utils.data.Dataset):
        def __init__(self, texts, labels):
            self.encodings = tokenizer(texts, truncation=True, padding=True)
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    X_train, X_val, y_train, y_val = train_test_split(df['text'], df['label'], test_size=0.2)
    train_dataset = NewsDataset(X_train.tolist(), y_train.tolist())
    val_dataset = NewsDataset(X_val.tolist(), y_val.tolist())

    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

    training_args = TrainingArguments(
        output_dir='./results',
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        num_train_epochs=3,
        evaluation_strategy="epoch",
        logging_dir='./logs',
        logging_steps=10,
        save_strategy="no"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )

    trainer.train()
    return model, tokenizer

def predict_sentiments(model, tokenizer, df):
    sentiment_pipe = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    predictions = sentiment_pipe(df["text"].tolist())
    df["sentiment"] = [1 if pred["label"] == "LABEL_1" else 0 for pred in predictions]
    return df

def show_dashboard(df):
    st.title("Indian Election Sentiment Dashboard")

    st.subheader("National-Level Sentiment")
    national_df = df[df["scope"] == "National"]
    national_summary = national_df.groupby("party")["sentiment"].mean().sort_values(ascending=False)
    st.bar_chart(national_summary)

    st.subheader("State-Level Sentiment")
    selected_state = st.selectbox("Choose a State", df[df["scope"] == "State"]["state"].dropna().unique())
    state_df = df[(df["scope"] == "State") & (df["state"] == selected_state)]
    if not state_df.empty:
        state_summary = state_df.groupby("party")["sentiment"].mean().sort_values(ascending=False)
        st.bar_chart(state_summary)
    else:
        st.warning("No data available for selected state.")

# MAIN
if __name__ == "__main__":
    st.set_page_config(page_title="Election Sentiment Dashboard", layout="wide")

    st.write("Loading collected data...")
    df = load_data("collected_data.xlsx")

    st.write("Training model...")
    model, tokenizer = train_model(df)

    st.write("Predicting sentiments...")
    df = predict_sentiments(model, tokenizer, df)

    show_dashboard(df)
