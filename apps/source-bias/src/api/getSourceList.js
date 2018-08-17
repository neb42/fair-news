import { get } from './utils';

const getSourceList = async () => {
  return get('/api/source');
};

export default getSourceList;