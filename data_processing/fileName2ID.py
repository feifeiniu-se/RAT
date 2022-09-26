# -*- coding:utf-8 -*-
import sqlite3

# translate file_path to codeBlockID

def read_mappings(path):
    connection = sqlite3.connect(path)
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute(
        "select * from Mapping")
    result = cursor.fetchall()

    mappings = {}
    for tmp in result:
        mappings[tmp[0]] = tmp[1]
    cursor.close()
    connection.close()
    return mappings

def updateCodeChange(path, codeChange, fileName2ID):
    assert len(codeChange) == len(fileName2ID)
    data = []
    for i in range(len(codeChange)):
        x = [fileName2ID[i], codeChange[i][0], codeChange[i][1]]
        data.append(x)
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.executemany("update code_change set codeBlockID = ? where commit_hash=? and file_path=?", data)
    connection.commit()

def updateFiles(path, files, fileName2ID):
    assert len(files) == len(fileName2ID)
    data = []
    for i in range(len(files)):
        x = [fileName2ID[i], files[i][0]]
        data.append(x)
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.executemany("update Files set codeBlockID = ? where file_path =?", data)
    connection.commit()

def updateCodeChange_method(path, codeChange, fileName2ID):
    assert len(codeChange) == len(fileName2ID)
    data = []
    for i in range(len(codeChange)):
        x = [fileName2ID[i], codeChange[i][0], codeChange[i][2]]
        data.append(x)
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.executemany("update code_change_method set codeBlockID = ? where commit_hash=? and method_name=?", data)
    connection.commit()
    cursor.close()
    connection.close()

def read_codeChange(path):
    connection = sqlite3.connect(path)
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute(
        "select * from code_change where codeBlockID=0")
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result

def read_files(path):
    connection = sqlite3.connect(path)
    connection.text_factory=str
    cursor = connection.cursor()
    cursor.execute("select file_path from Files where codeBlockID=0")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def read_codeChange_method(path):
    connection = sqlite3.connect(path)
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute(
        "select * from code_change_method")
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


def mapping(mappings, codeChange):
    res = []

    for tmp in codeChange:
        fileName = tmp[0]
        fileName = fileName.replace("/", ".")
        fileName = fileName.replace("drools-compiler/src/main/java/rules/", "org.drools.xml.rules.")
        fileName = fileName.replace(".package-info.", ".")
        filter = [id for signature, id in mappings.items() if signature in fileName and fileName.index(signature)==int(len(fileName)-len(signature)-5)]

        if(len(filter)==1):
            res.append(filter[0])
            continue
        elif(len(filter)>=1):
            res.append(filter[1])
            continue
        else:
            # 查不出来的有可能是default包中的，也有可能是确实不存在的，比如有的文件不包含类信息，只有包信息
            start = tmp[0].rindex("/")
            end = tmp[0].index(".")
            fileName = "default.package."+tmp[0][start+1:end]
            filter = [id for signature, id in mappings.items() if signature == fileName]
            if(len(filter)==1):
                res.append(filter[0])
                continue
            elif(len(filter)>=1):
                assert 1==3
            else:
                res.append(0)
    return res


def toRoot(methodSig):
    methodSig = methodSig.replace("...", "")
    sig = methodSig.split(":")[1]
    type = ""
    body = ""
    if(len(sig.split("_"))>1):
        type = sig.split("_")[0]
        if(len(type.split("."))>2):
            type_n = type.split(".")[-1]
            methodSig = methodSig.replace(type, type_n)
    tmp = sig.split("_")[-1]
    tmp = tmp[tmp.find("(")+1:tmp.find(")")]
    params = tmp.split(", ")
    for p in params:
        if(len(p.split("."))>2):
            p_n = p.split(".")[-1]
            methodSig = methodSig.replace(p, p_n)

    return methodSig


def mapping_method(mappings, codeChange):
    res = []
    for tmp in codeChange:
        methodName = tmp[2]
        if(".NonMethodPart:nonMethodPart" in methodName):
            methodName = methodName.replace(".NonMethodPart:nonMethodPart", "")
        filter = [id for signature, id in mappings.items() if signature == methodName]

        if(len(filter)==1):
            res.append(filter[0])
            continue
        elif(len(filter)>=1):
            assert 1 == 3
        else:
            # 查不出来的有可能是default包中的，也有可能是确实不存在的，比如有的文件不包含类信息，只有包信息
            methodName = "default.package."+tmp[2]
            filter = [id for signature, id in mappings.items() if signature == methodName]
            if(len(filter)==1):
                res.append(filter[0])
                continue
            elif(len(filter)>=1):
                assert 1==3
            else:
                methodName = toRoot(tmp[2])
                filter = [id for signature, id in mappings.items() if signature == methodName]
                if(len(filter)==1):
                    res.append(filter[0])
                    continue
                elif(len(filter)>=1):
                    assert 1==3;
                else:
                    res.append(0)
    return res


def transfer(database):
    data = []
    connection = sqlite3.connect(database)
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute("select distinct file_path, codeBlockID from code_change")
    result = cursor.fetchall()
    mapping = {}
    for tmp in result:
        mapping[tmp[0]] = tmp[1]

    cursor.execute("select file_path from Files where codeBlockID=0")
    result = cursor.fetchall()
    for tmp in result:
        x = [mapping.get(tmp[0]), tmp[0]]
        data.append(x)

    cursor.executemany("update Files set codeBlockID = ? where file_path =?", data)
    connection.commit()
    cursor.close()
    connection.close()


def wildfly(database):
    # 该函数是为了将wildfly项目的commit_files_link中的file_path填入files中
    files = set()
    data = []
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("select files from Commit_files_link")
    result = cursor.fetchall()
    for tmp in result:
        f = tmp[0].replace("[","").replace("]","").split(", ")
        files = files.union(set(f))
    for f in files:
        x = [f,0]
        data.append(x)
    cursor.executemany("insert into Files values(?, ?)", data)
    print("files")
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    projects = ["derby", "drools", "hornetq", "izpack", "keycloak", "log4j2", "railo", "seam2", "teiid", "weld", "wildfly"]
    for p in projects[1:2]:
        print(p)
        database = "C:/Users/Feifei/dataset/tracescore/"+p+".sqlite3"


        # wildfly(database)
        #         先从code_change表中读取已经mapping过的文件，然后再用上述方法转化
        # transfer(database) #1
        # print("transfer")

        mappings = read_mappings(database)
        # codeChange = read_codeChange(database)
        files = read_files(database)
        print("mapping...")
        fileName2ID = mapping(mappings, files)
        # updateCodeChange(database, codeChange, fileName2ID)
        # codeChange = read_codeChange_method(database)
        # fileName2ID = mapping_method(mappings, codeChange)
        # updateCodeChange_method(database, codeChange, fileName2ID)
        print("updating...")
        updateFiles(database, files, fileName2ID)
        print("Over")



