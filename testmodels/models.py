# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import sqlite3

import MySQLdb

from testmodels import const
import time
# import MySQLdb

class TestModels():
    db_name = const.SQLITE_DB_NAME

    @classmethod
    def db_connect(self):
        try:
            conn = MySQLdb.connect(host="192.168.8.118",
                                   user="root",
                                   passwd="",
                                   db="django")
        except MySQLdb.Error:
            time.sleep(0.5)
            db = self.db_connect()
        return conn

    @classmethod
    def set_status(self, status):

        db = self.db_connect()
        cursor = db.cursor()
        data = (status, 1)
        cursor.execute("UPDATE tbl_test2 SET status=%s WHERE id=%s" % data)
        db.commit()
        cursor.close()

    @classmethod
    def set_find_type(self, find_type):

        try:
            db = self.db_connect()
            cursor = db.cursor()
            data = (find_type, 1)
            cursor.execute("UPDATE tbl_test2 SET find_type=%s WHERE id=%s" % data)
        except MySQLdb.Error as error:
            print(error)
        finally:
            db.commit()
            cursor.close()

    @classmethod
    def set_file_name(self, file_name):

        try:
            db = self.db_connect()
            cursor = db.cursor()
            data = (file_name, 1)
            cursor.execute("UPDATE tbl_test2 SET file_name=%s WHERE id=%s" % data)
        except MySQLdb.Error as error:
            print(error)
        finally:
            db.commit()
            cursor.close()

    @classmethod
    def set_test2_all_data(self, find_type, cur_alphaindex, cur_linkindex, file_name, status):
        # prepare a cursor object using cursor() method
        db = self.db_connect()
        cursor = db.cursor()

        # execute SQL query using execute() method.
        cursor.execute(
            "UPDATE tbl_test2 SET find_type=%s, current_alphaindex=%s, current_linkindex=%s, file_name=%s, status=%s WHERE id=1" %
            (find_type, cur_alphaindex, cur_linkindex, file_name, status))
        db.commit()
        cursor.close()

    @classmethod
    def set_test2_index_data(self, cur_alphaindex, cur_linkindex):
        # prepare a cursor object using cursor() method
        db = self.db_connect()
        cursor = db.cursor()

        # execute SQL query using execute() method.
        cursor.execute(
            "UPDATE tbl_test2 SET current_alphaindex=%s, current_linkindex=%s WHERE id=1" % (
            cur_alphaindex, cur_linkindex))
        db.commit()
        cursor.close()

    @classmethod
    def set_test2_linkindex_data(self):
        # prepare a cursor object using cursor() method
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("SELECT current_linkindex FROM tbl_test2 WHERE id=1")

        data = cursor.fetchone()
        linkindex = int(data[0]) + 1
        # execute SQL query using execute() method.
        cursor.execute(
            "UPDATE tbl_test2 SET current_linkindex=%s WHERE id=%s" % (linkindex, 1))
        cursor.commit()
        cursor.close()

    @classmethod
    def get_test2_data(self):

        # prepare a cursor object using cursor() method
        db = self.db_connect()
        cursor = db.cursor()

        # execute SQL query using execute() method.
        cursor.execute(
            "SELECT find_type,current_alphaindex,current_linkindex,file_name,status FROM tbl_test2 WHERE id=1")

        data = cursor.fetchone()
        cursor.close()
        return data

    @classmethod
    def set_init_count(self):

        # prepare a cursor object using cursor() method
        db = self.db_connect()
        cursor = db.cursor()

        # execute SQL query using execute() method.
        data = (0, 0, 0, 1)
        cursor.execute(
            "UPDATE tbl_product_count SET all_product_count=%s, find_product_count=%s, fail_product_count=%s where id=%s" % data)
        db.commit()
        cursor.close()

    @classmethod
    def get_find_count(self):

        # prepare a cursor object using cursor() method
        db = self.db_connect()
        cursor = db.cursor()

        # execute SQL query using execute() method.
        cursor.execute(
            "SELECT all_product_count,find_product_count,fail_product_count FROM tbl_product_count WHERE id=1")

        # Fetch a single row using fetchone() method.
        data = cursor.fetchone()
        # disconnect from server
        cursor.close()
        return data

    @classmethod
    def add_prod_info(self, prodid, category, crawldate):

        db = self.db_connect()
        cursor = db.cursor()
        d = (prodid, category, crawldate)
        cursor.execute("INSERT INTO tbl_product_info(prodid, category, crawldate) VALUES(%s,%s,%s)", d)
        db.commit()
        cursor.close()


    @classmethod
    def get_prod_info(self, prodid):
        db = self.db_connect()
        cursor = db.cursor()
        query = "SELECT id,prodid,category,crawldate FROM tbl_product_info WHERE prodid=%s"
        d = (prodid)
        cursor.execute(query, [d])
        data = cursor.fetchone()
        cursor.close()
        return data

    @classmethod
    def del_prod_info(self, category):

        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("DELETE FROM tbl_product_info WHERE category=%s", [category])
        db.commit()
        cursor.close()

    @classmethod
    def add_cat_info(self, category_url, category_name):

        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("INSERT INTO tbl_category(category_url, category_name) VALUES(%s,%s)",
                       (category_url, category_name))
        db.commit()
        cursor.close()

    @classmethod
    def get_cat_info(self, id):
        try:
            db = self.db_connect()
            cursor = db.cursor()
            query = "SELECT category_url,category_name FROM tbl_category WHERE id=%s"
            d = (id)
            cursor.execute(query, [d])
            data = cursor.fetchone()
        except MySQLdb.Error as error:
            print(error)

        finally:
            cursor.close()
        return data