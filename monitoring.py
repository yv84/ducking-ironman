#!/usr/local/bin/python
# coding: utf-8
# Python 3.2.1.1
# Юдинцев В.Н. / 01.07.2012

import time
import datetime
import os
import sys
import re

import serial

#-----------------------------------------
mgsG = (b'\r%07\r\n', #0
         b'\r$D\r\n', #1
         b'\r$B\r\n', #2
         b'\r$9\r\n', #3
         b'\r$7\r\n', #4
         b'\r$5\r\n', #5
         b'\r$3\r\n', #6
         b'\r$1\r\n', #7
         b'\r$0\r\n') #8
mgsGn = (b'',
    b'$D\r\n',
    b'$B\r\n',
    b'$9\r\n',
    b'$7\r\n',
    b'$5\r\n',
    b'$3\r\n',
    b'$1\r\n',
    b'')

mgs2 = (b'G826\r',  #0     '\rG826\r'
      b'STATUS\r',  #1
    b'STATUS R\r',  #2
           b'1\r',  #3
           b'2\r',  #4
           b'M\r',  #5
           b'5\r')  #6
mgs3 = b'\r'
mgsA = (b'%\r\n',         #0
    b'%0113131313131310', #1
     b'%011313131313130', #2
      b'%01131313131310', #3
       b'%0113131313130', #4
        b'%011313131310', #5
         b'%01131313130', #6
          b'%0113131310', #7
           b'%011313130', #8
            b'%01131310', #9
             b'%0113130', #10
              b'%011310', #11
               b'%01130', #12
                b'%0110', #13
                  b'%01') #14
mgsAn = (b'', 
     b'OP-Slave\r\n',
    b'6/2-Master\r\n',
    b'6/2-Slave\r\n',
    b'5/2-Master\r\n',
    b'5/2-Slave\r\n',
    b'4/2-Master\r\n',
    b'4/2-Slave\r\n',
    b'3/2-Master\r\n',
    b'3/2-Slave\r\n',
    b'2/2-Master\r\n',
    b'2/2-Slave\r\n',
    b'1/2-Master\r\n',
    b'1/2-Slave\r\n',
    b'OUP-Master\r\n')

def return_bytes(func):          # for join
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return b''
    return wrapper

@return_bytes
def sleep(t):
    time.sleep(t)

def pretty_print(s:bytes) -> str:
    return '\n'.join(
            str(i)[2:-1] for i in re.split(
            b'(?:\r\n|\r|\n|[\x1b]\S*?(?:H|J)\d*){1,}',
            s) if i)
    
def mg_read(t:float) -> bytes:
    now = time.time()
    y = b''  #ждем 10 секунд и показываем содержимое буфера
    while (ser.inWaiting() !=0 ) or (now+t > time.time()):
        if ser.inWaiting() !=0:
            y += ser.read(ser.inWaiting())
        sleep(0.03)
    print(pretty_print(y))
    return b'\r\n' + y

@return_bytes
def mg_write(x:bytes):
    for i in range(len(x)):
        ser.write(x[i:i+1])
        sleep(0.5)

#-------------------------------------------------
#                  side 1
#-------------------------------------------------

def opros1(i:int) -> bytes:
    t = float(5+(9-i)*1+(9-i)**2*0.4+(9-i)**3*0.01)  # delay
    print('\n\n\n'+'Open ' + str(mgsG[i])+'\n\n\n')
    s = mgsGn[i]       
    mg_write(mgsG[i])             #заходим в нужный нуп
    if i == 8:
        s = b''.join((s,
        mg_read(t),
        mg_write(mgs3+mgs2[6]),   #выходим из первого нупа
        mg_read(t),
        mgsA[0],
        mg_read(t)))
    else: 
        s = b''.join((s,
        mg_read(t),
        mg_write(mgs3+mgs2[3]),   #заходим в первый пункт меню
        mg_read(t),
        mg_write(mgs3+mgs2[0]),   #G826
        mg_read(t),
        mg_write(mgs3+mgs2[5]),   #заходим в главное меню
        mg_read(t),
        mg_write(mgs3+mgs2[4]),   #заходим во второй пункт меню
        mg_read(t),
        mg_write(mgs3+mgs2[1]),   #STATUS
        mg_read(t),
        mg_write(mgs3+mgs2[2]),   #STATUS R
        mg_read(t)))
    return s

