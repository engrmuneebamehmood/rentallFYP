from .utils import *

def build_recommendation_model(user_id):
    car_df, tfidf_matrix, tfidf_vectorizer = build_car_description_matrix()

    ordered_cars = get_ordered_cars(user_id)

    # Calculate cosine similarities
    cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Get recommendations based on user's past orders
    recommended_cars = []
    for car_id in ordered_cars:
        car_index = car_df[car_df['car_id'] == car_id].index[0]
        similar_cars_indices = cosine_similarities[car_index].argsort()[-6:-1][::-1]  # Get top 5 similar cars
        recommended_cars.extend(car_df.iloc[similar_cars_indices]['car_id'].tolist())

    # Remove duplicates and cars already ordered by the user
    recommended_cars = list(set(recommended_cars) - set(ordered_cars))

    return recommended_cars[:10]  # Return top 10 recommended cars
