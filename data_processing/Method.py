class Method:
    def __init__(self, method):
        # self.commit = method[0]
        # self.filePath = method[1]
        # self.file_status = ""
        self.name = method[2]
        self.type = method[3]
        self.startLine = method[4]
        self.endLine = method[5]
        self.addedLine = method[6]
        self.removedLine = method[7]
        self.methodBlockID = method[8]


