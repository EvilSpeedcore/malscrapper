import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class FeatureConstructor(object):
    def __init__(self, ):
        pass

    def preprocess(self, filename):
        df = pd.read_csv(filename).dropna()
        df['Personal score'] = (df['Personal score'] > 7).astype(int)
        print("Исходные признаки:\n{0}". format(list(df.columns)))
        initial_data = pd.get_dummies((df[['Episodes', 'Genres', 'Score', 'Source', 'Studios', 'Type']]))
        labels = df['Personal score']
        x_train, x_test, y_train, y_test = train_test_split(initial_data, labels, random_state=0, test_size=0.3)
        standart_scaler = StandardScaler()
        x_train_std = standart_scaler.fit_transform(x_train)
        x_test_std = standart_scaler.fit_transform(x_test)

