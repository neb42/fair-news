import axios from 'axios';
import mimir from 'mimir';
import Mercury from '@postlight/mercury-parser';
import * as tf from '@tensorflow/tfjs';

const maxWords = 1000;
const modelUrl = 'https://storage.googleapis.com/faculty-models/model.json';
const labelClassesUrl = 'https://storage.googleapis.com/faculty-models/label_classes.json';
const bagOfWordsUrl = 'https://storage.googleapis.com/faculty-models/bag_of_words.json';

const validCategories = ['politics'];

const loadModel = () => {
  return tf.loadLayersModel(modelUrl);
};

const loadLabelClasses = async () => {
  const response = await axios.get(labelClassesUrl);
  return response.data;
};

const loadBagOfWords = async () => {
  const response = await axios.get(bagOfWordsUrl);
  return response.data;
};

const getPageContent = async (url) => {
  const page = await Mercury.parse(url);
  return page.content.replace(/(<([^>]+)>)/ig, '');
};

const getPageVector = async (url) => {
  const content = await getPageContent(url);
  const bagOfWords = await loadBagOfWords();
  const vocab = new Array(maxWords).fill('');
  Object.keys(bagOfWords).forEach(key => {
    const pos = bagOfWords[key];
    if (pos < maxWords) {
      vocab[pos] = key;
    }
  });
  return mimir.bow(content, { words: vocab }).map(v => v === 0 ? 0 : 1);
};

const getArticleType = async (url) => {
  const [ model, labelClasses, vector ] = await Promise.all([
    loadModel(),
    loadLabelClasses(),
    getPageVector(url),
  ]);
  const predictionsTensor = model.predict(tf.tensor([vector]));
  const predictions = Array.from(predictionsTensor.dataSync()); 
  const classIndex = predictions.indexOf(Math.max(...predictions));
  return labelClasses[classIndex];
};

export const validateArticleType = async (url) => {
  const articleType = await getArticleType(url);
  console.log('article type prediction: ', articleType)
  return validCategories.includes(articleType);
};