import sys

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
        print(f"[ERROR] can't resolve token: {e}")
        return None
    
def main():
    value = sys.argv
    value.pop(0)
    print(value)
    print(checkTokens(value))

if __name__ == "__main__":
    main()