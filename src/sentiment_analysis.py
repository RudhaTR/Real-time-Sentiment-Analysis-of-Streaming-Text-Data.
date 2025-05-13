import torch
import transformers
from pysentimiento import create_analyzer
from pysentimiento.preprocessing import preprocess_tweet
import time
import queue


class SentimentAnalyzer:

    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.drop_counter = 0

        try:
            self.analyzer = create_analyzer(task="sentiment", lang="en")
        except Exception as e:
            print(f"Error initializing sentiment analyzer: {e}")
            self.analyzer = None


    def preprocess(self,text):
        # Preprocess the text
        processed_text = ""
        try:
            processed_text = preprocess_tweet(text, lang="en")
        except Exception as e:
            print(f"Error preprocessing text: {e}")
            processed_text = text

        return processed_text
    

    def analyze_stream(self):


        if self.analyzer is None:
            print("Sentiment analyzer not initialized.")
            self.output_queue.put(None)
            return 
        
        while(True):
            input_dict = self.input_queue.get()

            if input_dict is None:
                print("No more data to process.")
                break
            
            comment = input_dict['Comment']
            sentiment = input_dict['Sentiment']
            preprocessed_comment = self.preprocess(comment)
            sentiment_analysis = self.analyzer.predict(preprocessed_comment)

            sentiment_analysis_probability = sentiment_analysis.probas
            sentiment_analysis_label = sentiment_analysis.output

            output_dict = {
                'Comment': comment,
                'Original_Sentiment': sentiment,
                'Sentiment_Analysis_Probability': sentiment_analysis_probability,
                'Sentiment_Analysis_Label': sentiment_analysis_label
            }

            try:

                self.output_queue.put(output_dict, block=False)
            except queue.Full:
                self.drop_counter += 1

            self.input_queue.task_done()

        self.input_queue.task_done()
        self.output_queue.put(None)
        print(f"Sentiment analysis completed. Total items Dropped at output queue: {self.drop_counter}")

