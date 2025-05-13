import pandas as pd
import random
import time
from langdetect import detect
import queue


class DataSource:

    def __init__(self,shared_queue,target_language="en",data_file_path="./data/StreamData.csv"):

        self.stream_queue = shared_queue
        self.data_file_path = data_file_path
        self.target_language = target_language

        self.df = None
        self.size = 0

        try:
            self.df = pd.read_csv(self.data_file_path)
            self.size = self.df.shape[0]
            self.columns = self.df.columns

            print(f"Data loaded from {self.data_file_path}")
            print(f"Data size: {self.size}")
        except FileNotFoundError:
            print(f"File not found: {self.data_file_path}")

        self.drop_counter = 0

    def start_streaming(self,mindelay=0.1, maxdelay=3,max_stream_items=150):
        """
        Simulate a data stream by creating a producer.
        """


        if self.df is None or self.size == 0:
            print("DataFrame is empty or not loaded.")
            self.stream_queue.put(None)
            return
        
        no_items_successfully_streamed = 0

        while(no_items_successfully_streamed < max_stream_items):

            row = random.randint(0, self.size-1)
            data = self.df.iloc[row]

            comment = data[self.columns[0]]

            detected_lang = None
            try:
                if isinstance(comment, str) and comment.strip():
                    detected_lang = detect(comment)
            except Exception as e:
                print(f"Error detecting language: {e}")
                detected_lang = None
 

            if(detected_lang ==self.target_language):
                
                data = data.to_dict()

                try:
                    self.stream_queue.put(data, block=False)
                    no_items_successfully_streamed += 1
                except queue.Full:
                    self.drop_counter += 1
                    print(f"Queue is full. Dropping item: {data}")
                    pass

            delay = random.uniform(mindelay, maxdelay)
            time.sleep(delay)

        
        self.stream_queue.put(None)
        print(f"Data streaming completed. Total items dropped at input queue: {self.drop_counter}")
        
        