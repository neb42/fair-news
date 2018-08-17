const HTTP_STATUS_ERROR = '[http-status-error]';

const parseJSON = (response: Response): Promise<any> => {
  if (response.status === 204) {
    return Promise.resolve();
  }
  return response.json();
};

const checkStatus = (response: Response) => {
  if (response.status >= 200 && response.status < 300) {
    return response;
  }
  const error: ResponseError = new Error(
    `${response.status} ${response.statusText}`
  );
  error.name = HTTP_STATUS_ERROR;
  error.response = response;
  throw error;
};


export const addBearerToken = (token: string, config: Object = {}) => {
  config.headers = config.headers || {};
  config.headers.Authorization = `Bearer ${token}`;
  return config;
};

export const addBody = (
  body: Object | Array<*>,
  config: Object,
  method: string = 'POST'
) => {
  config.headers = config.headers || {};
  config.headers.Accept = 'application/json';
  config.headers['Content-Type'] = 'application/json';
  config.method = method;
  config.body = JSON.stringify(body);
  return config;
};

const makePostRequestConfig = (
  body: Object,
  config: Object = {}
) => {
  return addBody(body, config);
};

const makePutRequestConfig = (
  body: Object,
  config: Object = {}
) => {
  return addBody(body, config, 'PUT');
};

const makePatchRequestConfig = (
  body: Object | Array<*>,
  config: Object = {}
) => {
  return addBody(body, config, 'PATCH');
};

const makeDeleteRequestConfig = (
  body: Object,
  config: Object = {}
) => {
  return addBody(body, config, 'DELETE');
};

export const get = (uri: string) => {
  return fetch(uri)
    .then(checkStatus)
    .then(parseJSON);
}

export const post = (uri: string, body: Object) => {
  return fetch(uri, makePostRequestConfig(body))
    .then(checkStatus)
    .then(parseJSON);
}

export const put = (uri: string, body: Object) => {
  return fetch(uri, makePutRequestConfig(body))
    .then(checkStatus)
    .then(parseJSON);
}

export const patch = (uri: string, body: Object) => {
  return fetch(uri, makePatchRequestConfig(body))
    .then(checkStatus)
    .then(parseJSON);
}

export const del = (uri: string, body: Object) => {
  return fetch(uri, makeDeleteRequestConfig(body))
    .then(checkStatus)
    .then(parseJSON);
}
