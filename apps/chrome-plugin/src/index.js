chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
  const source_id_to_image = {
      'bbc-news': 'https://dearman.co.uk/wp-content/uploads/2016/05/bbc-news-story.jpg',
      'vice-news': 'https://i.kym-cdn.com/entries/icons/facebook/000/018/531/og-image.jpg',
      'the-guardian-uk': 'https://www.gopromotional.co.uk/blog/wp-content/uploads/2013/05/gopromotional_the_guardian_logo_square.jpg',
      'independent': 'https://static.independent.co.uk/s3fs-public/thumbnails/image/2017/06/02/11/independent-logo-eagle.png?w968h681',
      'the-economist': 'https://image3.mouthshut.com/images/imagesp/925030388s.jpg',
      'the-telegraph': 'http://www.gretchenpeters.com/worldpetershellocruel/wp-content/uploads/2015/12/The_Daily_Telegraph-logo11.jpg',
      'the-new-york-times': 'https://www.poorpeoplescampaign.org/wp-content/uploads/2018/02/the-new-york-times-square-300x300.jpg',
      'the-wall-street-journal': 'https://www.holehike.com/wp-content/uploads/2018/03/WSJ-Logo-square.jpg',
      'reuters': 'https://s3.reutersmedia.net/resources_v2/images/reuters_social_logo.png',
      'associated-press': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Associated_Press_logo_2012.svg/220px-Associated_Press_logo_2012.svg.png',
  };

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
        <img style="${styles.image}" src="${source_id_to_image[article.source_id]}" />
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

  function addSimilarArticlesToPage(similarArticles) {
    chrome.tabs.executeScript({
      code: 'document.body.innerHTML += \'' +
        buildHTML(similarArticles).replace(/(\r\n\t|\n|\r\t)/gm,"") +
        '\';',
      });
  }

  function setupTensorflow() {
    chrome.tabs.executeScript(tab.id, {
      code: 'document.body.appendChild(document.createElement("script")).src = "https://cdnjs.cloudflare.com/ajax/libs/tensorflow/1.2.2/tf.min.js";',
    });
  }

  function getPageContent() {
    return '';
  }

  function checkForNewsArticle() {
    const modelUrl = 'https://storage.googleapis.com/faculty-models/model.json';
    tf.loadLayersModel(modelUrl).then(function(model) {
      const prediction = model.predict(getPageContent());
      return prediction === 'news';
    });
  }

  function getSimilarArticles() {
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
        return json.similar_articles;
      });
  }

  if (changeInfo.url && !changeInfo.url.startsWith('chrome')) {
    setupTensorflow();
    checkForNewsArticle().then(function (isNewsArticle) {
      if (isNewsArticle) {
        getSimilarArticles().then(addSimilarArticlesToPage);
      }
    }).catch(function(error) {

    });
  }
});
