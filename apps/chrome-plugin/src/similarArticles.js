import axios from 'axios';

const baseUrl = 'https://fair-news-knn.api.sherlockml.io';
const apiKey = 'rdiyMKHKcMfIQrwSTfu6nMICOTBdcnccOAsdl7vDJIvgXeLqoh';

export const getSimilarArticles = async () => {
  const response = await axios.get(
    `${baseUrl}/predict?url=${encodeURIComponent(changeInfo.url)}`,
    {
      headers: {
        'SherlockML-UserAPI-Key': apiKey,
      },
    }
  );
  return response.data.similar_articles;
};