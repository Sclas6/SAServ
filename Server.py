import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from chatRoom import chatRoom as RoomList

#ip=socket.gethostbyname(socket.gethostname())
ip="10.75.120.171"
print(ip)
port=19071
rl=RoomList()
#'''
def createRoom(name,user,pwd):
    r=rl.createRoom(name,user,pwd)
    if(r!=None):
        print(f"[CREATE] *{rl.rooms} NAME:{r.name} CREATOR:{r.user1}")
        return True
    return False
#'''
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
        datalen=len(list)-2
        for i in list[1:]:
            datalen+=len(i)
        """    
        if(int(list[0])==datalen):
            for i in range(len(list)-1):
                list[i]=list[i+1]
            del list[-1]
            return list
        else:
            return None
        """
        i = 0
        j = 0
        result=[]
        while(i<int(list[0])):
            #print(i)
            #print(j)
            result.append(list[j+1])
            #result[j]=list[j+1]
            j+=1
            #print("b")
            i+=len(list[j])
            i+=1
        #print(result)
        return result

    except Exception as e:
        print(e)
        return None

def saChat(conn):
    room=None
    buf=1024
    matched=False
    defence=False
    end=False
    print(f"[*] Thread: {threading.currentThread().getName()}",flush=True)
    while end==False:
        print("[debug] start roop_main")
        while matched==False:
            print("[debug] start roop_menu")
            try:
                conn.settimeout(120.0)
                data = conn.recv(buf).decode('utf-8')
                #print(f"[debug] recv:{data}")
                conn.settimeout(None)
                tokens=data.split()
                #受け取ったコマンドの文字数の整合性
                tokens=checkTokens(tokens)
                #print(f"[debug] tokens:{tokens}, len:{len(tokens)}")
                if(tokens==None and data !=""):
                    conn.send(bytes(shapeMsg("err msg solution"),"utf-8"))
                    continue
                elif data=="":
                    end=True
                    break
                if tokens[0]=="show":
                    conn.send(bytes(shapeMsg(showRooms()),"utf-8"))
                elif tokens[0]=="quit":
                    conn.send(bytes(shapeMsg("end connection"),"utf-8"))
                    print("[debug] recv quit")
                    end=True
                    break
                elif tokens[0]=="create"and (len(tokens)==3 or len(tokens)==4):
                    if len(tokens)==4:
                        pwd=tokens[3]
                    else:
                        pwd=None
                    if createRoom(tokens[1],tokens[2],pwd)==True:
                        room=rl.searchRoom(tokens[1])
                        #conn.send(bytes(shapeMsg(f"acc"),"utf-8"))
                        defence=True
                        i=0
                        while True:
                            sleep(1)
                            try:
                                conn.setblocking(False)
                                if(conn.recv(1024).decode("utf-8").split()[1]=="exit"):
                                    rl.closeRoom(room.name)
                                    #conn.send(bytes(shapeMsg(f"acc"),"utf-8"))
                                    break
                                conn.setblocking(True)
                            except Exception as e:
                                pass
                            if room.num==2:
                                matched=True
                                conn.send(bytes(shapeMsg(f"matching {room.user2}"),"utf-8"))
                                break
                            elif i>120:
                                conn.send(bytes(shapeMsg(f"err matching timeout"),"utf-8"))
                                rl.closeRoom(room.name)
                                break
                            i+=1
                    else:
                        conn.send(bytes(shapeMsg(f"err creation refused"),"utf-8"))
                elif tokens[0]=="join" and (len(tokens)==3 or len(tokens)==4):
                    if len(tokens)==4:
                        pwd=tokens[3]
                    else: pwd=None
                    if rl.joinRoom(tokens[1],tokens[2],pwd)==True:
                        matched=True
                        room=rl.searchRoom(tokens[1])
                        #conn.send(bytes(shapeMsg(f"acc"),"utf-8"))
                        defence=False
                    else:
                        conn.send(bytes(shapeMsg(f"err wrong name or pwd"),"utf-8"))
                elif tokens[0]=="chk_join":
                    if len(tokens)==4:
                        pwd=tokens[3]
                    else: pwd=None
                    roomInfo = rl.searchRoom(tokens[1])
                    if(roomInfo!=None):
                        if roomInfo.pwd==pwd:
                            conn.send(bytes(shapeMsg(f"ok join {tokens[1]} {tokens[2]} {pwd}"),"utf-8"))
                            continue
                    conn.send(bytes(shapeMsg(f"err wrong _room_or_password"),"utf-8"))
                elif tokens[0]=="chk_create":
                    if rl.searchRoom(tokens[1])==None:
                        conn.send(bytes(shapeMsg(f"ok create_{tokens[1]}"),"utf-8"))
                        continue
                    conn.send(bytes(shapeMsg(f"err {tokens[1]}_already_exists"),"utf-8"))
                else:
                    conn.send(bytes(shapeMsg(f"err unknown_command"),"utf-8"))
            except socket.error as e:
                print(f"SOCKET ERROR:{e}")
                rl.closeRoom(room.name)
                break
        # Matching True
        print("[debug] end matching roop")
        while defence==False and matched==True:
            print("[debug] start attack roop")
            if rl.searchRoom(room.name)==None:
                matched=False
                conn.send(bytes(shapeMsg(f"err disconnected"),"utf-8"))
                break
            try:
                conn.settimeout(120.0)
                data = conn.recv(buf).decode('utf-8')
                conn.settimeout(None)
                tokens = data.split()
                #print(tokens)
                tokens = checkTokens(tokens)
                if(tokens==None):
                    #conn.send(bytes(shapeMsg("err msg solution"),"utf-8"))
                    end=True
                    break
                if len(tokens)==0:
                    end=True
                    break
                if tokens[0]=="exit":
                    print("[debug] exit room")
                    rl.setCtr(room.name,"ctr l_0")
                    rl.exitRoom(room.name)
                    matched=False
                    break
                elif tokens[0]=="ctr":
                    rl.setCtr(room.name,tokens[1])
                else:
                    end=True
                    break
                print(f"[ROOM] {room.name}_ctr:{room.ctr}")
            except socket.error as e:
                print(f"SOCKET ERROR:{e}")
                rl.setCtr(room.name,"ctr l_0")
                end=True
                rl.exitRoom(room.name)
                break
        c_prev=None
        i=0
        while defence==True and matched==True:
            #切断の検知
            try:
                conn.setblocking(False)
                if len(conn.recv(1024).decode("utf-8").split())==0:
                    rl.closeRoom(room.name)
                    end=True
                    break
                else:
                    pass
                conn.setblocking(True)
            except socket.error as e:
                pass
                #print(f"[debug] ERROR:{e}")
            if room.num!=2:
                matched=False
                rl.closeRoom(room.name)
                conn.send(bytes(shapeMsg(f"err disconnected"),"utf-8"))
                break
            c=rl.getCtr(room.name)
            try:
                if c!=c_prev:
                    print("[debug] ctr updated")
                    conn.send(bytes(shapeMsg(f"ctr {c}"),"utf-8"))
                    c_prev=c
                    i=0
                sleep(0.01)
                i+=1
            except socket.error as e:
                print(f"SOCKET ERROR:{e}")
                rl.closeRoom(room.name)
                break
            if i>1200:
                conn.send(bytes(shapeMsg(f"err TIMED_OUT {i}"),"utf-8"))
                rl.closeRoom(room.name)
                matched=False
                break
    print("[debug] end one roop")
    if room!=None:
        if defence==True:
            rl.closeRoom(room.name)
        else:
            rl.exitRoom(room.name)
    print(f"[{threading.currentThread().getName()} CLOSED]")

def main():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((ip,port))
    s.listen(socket.SOMAXCONN)
    createRoom("Room1","User1",None)
    createRoom("Room2","User2","pass")
    createRoom("Room3","User3","word")
    rl.joinRoom("Room3","UserT","word")
    with ThreadPoolExecutor(max_workers=100) as executor:
        while True:
            conn,addr = s.accept()
            print("[*] Connected!! [ Source : {}]".format(addr),flush=True)
            executor.submit(saChat,conn)

if __name__=='__main__':
    main()
