import queue
import threading
from src.data_src import DataSource
from src.sentiment_analysis import SentimentAnalyzer
from src.data_aggregator import DataAggregator  
import time


if __name__ == "__main__":
    try:
        shared_input_queue = queue.Queue(maxsize=3)
        shared_output_queue = queue.Queue(maxsize=3)

        data_source = DataSource(shared_input_queue,data_file_path="data/StreamData.csv",target_language="en")
        sentiment_analyzer = SentimentAnalyzer(shared_input_queue,shared_output_queue)
        data_aggregator = DataAggregator(shared_output_queue, alpha=0.1, max_recent_comments=5)

        data_source_thread = threading.Thread(
            target=data_source.start_streaming,
            kwargs={
                'mindelay': 0.1,
                'maxdelay': 3,
                'max_stream_items': 5
            })
        sentiment_analyzer_thread = threading.Thread(
            target=sentiment_analyzer.analyze_stream
            )
        data_aggregator_thread = threading.Thread(
            target=data_aggregator.process_analysis_stream
            )
        
        print("Starting threads...")
        data_source_thread.start()
        sentiment_analyzer_thread.start()
        data_aggregator_thread.start()

        start_time = time.time()
        maxtime = 5

        print("Main thread is processing data...")
        while time.time() - start_time < maxtime:
            try:
                current_ema = data_aggregator.get_ema_score() # Your getter method
                counts = data_aggregator.get_sentiment_counts() # Your getter method
                recent = data_aggregator.get_recent_comments() # Your getter method
                total = data_aggregator.get_total_processed() # Your getter method

                print(f"Time: {time.time() - start_time:.2f}s | Total Processed: {total} | Current EMA: {current_ema:.2f}")
                print(f"Sentiment Counts: POS={counts.get('POS', 0)}, NEU={counts.get('NEU', 0)}, NEG={counts.get('NEG', 0)}")
                print("Recent Comments:")
                if recent:   
                    for comment_data in recent:
                        print(f"  - Score: {comment_data.get('comment_score', 0):.2f}, Label: {comment_data.get('label', 'Unknown')}, Text: \"{comment_data.get('text', '')[:50]}...\"")
                else:
                    print("  (No recent comments processed yet by Aggregator)")
                print("-" * 40) 

                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error in main thread: {e}")
            except KeyboardInterrupt:
                print("Keyboard interrupt received. Exiting...")
                exit(0)
            time.sleep(0.1)


        
        print("\nMonitoring duration finished in Main Thread.")
        print("Waiting for pipeline threads to complete tasks...")


        shared_input_queue.join()
        print("Raw-to-Analyzer queue is empty and all tasks done.")
        
        shared_output_queue.join()
        print("Analyzer-to-Aggregator queue is empty and all tasks done.")
        


        data_source_thread.join()
        print("Data source thread finished. join is complete")
        sentiment_analyzer_thread.join()
        print("Sentiment analyzer thread finished. join is complete")
        data_aggregator_thread.join()
        print("Data aggregator thread finished. join is complete")

        print("All threads have completed their tasks.")
        print("Exiting main thread.")



    except KeyboardInterrupt:
        print("\nPipeline interrupted by user. Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    
