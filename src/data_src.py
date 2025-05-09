import pandas as pd
import random
import time
import fasttext


class DataSource:

    def __init__(self):
        self.model = fasttext.load_model("../models/lid.176.ftz")
        self.df = pd.read_csv("../data/StreamData.csv")
        