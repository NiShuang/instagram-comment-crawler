# -*- coding: UTF-8 -*-

import openpyxl
import requests
import re
import json
import sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")


class InsCommentCrawler:
    def __init__(self):
        pass

    @staticmethod
    def get_comment_by_post(post_id, max_count):
        post_url = 'https://www.instagram.com/p/' + post_id + '/'
        api_url = 'https://www.instagram.com/graphql/query/'
        comment_list = []
        page = requests.get(post_url).text
        pattern = re.compile("window._sharedData = (.*?);</script>", re.S)
        items = re.findall(pattern, page)
        data = json.loads(items[0])
        comment_data = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_parent_comment']
        page_info = comment_data['page_info']
        has_next = page_info['has_next_page']
        end_cursor = page_info['end_cursor']
        comment_list.extend(comment_data['edges'])

        while has_next and len(comment_list) < max_count:
            variables = {
                'shortcode': post_id,
                'first': 100,
                'after': end_cursor
            }
            params = {
                'query_hash': '97b41c52301f77ce508f55e66d17620e',  # 固定不变
                'variables': json.dumps(variables)
            }
            page = requests.get(api_url, params).text
            data = json.loads(page)
            comment_data = data['data']['shortcode_media']['edge_media_to_parent_comment']
            page_info = comment_data['page_info']
            has_next = page_info['has_next_page']
            end_cursor = page_info['end_cursor']
            comment_list.extend(comment_data['edges'])

        result = []
        for comment in comment_list:
            item = [
                post_id,
                comment['node']['text'],
                comment['node']['edge_liked_by']['count'],
                comment['node']['owner']['username']
            ]
            result.append(item)
        return result


if __name__ == '__main__':
    post_id_list = ['B2ezUH9neeN', 'B1wRenonmXW', 'B1ebEUhnomP', 'B1ZipeqHclh', 'B1MdhDlhIJV', 'B0WWM66HSyw',
                    'Bz8dCqfHVZn', 'Bz06boDn6Ip', 'Bzs8qTWHXQ1', 'BzgLRicH9Jm', 'BzOwx8QHcH0', 'BzJEYe4hWe7',
                    'BzGYmm2HzUu', 'By-9GUbHyag']
    crawler = InsCommentCrawler()
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    for post_id in post_id_list:
        print post_id
        try:
            comments = crawler.get_comment_by_post(post_id, 100)
        except:
            print 'sleep 20s'
            time.sleep(20)
            try:
                comments = crawler.get_comment_by_post(post_id, 100)
            except:
                print 'sleep 20s'
                time.sleep(20)
                continue
        for comment in comments:
            worksheet.append(comment)
    workbook.save("/Users/insta360/Downloads/instagram_comments.xlsx")


