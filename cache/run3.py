import datetime
import math
import os
import sqlite3

from cache.load_data import read_commits, insert_database, insert_database_vector
from data_processing.database import read_sqlite
from evaluation.evaluation import evaluation
import numpy as np

# 严格查询issue的GT中文件曾经被重命名过
# bug prediction in google  Does Bug Prediction Support Human Developers?
# Findings from a Google Case Study
def parser_log(file):
    mapping_files = {}
    log_file = "C:/Users/Feifei/dataset/projects/logs/" + file + "_log.txt"
    f = open(log_file, encoding="utf8")
    line = f.readline()
    while line:
        line = line.replace("\n", "")
        if line.endswith(".java"):
            if line.startswith("M	") or line.startswith("A	") or line.startswith("D	"):
                strs = line.split("	")
                if strs[1] not in mapping_files:
                    mapping_files[strs[1]] = len(mapping_files)
                    # print()
            elif line.startswith("R0") or line.startswith("R100	"):
                strs = line.split("	")
                if strs[1] not in mapping_files:
                    mapping_files[strs[1]] = len(mapping_files)
                mapping_files[strs[2]] = mapping_files[strs[1]]
            elif line.startswith("C0"):
                strs = line.split("	")
                if strs[1] not in mapping_files:
                    mapping_files[strs[1]] = len(mapping_files)
                if strs[2] not in mapping_files:
                    mapping_files[strs[2]] = len(mapping_files)
        line = f.readline()
    database = "C:/Users/Feifei/dataset/tracescore/" + file + ".sqlite3"
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("select * from Files")
    result = cursor.fetchall()
    for tmp in result:
        mapping_files[tmp[0]] = tmp[1]
    return mapping_files

def loadFileCommitHistory(commits):
    commits.sort(key=lambda x:x.commit_date)
    fileHistories = {}
    for commit in commits:
        for f in commit.files:
            if f in fileHistories:
                fileHistories.get(f).append(commit)
            else:
                fileHistories[f] = []
                fileHistories[f].append(commit)

    return fileHistories

def isBugFixing(message):
    message = message.lower()
    if "fix" in message or "bug" in message or file+"-" in message:
        return True
    return False

def versionHistoryCompute(issues, fileHistories):
    for bug in issues:
        end_date = bug.first_commit_date
        file_score = {} # filePath:score
        for f,v in fileHistories.items():
            v.sort(key=lambda x: x.commit_date)
            start_date = v[0].commit_date
            v = [commit for commit in v if isBugFixing(commit.message) and commit.commit_date<end_date]
            if len(v)>0:
                score = 0.0
                rangeTime = float((end_date-start_date).total_seconds()/60)
                for commit in v:
                    normalized_t = float((commit.commit_date-start_date).total_seconds()/60) / rangeTime
                    # print(normalized_t)
                    score = score + float(1/(1+np.exp(-12*normalized_t+12)))
                if score>0.0:
                    file_score[f] = score
        bug.cache_score = file_score

def versionHistoryCompute2(issues, fileHistories):
    test_set = set()
    for bug in issues[:]:
        end_date = bug.created_date
        file_score = {} # filePath:score
        for f,v in fileHistories.items():
            v.sort(key=lambda x: x.commit_date)
            start_date = v[0].commit_date
            v = [commit for commit in v if isBugFixing(commit.message) and commit.commit_date<end_date]
            print(len(v))
            # names = set(file_mapping[f] for x in v for f in x.files)
            if f in set(x.filePath for x in issue.files):
                print(f)
                names = set(fp for x in v for fp in x.files if file_mapping[fp]==f)
                print(names)
                if len(names)>0:
                    test_set.add(issue.issue_id)
            if len(v)>0:
                score = 0.0
                rangeTime = float((end_date-start_date).total_seconds()/60)
                for commit in v:
                    normalized_t = float((commit.commit_date-start_date).total_seconds()/60) / rangeTime
                    # print(normalized_t)
                    score = score + float(1/(1+np.exp(-12*normalized_t+12)))
                if score>0.0:
                    file_score[f] = score
        bug.bluir_score = file_score
    return test_set


def evaluate(bugs):
    print(len(bugs), end=";")
    # train_size = int(len(bugReport) * 0.8)
    test_bugs = bugs[:]

    for issue in test_bugs:
        sorted_files2 = sorted(issue.cache_score.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        issue.predict_bf = [x[0] for x in sorted_files2 if x[0] in issue.source_files]

    ground_truth = [set(f.filePath for f in issue.files if f.filePath != "/dev/null" and f.filePath is not None) for issue in test_bugs]
    predict_result = [issue.predict_bf for issue in test_bugs]

    index = [i for i in range(len(ground_truth)) if len(ground_truth[i]) == 0]
    ground_truth = [ground_truth[i] for i in range(len(ground_truth)) if i not in index]
    predict_result = [predict_result[i] for i in range(len(predict_result)) if i not in index]

    evaluation(ground_truth, predict_result)

def evaluate2(bugs):
    print(len(bugs), end=";")
    # train_size = int(len(bugReport) * 0.8)
    test_bugs = bugs[:]

    for issue in test_bugs:
        sorted_files2 = sorted(issue.cache_score.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        issue.predict_bf = [x[0] for x in sorted_files2 if x[0] in issue.source_files]

        sorted_files3 = sorted(issue.bluir_score.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        issue.predict_bf_r = [x[0] for x in sorted_files3 if x[0] in issue.source_files]


    ground_truth = [set(f.filePath for f in issue.files if f.filePath != "/dev/null" and f.filePath is not None) for issue in test_bugs if issue.issue_type=="Bug"]
    predict_result = [issue.predict_bf for issue in test_bugs if issue.issue_type=="Bug"]

    index = [i for i in range(len(ground_truth)) if len(ground_truth[i]) == 0]
    ground_truth = [ground_truth[i] for i in range(len(ground_truth)) if i not in index]
    predict_result = [predict_result[i] for i in range(len(predict_result)) if i not in index]
    evaluation(ground_truth, predict_result)




path = "C:/Users/Feifei/dataset/tracescore"
path2 = "C:/Users/Feifei/dataset/issues"
files = ["derby", "drools", "hornetq", "izpack", "keycloak", "log4j2", "railo", "seam2", "teiid", "weld", "wildfly"]
test_set = set()

for file in files[2:]:
    # file = "wildfly.sqlite3"
    print(file, end=" ")
    filePath = path+"\\"+file + ".sqlite3"
    filePath2 = path2+"\\"+file+".sqlite3"
    issues = read_sqlite(filePath)
    issues = [x for x in issues if x.issue_type == "Bug"]
    # print(len(issues))
    commits = read_commits(filePath2)
    file_history = loadFileCommitHistory(commits) # {filePath: file commit history}
    versionHistoryCompute(issues, file_history)
    commits = []
    # evaluate(issues)

    # convert all file_path to fid
    file_mapping = parser_log(file)

    file_history_ = {}
    for f,v in file_history.items():
        if f not in file_mapping:
            file_mapping[f] = len(file_mapping)
        fid = file_mapping[f]
        if fid in file_history_:
            file_history_[fid].extend(v)
        else:
            file_history_[fid] = v
    for issue in issues:
        source_files = [file_mapping[f] for f in issue.source_files]
        issue.source_files = source_files
        for i in range(len(issue.files)):
            if issue.files[i].filePath != "/dev/null":
                issue.files[i].filePath = file_mapping[issue.files[i].filePath]


    test_set = versionHistoryCompute2(issues, file_history_)
    print(test_set)
    # print(";")
    evaluate2(issues)


