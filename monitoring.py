#!/usr/local/bin/python
# coding: utf-8
# Python 3.2.1.1
# Yudintsev Vladimir / 01.07.2012

import time
import serial
import os
import sys
import re


#-------------------------------------------------------------------------------------
#                                    side 1
#-------------------------------------------------------------------------------------
mgsG=('\r%07\r\n'.encode('ascii'), #0
      '\r$D\r\n'.encode('ascii'), #1
      '\r$B\r\n'.encode('ascii'), #2
      '\r$9\r\n'.encode('ascii'), #3
      '\r$7\r\n'.encode('ascii'), #4
      '\r$5\r\n'.encode('ascii'), #5
      '\r$3\r\n'.encode('ascii'), #6
      '\r$1\r\n'.encode('ascii'), #7
      '\r$0\r\n'.encode('ascii')) #8
mgsGn= (''.encode('ascii'),
        '$D\r\n'.encode('ascii'),
	'$B\r\n'.encode('ascii'),
	'$9\r\n'.encode('ascii'),
	'$7\r\n'.encode('ascii'),
	'$5\r\n'.encode('ascii'),
	'$3\r\n'.encode('ascii'),
	'$1\r\n'.encode('ascii'),
	''.encode('ascii'))

mgs2=(    'G826\r'.encode('ascii'),  #0     '\rG826\r'
        'STATUS\r'.encode('ascii'),  #1
      'STATUS R\r'.encode('ascii'),  #2
             '1\r'.encode('ascii'),  #3
             '2\r'.encode('ascii'),  #4
             'M\r'.encode('ascii'),  #5
             '5\r'.encode('ascii'))  #6
mgs3='\r'.encode('ascii')
mgsA=(                '%\r\n'.encode('ascii'), #0
     '%0113131313131310'.encode('ascii'), #1
      '%011313131313130'.encode('ascii'), #2
       '%01131313131310'.encode('ascii'), #3
        '%0113131313130'.encode('ascii'), #4
         '%011313131310'.encode('ascii'), #5
          '%01131313130'.encode('ascii'), #6
           '%0113131310'.encode('ascii'), #7
            '%011313130'.encode('ascii'), #8
             '%01131310'.encode('ascii'), #9
              '%0113130'.encode('ascii'), #10
               '%011310'.encode('ascii'), #11
                '%01130'.encode('ascii'), #12
                 '%0110'.encode('ascii'), #13
                   '%01'.encode('ascii')) #14
mgsAn= (''.encode('ascii'), 
	'OP-Slave\r\n'.encode('ascii'),
	'6/2-Master\r\n'.encode('ascii'),
	'6/2-Slave\r\n'.encode('ascii'),
	'5/2-Master\r\n'.encode('ascii'),
	'5/2-Slave\r\n'.encode('ascii'),
	'4/2-Master\r\n'.encode('ascii'),
	'4/2-Slave\r\n'.encode('ascii'),
	'3/2-Master\r\n'.encode('ascii'),
	'3/2-Slave\r\n'.encode('ascii'),
	'2/2-Master\r\n'.encode('ascii'),
	'2/2-Slave\r\n'.encode('ascii'),
	'1/2-Master\r\n'.encode('ascii'),
	'1/2-Slave\r\n'.encode('ascii'),
	'OUP-Master\r\n'.encode('ascii'))


ser=serial.Serial()
ser.baudrate=9600
ser.port=8
ser.parity='N'
ser.stopbits=1
ser.timeout=60
ser.xonxoff=True
ser.rtscts=False
ser.dsrdtr=False
ser.open()
time.sleep(3)
print('Connect...')

def mg_read(x, t):
    now = time.time()
    y=''.encode('ascii')              #ждем 10 секунд и показываем содержимое буфера
    while (ser.inWaiting() !=0 ) or (now+t > time.time()):
        if ser.inWaiting() !=0:
            y = y + ser.read(ser.inWaiting())
        time.sleep(0.03)
    x = x + '\r\n'.encode('ascii') + y
    print(str(y))
    return x
  
def mg_write(x):
    for i in range(len(x)):
        ser.write(x[i:i+1])
        time.sleep(0.5)

def opros1(i,x):
    t = float(5+(9-i)*1+(9-i)**2*0.4+(9-i)**3*0.01)  # delay
    print('\n\n\n'+'Open ' + str(mgsG[i])+'\n\n\n')
    x = x + mgsGn[i]                          #вспомогательная информация для записи в файл
    mg_write(mgsG[i])                        #заходим в нужный нуп
    if i==8:
        mg_read(x, t)
        mg_write(mgs3+mgs2[6])                  #выходим из первого нупа
        x=mg_read(x, t)
        mg_write(mgsA[0])
        x=mg_read(x, t)
    else: 
        x=mg_read(x, t)
        mg_write(mgs3+mgs2[3])                  #заходим в первый пункт меню
        x=mg_read(x, t)
        mg_write(mgs3+mgs2[0])                  #G826
        x=mg_read(x, t)
        mg_write(mgs3+mgs2[5])                  #заходим в главное меню
        x=mg_read(x, t)
        mg_write(mgs3+mgs2[4])                  #заходим во второй пункт меню
        x=mg_read(x, t)
        mg_write(mgs3+mgs2[1])                  #STATUS
        x=mg_read(x, t)
        mg_write(mgs3+mgs2[2])                  #STATUS R
        x=mg_read(x, t)
    x=x+'\r\n\r\n\r\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\r\n\r\n\r\n'.encode('ascii')
    return x