#-------------------------------------------------
#                   side 2
#-------------------------------------------------

def opros2(i:int) -> bytes:
    t = float(3+(15-i)*0.35+(15-i)*(15-i)*0.035)       # delay
    print('\n\n\n'+'Open ' + str(mgsA[i])+'\n\n\n')
    s = mgsAn[i]                 
    if i == 14:
        s = b''.join((s,
        mg_write(mgsA[0]),
        mg_read(t)))
    s = b''.join((s,
    mg_write(mgsA[i]),            #заходим в нужный нуп
    sleep(1),
    mg_write(b'\r\n'),
    mg_read(t),
    mg_write(mgs2[3]),            #заходим в первый пункт меню
    mg_read(t),
    mg_write(mgs2[0]),            #G826
    mg_read(t),
    mg_write(mgs2[5]),            #заходим в главное меню
    mg_read(t),
    mg_write(mgs2[4]),            #заходим во второй пункт меню
    mg_read(t),
    mg_write(mgs2[1]),            #STATUS
    mg_read(t)))
    if i == 14:
        s = b''.join((s,
        mg_write(mgs2[5]),        #заходим в главное меню
        mg_read(t),
        mg_write(mgs2[6]),        #выходим из первого нупа
        mg_read(t),
        mg_write(mgsA[0]),
        mg_read(t),
        mg_write(mgs3)))
    return s

#-------------------------------------------------
def get_filename_data(s:str) -> str:
    #name n #ext r
    #проверяем что у файла есть расширение и разделяем
    if s.find('.')>0:
        (n,r) = s.rsplit('.',1)
        r = '.'+r
    else:
        (n,r) = (s,'')
    #добавляем к имени файла дату
    return ''.join((
        n,
        '_', datetime.datetime.now().strftime("%d%m%y"),
        r))

def rename_file(path_file:str) -> str:
    #выделяем имя файла из путь+имя
    path1 = os.path.split(path_file)[0]
    f = os.path.split(path_file)[1]
    #получаем имя файла с учетом даты
    f_data = get_filename_data(f)
    #проверяем существует ли каталог, в который поместим файлы
    if not os.path.exists(path1):
        os.system('echo create katalog')
        os.makedirs(path1)
    #новое имя
    return os.path.normpath(path1+'/'+f_data)


# match pattern -> file
wrmatch = lambda myfile, x, val: \
    myfile.write(''.join((x,' : ', val if val else '', '\n')) ) \
    if x else x

# create Gen for pattern: join, decode -> del \r\n -> add '|'
namemgsGen = lambda x: ((lambda i : \
    ''.join((i.decode('latin-1').replace('$', '\$')[:-2], '|')) \
    if i else '')(i) for i in x)


patternGn = ''.join((r"""(?x)
    ^
    (?:
        (?P<name>""",
        ''.join((namemgsGen(mgsGn)) )[:-1],
        r""")
      |
        (?:
        Errored\sblocks\s+
            :\s\s    (?P<err1>\d+)   \s\s    (?P<err2>\d+)
            # Errored blocks           :  00000189  00000023
        |
        SYNC: .+ 
            GAIN:.?(?P<gain>\d+\.?\d*)\s+
            SQ:.?(?P<sq>\d+\.?\d*)
            # SYNC: 02    OPS: 01    PWR:+13.00    GAIN:+15.07    SQ:+07.4
        )
    )
    $
    """))


