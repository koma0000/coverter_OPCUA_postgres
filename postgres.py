from datetime import datetime
import psycopg2
from parse_config import ParserXML
import logger_info

pXML = ParserXML().parser()


class Postgres():
    # Инициализируем конфиг из XML
    def __init__(self):
        self.logger = logger_info.LogginMyApp().get_logger(__name__)

    # Создаем подключение к базе
    def connection(self):
        try:
            self.connect = psycopg2.connect(database=pXML['database']['db_name'],
                                            user=pXML['database']['db_user'],
                                            password=pXML["database"]['db_password'],
                                            host=pXML["database"]['db_host'],
                                            port=pXML["database"]['db_port'])
            self.logger.info("Подключено к базе данных PostgreSQL")
            return self.connect

        except psycopg2.OperationalError as e:
            self.logger.info("Подключение к базе данных прошло c ошибкой: " + str(e))
            # print("The error " + e + "occurred")

    # Запрос на вывод всех тегов из базы данных для сравнения с сервером OPC
    def selectTags(self):
        try:
            self.sqlSelect = 'SELECT ' + str(pXML['database']['tb_column_tag']) + ", " + str(
                pXML['database']['tb_column_id_tag']) + ' FROM ' + str(pXML['database']['tb_name']) + ' WHERE ' + str(
                pXML['database']['tb_column_tag']) + " IS NOT NULL and tag_name <>'-'"
            self.connection = self.connection()
            self.cursor = self.connection.cursor()
            self.cursor.execute(self.sqlSelect)
            _selectTags = [self.i for self.i in self.cursor.fetchall()]
            self.connection.close()
            return _selectTags
        except Exception as e:
            self.logger.warning('selectTags  ' + str(e))


    # Запрос записи в базу, тегов с их значениями
    def insertTagsValues(self, listValue, toWhichTable):
        self.connection = self.connection()
        for key, value in listValue.items():
            try:
                self.tempstamp = datetime.now()
                self.sqlInsert = "INSERT INTO " + str(toWhichTable) + " (" + str(
                    pXML['database']['tb_isert_id_tag']) + ", " + str(
                    pXML['database']['tb_isert_value']) + ", " + str(
                    pXML['database']['tb_isert_timestamp']) + ") VALUES (\'" + str(key) + "\', \'" + str(
                    ('%.3f' % value)) + "\', '" + str(self.tempstamp) + "\')"
                self.cursor = self.connection.cursor()
                self.cursor.execute(self.sqlInsert)
                self.connection.commit()
            except Exception as e:
                self.logger.warning('Не записалось в базу тег {0} {1}'.format(str(key), e))
        self.connection.close()

    def insertIfNotConnectOpc(self, toWhichTable):

        self.connection = self.connection()
        selectTags = Postgres().selectTags()
        for tag in selectTags:
            tempstamp = datetime.now()
            sqlInsert = "INSERT INTO " + str(toWhichTable) + " (" + str(
                pXML['database']['tb_isert_id_tag']) + ", " + str(
                pXML['database']['tb_isert_value']) + ", " + str(
                pXML['database']['tb_isert_timestamp']) + ") VALUES (\'" + str(tag[1]) + "\', \'" + str(
                0) + "\', '" + str(tempstamp) + "\')"

            try:
                self.cursor = self.connection.cursor()
                self.cursor.execute(sqlInsert)
                self.connection.commit()
            except:
                self.logger.warning('insertIfNotConnectOpc Не записалось в базу тег {0} {1}'.format(str(tag[1]), e))
                continue
        self.connection.close()

# if __name__ == "__main__":
#     Postgres().insertIfNotConnectOpc(ParserXML().parser()['rate_5_min']['cl_table'])
# Postgres().insert()
