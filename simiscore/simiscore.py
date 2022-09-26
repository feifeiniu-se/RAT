import sqlite3
import os

from data_processing.database import read_sqlite, read_cha, read_files
import datetime
from sklearn.metrics.pairwise import cosine_similarity

from tracescore.BF_R import BF_R
from buglocator import BF
from buglocator_R import BF_R


def calculate(issues):
    bugReport = [x for x in issues if x.issue_type == "Bug"]
    print(len(bugReport), end=";")
    train_size = int(len(bugReport) * 0.8)
    test_bugs = bugReport[:]
    # test_bugs = bugReport[train_size:]

    # 计算相似性
    for i in range(len(test_bugs)):
        issue = test_bugs[i]  # 当前的issue
        # # 找到list中符合条件的第一个 然后截取第一个到当前issue的前一个，都是within365的 并且根据sourceFile的数量过滤
        index = bugReport.index(issue)
        within365 = bugReport[:index]
        within365 = [x for x in within365 if (issue.first_commit_date>x.fixed_date)]
        # within365 = test_bugs[:i]
        issue.artifacts = [x for x in within365] #不把修改文件过多的requirement和bug report过滤掉，会有些许的提升，因此此处不过滤
        issue.artif_sim = [cosine_similarity(issue.tfidf, x.tfidf) for x in issue.artifacts]
        issue.artif_sim = [float(x[0][0]) for x in issue.artif_sim]

    BF(test_bugs, file)#todo
    BF_R(test_bugs)


path = "C:/Users/Feifei/dataset/tracescore"
files = os.listdir(path)
# files = ["derby", "drools", "izpack", "log4j2", "railo", "seam2"]
files = ["derby", "drools", "hornetq", "izpack", "keycloak", "log4j2", "railo", "seam2", "teiid", "weld", "wildfly"]
print(";MAP;MRR;Top 1;Top 5;Top 10;P@1;P@5;P@10;R@1;R@5;R@10;Top 1%; Top 2%;Top 5%;Top 10%;Top 20%;Top 50%;R@1%;R@2%;R@5%;R@10%;R@20%;R@50%")
# print('issue_id;GT;Prediction;TP;TP/GT;TP/Prediction;Position;Days')
# for file in files:
for file in files[:]:
    # file = "wildfly.sqlite3"
    print(file, end=" ")
    filePath = path+"\\"+file + ".sqlite3"
    issues = read_sqlite(filePath)
    calculate(issues)
