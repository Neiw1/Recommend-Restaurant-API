**How to run the server code**

1. Nagivate into this folder directory.
2. Run Docker Daemon (Docker Desktop)
3. Run docker-compose build
4. Run docker-compose up

Make sure the port 5434 and 8000 are available

**IMPORTANT**
The first time running docker-compose up may not work because the API server need to wait for the databse to be configured (from lineman_dump.sql).
It will show an error, but after a few second (about 10-20 seconds), there will be a log like this: **database system is ready to accept connections**
Then you can press Control+C and run docker-compose up again to start the server. The database only needed to be configured when running the first time.


Example of GET
curl "http://localhost:8000/recommend/u00410?latitude=13.784249681722077&longitude=100.38462125225499&size=50&max_dis=10000.0&sort_dis=1.0"

Example of POST --> This adds a new restaurant to the database

curl -X POST "http://localhost:8000/restaurants" \
-H "Content-Type: application/json" \
-d '{"restaurant_id": "r123456", "index": 999999, "latitude": 11.123, "longitude": 100.123}'


**How to run performance test**

1. Nagivate into the perf_test folder
3. Run locust -f performance_test.py --host=http://127.0.0.1:8000
4. Go to http://localhost:8089

To run performance test, you might need to install dependencies seperately:

pip install locust pandas pyarrow