import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


class FeatureConstructor(object):
    def __init__(self, ):
        pass

    def preprocess(self, filename):
        df = pd.read_csv(filename).dropna()
        df['Personal score'] = (df['Personal score'] > 7).astype(int)
        print("Исходные признаки:\n{0}". format(list(df.columns)))

        initial_data = pd.get_dummies((df[['Episodes', 'Genres', 'Score', 'Source', 'Studios', 'Type']]))
        print("Признаки после кодирования:\n{0}".format(list(initial_data.columns)))

        labels = df['Personal score']
        x_train, x_test, y_train, y_test = train_test_split(initial_data, labels, random_state=0, test_size=0.3)
        standart_scaler = StandardScaler()
        x_train_std = standart_scaler.fit_transform(x_train)
        x_test_std = standart_scaler.fit_transform(x_test)

