import queue
import threading
from src.data_src import DataSource


if __name__ == "__main__":
    shared_queue = queue.Queue(maxsize=20)
    data_source = DataSource(shared_queue,data_file_path="data/StreamData.csv")

    data_source_thread = threading.Thread(
        target=data_source.start_streaming,
        kwargs={
            'mindelay': 0.1,
            'maxdelay': 3,
            'max_stream_items': 20
        })
    data_source_thread.start()

    print("Main thread started consuming from the queue...")

    while(True):
        comment_data_point = shared_queue.get()

        if comment_data_point is None:
            print("No more data to process.")
            shared_queue.task_done()
            break

        commenttext = comment_data_point['Comment']
        commentsentiment = comment_data_point['Sentiment']
        print(f"Received comment: {commenttext}\nwith sentiment: {commentsentiment}")