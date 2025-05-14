# mainApp.py

import queue
import threading
import time
from flask import Flask, render_template, jsonify # Import Flask, render_template, jsonify

# Import your pipeline components
from src.data_src import DataSource
from src.sentiment_analysis import SentimentAnalyzer
from src.data_aggregator import DataAggregator

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Global Variables for Pipeline Components ---
# We need to make the DataAggregator instance accessible to Flask routes
# Initializing them as None and setting them up in __main__
data_source = None
sentiment_analyzer = None
data_aggregator = None
raw_to_analyzer_queue = None
analyzer_to_aggregator_queue = None
threads = []


# --- Flask Routes ---

@app.route('/')
def index():
    """
    Renders the main HTML page.
    """
    # Flask will look for index.html in the 'templates' folder
    return render_template('index.html')

@app.route('/api/sentiment_data')
def get_sentiment_data():
    """
    API endpoint to provide the latest aggregated sentiment data.
    """
    # Ensure the data_aggregator instance is available
    if data_aggregator is None:
        return jsonify({"error": "Data aggregator not initialized"}), 500

    # Use the thread-safe getter methods to get the latest data
    # Acquire the lock implicitly within the getter methods
    current_ema = data_aggregator.get_ema_score()
    counts = data_aggregator.get_sentiment_counts()
    recent_comments = data_aggregator.get_recent_comments()
    total_processed = data_aggregator.get_total_processed()

    # Prepare the data as a dictionary to be returned as JSON
    aggregated_data = {
        "ema_score": current_ema,
        "sentiment_counts": counts,
        "recent_comments": recent_comments,
        "total_processed": total_processed
    }

    # Flask automatically converts the dictionary to a JSON response
    return jsonify(aggregated_data)


# --- Pipeline Setup and Thread Management ---

def run_pipeline():
    """
    Sets up and runs the data pipeline in separate threads.
    This function is called from the __main__ block.
    """
    global data_source, sentiment_analyzer, data_aggregator, raw_to_analyzer_queue, analyzer_to_aggregator_queue

    print("Setting up the pipeline...")

    # Queue 1: DataSource -> SentimentAnalyzer
    raw_to_analyzer_queue = queue.Queue(maxsize=20)

    # Queue 2: SentimentAnalyzer -> DataAggregator
    analyzer_to_aggregator_queue = queue.Queue(maxsize=20)

    # --- Create Instances ---
    data_source = DataSource(
        shared_queue=raw_to_analyzer_queue,
        data_file_path="data/StreamData.csv",
        target_language="en"
    )

    sentiment_analyzer = SentimentAnalyzer(
        input_queue=raw_to_analyzer_queue,
        output_queue=analyzer_to_aggregator_queue
    )

    data_aggregator = DataAggregator(
        input_queue=analyzer_to_aggregator_queue,
        alpha=0.1,
        max_recent_comments=5
    )

    # --- Create Threads ---
    print("Creating pipeline threads...")
    data_source_thread = threading.Thread(
        target=data_source.start_streaming,
        kwargs={
            'max_stream_items': 100, # Stream more items for a longer demo
            'mindelay': 0.1, # Shorter delays
            'maxdelay': 2
        }
        # Threads are non-daemon by default, which is good for critical tasks
    )

    sentiment_analyzer_thread = threading.Thread(
        target=sentiment_analyzer.analyze_stream # Make sure method name is correct
        # Non-daemon by default
    )

    data_aggregator_thread = threading.Thread(
        target=data_aggregator.process_analysis_stream # Make sure method name is correct
        # Non-daemon by default
    )

    threads.extend([data_source_thread, sentiment_analyzer_thread, data_aggregator_thread])

    # --- Start Threads ---
    print("Starting pipeline threads...")
    data_source_thread.start()
    sentiment_analyzer_thread.start()
    data_aggregator_thread.start()

    # Note: The main thread will now run the Flask server, not join queues directly here.
    # The threads will run in the background.
    # Shutdown will be handled by the sentinel propagation when DataSource finishes.


if __name__ == "__main__":
    # Run the pipeline setup in the main thread first
    run_pipeline()

    print("\nPipeline threads started. Starting Flask server...")
    print("Open your web browser and go to: http://127.0.0.1:5000/")

    # Run the Flask development server in the main thread
    # debug=True allows for hot-reloading during development
    app.run(debug=True)

    # When the Flask server stops (e.g., Ctrl+C), the main thread exits.
    # Since worker threads are non-daemon, the program will wait for them
    # to finish gracefully after the server stops and sentinel propagates.
    # You might still want explicit joins here for a cleaner shutdown
    # after the server stops, but the sentinel propagation is key.

    # Optional: Add explicit joins here if needed for robust shutdown after server stops
    print("\nFlask server stopped. Waiting for pipeline threads to finish...")
    analyzer_to_aggregator_queue.join()
    raw_to_analyzer_queue.join()
    for thread in threads:
        thread.join()  # Optional timeout for graceful shutdown
        if thread.is_alive():
            print(f"Thread {thread.name} is still running after join.")
        else:
            print(f"Thread {thread.name} has finished.")
    print("Pipeline threads finished.")
