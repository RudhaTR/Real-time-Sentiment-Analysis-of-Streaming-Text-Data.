# Real-time Sentiment Analysis of Streaming Text Data

**By:** Anirudh D Bhat

## 1. Project Description

This project implements a **real-time pipeline** for analyzing the sentiment of streaming text data. Leveraging a **multi-threaded architecture**, the system efficiently processes incoming text, performs sentiment analysis using a **pre-trained model**, and aggregates the results to provide **live insights** into the overall sentiment trend and distribution.

The pipeline consists of three main stages:

1.  **Data Source:** Simulates streaming data by reading comments from a local CSV file and pushing them into a **shared queue**.

2.  **Sentiment Analyzer:** Consumes raw text data from the queue, preprocesses it, performs sentiment analysis using a Hugging Face model (\`pysentimiento\`), and puts the analyzed results (including *sentiment label* and *probabilities*) into another **shared queue**.

3.  **Data Aggregator:** Consumes the analyzed data, calculates a **normalized sentiment score (0-100)** for each comment, maintains an **Exponential Moving Average (EMA)** of the sentiment score, and tracks overall sentiment counts. This aggregated data is stored internally and made available via *thread-safe getter methods*.

A basic **web interface**, built with *Flask*, serves as the frontend to visualize the aggregated sentiment data in **real-time**. The frontend periodically fetches the latest data from a backend API endpoint and updates a dashboard displaying the *live EMA*, *sentiment distribution counts*, and *recent comments* with their individual scores.

## 2. How to Run

Follow these steps to set up and run the project:

1.  **Clone the Repository:**

    ```bash
    git clone [Your Repository URL]
    cd [Your Project Directory]
    ```

2.  **Create a Virtual Environment:**
    It is highly recommended to use a **virtual environment** to manage project dependencies.

    ```bash
    # For Python 3
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**

    * **On Windows:**

        ```bash
        .\venv\Scripts\activate
        ```

    * **On macOS and Linux:**

        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    Install the required Python libraries.

    ```bash
    pip install -r requirements.txt
    ```


5.  **Ensure Data File Exists:**
    Make sure you have your \`StreamData.csv\` file located at \`data/StreamData.csv\` relative to the project root directory.
    You can choose any other data either. Just ensure it has Two columns of the name Comment and Sentiment referring to the same.

6.  **Run the Application:**
    Execute the main application script. This will start the data pipeline threads and the Flask web server.

    ```bash
    python mainApp.py
    ```

7.  **Access the Web Dashboard:**
    Once the Flask server starts, it will print a message indicating the address where it is running (usually \`http://127.0.0.1:5000/\`). Open this address in your web browser.

    You should see the sentiment analysis dashboard, which will start updating as data flows through the pipeline.

8.  **Stopping the Application:**
    To stop the application, press \`Ctrl+C\` in the terminal where \`mainApp.py\` is running. The program is designed to shut down *gracefully* after receiving the interrupt signal.