patternAn = ''.join((r"""(?x)
    ^
    (?:
        (?P<name>""",
        ''.join((namemgsGen(mgsAn)) )[:-1],
        r""")
      |
        (?:
        Errored\sblocks\s+
            :\s\s    (?P<err1>\d+).*
            # Errored blocks           :  00000189  00000023
        |
        Rx\sgain\s\s\s
            :\s\s(?P<gain>\d+\.?\d*)\s\w\w
            #Rx gain   :  24.7
        |
        Loop\sattn\.
            :\s\s(?P<loop>\d+\.?\d*)\s\w\w
            #Loop attn.:  19.1
        |
        SNR\s+
            :\s\s(?P<snr>\d+\.?\d*)\s\w\w
            #SNR       :  39.9
        )
    )
    $
    """))

def write_sideGn(pfile, x_G:bytes, patternGn:str):
    regex = re.compile(patternGn)

    for line in str(x_G).split('\\r\\n'):
        match = regex.search(line)
        if match:
            if match.groupdict()['name']: 
                wrmatch(pfile, '\n', match.groupdict()['name'])
            if match.groupdict()['err1']: 
                wrmatch(pfile, 'EB(M) ', str(int(match.groupdict()['err1'])) )
            if match.groupdict()['err2']: 
                wrmatch(pfile, 'EB(S) ', str(int(match.groupdict()['err2'])) )
            if match.groupdict()['gain']: 
                wrmatch(pfile, 'Gain  ', match.groupdict()['gain'])
            if match.groupdict()['sq']: 
                wrmatch(pfile, 'SQ    ', match.groupdict()['sq']) 
    
def write_sideAn(pfile, x_A:bytes, patternAn:str):
    regex = re.compile(patternAn)
    
    for line in str(x_A).split('\\r\\n'):
        match = regex.search(line)
        if match:
            if match.groupdict()['name']: 
                wrmatch(pfile, '\n', match.groupdict()['name'])
            if match.groupdict()['err1']: 
                wrmatch(pfile, 'EB(L) ', str(int(match.groupdict()['err1'])) )
            if match.groupdict()['gain']: 
                wrmatch(pfile, 'RX    ', match.groupdict()['gain'])
            if match.groupdict()['loop']: 
                wrmatch(pfile, 'LOOP  ', match.groupdict()['loop'])
            if match.groupdict()['snr']: 
                wrmatch(pfile, 'SNR   ', match.groupdict()['snr'])
    
def getExecPath():
        try:
            sFile = os.path.abspath(sys.modules['__main__'].__file__)
        except:
            sFile = sys.executable
        return os.path.dirname(sFile)


#-------------------------------------------------
try:
    f = os.path.normpath(str(sys.argv[1]))  #имя файла берем из аргумента
except IndexError:
    f = os.path.normpath(getExecPath() + '/../MG_log/MG_log.txt')

try:
    f = rename_file(f)
    print(f)

    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 8
    ser.parity = 'N'
    ser.stopbits = 1
    ser.timeout = 60
    ser.xonxoff = True
    ser.rtscts = False
    ser.dsrdtr = False
    ser.open()
    print('Connect rs-232 port...')
    
    x_G = b''.join((
        sleep(3), 
        mg_write(mgsG[0]),
        sleep(10),
        b'\r\n', 
            (b''.join(
            (b'\r\n'*3, b'!'*40, b'\r\n'*3),)
            ).join([opros1(i) for i in range(1,8)],),
        opros1(8),
        mg_write(mgs3),
        )
    )
    
    x_A = b''.join((
        sleep(5),
        b'\r\n', 
            (b''.join(
            (b'\r\n'*3, b'!'*40, b'\r\n'*3),)
            ).join([opros2(i) for i in range(1,15)],),
        )
    )

    ser.close()
    print('Close rs-232 port.')
    
    print('-'*74)

    with open(f,'w') as myfile:
        write_sideGn(myfile, x_G, patternGn)
        write_sideAn(myfile, x_A, patternAn)
        myfile.write(pretty_print(x_G))
        myfile.write(pretty_print(x_A))
        print('Save as '+ f) 

except Exception as err:
    print('Error: %s' %err)
finally:
    os.system('pause')


