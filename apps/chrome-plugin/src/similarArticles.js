import axios from 'axios';

const baseUrl = 'https://fair-news-knn.api.cloud.my.faculty.ai';
const apiKey = 'rdiyMKHKcMfIQrwSTfu6nMICOTBdcnccOAsdl7vDJIvgXeLqoh';

export const getSimilarArticles = async (url) => {
  const response = await axios.get(
    `${baseUrl}/predict?url=${encodeURIComponent(url)}`,
    {
      headers: {
        'UserAPI-Key': apiKey,
      },
    }
  );
  return response.data.similar_articles;
};