from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import random
import telnetlib
import time

BRAMKAIP = 'XXX.XXX.XXX.XXX'
PASS = 'password'

def suma_crc(pdu_string):
    suma = 0
    for x in range(0, len(pdu_string), 2):
        bstr = pdu_string[x:x+2]
        suma += int(bstr, 16)   
    return hex(suma)[-2:]

def pdu_encode(tekst):
    number   = 0
    bitcount = 0
    output   = ''
    byte_array = bytearray.fromhex(tekst)
    for x in byte_array:
        number = number + (x << bitcount)
        bitcount = bitcount + 1
        output = output + '%c' % (number % 128)
        number = number >> 7
        if bitcount == 7:
            output = output + '%c' % (number)
            bitcount = 0
            number = 0
    return output

def pdu_decode(string):
    n = 0
    bignum = 0
    for c in string:
        septet = ord(c)
        bignum |= septet << n
        n += 7
    m = 0
    l = []
    ret = ""
    while n > 0:
        mask = 0xFF << m
        l.append((bignum & mask) >> m)
        
        if len(hex(l[-1])) > 3: 
            ret = ret + (hex(l[-1])[-2:])
        else:
            ret = ret +"0"+ (hex(l[-1])[-1:])
        m += 8
        n -= 8
    return ret

def nr_tel_rot(nrt):
    if (len(nrt) % 2): nrt = nrt +"f" 
    ret = ''
    for i in range(1,len(nrt),2):
        ret += nrt[i]
        ret += nrt[i-1]
    return ret

def sms_buduj(nrtel, tresc):

    sh =''
    sl = len(tresc)
    if sl < 16 :
        sh = '0' + hex(len(tresc))[-1:]
    else:
        sh = hex(len(tresc))[-2:]
    sms_str =  '0001060981' + nr_tel_rot(nrtel) + '0000' + sh + pdu_decode(tresc)
    dl = (len(sms_str) / 2) -1
    scrc = suma_crc(sms_str)
    sms_str = 'AT^SM=1,' + str(int(dl)) + ',' + sms_str + ',' + scrc
    return sms_str

def sms_wyslij(nrt, tre):

    sms_line = sms_buduj(nrt, tre) + '\r\n'
    tn = telnetlib.Telnet(BRAMKAIP, 23, 6)
    time.sleep(1)
    txt = tn.read_very_eager()
    if not b'Login' in txt: return 1 
    tn.write(b"Admin\r\n")
    txt = tn.read_some()
    if not b'Password' in txt: return 2 
    tn.write(b"" + PASS + "\r\n")
    txt = tn.read_some()
    if not b'OK' in txt: return 3 
    tn.write(b"AT!G=A6\r\n")
    txt = tn.read_some()
    if not b'\r\n' in txt: return 4
    tn.write(bytes(sms_line, encoding='utf8'))
    txt = tn.read_some()
    if not b'OK' in txt: return 5
    txt = tn.read_some()
    if not b'\r\n' in txt: return 6
    txt = tn.read_some()
    if not b'smsout' in txt: return 7
    tn.write(b"AT!G=55\r\n")
    tn.read_some()
    return 0
