import { validateArticleType } from './articleType';
import { getSimilarArticles } from './similarArticles';
import { buildHTML } from './buildHTML';

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  try {
    if (changeInfo.url && !changeInfo.url.startsWith('chrome')) {
      console.log('url: ', changeInfo.url)
      const isValidArticle = await validateArticleType(changeInfo.url);
      if (isValidArticle) {
        const similarArticles = await getSimilarArticles(changeInfo.url);
        const html = buildHTML(similarArticles);
        chrome.tabs.executeScript({
          code: `
            var div=document.createElement("div");
            document.body.appendChild(div);
            div.innerHTML='${html.replace(/(\r\n\t|\n|\r\t)/gm,"")}';
          `,
        });
      }
    }
  } catch (error) {
    console.log(error)
  }
});
