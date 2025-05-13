import threading
from collections import deque



class DataAggregator:

    def __init__(self, input_queue, alpha=0.2, max_recent_comments=10):
        self.input_queue = input_queue
        self.alpha = alpha
        self.ema_score = 0
        self._is_first = True
        self.no_positive = 0
        self.no_negative = 0    
        self.no_neutral = 0
        self.total_processed = 0
        self.max_recent_comments = max_recent_comments
        self.recent_comments = deque(maxlen=max_recent_comments)
        self.lock = threading.Lock()



    def calculate_comment_score(self,probabilities):

        prob_neg = probabilities.get("NEG",0.0)
        prob_neu = probabilities.get("NEU",0.0)
        prob_pos = probabilities.get("POS",0.0)

        intermediate_score = (-1 * prob_neg) + (0 * prob_neu) +  (1 * prob_pos)
        scaled_score = ((intermediate_score+1)/2) * 100
        scaled_score = min(max(scaled_score, 0), 100)  

        return scaled_score

    def update_ema(self,comment_score):

        with self.lock:
            if self._is_first:
                self.ema_score = comment_score
                self._is_first = False
            else:
                self.ema_score = self.alpha * comment_score + (1 - self.alpha) * self.ema_score



    def process_analysis_stream(self):

        while True:

            input_dict = self.input_queue.get()

            if input_dict is None:
                print("No more data to process.")
                break

            comment = input_dict['Comment']
            original_sentiment = input_dict['Original_Sentiment']
            sentiment_analysis_probability = input_dict['Sentiment_Analysis_Probability']
            sentiment_analysis_label = input_dict['Sentiment_Analysis_Label']

           
            comment_score = self.calculate_comment_score(sentiment_analysis_probability, sentiment_analysis_label)

            with self.lock:
                self.update_ema(comment_score)
                if(sentiment_analysis_label == "POS"):
                    self.no_positive += 1
                elif(sentiment_analysis_label == "NEG"):
                    self.no_negative += 1
                elif(sentiment_analysis_label == "NEU"):
                    self.no_neutral += 1

                output_dict = {
                    'text': comment,
                    "comment_score": comment_score,
                    "label": sentiment_analysis_label
                    }

                self.recent_comments.append(output_dict)
            
            self.total_processed += 1
            self.input_queue.task_done()
        
        self.input_queue.task_done()
        print("Data aggregation completed.")

    def get_ema_score(self):
            with self.lock:
                return self.ema_score
            
    def get_recent_comments(self):
            with self.lock:
                return list(self.recent_comments)
            
    def get_sentiment_counts(self):
            with self.lock:
                return {
                    "POS": self.no_positive,
                    "NEG": self.no_negative,
                    "NEU": self.no_neutral
                }
            
    def get_total_processed(self):
            with self.lock:
                return self.total_processed
            

       
        