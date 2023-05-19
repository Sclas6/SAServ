from Room import Room

class RoomManager:
    rooms=0
    room_list=[]
    def __init__(self):
        pass

    def createRoom(self,name,user,pwd):
        if self.searchRoom(name)==None:
            r = Room(name,user,pwd)
            RoomManager.rooms+=1
            RoomManager.room_list.append(r)
            print(f"[ROOM]   CREATE: NAME:{r.name} CREATOR:{r.user1} [{self.rooms}]")
            return r
        return None

    def searchRoom(self,name):
        for i in RoomManager.room_list:
            if i.name==name:
                return i
        return None
    
    def joinRoom(self,room,user,pwd):
        target=self.searchRoom(room)
        if target!=None:
            if target.num<2:
                if target.joinRoom(user,pwd)==True:
                    print(f"[ROOM]   JOIN  : ROOM:{room} JOIN:{user}")
                    return True
        return False
    
    def getRooms(self):
        return self.rooms
    
    def exitRoom(self,name):
        target=self.searchRoom(name)
        if target!=None:
            print(f"[ROOM]   EXIT  : ROOM:{name} NAME:{target.user2}")
            target.num=1
            target.user2=None
            return True
        return False

    def closeRoom(self,name):
        target=self.searchRoom(name)
        if target!=None:
            RoomManager.rooms-=1
            RoomManager.room_list.remove(target)
            del self
            print(f"[ROOM]   CLOSE : NAME:{name}")
            return True
        return False
    
    def setCtr(self,name,ctr):
        target=self.searchRoom(name)
        if target!=None:
            target.ctr=ctr
            return True
        return False
    
    def getCtr(self,name):
        target=self.searchRoom(name)
        if target!=None:
            return target.ctr
        return "err don't exist room"
