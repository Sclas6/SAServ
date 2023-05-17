from Room import Room

class chatRoom:
    rooms=0
    room_list=[]
    def __init__(self):
        pass

    def createRoom(self,name,user,pwd):
        if self.searchRoom(name)==None:
            r = Room(name,user,pwd)
            chatRoom.rooms+=1
            chatRoom.room_list.append(r)
            return r
        return None

    def searchRoom(self,name):
        for i in chatRoom.room_list:
            if i.name==name:
                return i
        return None
    
    def joinRoom(self,room,user,pwd):
        target=self.searchRoom(room)
        if target!=None:
            if target.num<2:
                if target.joinRoom(user,pwd)==True:
                    return True
        return False
    
    def getRooms(self):
        return self.rooms
    
    def exitRoom(self,name):
        target=self.searchRoom(name)
        if target!=None:
            target.num=1
            target.user2=None
            return True
        return False

    def closeRoom(self,name):
        target=self.searchRoom(name)
        if target!=None:
            chatRoom.rooms-=1
            chatRoom.room_list.remove(target)
            del self
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
