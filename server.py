import pickle
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import h3
import math
from sqlalchemy import create_engine, text
from functools import lru_cache
import os

app = FastAPI()

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# load model from pickle file
with open('model.pkl', 'rb') as f:
    model: NearestNeighbors = pickle.load(f)

def get_restaurant_data():
    restaurant_query = "SELECT * FROM restaurants"
    return pd.read_sql(restaurant_query, engine).set_index('index')

@lru_cache(maxsize=10000)
def get_user_data(user_id: str):
    user_query = f"SELECT * FROM users WHERE user_id = '{user_id}'"
    return pd.read_sql(user_query, engine)

restaurant_df = get_restaurant_data()

class Restaurants(BaseModel):
    id: str
    difference: float
    displacement: int

class NewRestaurant(BaseModel):
    restaurant_id: str
    index: int
    latitude: float
    longitude: float

# get method: return recommended restaurants
@app.get('/recommend/{user_id}')
async def recommend(
    user_id: str,
    latitude: float,
    longitude: float,
    size: int = Query(20),
    max_dis: Optional[float] = Query(5000),
    sort_dis: Optional[float] = Query(0),
):
    # handle nan cases
    if isinstance(max_dis, float) and math.isnan(max_dis):
        max_dis = 5000
    if isinstance(sort_dis, float) and math.isnan(sort_dis):
        sort_dis = 0

    user_df = get_user_data(user_id)

    # find 2000 nearest neighbors to be recommend restaurants
    difference, ind = model.kneighbors(user_df.drop(columns='user_id'), n_neighbors=2000)
    recommend_df = restaurant_df.loc[ind[0]].copy()

    # set distance as restaurant score
    recommend_df['difference'] = difference[0]

    # convert to h3
    user_h3 = h3.latlng_to_cell(float(latitude), float(longitude), 9)
    recommend_df['h3_index'] = recommend_df.apply(lambda row: h3.latlng_to_cell(float(row['latitude']), float(row['longitude']), 9), axis=1)

    # compute distance and convert to meters
    recommend_df['displacement'] = recommend_df['h3_index'].apply(lambda h3_index: h3.grid_distance(user_h3, h3_index) * 29)
    recommend_df = recommend_df[recommend_df['displacement'] <= max_dis]

    if sort_dis == 1:
        sort_column = 'displacement'
    else:
        sort_column = 'difference'
    recommend_df = recommend_df.sort_values(by=sort_column)

    # response
    response = [
        Restaurants(
            id=row['restaurant_id'],
            difference=row['difference'],
            displacement=row['displacement'],
        ) for index, row in recommend_df.head(size).iterrows()
    ]
    return {'restaurants': response}

# post method: add restaurants into the database
@app.post('/restaurants')
async def add_restaurant(restaurant: NewRestaurant):
    insert_query = text("""
        INSERT INTO restaurants (restaurant_id, index, latitude, longitude)
        VALUES (:restaurant_id, :index, :latitude, :longitude)
    """)

    with engine.connect() as connection:
        connection.execute(insert_query, {
            'restaurant_id': restaurant.restaurant_id,
            'index': restaurant.index,
            'latitude': restaurant.latitude,
            'longitude': restaurant.longitude,
        })
        connection.commit()

    return {"message": "Added successfully!"}