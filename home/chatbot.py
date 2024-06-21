# chatbot.py

import os
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from sklearn.model_selection import train_test_split

# Download required NLTK data
nltk.download('punkt')

# Initialize tokenizer and model globally
tokenizer = Tokenizer()
model = None


def load_data(file_path):
    # Read the training data file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Separate questions and answers
    questions = []
    answers = []
    for line in lines:
        question, answer = line.strip().split('===')
        questions.append(question.lower())
        answers.append(answer.lower())

    return questions, answers


def preprocess_data(questions, answers):
    # Tokenize input and output sequences
    tokenizer.fit_on_texts(questions + answers)

    # Convert text to sequences
    questions_sequences = tokenizer.texts_to_sequences(questions)
    answers_sequences = tokenizer.texts_to_sequences(answers)

    # Pad sequences to ensure uniform length
    max_seq_length = max(max(len(seq) for seq in questions_sequences), max(len(seq) for seq in answers_sequences))
    questions_padded = pad_sequences(questions_sequences, maxlen=max_seq_length, padding='post')
    answers_padded = pad_sequences(answers_sequences, maxlen=max_seq_length, padding='post')

    return questions_padded, answers_padded, max_seq_length


def build_model(vocab_size, max_seq_length):
    # Define model architecture
    model = Sequential()
    model.add(Embedding(vocab_size, 128, input_length=max_seq_length))
    model.add(LSTM(128, return_sequences=True))
    model.add(Dense(vocab_size, activation='softmax'))

    # Compile the model
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model


def load_model():
    global model

    # Get the absolute path to the training data file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_file_path = os.path.join(base_dir, 'training_data.txt')

    # Load and preprocess training data
    questions, answers = load_data(train_file_path)
    questions_padded, answers_padded, max_seq_length = preprocess_data(questions, answers)

    # Split data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(questions_padded, answers_padded, test_size=0.2, random_state=42)

    # Define vocabulary size
    vocab_size = len(tokenizer.word_index) + 1

    # Build the model
    model = build_model(vocab_size, max_seq_length)

    # Train the model
    model.fit(X_train, y_train, epochs=20, batch_size=64, validation_data=(X_val, y_val))


def preprocess_input(input_text):
    tokens = word_tokenize(input_text.lower())
    sequence = tokenizer.texts_to_sequences([tokens])
    padded_sequence = pad_sequences(sequence, maxlen=model.input_shape[1], padding='post')
    return padded_sequence


def generate_response(input_text):
    input_sequence = preprocess_input(input_text)
    predicted_sequence = model.predict(input_sequence)[0]
    predicted_tokens = [tokenizer.index_word.get(np.argmax(token), '') for token in predicted_sequence]
    response = ' '.join(token for token in predicted_tokens if token)
    return response.strip()


def evaluate_model():
    # Get the absolute path to the test data file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(base_dir, 'test_data.txt')

    # Load and preprocess test data
    test_questions, test_answers = load_data(test_file_path)
    test_questions_padded, test_answers_padded, _ = preprocess_data(test_questions, test_answers)

    # Evaluate the model on the test data
    loss, accuracy = model.evaluate(test_questions_padded, test_answers_padded)
    print(f'Test Accuracy: {accuracy * 100:.2f}%')


if __name__ == "__main__":
    load_model()
    evaluate_model()
