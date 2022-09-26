# what's the performance of only using cache
import os

from cache.load_data import load_issues
from evaluation.evaluation import evaluation
import re

def getUniqueClassName(fileName):
    strs = re.split('\\|.|/', fileName)
    ids = []
    for i in range(len(strs)-1, -1, -1):
        if strs[i]=="org":
            break
        ids.append(strs[i])
    result = ""
    for i in range(len(ids)-1, -1, -1):
        result = result + ids[i]+"."
    if "org" in fileName:
        result = "org."+result
    return result[:-1]

def calculate(issues):
    bugReport = [x for x in issues if x.issue_type == "Bug"]
    print(len(bugReport), end=";")
    test_bugs = bugReport[:]

    for issue in test_bugs:
        cache_score = {}
        for k,v in issue.cache_score.items():
            k = getUniqueClassName(k)
            if k in cache_score:
                cache_score[k] = cache_score[k] + v
            else:
                cache_score[k] = v

        sorted_files = sorted(cache_score.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        issue.predict_bf = [x[0] for x in sorted_files]

        # cache_id_score = issue.cache_id_score
        # sorted_id = sorted(cache_id_score.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        # issue.predict_bf_r = [x[0] for x in sorted_id if x[0] in issue.source_files_ID]
    ground_truth = [set(getUniqueClassName(f.filePath) for f in issue.files if f.filePath!="/dev/null") for issue in test_bugs]
    predict_result = [issue.predict_bf for issue in test_bugs]
    evaluation(ground_truth, predict_result)
    # print(";", end="")
    # ground_truth = [set(f.classBlockID for f in issue.files if f.classBlockID is not None) for issue in test_bugs]
    # predict_result = [issue.predict_bf_r for issue in test_bugs]
    # evaluation(ground_truth, predict_result)

path = "C:/Users/Feifei/dataset/tracescore"
files = os.listdir(path)
# files = ["derby", "drools", "izpack", "log4j2", "railo", "seam2"]
files = ["derby", "drools", "hornetq", "izpack", "keycloak", "log4j2", "railo", "seam2", "teiid", "weld", "wildfly"]
print(";MAP;MRR;Top 1;Top 5;Top 10;P@1;P@5;P@10;R@1;R@5;R@10;Top 1%; Top 2%;Top 5%;Top 10%;Top 20%;Top 50%;R@1%;R@2%;R@5%;R@10%;R@20%;R@50%")
for file in files[:]:
    # file = "wildfly.sqlite3"
    print(file, end=" ")
    filePath = path+"\\"+file + ".sqlite3"
    issues = load_issues(filePath) # only read cache score, cache_id score, ground truth
    calculate(issues)