chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
  const styles = {
    container: [
      'all: unset;',
      'position: fixed;',
      'top: 50%;',
      'right: 15px;',
      'margin-top: -100px;',
      'background-color: #fff;',
      'width: 400px;',
      'display: flex;',
      'flex-direction: column;',
      'z-index: 999999999;',
      'box-shadow: 0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22);',
    ].join(''),
    header: [
      'display: flex;',
      'justify-content: space-between;',
      'align-items: center;',
      'padding: 10px 20px 0 10px;',
    ].join(''),
    brandName: [

    ].join(''),
    close: [

    ].join(''),
    article: [
      'display: flex;',
      'flex-direction: row;',
      'padding: 10px 10px 10px 0;',
    ].join(''),
    image: [
      'width: 80px;',
      'height: 80px;',
      'background-color: red;',
    ].join(''),
    info: [
      'display: flex;',
      'flex-direction: column;',
      'justify-content: space-evenly;',
      'margin-left: 10px;'
    ].join(''),
    title: [
      'font-size: 14px;',
      'font-weight: 500;',
    ].join(''),
    source: [
      'font-size: 14px;',
      'font-weight: 400;',
    ].join(''),
  };

  function buildArticleHTML(article) {
    return article ? `
      <a style="${styles.article}" href="${article.url}" target="_blank">
        <img style="${styles.image}" src="" />
        <div style="${styles.info}">
          <span style="${styles.title}">${article.title.replace('\'', '')}</span>
          <span style="${styles.source}">${article.source_id.replace('-', ' ')}</span>
        </div>
      </a>
    ` : '';
  }

  function buildHTML(similarArticles) {
    return `
      <div style="${styles.container}">
        <div style="${styles.header}">
          <span style="${styles.brandName}">Polar News</span>
          <button style="${styles.close}">&times;</button>
        </div>
        ${buildArticleHTML(similarArticles.left)}
        ${buildArticleHTML(similarArticles.center)}
        ${buildArticleHTML(similarArticles.right)}
      </div>
    `;
  }

  if (changeInfo.url && !changeInfo.url.startsWith('chrome')) {
    const url = 'https://fair-news-knn.api.sherlockml.io/predict?url=' + encodeURIComponent(changeInfo.url);
    const config = {
      method: 'GET',
      headers: {
        'SherlockML-UserAPI-Key': 'rdiyMKHKcMfIQrwSTfu6nMICOTBdcnccOAsdl7vDJIvgXeLqoh',
      },
    };
    fetch(url, config)
      .then(function(response) {
          if (response.status === 200) {
            return response.json();
          }
          return Promise.resolve();
      })
      .then(function(json) {
        if (json) {
          chrome.tabs.executeScript({ code: 'document.body.innerHTML += \'' + buildHTML(json.similar_articles).replace(/(\r\n\t|\n|\r\t)/gm,"") + '\';' });
        }
      })
      .catch(function(error) {
        console.log(error);
      });
  }
});
