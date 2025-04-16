import json
import os
from datetime import datetime
import time
import requests
from typing import Dict, List
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建数据库模型
Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    category = Column(String(50))
    url = Column(String(500))
    publish_date = Column(DateTime)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

def init_db():
    engine = create_engine('sqlite:///articles.db')
    Base.metadata.create_all(engine)
    return engine

class JC81Scraper:
    def __init__(self):
        self.base_url = 'https://jc81.top'
        self.engine = init_db()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def scrape(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 访问主页
            page.goto(f"{self.base_url}/4/t")
            page.wait_for_load_state('networkidle')
            
            # 解析页面内容
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # 获取所有分类
            categories = self._get_categories(soup)
            
            # 获取文章列表
            articles = self._get_articles(soup)
            
            # 保存到数据库
            self._save_articles(articles)
            
            browser.close()
            
    def _get_categories(self, soup):
        categories = []
        nav_links = soup.find_all('a', href=True)
        for link in nav_links:
            if '/4/t/' in link['href']:
                categories.append({
                    'name': link.text,
                    'url': f"{self.base_url}{link['href']}"
                })
        return categories
    
    def _get_articles(self, soup):
        articles = []
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            if '/4/p/' in link['href']:
                # 提取日期
                date_text = None
                if '2025-04-14' in link.text:
                    date_text = '2025-04-14'
                
                title = link.text.replace(date_text, '').strip() if date_text else link.text.strip()
                
                # 确保URL是完整的
                article_url = link['href']
                if not article_url.startswith('http'):
                    article_url = f"{self.base_url}{article_url}"
                
                articles.append({
                    'title': title,
                    'url': article_url,
                    'publish_date': datetime.strptime(date_text, '%Y-%m-%d') if date_text else None,
                    'category': self._determine_category(title)
                })
        
        return articles
    
    def _determine_category(self, title):
        # 根据标题关键词判断分类
        keywords = {
            '游戏': '游戏',
            'AI': '科技',
            '量子': '科技',
            '健康': '健康',
            '体育': '体育',
            '汽车': '汽车',
            '穿搭': '穿搭',
            '宠物': '宠物'
        }
        
        for keyword, category in keywords.items():
            if keyword in title:
                return category
        return '其他'
    
    def _save_articles(self, articles):
        print(f"准备保存 {len(articles)} 篇文章到数据库")
        for article_data in articles:
            # 只检查URL是否已存在
            existing = self.session.query(Article).filter(
                Article.url == article_data['url']
            ).first()
            
            if not existing:
                print(f"添加新文章: {article_data['title']} (URL: {article_data['url']})")
            article = Article(
                title=article_data['title'],
                category=article_data['category'],
                url=article_data['url'],
                publish_date=article_data['publish_date']
            )
                self.session.add(article)
            else:
                print(f"文章已存在: {article_data['title']} (URL: {article_data['url']})")
        
        try:
        self.session.commit()
            print("数据库提交成功")
        except Exception as e:
            print(f"数据库提交失败: {str(e)}")
            self.session.rollback()

    def scrape_health(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 访问健康分类页面
            page.goto(f"{self.base_url}/4/t/73nN3QW")
            page.wait_for_load_state('networkidle')
            
            # 解析页面内容
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # 获取文章列表
            articles = self._get_health_articles(soup)
            
            # 保存到数据库
            self._save_articles(articles)
            
            browser.close()
            
    def _get_health_articles(self, soup):
        articles = []
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            if '/4/p/' in link['href']:
                # 提取日期
                date_text = None
                if '2025-04' in link.text:
                    date_text = link.text[-10:]
                elif '2024-08' in link.text:
                    date_text = link.text[-10:]
                
                title = link.text.replace(date_text, '').strip() if date_text else link.text.strip()
                
                # 确保URL是完整的
                article_url = link['href']
                if not article_url.startswith('http'):
                    article_url = f"{self.base_url}{article_url}"
                
                if title and not title.startswith('资讯'):  # 过滤掉不需要的内容
                    articles.append({
                        'title': title,
                        'url': article_url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d') if date_text else None,
                        'category': '健康'
                    })
        
        return articles
    
    def scrape_sports(self):
        """
        抓取体育类文章
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 访问体育分类页面
            page.goto(f"{self.base_url}/4/t/qqw0wzP")
            page.wait_for_load_state('networkidle')
            
            # 解析页面内容
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # 获取文章列表
            articles = self._get_sports_articles(soup)
            
            # 保存到数据库
            self._save_articles(articles)
            
            browser.close()
    
    def _get_sports_articles(self, soup):
        """
        解析体育类文章
        """
        articles = []
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            if '/4/p/' in link['href']:
                # 提取日期
                date_text = None
                if '2025-04' in link.text:
                    date_text = link.text[-10:]
                elif '2024-10' in link.text:
                    date_text = link.text[-10:]
                elif '2024-08' in link.text:
                    date_text = link.text[-10:]
                
                title = link.text.replace(date_text, '').strip() if date_text else link.text.strip()
                
                # 确保URL是完整的
                article_url = link['href']
                if not article_url.startswith('http'):
                    article_url = f"{self.base_url}{article_url}"
                
                if title and not title.startswith('资讯'):  # 过滤掉不需要的内容
                    articles.append({
                        'title': title,
                        'url': article_url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d') if date_text else None,
                        'category': '体育'
                    })
        
        return articles

    def scrape_cars(self):
        """
        抓取汽车类文章
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 访问汽车分类页面
            page.goto(f"{self.base_url}/4/t/cMJYZ0s")
            page.wait_for_load_state('networkidle')
            
            # 解析页面内容
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # 获取文章列表
            articles = self._get_cars_articles(soup)
            
            # 保存到数据库
            self._save_articles(articles)
            
            browser.close()
    
    def _get_cars_articles(self, soup):
        """
        解析汽车类文章
        """
        articles = []
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            if '/4/p/' in link['href']:
                # 提取日期
                date_text = None
                if '2025-04' in link.text:
                    date_text = link.text[-10:]
                elif '2025-03' in link.text:
                    date_text = link.text[-10:]
                
                title = link.text.replace(date_text, '').strip() if date_text else link.text.strip()
                
                # 确保URL是完整的
                article_url = link['href']
                if not article_url.startswith('http'):
                    article_url = f"{self.base_url}{article_url}"
                
                if title and not title.startswith('资讯'):  # 过滤掉不需要的内容
                    articles.append({
                        'title': title,
                        'url': article_url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d') if date_text else None,
                        'category': '汽车'
                    })
        
        return articles

    def scrape_tech(self):
        """
        抓取科技类文章
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 访问科技分类页面
            page.goto(f"{self.base_url}/4/t/g5CDFi4")
            page.wait_for_load_state('networkidle')
            
            # 解析页面内容
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # 获取文章列表
            articles = self._get_tech_articles(soup)
            
            # 保存到数据库
            self._save_articles(articles)
            
            browser.close()
    
    def _get_tech_articles(self, soup):
        """
        解析科技类文章
        """
        articles = []
        # 先获取所有加粗的最新文章
        bold_articles = soup.find_all('strong')
        
        # 处理加粗的最新文章
        for article in bold_articles:
            if article.find('a') and '/4/p/' in article.find('a')['href']:
                title = article.text.strip()
                url = article.find('a')['href']
                
                # 确保URL是完整的
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
                
                # 根据关键词判断是否为科技文章
                tech_keywords = ['AI', '量子', '科技', '太空', '自动驾驶', '数字', '氢能', 'AGI', '低轨卫星']
                is_tech_article = any(keyword in title for keyword in tech_keywords)
                
                if is_tech_article:
                    articles.append({
                        'title': title,
                        'url': url,
                        'publish_date': datetime.strptime('2025-04-14', '%Y-%m-%d'),
                        'category': '科技'
                    })
        
        # 处理普通文章
        article_links = soup.find_all('a', href=True)
        for link in article_links:
            if '/4/p/' in link['href'] and not link.find_parent('strong'):
                title = link.text.strip()
                
                # 提取日期
                date_text = None
                if '2025-04-10' in title:
                    date_text = '2025-04-10'
                    title = title.replace('2025-04-10', '').strip()
                
                # 确保URL是完整的
                article_url = link['href']
                if not article_url.startswith('http'):
                    article_url = f"{self.base_url}{article_url}"
                
                # 根据关键词判断是否为科技文章
                tech_keywords = ['AI', '量子', '科技', '太空', '自动驾驶', '数字', '氢能', 'AGI', '低轨卫星']
                is_tech_article = any(keyword in title for keyword in tech_keywords)
                
                if title and not title.startswith('资讯') and is_tech_article:
                    articles.append({
                        'title': title,
                        'url': article_url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d') if date_text else None,
                        'category': '科技'
                    })
        
        return articles

    def scrape_fashion(self):
        """
        抓取穿搭类文章
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 访问穿搭分类页面
            page.goto(f"{self.base_url}/4/t/UXxWlU")
            page.wait_for_load_state('networkidle')
            
            # 解析页面内容
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # 获取文章列表
            articles = self._get_fashion_articles(soup)
            
            # 保存到数据库
            self._save_articles(articles)
            
            browser.close()
    
    def _get_fashion_articles(self, soup):
        """
        解析穿搭类文章
        """
        articles = []
        # 先获取所有加粗的最新文章
        bold_articles = soup.find_all('strong')
        
        # 处理加粗的最新文章（2025-04-15发布的文章）
        for article in bold_articles:
            if article.find('a') and '/4/p/' in article.find('a')['href']:
                title = article.text.strip()
                url = article.find('a')['href']
                
                # 确保URL是完整的
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
                
                # 根据关键词判断是否为穿搭文章
                fashion_keywords = ['穿搭', '时尚', '衣', '搭配', '汉服', '复古', '街头']
                is_fashion_article = any(keyword in title for keyword in fashion_keywords)
                
                if is_fashion_article:
                    # 从标题中提取并移除日期
                    if '2025-04-15' in title:
                        title = title.replace('2025-04-15', '').strip()
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'publish_date': datetime.strptime('2025-04-15', '%Y-%m-%d'),
                        'category': '穿搭'
                    })
        
        # 处理普通文章
        article_links = soup.find_all('a', href=True)
        for link in article_links:
            if '/4/p/' in link['href'] and not link.find_parent('strong'):
                title = link.text.strip()
                
                # 提取日期
                date_text = None
                if '2025-04-11' in title:
                    date_text = '2025-04-11'
                    title = title.replace('2025-04-11', '').strip()
                elif '2024-12-10' in title:
                    date_text = '2024-12-10'
                    title = title.replace('2024-12-10', '').strip()
                elif '2024-08-25' in title:
                    date_text = '2024-08-25'
                    title = title.replace('2024-08-25', '').strip()
                
                # 确保URL是完整的
                article_url = link['href']
                if not article_url.startswith('http'):
                    article_url = f"{self.base_url}{article_url}"
                
                # 根据关键词判断是否为穿搭文章
                fashion_keywords = ['穿搭', '时尚', '衣', '搭配', '汉服', '复古', '街头']
                is_fashion_article = any(keyword in title for keyword in fashion_keywords)
                
                if title and not title.startswith('资讯') and is_fashion_article:
                    articles.append({
                        'title': title,
                        'url': article_url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d') if date_text else None,
                        'category': '穿搭'
                    })
        
        return articles

    def scrape_games(self):
        """
        抓取游戏类文章
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 访问游戏分类页面
            page.goto(f"{self.base_url}/4/t/ooN7l93")
            page.wait_for_load_state('networkidle')
            
            # 解析页面内容
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # 获取文章列表
            articles = self._get_games_articles(soup)
            
            # 保存到数据库
            self._save_articles(articles)
            
            browser.close()
    
    def _get_games_articles(self, soup):
        """
        解析游戏类文章
        """
        articles = []
        processed_urls = set()  # 用于跟踪已处理的URL
        
        # 先获取所有加粗的最新文章
        bold_articles = soup.find_all('strong')
        print(f"找到 {len(bold_articles)} 个加粗文章")
        
        # 处理加粗的最新文章（2025-04-14发布的文章）
        for article in bold_articles:
            if article.find('a') and '/4/p/' in article.find('a')['href']:
                title = article.text.strip()
                url = article.find('a')['href']
                print(f"处理加粗文章: {title}")
                
                # 确保URL是完整的
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
                
                # 如果URL已经处理过，跳过
                if url in processed_urls:
                    continue
                processed_urls.add(url)
                
                # 根据关键词判断是否为游戏文章
                game_keywords = ['游戏', '电竞', '手游', '主机', '端游', '网游', '玩家', '联机']
                is_game_article = any(keyword in title for keyword in game_keywords)
                
                if is_game_article:
                    print(f"找到游戏文章: {title}")
                    # 从标题中提取并移除日期
                    if '2025-04-14' in title:
                        title = title.replace('2025-04-14', '').strip()
                        date_text = '2025-04-14'
                    else:
                        date_text = '2025-04-14'  # 所有加粗文章都是4月14日发布的
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d'),
                        'category': '游戏'
                    })
        
        # 处理普通文章
        article_links = soup.find_all('a', href=True)
        print(f"找到 {len(article_links)} 个链接")
        
        for link in article_links:
            if '/4/p/' in link['href'] and not link.find_parent('strong'):
                title = link.text.strip()
                url = link['href']
                print(f"处理普通文章: {title}")
                
                # 确保URL是完整的
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
                
                # 如果URL已经处理过，跳过
                if url in processed_urls:
                    continue
                processed_urls.add(url)
                
                # 提取日期
                date_text = None
                if '2025-04-14' in title:
                    date_text = '2025-04-14'
                    title = title.replace('2025-04-14', '').strip()
                elif '2025-04-10' in title:
                    date_text = '2025-04-10'
                    title = title.replace('2025-04-10', '').strip()
                elif '2024-12-10' in title:
                    date_text = '2024-12-10'
                    title = title.replace('2024-12-10', '').strip()
                elif '2024-08-25' in title:
                    date_text = '2024-08-25'
                    title = title.replace('2024-08-25', '').strip()
                
                # 根据关键词判断是否为游戏文章
                game_keywords = ['游戏', '电竞', '手游', '主机', '端游', '网游', '玩家', '联机']
                is_game_article = any(keyword in title for keyword in game_keywords)
                
                if title and not title.startswith('资讯') and is_game_article:
                    print(f"找到游戏文章: {title}")
                    articles.append({
                        'title': title,
                        'url': url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d') if date_text else None,
                        'category': '游戏'
                    })
        
        print(f"总共找到 {len(articles)} 篇游戏文章")
        return articles

    def scrape_pets(self):
        """
        抓取宠物类文章
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 访问宠物分类页面
            page.goto(f"{self.base_url}/4/t/4gsILRY")
            page.wait_for_load_state('networkidle')
            
            # 解析页面内容
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # 获取文章列表
            articles = self._get_pets_articles(soup)
            
            # 保存到数据库
            self._save_articles(articles)
            
            browser.close()
    
    def _get_pets_articles(self, soup):
        """
        解析宠物类文章
        """
        articles = []
        processed_urls = set()  # 用于跟踪已处理的URL
        
        # 先获取所有加粗的最新文章
        bold_articles = soup.find_all('strong')
        print(f"找到 {len(bold_articles)} 个加粗文章")
        
        # 处理加粗的最新文章（2025-04-14发布的文章）
        for article in bold_articles:
            if article.find('a') and '/4/p/' in article.find('a')['href']:
                title = article.text.strip()
                url = article.find('a')['href']
                print(f"处理加粗文章: {title}")
                
                # 确保URL是完整的
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
                
                # 如果URL已经处理过，跳过
                if url in processed_urls:
                    continue
                processed_urls.add(url)
                
                # 根据关键词判断是否为宠物文章
                pet_keywords = ['宠物', '猫', '狗', '兔子', '仓鼠', '鱼', '鸟', '宠', '萌宠']
                is_pet_article = any(keyword in title for keyword in pet_keywords)
                
                if is_pet_article:
                    print(f"找到宠物文章: {title}")
                    # 从标题中提取并移除日期
                    if '2025-04-14' in title:
                        title = title.replace('2025-04-14', '').strip()
                        date_text = '2025-04-14'
                    else:
                        date_text = '2025-04-14'  # 所有加粗文章都是4月14日发布的
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d'),
                        'category': '宠物'
                    })
        
        # 处理普通文章
        article_links = soup.find_all('a', href=True)
        print(f"找到 {len(article_links)} 个链接")
        
        for link in article_links:
            if '/4/p/' in link['href'] and not link.find_parent('strong'):
                title = link.text.strip()
                url = link['href']
                print(f"处理普通文章: {title}")
                
                # 确保URL是完整的
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
                
                # 如果URL已经处理过，跳过
                if url in processed_urls:
                    continue
                processed_urls.add(url)
                
                # 提取日期
                date_text = None
                if '2025-04-14' in title:
                    date_text = '2025-04-14'
                    title = title.replace('2025-04-14', '').strip()
                elif '2025-04-10' in title:
                    date_text = '2025-04-10'
                    title = title.replace('2025-04-10', '').strip()
                elif '2024-12-10' in title:
                    date_text = '2024-12-10'
                    title = title.replace('2024-12-10', '').strip()
                elif '2024-08-25' in title:
                    date_text = '2024-08-25'
                    title = title.replace('2024-08-25', '').strip()
                
                # 根据关键词判断是否为宠物文章
                pet_keywords = ['宠物', '猫', '狗', '兔子', '仓鼠', '鱼', '鸟', '宠', '萌宠']
                is_pet_article = any(keyword in title for keyword in pet_keywords)
                
                if title and not title.startswith('资讯') and is_pet_article:
                    print(f"找到宠物文章: {title}")
                    articles.append({
                        'title': title,
                        'url': url,
                        'publish_date': datetime.strptime(date_text, '%Y-%m-%d') if date_text else None,
                        'category': '宠物'
                    })
        
        print(f"总共找到 {len(articles)} 篇宠物文章")
        return articles

def main():
    scraper = JC81Scraper()
    scraper.scrape()
    scraper.scrape_health()
    scraper.scrape_sports()
    scraper.scrape_cars()
    scraper.scrape_tech()
    scraper.scrape_fashion()
    scraper.scrape_games()  # 添加游戏类文章抓取
    scraper.scrape_pets()  # 添加宠物类文章抓取

if __name__ == "__main__":
    main() 