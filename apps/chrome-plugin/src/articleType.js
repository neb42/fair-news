import axios from 'axios';
import * as tf from '@tensorflow/tfjs';

const modelUrl = 'https://storage.googleapis.com/faculty-models/model.json';
const labelClassesUrl = 'https://storage.googleapis.com/faculty-models/label_classes.json';

const validCategories = ['politics'];

const loadModel = () => {
  return tf.loadLayersModel(modelUrl);
};

const loadLabelClasses = async () => {
  const response = await axios.get(labelClassesUrl);
  return response.data;
};

const getPageContent = () => {
  return '';
};

const getArticleType = async () => {
  const model = await loadModel();
  const labelClasses = await loadLabelClasses();
  const pageContent = getPageContent();
  const prediction = model.predict(pageContent);
  return labelClasses[prediction];
};

export const validateArticleType = async () => {
  const articleType = await getArticleType();
  return validCategories.includes(articleType);
};