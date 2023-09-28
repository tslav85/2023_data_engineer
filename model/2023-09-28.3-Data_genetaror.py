#Библиотеки
import json
import datetime
import random
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
from sys import stdout
import sqlalchemy
import os

#Глобальные переменные
meteo_file_path = u'meteo\meteo_data.xlsx'

#Функции

def str_to_datetime(time):
    return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

def datetime_to_str(time_dt):
    return time_dt.strftime("%Y-%m-%d %H:%M:%S")

def to_datetime(time):
    return str_to_datetime(time) if not isinstance(time, datetime.datetime) else time

#Классы

class СPhysicalValOutdoorLighting:
#    tbl = pd.DataFrame(columns=([]))
    
    def __init__(self, path):
        # загрузить данные из метеостанции
        self.tbl= pd.read_excel(path)
        #self.tbl['Время'] = pd.to_datetime(self.tbl['Время'])
        self.tbl['timestamp'] = self.tbl['Время'].values.astype(np.int64) // 10 ** 9 - 10800
        self.tbl = self.tbl.sort_values(by='timestamp')

    def getOutdoorLighting(self, time):
        # возвращает интерполированное значение освещения на улице
        # значение равно освещенности, попадающему через окно без жалюзей
        x = to_datetime(time).timestamp()
        #xp = OutdoorLighting.tbl['timestamp']
        #fp = OutdoorLighting.tbl['Солн_рад']
        xp = self.tbl['timestamp']
        fp = self.tbl['Солн_рад']
        
        interp = np.interp(x, xp, fp)
        return interp  * 80 * 3 / 100 # примерно в Люксах

######

class СPhysicalValIndoorLighting:
        
    def __init__(self):
        pass 

    def getIntdoorLighting(self, OutdoorLighting, BlindsPosition, IndoorLSLighting):
        return OutdoorLighting * BlindsPosition + IndoorLSLighting
        
    def getIntdoorColorTemp(self, OutdoorLighting, IndoorLSLighting, IndoorLSColorTemp):
        if OutdoorLighting > IndoorLSLighting:
            return '7000 K'
        else:
            return IndoorLSColorTemp
    
#####

class СPhysicalValOutdoorTemperature:
    
    def __init__(self, path):
        self.tbl= pd.read_excel(path)
        #self.tbl['Время'] = pd.to_datetime(self.tbl['Время'])
        self.tbl['timestamp'] = self.tbl['Время'].values.astype(np.int64) // 10 ** 9 - 10800
        self.tbl = self.tbl.sort_values(by='timestamp')

    def getOutdoorTemperature(self, time):
        x = to_datetime(time).timestamp()
        #xp = OutdoorLighting.tbl['timestamp']
        #fp = OutdoorLighting.tbl['Температура']
        xp = self.tbl['timestamp']
        fp = self.tbl['Температура']
        
        interp = np.interp(x, xp, fp)
        return interp

#####

class СPhysicalValIndoorTemperature:
    
    def __init__(self, temp):
        self.indoor_temp = temp        
        self.k1_temp = 0.02 # при выкл конд
        self.k2_temp = 0.05 # при вкл конд
        self.k3_temp = 0.1 # открыто окно

    def getIndoorTemperature(self, WindowStatus, CondStatus, OutdoorTemp):
        # возвращает значение температуры в комнате
        if WindowStatus == 1:
            self.indoor_temp += (OutdoorTemp - self.indoor_temp) * self.k3_temp
        elif WindowStatus == 0 and CondStatus == 1:
            self.indoor_temp += (24 - self.indoor_temp) * self.k2_temp
        elif WindowStatus == 0 and CondStatus == 0:
            self.indoor_temp += (OutdoorTemp - self.indoor_temp) * self.k1_temp
        #print(self.indoor_temp)
        return self.indoor_temp
    
    def getIndoorTempOld(self):
        return self.indoor_temp

#####

class СEventInTheRoom:
    #Событие в комнате. Задаётся сценарием
    # Класс для окна, двери, движения, протечки, дыма
  
    def __init__(self):
        self.intervals = []

    def setDiapazones(self, time_from, time_to):
        # период когда событе = 1
        self.intervals.append({'from': time_from, 'to': time_to})
  
    def checkDiapazones(self, time):
        flag = False
        timecheck = to_datetime(time)
        for rngs in self.intervals:
            if timecheck >= rngs['from'] and timecheck < rngs['to']:
                flag = True
                break
        if flag:
            return 1
        else:
            return 0

