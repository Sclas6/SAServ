class Room:
    def __init__(self,name,user1,pwd):
        self.name=name
        self.user1=user1
        self.user2=None
        self.num=1
        self.pwd=pwd
        self.ctr="ctr [2,1,0]"
        self.msg=""
    
    def __repr__(self):
        #解釈しやすい名前にする
        #return f"[Room] Name: {self.name} Member: {self.num}"
        return f"{self.name} {self.user1} {self.num}"

    def joinRoom(self,user,pwd):
        if self.pwd is not None:
            if pwd==self.pwd:
                self.user2=user
                self.num+=1
                return True
            else:return False
        else:
            self.user2=user
            self.num+=1
            return True
