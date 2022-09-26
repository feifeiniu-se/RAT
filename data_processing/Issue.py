import datetime


class Issue:
    def __init__(self, info):
        self.issue_id = info[0]
        self.issue_type = info[1]
        self.fixed_date = datetime.datetime.strptime(info[2].replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S")
        self.created_date = datetime.datetime.strptime(info[5].replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S")
        self.first_commit_date = '2022-12-31 11:59:59'
        self.first_commit_hash = set()
        self.summary_stem = info[3]
        self.description_stem = info[4]
        self.tfidf = []
        self.bert = []
        self.files = [] # ground truth of file level
        # self.methods = [] # ground truth of method level
        self.artifacts = []
        self.artif_sim = []
        self.source_files = set() # file path of all source code at current version
        self.source_files_ID = set() # file id of all source code at current version

        self.predict_bf = []
        self.predict_bf_r = []
        self.predict_bfm_r = []
        self.predict_bm = []
        self.predict_bm_r = []
        self.predict_bm_rw = []
        self.predict_bm_w = []
        self.predict_bm_r_f = []

        self.original_summary = ""
        self.original_description = ""

        self.cache_score = {}
        self.bluir_score = {}
        self.amalgam = []
        self.cache_id_score = {}
        self.bluir_id_score = {}
        self.simi_score = {}
        self.simi_id_score = {}
        self.amalgam_score = {}
        self.ablots = []
        self.ablots_score = {}

        self.cache_score_new = {}
        self.cache_id_score_new = {}

        self.refactoring = {}
        self.refactoring_method = {}

    def findFile(self, fileName, commit):
        for file in self.files:
            if (file.filePath==fileName or file.new_filePath==fileName) and file.commit==commit:
                return file
        return None


