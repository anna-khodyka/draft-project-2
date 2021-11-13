"""
                  neural network command analyzer
"""

# pylint: disable=W0614
# pylint: disable=C0103
# pylint: disable=W1514
# pylint: disable=E0611
# pylint: disable=W0401
# pylint: disable=E0402



import sys
import os
import json
import pickle
from numpy import array

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
lemmatizer = WordNetLemmatizer()


def load_saved_data():
    """
    Loading saved data: intents dictionary, neural model, training sets
    :param :
    :return: json, set, set, model
    """
    prefix = ""
    if __name__ == "bot.neural_code":
        prefix = "../bot/"
    elif __name__ == "neural_code":
        prefix = "../"
    model = load_model(f"{prefix}chatbot_model.model")

    with open(f"{prefix}data/intents.json", "r") as file:
        intents = json.loads(file.read())
    with open(f"{prefix}data/words.pkl", "rb") as file:
        words = pickle.load(file)
    with open(f"{prefix}data/classes.pkl", "rb") as file:
        classes = pickle.load(file)
    return intents, words, classes, model


def clean_up_sentence(sentence):
    """
    Cleaninig sentence using tokenizer and lemmatizer
    :param sentence:
    :return: list (of words)
    """
    sentence_words = word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence, words):
    """
    Collect the bag of words from user sentence in terms of training set dictionary
    :param sentence:
    :param words:
    :return: np.array
    """
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for word_ in sentence_words:
        for i, word in enumerate(words):
            if word == word_:
                bag[i] = 1
    return array(bag)


def predict_class(sentence):
    """
    Using neural network model try to define from user sentence the
    intention class that has the maximum probability

    :param sentence:
    :return: list of intents classes ranged by probability, intentions dictionary
    """
    intents, words, classes, model = load_saved_data()
    bow = bag_of_words(sentence, words)
    res = model.predict(array([bow]))[0]
    ERROR_THRESHOLD = 0.55
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for res in results:
        return_list.append({"intent": classes[res[0]], "probability": str(res[1])})
    return return_list, intents


def get_response(intents_list, intents):
    """
    Find a function name to call using predicted intention.
    :param intents_list:
    :param intents:
    :return: dict{'description':, 'to_call':}
    """
    tag = intents_list[0]["intent"]
    list_of_intents = intents["intents"]
    result = None
    for i in list_of_intents:
        if i["tag"] == tag:
            result = {"description": i["responses"][0], "to_call": i["tag"]}
            break
    return result
