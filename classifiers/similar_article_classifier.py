import logging
from datetime import datetime, timedelta

from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer


class SimilarArticleClassifier(object):
    def perdict(self, test_article):
        articles = self.load_articles_for_date(test_article.published_at)

        # List of named entities
        named_entities_list = list(map(lambda x: ' '.join(x.named_entities), articles))
        named_entities_list.append(' '.join(test_article.named_entities))

        # TF-IDF matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(named_entities_list)

        # Fit KNN
        nbrs = NearestNeighbors(n_neighbors=10)
        nbrs.fit(tfidf_matrix)

        # Predict
        test_row = tfidf_matrix.getrow(len(named_entities_list) - 1)
        distances, indices = nbrs.kneighbors(test_row)

        # Format predictions
        similar_articles = []
        for idx, val in enumerate(indices.flatten()[1:]):
            article = articles[val]
            distance = distances.flatten()[idx]
            similar_articles.append({
                'distance': distance,
                'article': article,
            })
        return similar_articles


    def load_articles_for_date(article_date):
        pass