#####
class СSensor:
    # Класс для всех датчиков, создаётся переменное количество столбцов для записи

    def __init__(self, UserCode, code, name, tablename, cols):
        self.EelectricPower = 10
        self.tablename = tablename
        self.UserCode = UserCode
        self.name = name
        self.SensorCode = code
        self.cols = ['UserCode',' SensorCode']
        self.cols.extend(cols)
        #print(self.cols)
        self.tmp_dict = dict.fromkeys(cols)
        self.tmp_dict['UserCode'] = UserCode
        self.tmp_dict['SensorCode'] = code
        #print(self.tmp_dict)
        self.list_of_values = []
        #self.tbl = pd.DataFrame(columns=(self.cols))
        

    def setValues(self, **kwargs):
        # Фиксирование события в таблице
        # Аргументы должны соответстовать cols!!!
        #self.tbl = self.tbl.append(kwargs, ignore_index = True)
        for key in kwargs:
            if key == 'time':
                self.tmp_dict[key] = datetime_to_str(kwargs[key])
            else:
                self.tmp_dict[key] = kwargs[key]
        #print(self.tmp_dict)
        self.list_of_values.append(self.tmp_dict.copy())
    
    def writeToFile(self, path):
        # Запись результатов измерений в файл Excel
        full_path = path + '\\' + self.name + '.xlsx'
        self.tbl['UserCode'] = self.UserCode
        self.tbl['SensorCode'] = self.code
        self.tbl.to_excel(full_path, index=False)
    
    def writeToDB(self, ngn):        
        self.tbl['code'] = self.code
        self.tbl.to_sql(self.tablename, ngn, if_exists='append', index = False)
    
    def getEelectricPower(self):
        return self.EelectricPower
    
    def getDict(self):
        return self.list_of_values
    
    def getFullJSON(self):
        return json.dumps(self.list_of_values)
    
    def getCurrentJSON(self):
        return json.dumps(self.tmp_dict)    
    
    def writeJsonToFile(self, path):
        full_path = path + '\\' + self.name + '.json'
        with open(full_path, 'w') as file:
            json.dump(self.list_of_values, file)

    def writeCSV(self, path):
        full_path = path + '\\' + self.name + '_' + self.SensorCode + '.csv'
        df = pd.DataFrame(self.list_of_values)
        if os.path.exists(full_path):
            df.to_csv(full_path, sep=';', encoding='utf-8', index=False, mode='a', header= False)
        else:
            df.to_csv(full_path, sep=';', encoding='utf-8', index=False)
        


#####

class СDevCondition:
   
    def __init__(self):
        self.intervals = []
        self.PowerConst = 100
    
    def getCondStatus(self, OutdoorTemp, IndoorTemp, WindowStatus, IsMovement):
        if WindowStatus == 0 and IndoorTemp >= 25 and IsMovement == 1:
            return 1
        else:
            return 0
    
    def getEelectricPower(self, OutdoorTemp, IndoorTemp, WindowStatus, IsMovement):
        if self.getCondStatus(OutdoorTemp, IndoorTemp, WindowStatus, IsMovement) == 1:
            return (OutdoorTemp - IndoorTemp) * self.PowerConst
        else:
            return 0

#####

