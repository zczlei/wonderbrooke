from flask import Flask, jsonify, send_from_directory
from sqlalchemy import create_engine, text
import os
import sqlite3

# 设置静态文件目录
app = Flask(__name__, static_url_path='', static_folder='.')

# 创建数据库连接
engine = create_engine('sqlite:///articles.db')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/categories/<path:filename>')
def serve_category(filename):
    return send_from_directory('categories', filename)

@app.route('/api/articles', methods=['GET'])
def get_articles():
    with engine.connect() as conn:
        # 获取所有文章，按发布日期降序排序
        result = conn.execute(text("""
            SELECT id, title, category, url, publish_date 
            FROM articles 
            ORDER BY publish_date DESC
        """))
        articles = []
        for row in result:
            articles.append({
                'id': row[0],
                'title': row[1],
                'category': row[2],
                'url': row[3],
                'publish_date': row[4]
            })
        return jsonify(articles)

@app.route('/api/articles/<category>', methods=['GET'])
def get_articles_by_category(category):
    with engine.connect() as conn:
        # 获取指定分类的文章，按发布日期降序排序
        result = conn.execute(text("""
            SELECT id, title, category, url, publish_date 
            FROM articles 
            WHERE category = :category
            ORDER BY publish_date DESC
        """), {"category": category})
        articles = []
        for row in result:
            articles.append({
                'id': row[0],
                'title': row[1],
                'category': row[2],
                'url': row[3],
                'publish_date': row[4]
            })
        return jsonify(articles)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    with engine.connect() as conn:
        # 获取所有分类及其文章数量
        result = conn.execute(text("""
            SELECT category, COUNT(*) as count 
            FROM articles 
            GROUP BY category 
            ORDER BY count DESC
        """))
        categories = []
        for row in result:
            categories.append({
                'category': row[0],
                'count': row[1]
            })
        return jsonify(categories)

@app.route('/api/articles')
def get_all_articles():
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles ORDER BY publish_date DESC')
    articles = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': article[0],
        'title': article[1],
        'category': article[2],
        'url': article[3],
        'publish_date': article[4],
        'content': article[5],
        'created_at': article[6]
    } for article in articles])

@app.route('/api/articles/<category>')
def get_category_articles(category):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE category = ? ORDER BY publish_date DESC', (category,))
    articles = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': article[0],
        'title': article[1],
        'category': article[2],
        'url': article[3],
        'publish_date': article[4],
        'content': article[5],
        'created_at': article[6]
    } for article in articles])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    
    app.run(host='0.0.0.0', port=args.port, debug=True) 