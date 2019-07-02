import { validateArticleType } from './articleType';
import { getSimilarArticles } from './similarArticles';
import { buildHTML } from './buildHTML';

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  try {
    if (changeInfo.url && !changeInfo.url.startsWith('chrome')) {
      const isValidArticle = await validateArticleType();
      if (isValidArticle) {
        const similarArticles = await getSimilarArticles();
        const html = buildHTML(similarArticles);
        chrome.tabs.executeScript({
          code: `document.body.innerHTML += '${html.replace(/(\r\n\t|\n|\r\t)/gm,"")}';`,
        });
      }
    }
  } catch (error) {

  }
});
