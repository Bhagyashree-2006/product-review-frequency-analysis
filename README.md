# Product Review Frequency Analysis

**Student ID:** 24691A3219  
**Big Data Analytics project**

## Project objective

Use Hadoop MapReduce to count product reviews at scale and identify how review volume changes by month, product, and category. The project demonstrates distributed storage with HDFS and distributed aggregation with Hadoop Streaming.

## What the program measures

- Reviews per calendar month
- Reviews per product
- Reviews per product category

The result is a frequency count, not a review rate. A rate such as reviews per 100 sales can only be calculated if a sales denominator is available.

## Input data

Put a UTF-8 CSV at `data/reviews.csv`, with one review per line and these header names:

```text
review_id,product_id,category,review_date,rating
```

`product_id`, `category`, `review_date` are required for this starter. Extra columns are okay. Dates should be in a recognizable form such as `2026-10-31`. Do not use personal names, email addresses, or other direct identifiers. For the first test, use `data/sample_reviews.csv`.

## How MapReduce works here

1. **HDFS** stores the input file across the Hadoop file system.
2. **Mapper** reads each review row and emits three key/value pairs: month, product, and category, each with a value of `1`.
3. Hadoop shuffles and groups equal keys across mapper tasks.
4. **Reducer** adds each group of values and writes the total review count.
5. The output is saved in HDFS under `output/review_counts/`.

The mapper and reducer are Python scripts run by Hadoop Streaming. Streaming lets Hadoop use executable scripts as mapper and reducer programs; each reads standard input and writes tab-separated results to standard output. See the [Apache Hadoop Streaming guide](https://hadoop.apache.org/docs/current/hadoop-streaming/HadoopStreaming.html).

## Browser demo

The Streamlit dashboard provides a browser-based demo with review counts and charts by month, product, and category. It uses the same CSV fields and date formats as the Hadoop mapper. The dashboard processes uploaded CSVs in the app process; use the Hadoop Streaming job above for distributed processing on large datasets.

Run it locally from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. Open it in your browser. On Windows PowerShell, activate the environment with `.venv\\Scripts\\Activate.ps1` instead of the `source` command.

## Publish the browser demo

Streamlit Community Cloud deploys the dashboard from GitHub. First push this project to a GitHub repository. Then sign in at [share.streamlit.io](https://share.streamlit.io), choose **Create app**, select your repository and the `main` branch, set the app file path to `app.py`, and select **Deploy**. The deployed dashboard gets a shareable `streamlit.app` URL. The Hadoop cluster itself is not hosted by this dashboard; running the distributed Hadoop job in the cloud requires a separate Hadoop service or cluster.

## Build and run (Ubuntu or WSL2)

Hadoop must already be installed and configured, with HDFS and YARN running for a pseudo-distributed setup. Use the Hadoop installation provided by your instructor if available.

1. Open this project in VS Code. If you are on Windows, use VS Code's WSL extension and open the project from Ubuntu/WSL.
2. Check Hadoop is available:

   ```bash
   hadoop version
   hdfs dfs -ls /
   ```

3. From the project directory, make scripts executable and upload the sample CSV to HDFS:

   ```bash
   chmod +x analysis_mapper.py analysis_reducer.py
   hdfs dfs -mkdir -p /user/$USER/product-review-frequency/input
   hdfs dfs -put -f data/sample_reviews.csv /user/$USER/product-review-frequency/input/reviews.csv
   ```

4. Find the Streaming JAR and run the job. Replace `INPUT` and `OUTPUT` with the full HDFS paths shown below if your username differs:

   ```bash
   STREAMING_JAR=$(find "$HADOOP_HOME/share/hadoop/tools/lib" -name 'hadoop-streaming-*.jar' | head -n 1)
   INPUT=/user/$USER/product-review-frequency/input/reviews.csv
   OUTPUT=/user/$USER/product-review-frequency/output/review_counts
   hdfs dfs -rm -r -f "$OUTPUT"
   hadoop jar "$STREAMING_JAR" \
     -files analysis_mapper.py,analysis_reducer.py \
     -mapper "./analysis_mapper.py" \
     -reducer "./analysis_reducer.py" \
     -input "$INPUT" \
     -output "$OUTPUT"
   ```

5. View the results:

   ```bash
   hdfs dfs -cat "$OUTPUT"/part-*
   ```

   Output keys start with `MONTH`, `PRODUCT`, or `CATEGORY`, followed by the group name and its count. To save a local copy:

   ```bash
   mkdir -p reports
   hdfs dfs -get -f "$OUTPUT" reports/hadoop-output
   ```

6. Replace the sample input with your real file. Upload it to a new HDFS input folder, update `INPUT`, and rerun. Hadoop does not allow an existing output folder, so remove or rename the previous output directory before each run.

## Project report outline

1. Title page: project title and Student ID 24691A3219
2. Abstract and problem statement
3. Objectives and dataset description/source
4. Big Data design: HDFS, mapper, shuffle/sort, reducer, output
5. Implementation and run commands
6. Results: tables or charts from the Hadoop output
7. Findings, limitations, and conclusion
8. References

Use real data for final findings. The sample file is only a small functional demo; it cannot support claims about actual customers or products.
