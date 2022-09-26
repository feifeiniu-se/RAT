class File:
    def __init__(self, file):
        self.commit = file[0]
        self.filePath = file[1]
        self.addedLine = file[2]
        self.removedLine = file[3]
        self.classBlockID = file[4]
        self.committed_date = file[7]
        self.last_modify_date = file[5]
        self.last_modify_hash = file[2]
        self.new_filePath = file[9]
        self.new_classBlockID = file[10]
        self.methods = set()