x='\r\n'.encode('ascii')
mg_write(mgsG[0])
time.sleep(10)
x=opros1(1,x)
x=opros1(2,x) 
x=opros1(3,x) 
x=opros1(4,x) 
x=opros1(5,x) 
x=opros1(6,x) 
x=opros1(7,x) 
opros1(8,''.encode('ascii'))
mg_write(mgs3)

x_G = x[:]

#-------------------------------------------------------------------------------------
#                                    side 2
#-------------------------------------------------------------------------------------


def opros2(i,x):
    t = float(3+(15-i)*0.35+(15-i)*(15-i)*0.035)       # delay
    print('\n\n\n'+'Open ' + str(mgsA[i])+'\n\n\n')
    x = x + mgsAn[i]                          #вспомогательная информация для записи в файл
    if i==14:
        mg_write(mgsA[0])
        x=mg_read(x, t)
    mg_write(mgsA[i])                  #заходим в нужный нуп
    time.sleep(1)
    mg_write('\r\n'.encode('ascii')) 
    x=mg_read(x, t)
    mg_write(mgs2[3])                  #заходим в первый пункт меню
    x=mg_read(x, t)
    mg_write(mgs2[0])                  #G826
    x=mg_read(x, t)
    mg_write(mgs2[5])                  #заходим в главное меню
    x=mg_read(x, t)
    mg_write(mgs2[4])                  #заходим во второй пункт меню
    x=mg_read(x, t)
    mg_write(mgs2[1])                  #STATUS
    x=mg_read(x, t)
    if i==14:
        mg_write(mgs2[5])                  #заходим в главное меню
        x=mg_read(x, t)
        mg_write(mgs2[6])                  #выходим из первого нупа
        x=mg_read(x, t)
        mg_write(mgsA[0])
        x=mg_read(x, t)
        mg_write(mgs3)
    x=x+'\r\n\r\n\r\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\r\n\r\n\r\n'.encode('ascii')
    return x

x='\r\n'.encode('ascii')
time.sleep(5)
x=opros2(1,x)
x=opros2(2,x)
x=opros2(3,x)
x=opros2(4,x)
x=opros2(5,x)
x=opros2(6,x)
x=opros2(7,x)
x=opros2(8,x)
x=opros2(9,x)
x=opros2(10,x)
x=opros2(11,x)
x=opros2(12,x)
x=opros2(13,x)
x=opros2(14,x)
ser.close()
print('Close.')
x_A = x[:]


#Вывод информации на экран
#z=str(x).split('\\r\\n')
print('--------------------------------------------------------------------------')
for key in str(x_G).split('\\r\\n'):
    print(key)
for key in str(x_A).split('\\r\\n'):
    print(key)
print('--------------------------------------------------------------------------')
#


def get_filename_data(s):
    #name n #ext r
    #проверяем что у файла есть расширение и разделяем
    if s.find('.')>0:
        (n,r)=s.rsplit('.',1)
    else:
        (n,r)=(s,'')
    if r!='':
        r='.'+r
    #добавляем к имени файла дату
    n = n + '_' + \
        (lambda t : '0'+str(time.localtime()[2]) if time.localtime()[2]<10 \
         else str(time.localtime()[2]))(0) \
      + (lambda t : '0'+str(time.localtime()[1]) if time.localtime()[1]<10 \
         else str(time.localtime()[1]))(0) \
      + str(time.localtime()[0])[2:]
    return n+r

def rename_file(path_file):
    #выделяем имя файла из путь+имя
    path1=os.path.split(path_file)[0]
    f=os.path.split(path_file)[1]
    #получаем имя файла с учетом даты
    f_data=get_filename_data(f)
    #проверяем существует ли каталог, в который поместим файлы
    if not os.path.exists(path1):
        os.system('echo create katalog')
        os.makedirs(path1)
    #новое имя
    return (path1+'\\'+f_data)


def matchLineWithPattern(text, pattern):
    for match in re.finditer(pattern, text):
        s = match.start()
        e = match.end()
        return ('%s' % text[s:e])

wrmatch = lambda myfile, x: myfile.write(''.join((x,'\n')) ) if x else x


f=str(sys.argv[1])                           #имя файла берем из аргумента
f=rename_file(f)
try:
    if __name__ == '__main__':             # если запускается как сценарий  
        if (f) != (''):                       # отобразить постранично содержимое 
            myfile=open(f,'w')                   # файла, указанного в командной строк
            pattern  = '(^\$D$)|(^\$B$)|(^\$9$)|(^\$7$)|(^\$5$)|(^\$3$)|(^\$1$)|(^OP-Slave$)|(^6/2-Master$)|(^6/2-Slave$)|(^5/2-Master$)|(^5/2-Slave$)|(^4/2-Master$)|(^4/2-Slave$)|(^3/2-Master$)|(^3/2-Slave$)|(^2/2-Master$)|(^2/2-Slave$)|(^1/2-Master$)|(^1/2-Slave$)|(^OUP-Master$)|(Errored blocks(\d|[ :])+)|(SYNC: ([A-Za-z0-9]|[ :.+])+)|(GAIN:.[.\d]+.*SQ:.[.\d]+)|(Rx gain.*[.\d]+)|(Loop attn.*[.\d]+)|(SNR.*[.\d]+)'
            for key in str(x_G).split('\\r\\n'):
                wrmatch(myfile, matchLineWithPattern(key, pattern))
            for key in str(x_A).split('\\r\\n'):
                wrmatch(myfile, matchLineWithPattern(key, pattern))
            for key in str(x_G).split('\\r\\n'):
                myfile.write(key+'\n')
            for key in str(x_A).split('\\r\\n'):
                myfile.write(key+'\n')
            myfile.close()
            print('Save as '+ f) 
except:
    print('error') 

os.system('pause')
