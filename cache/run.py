import datetime
import math
import os

from cache.load_data import read_commits, insert_database, insert_database_vector
from data_processing.database import read_sqlite
from evaluation.evaluation import evaluation

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
    return mapping_files

def versionHistoryCompute(issues, commits_all, days):
    for bug in issues:
        end_date = bug.first_commit_date
        # end_date = datetime.datetime.strptime(bug.fixed_date.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S")
        start_date = end_date - datetime.timedelta(days=days)
        commits = [c for c in commits_all if c.commit_date>start_date and c.commit_date<end_date]
        # print(len(commits))
        rangeTime = days*24*60
        file_score = {} # file_path, score
        for c in commits:
            normalized_t = float((c.commit_date-start_date).total_seconds()/60) / float(rangeTime)
            score = 1/(1+math.exp(-12*normalized_t+12))
            for f in c.files:
                if f in file_score:
                    file_score[f] = file_score[f] + score
                else:
                    file_score[f] = score
        bug.cache_score = file_score

def versionHistoryCompute_vector(issues, commits_all):
    for bug in issues:
        end_date = bug.first_commit_date
        start_date = end_date - datetime.timedelta(days=365)
        commits = [c for c in commits_all if c.commit_date>start_date and c.commit_date<end_date]
        file_score = {}
        # print(len(commits))

        for c in commits:
            range_days = float((end_date-c.commit_date).total_seconds()/86400)
            if range_days<28:
                value = int(range_days)
            else:
                value = int(range_days/7) + 24
            for f in c.files:
                if f in file_score:
                    file_score[f][value] = file_score[f][value] + 1
                else:
                    file_score[f] = [0 for i in range(77)]
                    file_score[f][value] = file_score[f][value] + 1
        bug.cache_score_new = file_score
    return issues

def evaluate(bugs, file_name):
    print(len(bugs), end=";")
    # train_size = int(len(bugReport) * 0.8)
    test_bugs = []

    mapping_files = parser_log(file_name)

    for issue in bugs:
        cache_score = {}
        flag = False
        for k, v in issue.cache_score.items():
            if k not in mapping_files:
                mapping_files[k] = len(mapping_files)
            fid = mapping_files.get(k)
            if fid in cache_score:
                flag=True
                cache_score[fid] = cache_score[fid] + v
                # print()
            else:
                cache_score[fid] = v

        sorted_files = sorted(cache_score.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        issue.predict_bf_r = [x[0] for x in sorted_files]

        sorted_files2 = sorted(issue.cache_score.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        issue.predict_bf = [x[0] for x in sorted_files2]

        if flag==True:
            test_bugs.append(issue)


    ground_truth = [set(f.filePath for f in issue.files if f.filePath != "/dev/null") for issue in test_bugs]
    predict_result = [issue.predict_bf for issue in test_bugs]
    evaluation(ground_truth, predict_result)

    ground_truth = [set(mapping_files[f.filePath] for f in issue.files if f.filePath != "/dev/null") for issue in test_bugs]
    predict_result = [issue.predict_bf_r for issue in test_bugs]
    print(";", end="")
    evaluation(ground_truth, predict_result)


path = "C:/Users/Feifei/dataset/tracescore"
path2 = "C:/Users/Feifei/dataset/issues"
files = ["derby", "drools", "hornetq", "izpack", "keycloak", "log4j2", "railo", "seam2", "teiid", "weld", "wildfly"]
for file in files[:]:
    # file = "wildfly.sqlite3"
    print(file, end=" ")
    filePath = path+"\\"+file + ".sqlite3"
    filePath2 = path2+"\\"+file+".sqlite3"
    issues = read_sqlite(filePath)
    issues = [x for x in issues if x.issue_type == "Bug"]
    # print(len(issues))
    commits = read_commits(filePath2)
    # print(len(commits))
    versionHistoryCompute(issues, commits, 3650)
    commits = []
    evaluate(issues, file)
    # insert_database(filePath, bugs)
    # bugs = versionHistoryCompute_vector(issues, commits) # calculate recent one year, [1d, 2d, 3d, 1w, 2w, 1m, 1y]
    # insert_database_vector(filePath, bugs)

