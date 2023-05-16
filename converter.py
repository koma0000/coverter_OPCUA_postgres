# -*- coding: utf-8 -*-
from datetime import datetime
from opcua import Client
from parse_config import ParserXML
from logger_info import LogginMyApp
from postgres import Postgres
import schedule, time
from threading import Timer
import datetime

pXML = ParserXML().parser()


class OpcUAClient:
    def __init__(self):
        self.tagsElement = None
        self.logger = LogginMyApp().get_logger(__name__)
        self.listValue = {}
        self.empty_tags = []
        self.empty_node = []

    def get_ua_type(self, value):
        if value.__class__.__name__ == 'int':
            return int(value)
        elif value.__class__.__name__ == 'float':
            return float(value)
        elif value.__class__.__name__ == 'bool':
            if value == "True":
                return 1
            else:
                return 0
        elif value.__class__.__name__ == 'str':
            return str(value)
        elif value.__class__.__name__ == 'double':
            return float(value)
        else:
            return None

    def connectClient(self, toWhichTable):
        try:
            try:
                self.client = Client(pXML['opcserver_master']['opc_host'])
                self.client.connect()
                self.logger.info(f"Подключился к серверу: {pXML['opcserver_master']['opc_host']}")
                return self.client
            except Exception:
                self.logger.warning(f"Не подключился к серверу: {pXML['opcserver_master']['opc_host']}")
                try:
                    self.client = Client(pXML['opcserver_slave']['opc_host'])
                    self.client.connect()
                    self.logger.warning("Connect slave server: " + pXML['opcserver_master']['opc_host'])
                    return self.client
                except Exception:
                    self.logger.warning(f"Не подключился к серверу: {pXML['opcserver_slave']['opc_host']} Проверьте 2 сервера")
                
        except ConnectionRefusedError:
            Postgres().insertIfNotConnectOpc(toWhichTable)

            # time.sleep(60)
            # if self.myTime == 0:
            #     self.logger.warning("No connection to server OPC")

            # OpcUAClient().connectClient()

    # Берет названия тегов из базы, ищет на сервере OPC считывая их значение и отправляет обратно в базу
    def processPostrgres(self, client, toWhichTable):
        try:
            for self.tagsElement in Postgres().selectTags():  # ['GD06.UF01UD01.KS01.GCA.CTGA_AVO1.Socket_PLC.Value', '232']
                # print(self.tagsElement)
                try:
                    self.node = client.get_node('ns=1;s=ROOT.' + str(self.tagsElement[0]))
                except Exception as e:
                    try:
                        self.node = client.get_node('ns=1;s=' + str(self.tagsElement[0]))
                    except Exception as e:
                        self.empty_node.append(self.tagsElement[0])
                        continue
                    continue
                # print(self.node)
                # print(self.node.get_value())
                try:
                    self.listValue[self.tagsElement[1]] = self.get_ua_type(self.node.get_value())
                    # print(str(self.node) + " : " + str(self.node.get_value()))
                except Exception as e:
                    self.listValue[self.tagsElement[1]] = 0
                    self.empty_tags.append(self.tagsElement[1])

            if self.empty_tags:
                self.logger.warning(f" Пустые значения тегов: {len(self.empty_tags)}, {self.empty_tags}")
            if self.empty_node:
                self.logger.warning(f" Не удалось подключится к следующим тегам: {self.empty_node}")
            Postgres().insertTagsValues(self.listValue, toWhichTable)
            # self.logger.info("Данные отправлены в базу")
        except ConnectionRefusedError:
            self.logger.warning('Нет связи с сервером OPC')
            Postgres().insertIfNotConnectOpc(toWhichTable)
            self.logger.info("Данные записанны с нулевыми значениями")


def everyFiveMinutes():
    try:
        table = ParserXML().parser()['rate_5_min']['cl_table']
        clientUA = OpcUAClient()
        clientUA.processPostrgres(clientUA.connectClient(table), table)
        clientUA.client.disconnect()
        del clientUA
    except Exception as e:
        logger = LogginMyApp().get_logger(__name__)
        logger.warning(f"{everyFiveMinutes}  " + str(e))


def everyOneHour():
    try:
        table = ParserXML().parser()['rate_1_hour']['cl_table']
        #print("В раз час: ")
        clientUA = OpcUAClient()
        clientUA.processPostrgres(clientUA.connectClient(table), table)
        clientUA.client.disconnect()
        del clientUA
    except Exception as e:
        logger = LogginMyApp().get_logger(__name__)
        logger.warning(f"{everyOneHour}  " + str(e))

def everyOneDay():
    try:
        table = ParserXML().parser()['rate_1_day']['cl_table']
        #print("В раз день: ")
        clientUA = OpcUAClient()
        clientUA.processPostrgres(clientUA.connectClient(table), table)
        clientUA.client.disconnect()
        del clientUA
    except Exception as e:
        logger = LogginMyApp().get_logger(__name__)
        logger.warning(f"{everyOneDay}  " + str(e))

if __name__ == '__main__':
    print("Version - 3.2 150523 ")
    schedule.every().hour.at(":50").do(everyOneHour)
    schedule.every().day.at("08:00:00").do(everyOneDay)

    while True:
        schedule.run_pending()
        if int(time.strftime("%M")) % 5 == 0:
    	    everyFiveMinutes()
        time.sleep(60)
    # while True:
    #     myTime = int(time.strftime("%M"))
    #     print(myTime)
    #     if myTime % 5 == 0 or myTime == 0:
    # \
    #         schedule.every(5).minutes.at(':00').do()
    #
    #         break
    #     else:
    #         myTime = int(time.strftime("%M"))
    #     time.sleep(5)
    #
    # schedule.every().hour.at(':50').do(everyOneHour)
    # schedule.every().day.at("08:00:00").do(everyOneDay)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # OpcUAClient().everyFiveMinutes()
