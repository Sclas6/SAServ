import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from RoomManager import RoomManager as RoomList

ip = "157.7.214.224"
print(ip)
port = 19071
rl = RoomList()

def showRooms():
    msg=""
    for i in RoomList.room_list:
        msg+=f"{i} "
    msg=msg[:-1]
    if msg=="":
        msg="nothing"
    return msg

def shapeMsg(msg):
    i = len(msg)
    return f"{i} {msg}\n"

def checkTokens(list):
    try:
        if len(list)==0:
            return list
        datalen=len(list)-2
        for i in list[1:]:
            datalen+=len(i)
        i = 0
        j = 0
        result=[]
        while(i<int(list[0])):
            result.append(list[j+1])
            j+=1
            i+=len(list[j])
            i+=1
        return result
    except Exception as e:
        print(f"[ERROR] can't resolve token: {e}")
        return None

def saChat(conn):
    room=None
    buf=1024
    defence=False
    tokens = None
    data = ""
    timed_out = 30
    print(f"[THREAD] CREATE: {threading.currentThread().getName()}",flush=True)
    
    try:
        conn.settimeout(timed_out)
        data = conn.recv(buf).decode('utf-8')
        conn.settimeout(None)
        tokens = checkTokens(data.split())
    except Exception as e:
        print(f"[ERROR] {e}")

    if(tokens==None and data!= ""):
        conn.send(bytes(shapeMsg("err msg solution"),"utf-8"))
    elif(data==""): pass

    else:
        if tokens[0] == "show":
            conn.send(bytes(shapeMsg(showRooms()),"utf-8"))
        elif tokens[0]=="chk_join":
            if len(tokens)==4:
                pwd=tokens[3]
            else: pwd=None
            roomInfo = rl.searchRoom(tokens[1])
            if(roomInfo!=None):
                if roomInfo.pwd==pwd:
                    conn.send(bytes(shapeMsg(f"ok join {tokens[1]} {tokens[2]} {pwd}"),"utf-8"))
                else:
                    conn.send(bytes(shapeMsg(f"err wrong password"),"utf-8"))
            else:
                conn.send(bytes(shapeMsg(f"err room not exist"),"utf-8"))
        elif tokens[0]=="chk_create":
            if rl.searchRoom(tokens[1])==None:
                conn.send(bytes(shapeMsg(f"ok create_{tokens[1]}"),"utf-8"))
            else:
                conn.send(bytes(shapeMsg(f"err {tokens[1]}_already_exists"),"utf-8"))
        elif tokens[0]=="create"and (len(tokens)==3 or len(tokens)==4):
            if len(tokens) == 4:
                pwd = tokens[3]
            else: pwd = None
            room = rl.createRoom(tokens[1],tokens[2],pwd)
            i = 0
            matching = False
            while i < timed_out:
                try:
                    conn.setblocking(False)
                    msg = conn.recv(buf).decode("utf-8")
                    conn.setblocking(True)
                    if msg == "":
                        rl.closeRoom(room.name)
                        break
                    if msg.split()[1] == "exit":
                        rl.closeRoom(room.name)
                        break
                except Exception as e:
                    pass
                if room.num == 2:
                    conn.send(bytes(shapeMsg(f"matching {room.user2}"),"utf-8"))
                    matching = True
                    break
                if i > timed_out:
                    conn.send(bytes(shapeMsg(f"err timeout"),"utf-8"))
                    rl.closeRoom(room.name)
                    break
                sleep(1)
            if matching == True:
                c_prev = "ctr [2,1,0]"
                i = 0
                while True:
                    try:
                        conn.setblocking(False)
                        msg = conn.recv(buf).decode("utf-8")
                        conn.setblocking(True)
                        if msg == "":
                            rl.closeRoom(room.name)
                            break
                        tokens = checkTokens(msg.split())
                        if tokens[0] == "exit":
                            rl.closeRoom(room.name)
                            break
                    except Exception as e:
                        pass
                    if room.num != 2:
                        rl.closeRoom(room.name)
                        conn.send(bytes(shapeMsg(f"err disconnected"),"utf-8"))
                        break
                    c = rl.getCtr(room.name)
                    if c != c_prev:
                        conn.send(bytes(shapeMsg(f"ctr {c}"),"utf-8"))
                        c_prev = c
                        i = 0
                    sleep(1 / 100)
                    i += 1
                    if i > 100 * 300:
                        conn.send(bytes(shapeMsg(f"err TIMED_OUT {i}"),"utf-8"))
                        rl.closeRoom(room.name)
                        break
                rl.closeRoom(room.name)
        elif tokens[0]=="join" and (len(tokens)==3 or len(tokens)==4):
            if len(tokens) == 4:
                pwd = tokens[3]
            else: pwd = None
            rl.joinRoom(tokens[1],tokens[2],pwd)
            room = rl.searchRoom(tokens[1])
            while True:
                if rl.searchRoom(room.name) == None:
                    conn.send(bytes(shapeMsg(f"err disconnected"),"utf-8"))
                    break
                try:
                    conn.settimeout(300)
                    msg = conn.recv(buf).decode("utf-8")
                    conn.settimeout(None)
                    if msg == "":
                        rl.setCtr(room.name, "ctr [2,1,0]")
                        rl.exitRoom(room.name)
                        break
                    tokens = checkTokens(msg.split())
                    if tokens == None:
                        rl.setCtr(room.name, "ctr [2,1,0]")
                        rl.exitRoom(room.name)
                        break
                    if tokens[0] == "exit":
                        rl.setCtr(room.name, "ctr [2,1,0]")
                        rl.exitRoom(room.name)
                        break
                    elif tokens[0] == "ctr":
                        rl.setCtr(room.name, tokens[1])
                    else:
                        break
                except Exception as e:
                    rl.setCtr(room.name, "ctr [2,1,0]")
                    rl.exitRoom(room.name)
                    print(e)
                    break
            rl.exitRoom(room.name)
        else:
            conn.send(bytes(shapeMsg(f"err unknown_command"),"utf-8"))
    print(f"[THREAD] CLOSE: {threading.currentThread().getName()}]")

def main():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((ip,port))
    s.listen(socket.SOMAXCONN)
    rl.createRoom("TestRoom","TestUser",None)
    with ThreadPoolExecutor(max_workers=100) as executor:
        while True:
            conn,addr = s.accept()
            print(f"[SOCKET] CONNECT: {addr}]",flush=True)
            executor.submit(saChat,conn)

if __name__=='__main__':
    main()
