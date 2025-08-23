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

**How to run with Kubernetes**

1. **Enable Kubernetes in Docker Desktop:**
   - Go to Docker Desktop's **Settings > Kubernetes**.
   - Check the **Enable Kubernetes** box and click **Apply & Restart**.

2. **Build the Docker Image:**
   ```bash
   docker build -t recommended-restaurant-api:latest .
   ```

3. **Deploy to Kubernetes:**
   - Apply the Kubernetes manifest files located in the `kubernetes` directory.
   ```bash
   kubectl apply -f kubernetes/
   ```

4. **Initialize the Database:**
   - Get the name of the postgres pod:
   ```bash
   kubectl get pods -l app=postgres -o jsonpath='{.items[0].metadata.name}'
   ```
   - Load the data from `lineman_dump.sql` into the database (replace `<postgres-pod-name>` with the name from the previous command):
   ```bash
   kubectl exec -i <postgres-pod-name> -- psql -U postgres -d lineman < lineman_dump.sql
   ```

5. **Access the Application:**
   - The application will be available at `http://localhost:8000`.
   - You can test it with the following command:
   ```bash
   curl "http://localhost:8000/recommend/u00410?latitude=13.784249681722077&longitude=100.38462125225499&size=50&max_dis=10000.0&sort_dis=1.0"
   ```
