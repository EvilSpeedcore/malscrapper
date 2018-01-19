import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


class FeatureConstructor(object):
    def __init__(self):
        pass

    def preprocess(self, filename):
        df = pd.read_csv(filename).dropna()
        df['Personal score'] = (df['Personal score'] > 8).astype(int)
        initial_data = pd.get_dummies((df[['Episodes', 'Genres', 'Score', 'Source', 'Studios', 'Type']]))
        labels = df['Personal score']
        x_train, x_test, y_train, y_test = train_test_split(initial_data, labels, random_state=0, test_size=0.3)
        forest = RandomForestClassifier(n_estimators=1000, random_state=42, n_jobs=-1)
        forest.fit(x_train, y_train)
        print("Правильность на обучающем наборе: {:.3f}".format(forest.score(x_train, y_train)))
        print("Правильность на тестовом наборе: {:.3f}".format(forest.score(x_test, y_test)))
        print('Важности признаков:\n{}'.format(forest.feature_importances_))