class СDevLightingSystem:
    
    def __init__(self):
        self.intervals = []
        self.LightingMax = 300 #Люкс
        self.PowerMax = 200 # Ватт
            
    def setDiapazones(self, time_from, time_to):
        # период включения
        self.intervals.append({'from': time_from, 'to': time_to})
    
    def checkDiapazones(self, time):
        flag = False
        timecheck = to_datetime(time)
        for rngs in self.intervals:
            if timecheck >= rngs['from'] and timecheck < rngs['to']:
                flag = True
                break
        if flag:
            return 1
        else:
            return 0
    
    def IsSwitchedOn(self, time, OutdoorLighting, IsMovement):
        PowerOn = self.checkDiapazones(time)
        if OutdoorLighting < self.LightingMax and IsMovement == 1 and PowerOn == 1:
            return 1
        else:
            return 0
        
    
    def getEelectricPower(self, time, OutdoorLighting, IsMovement):
        if self.IsSwitchedOn(time, OutdoorLighting, IsMovement) == 1:
            return self.PowerMax * ((self.LightingMax - OutdoorLighting) / self.LightingMax)
        else:
            return 0

    
    def getColorTemperature(self, time, OutdoorLighting, IsMovement):
        if self.IsSwitchedOn(time, OutdoorLighting, IsMovement) == 1:
            hours = to_datetime(time).hour
            if hours > 6 and hours < 20:
                return '5000 K'
            else:
                return '3000 K'
        else:
            return 'Выкл.'

    def getLighting(self, time, OutdoorLighting, IsMovement):
        if self.IsSwitchedOn(time, OutdoorLighting, IsMovement) == 1:
            return  self.LightingMax - OutdoorLighting
        else:
            return 0
        
#####

class СDevRefrigerator:
    
    def __init__(self):
        self.intervals = []
        self.PowerMax = 200
    
    def getEelectricPower(self, time):
        minutes = to_datetime(time).minute
        if (minutes >= 0 and minutes <5) or \
        (minutes >= 15 and minutes <20) or \
        (minutes >= 30 and minutes <35) or \
        (minutes >= 45 and minutes <50):
            return self.PowerMax
        else:
            return 0
            
class СDevTelevisor:
   
    def __init__(self):
        self.intervals = []
        self.PowerMax = 110
        self.PowerMin = 20
            
    def setDiapazones(self, time_from, time_to):
        # период когда событе = 1
        self.intervals.append({'from': time_from, 'to': time_to})
    
    def checkDiapazones(self, time):
        flag = False
        timecheck = to_datetime(time)
        for rngs in self.intervals:
            if timecheck >= rngs['from'] and timecheck < rngs['to']:
                flag = True
                break
        if flag:
            return 1
        else:
            return 0
    
    def getEelectricPower(self, time):
        if self.checkDiapazones(time) == 1:
            return self.PowerMax
        else:
            return self.PowerMin

#####

class СDevBlinds:
    
    def __init__(self):
        self.PowerConst = 5
        self.LightingConst = 300 #Люкс
    
    def getEelectricPower(self):
        return self.PowerConst
    
    def getBlindsPosition(self, OutdoorLighting):
        if OutdoorLighting <= self.LightingConst:
            return 1
        else:
            return self.LightingConst / OutdoorLighting

#####
class СPhysicalElectricityConsumption:
    
    def __init__(self):
        self.TotalPowerInCicle = 0
            
    def addDevicePower(self, power):
        self.TotalPowerInCicle += power
    
    def restartCycle(self):
        self.TotalPowerInCicle = 0
    
    def getTotalPower(self):
        return self.TotalPowerInCicle

