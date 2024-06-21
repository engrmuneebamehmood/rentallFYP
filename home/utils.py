import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Order, Car

def build_car_description_matrix():
    # Get all cars
    cars = Car.objects.all()

    # Create a DataFrame with car descriptions
    car_ids = []
    car_descriptions = []
    for car in cars:
        car_ids.append(car.id)
        car_descriptions.append(car.name + ' ' + car.category)

    car_data = {'car_id': car_ids, 'description': car_descriptions}
    car_df = pd.DataFrame(car_data)

    # TF-IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(car_df['description'])

    return car_df, tfidf_matrix, tfidf_vectorizer

def get_ordered_cars(user_id):
    ordered_cars = Order.objects.filter(user_id=user_id, is_complete=True).values_list('car_id', flat=True)
    return ordered_cars
