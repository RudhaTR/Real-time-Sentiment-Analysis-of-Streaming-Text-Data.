import pandas as pd


totaldata = pd.read_csv('YoutubeCommentsDataSet.csv')
TrainingData = totaldata.sample(frac=0.8, random_state=1)
StreamData = totaldata.drop(TrainingData.index)
TrainingData.dropna(inplace=True)
StreamData.dropna(inplace=True)

TrainingData.to_csv('TrainingData.csv', index=False)
StreamData.to_csv('StreamData.csv', index=False)