import { get } from './utils';

const getSourceList = async () => {
  // await new Promise(resolve => setTimeout(resolve, 3000));
  // return [
  //   {
  //     source_id: 'string',
  //     name: 'string',
  //     description: 'string',
  //     url: 'https://url1.com',
  //     language_code: 'string',
  //     country_code: 'string',
  //   }
  // ];
  const response = await get('/api/source');
  return response.sources;
};

export default getSourceList;