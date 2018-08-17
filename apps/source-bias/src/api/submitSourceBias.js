import { post } from './utils';

const submitSourceBias = (sourceId, politicalBias, reliability) => {
  return post(`/api/source/${sourceId}/bias`, {
    'politicalBias': politicalBias,
    'reliability': reliability,
  });
};

export default submitSourceBias;