class СMainOneUserClass:
    def __init__(self, UserCode):
        self.UserCode = UserCode
        self.meteo_file_path = u'meteo\meteo_data.xlsx'
        self.sensors_path = 'Датчики'
        self.time_val = str_to_datetime('2023-08-01 06:00:00')
        self.time_end = str_to_datetime('2023-08-30 23:59:00')
        self.num_of_diap =  int((self.time_end - self.time_val).total_seconds() / 10)
        print('num_of_diap=', self.num_of_diap)

    def initClasses(self):
    
        ### Инициализация классов
        #------------------------
        
        ## Физические параметры
        #----------------------
        
        # Освещение на улице
        self.OutdoorLighting = СPhysicalValOutdoorLighting(self.meteo_file_path)
        
        # Освещение в комнате
        self.IndoorLighting = СPhysicalValIndoorLighting()
        
        # Температура на улице
        self.OutdoorTemperature = СPhysicalValOutdoorTemperature(self.meteo_file_path)
        
        # Температура в комнате
        self.IndoorTemperature = СPhysicalValIndoorTemperature(22)
        
        # Потребление электроэнергии
        self.ElectricityConsumption = СPhysicalElectricityConsumption()
        
        
        ## События: окно, дверь, движение, протечка, дым
        #------------
        
        # окно
        self.EventWindow = СEventInTheRoom()
        
        # дверь
        self.EventDoor = СEventInTheRoom()
        
        # движение
        self.EventMovement = СEventInTheRoom()
        
        # протечка
        self.EventLeakage = СEventInTheRoom()
        
        # дым
        self.EventSmoke = СEventInTheRoom()
        
        ## Устройства
        #------------
        
        #Кондиционер
        self.Condition = СDevCondition()
        
        #Жалюзи с приводом
        self.Blinds = СDevBlinds()
        
        #Система освещения
        self.LightingSystem = СDevLightingSystem()
        
        #Холодильник
        self.Refrigerator = СDevRefrigerator()
        
        #Телевизор
        self.Televisor = СDevTelevisor()
        
        ## Датчики
        #---------
        
        # Освещение на улице
        self.SensorOutdoorLighting = СSensor(self.UserCode, 'SOL', 'Наружное освещение', 'SensorOutdoorLighting', ['time', 'lighting'])
        
        # Освещение в комнате
        self.SensorIndoorLighting = СSensor(self.UserCode, 'SIL', 'Внутреннее освещение', 'SensorIndoorLighting', ['time', 'lighting', 'light_temp'])
        
        # Температура на улице
        self.SensorOutdoorTemperature = СSensor(self.UserCode, 'SOT', 'Наружная температура', 'SensorOutdoorTemperature', ['time', 'temperature'])
        
        # Темперактура в комнате
        self.SensorIndoorTemperature = СSensor(self.UserCode, 'SIT', 'Внутренняя температура', 'SensorIndoorTemperature',  ['time', 'temperature'])
        
        # Жалюзи (позиция)
        self.SensorBlinds = СSensor(self.UserCode, 'SB', 'Жалюзи (позиция)', 'SensorBlinds', ['time', 'position'])
        
        # Окно (откр,закр)
        self.SensorWindow = СSensor(self.UserCode, 'SSW', 'Окно (откр,закр)', 'SensorWindow', ['time', 'status'])
        
        # Телевизор (Вкл,Выкл)
        self.SensorTV = СSensor(self.UserCode, 'SSTV', 'Телевизор (Вкл,Выкл)', 'SensorTV', ['time', 'status'])
        
        # Кондиционер (Вкл,Выкл)
        self.SensorCond = СSensor(self.UserCode, 'SSCO', 'Кондиционер (Вкл,Выкл)', 'SensorCond', ['time', 'status'])
        
        # ВнутрОсвещ (Вкл,Выкл)
        self.SensorLS = СSensor(self.UserCode, 'SSLS', 'ВнутрОсвещ (Вкл,Выкл)', 'SensorLighting_system', ['time', 'status'])
        
        # Дверь (откр,закр)
        self.SensorDoor = СSensor(self.UserCode, 'SSD', 'Дверь (откр,закр)', 'SensorDoor', ['time', 'status'])
        
        # Движение (есть,нет)
        self.SensorMovement = СSensor(self.UserCode, 'SSM', 'Движение (есть,нет)', 'SensorMovement', ['time', 'status'])
        
        # Протечка (есть,нет)
        self.SensorLeakage = СSensor(self.UserCode, 'SSL', 'Протечка (есть,нет)', 'SensorLeakage', ['time', 'status'])
        
        # Дым (есть,нет)
        self.SensorSmoke = СSensor(self.UserCode, 'SSS', 'Дым (есть,нет)', 'SensorSmoke', ['time', 'status'])
        
        # Электроэнергия (Ватт)
        self.SensorElectricalEnergy = СSensor(self.UserCode, 'SEE', 'Электроэнергия (Ватт)', 'SensorElectricalEnergy', ['time', 'power'])

    def setScenarios(self):    

        #Сценарии
        #Запуск на период начиная с '2022-08-15 06:00:00' до '2022-08-17 00:00:00'
        # !!!!! >>>>>>
        # предусмотреть разную длительность событий  
        
        date_start = datetime.date(2023,8,1)
        date_end = datetime.date(2023,8,31)
        delta = date_end - date_start
        
        ## Окно
        # -----
        # Окно открыто с 6 до 8 утра 2023-08-01
        # Движение в комнате в это же время
        # 
        start_day = datetime.datetime(2023,8,1,0,0,0)
        for i in range(int(delta.days)+1):
            day = start_day + datetime.timedelta(days=i)
            time_start = day + datetime.timedelta(hours=6) +   datetime.timedelta(minutes= random.randint(0, 30))
            time_end   = time_start + datetime.timedelta(minutes= random.randint(60, 90))
            time_end_window  = time_start + datetime.timedelta(minutes= random.randint(10, 20))
            #print(time_start, ',', time_end)
            #
            #print('window, movement', time_start, time_end)
            self.EventWindow.setDiapazones(time_start, time_end_window)
            self.EventMovement.setDiapazones(day, time_end)
            time_start = time_end
            time_end = time_start + datetime.timedelta(minutes= random.randint(3, 5))
            # дверь открыта до 5 минут
            self.EventDoor.setDiapazones(time_start, time_end)
            #print('door', time_start, time_end)
            
        # движение в комнате    
        for i in range(int(delta.days)+1):
            day = start_day + datetime.timedelta(days=i)
         
            end_day = start_day + datetime.timedelta(days=i+1) - datetime.timedelta(seconds=10)
            #print(day, end_day)
            time_start = day + datetime.timedelta(hours=18) + datetime.timedelta(minutes= random.randint(30, 60))
            time_end_door = time_start + datetime.timedelta(minutes= random.randint(3, 5))
            time_end   = time_start + datetime.timedelta(minutes= random.randint(250, 299))
            #print('movement, door', time_start, time_end_door, time_end)
            self.EventMovement.setDiapazones(time_start, end_day)
            self.EventDoor.setDiapazones(time_start, time_end_door)
            self.LightingSystem.setDiapazones(time_start, time_end)
            self.Televisor.setDiapazones(time_start, time_end)
                    
        
        ## Дым - разовое событие
        self.EventSmoke.setDiapazones(to_datetime('2023-08-02 17:00:00'), to_datetime('2023-08-02 17:30:00'))
        
        ## Протечка - разовое событие
        self.EventLeakage.setDiapazones(to_datetime('2023-08-02 17:05:00'), to_datetime('2023-08-02 18:00:00'))


    def Calculate(self):          
        #Расчёт
        #Запуск на период начиная с '2023-08-01 06:00:00' до '2022-08-03 00:00:00'
        # это 42 часа или 15120 интервалов по 10 секунд

        #time_val = str_to_datetime('2023-08-01 06:00:00')

        rng = self.num_of_diap
        #rng = 250000
        for i in range(rng+1):
            stdout.write("\ruser: {}, Переменная: {}, Время: {}, процент: {}".format(self.UserCode, i, self.time_val, round(i/rng*100,2)))
            stdout.flush()
            ## физика
            #--------
    
            self.ElectricityConsumption.restartCycle()
            self.ElectricityConsumption.addDevicePower(self.Condition.getEelectricPower(self.OutdoorTemperature.getOutdoorTemperature(self.time_val), self.IndoorTemperature.getIndoorTemperature(self.EventWindow.checkDiapazones(self.time_val), self.Condition.getCondStatus(self.OutdoorTemperature.getOutdoorTemperature(self.time_val), self.IndoorTemperature.getIndoorTempOld(), self.EventWindow.checkDiapazones(self.time_val), self.EventMovement.checkDiapazones(self.time_val)),  self.OutdoorTemperature.getOutdoorTemperature(self.time_val)), self.EventWindow.checkDiapazones(self.time_val), self.EventMovement.checkDiapazones(self.time_val)))
            self.ElectricityConsumption.addDevicePower(self.Blinds.getEelectricPower())
            self.ElectricityConsumption.addDevicePower(self.LightingSystem.getEelectricPower(self.time_val, self.OutdoorLighting.getOutdoorLighting(self.time_val), self.EventMovement.checkDiapazones(self.time_val)))
            self.ElectricityConsumption.addDevicePower(self.Refrigerator.getEelectricPower(self.time_val))
            self.ElectricityConsumption.addDevicePower(self.Televisor.getEelectricPower(self.time_val))
            #Все датчики это 10 * 14
            self.ElectricityConsumption.addDevicePower(10*14)
            
            ## датчики
            #---------
            
            # Освещение на улице
            self.SensorOutdoorLighting.setValues(time=self.time_val, lighting = self.OutdoorLighting.getOutdoorLighting(self.time_val))
            
            # Температура на улице
            self.SensorOutdoorTemperature.setValues(time=self.time_val, temperature = self.OutdoorTemperature.getOutdoorTemperature(self.time_val))
            
            # Температура в комнате 
            self.temp_indoor = self.IndoorTemperature.getIndoorTemperature(self.EventWindow.checkDiapazones(self.time_val), \
                                                                                                                  self.Condition.getCondStatus(self.OutdoorTemperature.getOutdoorTemperature(self.time_val), self.IndoorTemperature.getIndoorTempOld(), self.EventWindow.checkDiapazones(self.time_val), self.EventMovement.checkDiapazones(self.time_val)), \
                                                                                                                  self.OutdoorTemperature.getOutdoorTemperature(self.time_val))
            self.SensorIndoorTemperature.setValues(time=self.time_val, temperature = self.temp_indoor)
            
            # Освещение в комнате 
            #light_temperature = IndoorLighting.getIntdoorColorTemp(OutdoorLighting.getOutdoorLighting(time_val), Blinds.getBlindsPosition(OutdoorLighting.getOutdoorLighting(time_val)), LightingSystem.getLighting(time_val, OutdoorLighting.getOutdoorLighting(time_val), EventMovement.checkDiapazones(time_val) ) )
            
            self.light_temperature = self.IndoorLighting.getIntdoorColorTemp(self.OutdoorLighting.getOutdoorLighting(self.time_val), self.LightingSystem.getLighting(self.time_val, self.OutdoorLighting.getOutdoorLighting(self.time_val), self.EventMovement.checkDiapazones(self.time_val)), self.LightingSystem.getColorTemperature(self.time_val, self.OutdoorLighting.getOutdoorLighting(self.time_val), self.EventMovement.checkDiapazones(self.time_val)))
            
            self.light = self.IndoorLighting.getIntdoorLighting(self.OutdoorLighting.getOutdoorLighting(self.time_val), \
                                                      self.Blinds.getBlindsPosition(self.OutdoorLighting.getOutdoorLighting(self.time_val)), \
                                                      self.LightingSystem.getLighting(self.time_val, self.OutdoorLighting.getOutdoorLighting(self.time_val), \
                                                                                 self.EventMovement.checkDiapazones(self.time_val)) )
               
            
            self.SensorIndoorLighting.setValues(time=self.time_val, lighting=self.light , light_temp=self.light_temperature)
            
            # Позиция жалюзи
            self.SensorBlinds.setValues(time=self.time_val, position=self.Blinds.getBlindsPosition(self.OutdoorLighting.getOutdoorLighting(self.time_val)))
            
            # Окно
            self.SensorWindow.setValues(time=self.time_val, status=self.EventWindow.checkDiapazones(self.time_val))
            
            # Дверь
            self.SensorDoor.setValues(time=self.time_val, status=self.EventDoor.checkDiapazones(self.time_val))
            
            # Движение
            self.SensorMovement.setValues(time=self.time_val, status=self.EventMovement.checkDiapazones(self.time_val))
            
            # Протечка
            self.SensorLeakage.setValues(time=self.time_val, status=self.EventLeakage.checkDiapazones(self.time_val))
            
            # Дым
            self.SensorSmoke.setValues(time=self.time_val, status=self.EventSmoke.checkDiapazones(self.time_val))
            
            # Телевизор (Вкл,Выкл)
            self.SensorTV.setValues(time=self.time_val, status=self.Televisor.checkDiapazones(self.time_val))
        
            # Кондиционер (Вкл,Выкл)
            self.SensorCond.setValues(time=self.time_val, status=self.Condition.getCondStatus(self.OutdoorTemperature.getOutdoorTemperature(self.time_val), self.IndoorTemperature.getIndoorTempOld(), self.EventWindow.checkDiapazones(self.time_val), self.EventMovement.checkDiapazones(self.time_val)))
        
            # ВнутрОсвещ (Вкл,Выкл)
            self.SensorLS.setValues(time=self.time_val, status=self.LightingSystem.IsSwitchedOn(self.time_val, self.OutdoorLighting.getOutdoorLighting(self.time_val), self.EventMovement.checkDiapazones(self.time_val)))
                
            # Энергопотребление
            self.SensorElectricalEnergy.setValues(time=self.time_val, power=self.ElectricityConsumption.getTotalPower())
            
            self.time_val += datetime.timedelta(seconds=10)
            
        print("")

    def writeToFileCSV(self): 
        # печать результатов из датчиков в файлы
        
        # Освещение на улице
        #self.SensorOutdoorLighting.writeJsonToFile(self.sensors_path)
        self.SensorOutdoorLighting.writeCSV(self.sensors_path)
        #SensorOutdoorLighting.writeToDB(db_engine)
        
        # Температура на улице
        #self.SensorOutdoorTemperature.writeJsonToFile(self.sensors_path)
        self.SensorOutdoorTemperature.writeCSV(self.sensors_path)
        #SensorOutdoorTemperature.writeToDB(db_engine)
        
        # Температура в комнате 
        #self.SensorIndoorTemperature.writeJsonToFile(self.sensors_path)
        self.SensorIndoorTemperature.writeCSV(self.sensors_path)
        #SensorIndoorTemperature.writeToDB(db_engine)
        
        # Освещение в комнате
        #self.SensorIndoorLighting.writeJsonToFile(self.sensors_path)
        self.SensorIndoorLighting.writeCSV(self.sensors_path)
        #SensorIndoorLighting.writeToDB(db_engine)
        
        # Позиция жалюзи
        #self.SensorBlinds.writeJsonToFile(self.sensors_path)
        self.SensorBlinds.writeCSV(self.sensors_path)
        #SensorBlinds.writeToDB(db_engine)
        
        # Окно
        #self.SensorWindow.writeJsonToFile(self.sensors_path)
        self.SensorWindow.writeCSV(self.sensors_path)
        #SensorWindow.writeToDB(db_engine)
        
        # Дверь
        #self.SensorDoor.writeJsonToFile(self.sensors_path)
        self.SensorDoor.writeCSV(self.sensors_path)
        #SensorDoor.writeToDB(db_engine)
        
        # Движение
        #self.SensorMovement.writeJsonToFile(self.sensors_path)
        self.SensorMovement.writeCSV(self.sensors_path)
        #SensorMovement.writeToDB(db_engine)
                
        # Протечка
        #self.SensorLeakage.writeJsonToFile(self.sensors_path)
        self.SensorLeakage.writeCSV(self.sensors_path)
        #SensorLeakage.writeToDB(db_engine)
        
        # Дым
        #self.SensorSmoke.writeJsonToFile(self.sensors_path)
        self.SensorSmoke.writeCSV(self.sensors_path)
        #SensorSmoke.writeToDB(db_engine)
        
        # Телевизор (Вкл,Выкл)
        #self.SensorTV.writeJsonToFile(self.sensors_path)
        self.SensorTV.writeCSV(self.sensors_path)
        #SensorTV.writeToDB(db_engine)
        
        # Кондиционер (Вкл,Выкл)
        #self.SensorCond.writeJsonToFile(self.sensors_path)
        self.SensorCond.writeCSV(self.sensors_path)
        #SensorCond.writeToDB(db_engine)
        
        # ВнутрОсвещ (Вкл,Выкл)
        #self.SensorLS.writeJsonToFile(self.sensors_path)
        self.SensorLS.writeCSV(self.sensors_path)
        #SensorLS.writeToDB(db_engine)
        
        # Электропотребление 
        #self.SensorElectricalEnergy.writeJsonToFile(self.sensors_path)
        self.SensorElectricalEnergy.writeCSV(self.sensors_path)
        #SensorElectricalEnergy.writeToDB(db_engine)
        
        
# начальное время
start_time = datetime.datetime.now() 

users = [СMainOneUserClass("user"+f"{i+1}".zfill(4)) for i in range(10)]
for i in users:
    i.initClasses()
    i.setScenarios()
    i.Calculate()
    i.writeToFileCSV()
    
# конечное время
end_time = datetime.datetime.now() 
print(f'\nElapsed time to calc: \nstart: {start_time}, \nend: {end_time} \ntotal: {end_time - start_time}')    

