from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from datetime import datetime
import mysql.connector
import opencc

class StockInfoPipeline:
    def __init__(self, host, user, password, database, table):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.table = table
        self.converter = opencc.OpenCC('s2t.json')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('SQL_HOST'),
            user=crawler.settings.get('SQL_USER'),
            password=crawler.settings.get('SQL_PASSWORD'),
            database=crawler.settings.get('SQL_DATABASE'),
            table=crawler.settings.get('SQL_TABLE')
        )

    def open_spider(self, spider):
        print(self.host, self.user, self.password)
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

        # 表示開始使用
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        # 結束使用
        self.cursor.close()
        # 關閉連線
        self.connection.close()
    
    def process_item(self, item, spider):
        try:
            # print('=======================================')
            title = self.converter.convert(item['title'])
            url = self.converter.convert(item['url'])
            content = self.converter.convert(item['content'])
            self.cursor.execute(f'''
                                INSERT INTO `{self.table}`
                                (`title`, `url`, `content`)
                                VALUES
                                ('{title}', '{url}', '{content}')
                                '''
            )

            self.connection.commit()
            return item
        except mysql.connector.Error as e:
            raise DropItem(f'Error inserting item: {e}')
        # except:
        #     raise DropItem(f'item have nothing.')