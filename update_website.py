import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

def load_articles(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def update_index_html(articles):
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    # 更新主要新闻列表
    main_news = soup.select_one(".col-md-8")
    main_news.clear()
    
    # 添加特色文章
    featured_div = soup.new_tag("div", attrs={"class": "featured-article mb-4"})
    first_article = articles["tech"][0]  # 使用科技类别的第一篇文章作为特色文章
    featured_div.append(create_news_item(first_article))
    main_news.append(featured_div)
    
    # 添加其他文章
    for category in articles:
        for article in articles[category][1:]:  # 跳过第一篇文章，因为已经作为特色文章
            main_news.append(create_news_item(article))
    
    # 更新今日速读
    today_read = soup.select_one(".today-read-list")
    today_read.clear()
    for article in articles["games"][:6]:  # 使用游戏类别的文章作为今日速读
        item = soup.new_tag("div", attrs={"class": "list-group-item"})
        h5 = soup.new_tag("h5")
        h5.string = article["title"]
        item.append(h5)
        today_read.append(item)
    
    # 更新排行榜
    ranking_list = soup.select_one(".ranking-list")
    ranking_list.clear()
    for article in articles["tech"][:6]:  # 使用科技类别的文章作为排行榜
        li = soup.new_tag("li")
        li.string = article["title"]
        ranking_list.append(li)
    
    # 更新精选好文
    hot_articles = soup.select(".hot-article-item")
    for i, article in enumerate(articles["tech"][:2]):  # 使用科技类别的前两篇文章作为精选好文
        if i < len(hot_articles):
            hot_articles[i].clear()
            img = soup.new_tag("img", attrs={"class": "hot-article-img", "src": article["image"], "alt": article["title"]})
            content = soup.new_tag("div", attrs={"class": "hot-article-content"})
            h5 = soup.new_tag("h5")
            h5.string = article["title"]
            date = soup.new_tag("div", attrs={"class": "article-date"})
            date.string = f"资讯 {article['date']}"
            content.append(h5)
            content.append(date)
            hot_articles[i].append(img)
            hot_articles[i].append(content)
    
    # 保存更新后的文件
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup))

def create_news_item(article):
    soup = BeautifulSoup("", "html.parser")
    div = soup.new_tag("div", attrs={"class": "news-item"})
    
    img = soup.new_tag("img", attrs={"class": "news-img", "src": article["image"], "alt": article["title"]})
    content = soup.new_tag("div", attrs={"class": "news-content"})
    h5 = soup.new_tag("h5")
    h5.string = article["title"]
    date = soup.new_tag("div", attrs={"class": "news-date"})
    date.string = article["date"]
    
    content.append(h5)
    content.append(date)
    div.append(img)
    div.append(content)
    
    return div

def main():
    # 获取最新的文章文件
    article_files = [f for f in os.listdir() if f.startswith("articles_") and f.endswith(".json")]
    if not article_files:
        print("No article files found!")
        return
    
    latest_file = max(article_files)
    articles = load_articles(latest_file)
    update_index_html(articles)
    print("Website updated successfully!")

if __name__ == "__main__":
    main() 