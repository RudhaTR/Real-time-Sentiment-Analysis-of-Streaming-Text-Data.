import queue
import threading
from src.data_src import DataSource
from src.sentiment_analysis import SentimentAnalyzer


if __name__ == "__main__":
    shared_input_queue = queue.Queue(maxsize=3)
    shared_output_queue = queue.Queue(maxsize=3)
    data_source = DataSource(shared_input_queue,data_file_path="data/StreamData.csv",target_language="en")
    sentiment_analyzer = SentimentAnalyzer(shared_input_queue,shared_output_queue)

    data_source_thread = threading.Thread(
        target=data_source.start_streaming,
        kwargs={
            'mindelay': 0.1,
            'maxdelay': 3,
            'max_stream_items': 5
        })
    
    sentiment_analyzer_thread = threading.Thread(
        target=sentiment_analyzer.analyze_stream)
    

    data_source_thread.start()
    sentiment_analyzer_thread.start()

    while True:
        try:
            output_dict = shared_output_queue.get()
            if output_dict is None:
                print("No more data to process.")
                break
            print(output_dict)
        except queue.Empty:
            print("Output queue is empty.")
            break

    shared_input_queue.join()
