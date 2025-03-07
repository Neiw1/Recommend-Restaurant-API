from locust import HttpUser, task, between
import pandas as pd

request_data = pd.read_parquet("request.parquet")

class FastAPIUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    @task
    def recommend(self):
        for index, row in request_data.iterrows():
            user_id = row['user_id']
            latitude = row['latitude']
            longitude = row['longitude']
            size = row['size']
            max_dis = row['max_dis']
            sort_dis = row['sort_dis']
            
            self.client.get(f"/recommend/{user_id}?latitude={latitude}&longitude={longitude}&size={size}&max_dis={max_dis}&sort_dis={sort_dis}")

# Run locust -f performance_test.py --host=http://127.0.0.1:8000
# Go to http://localhost:8089


