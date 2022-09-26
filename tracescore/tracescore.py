import sqlite3
import os

from data_processing.database import read_sqlite, read_cha, read_files
import datetime
from sklearn.metrics.pairwise import cosine_similarity

from BF_R import BF_R
from BF import BF

PM = False
# todo
if PM == True:
    big_bug_req_filter = True
    whole_history = False
else:
    big_bug_req_filter = False
    whole_history = True


def filter_similarity(test_bugs, threshold):
    for issue in test_bugs:
        index = [i for i in range(len(issue.artif_sim)) if issue.artif_sim[i]>threshold]
        issue.artif_sim = [issue.artif_sim[i] for i in index]
        issue.artifacts = [issue.artifacts[i] for i in index]


def motivating_example(test_bugs, history):
    cases = {}
    mapping_file = read_files(filePath)
    for issue in test_bugs:
        x1 = issue.predict_bf
        x2 = issue.predict_bf_r
        gt_file = set(f.new_filePath for f in issue.files if f.new_filePath!="/dev/null")
        gt_id = set(f.classBlockID for f in issue.files if f.classBlockID is not None)
        files = {}
        for f in gt_file:
            if f not in x1[:10]:
                if mapping_file.get(f) in x2[:1] and mapping_file.get(f) in gt_id:
                    tmp = []
                    for i in range(len(x1)):
                        if mapping_file[x1[i]]==mapping_file.get(f):
                            tmp.append(i)
                    files[f] = tmp
        cases[issue] = files
    # for k,v in cases.items():
    #     if 1 in k.artif_sim and len(v)>0:
    #         for i in range(len(k.artifacts)):
    #             if k.artif_sim[i] == 1:
    #                 for f in v:
    #                     if f in [f.new_filePath for f in k.artifacts[i].files if f.new_filePath!="/dev/null"]:
    #                         print("OK")


    print("OK")





def calculate(issues, filePath):
    bugReport = [x for x in issues if x.issue_type == "Bug"]
    # print(len(bugReport), end=";")
    print(len(bugReport), end=";")
    test_bugs = bugReport[:]

    # 计算相似性
    for i in range(len(test_bugs)):
        issue = test_bugs[i]  # 当前的issue
        index = issues.index(issue)
        # # 找到list中符合条件的第一个 然后截取第一个到当前issue的前一个，都是within365的 并且根据sourceFile的数量过滤
        if whole_history==True:
            within365 = issues[:index]
            within365 = [x for x in within365 if (issue.first_commit_date>x.fixed_date)]
        else:
            within365 = [x for x in issues[:index] if (issue.first_commit_date - x.fixed_date).days <= 365 and issue.first_commit_date>x.fixed_date]
            # within365 = [x for x in issues[:index] if (issue.created_date - x.fixed_date).days <= 365 and issue.created_date>x.fixed_date]
        if big_bug_req_filter==True:
            issue.artifacts = [x for x in within365 if (x.issue_type == "Bug" and len(set(f.filePath for f in x.files)) <= 10) or (x.issue_type != "Bug" and len(set(f.filePath for f in x.files)) <= 20)]
        else:
            issue.artifacts = [x for x in within365] #不把修改文件过多的requirement和bug report过滤掉，会有些许的提升，因此此处不过滤
        issue.artif_sim = [cosine_similarity(issue.tfidf, x.tfidf) for x in issue.artifacts]
        issue.artif_sim = [float(x[0][0]) for x in issue.artif_sim]

    # 数据库读取issue_link 如果两个issue之间存在连接 将权重设为1
    connection = sqlite3.connect(filePath)
    connection.text_factory = str
    cursor = connection.cursor()

    issue_mapping = {issue.issue_id:issue for issue in test_bugs}
    link_mapping = {} # issue_id, set()
    cursor.execute("select * from issue_link")
    result = cursor.fetchall()
    for tmp in result:
        if tmp[0] in link_mapping:
            link_mapping[tmp[0]].add(tmp[1])
        else:
            link_mapping[tmp[0]] = set()
            link_mapping[tmp[0]].add(tmp[1])
        if tmp[1] in link_mapping:
            link_mapping[tmp[1]].add(tmp[0])
        else:
            link_mapping[tmp[1]] = set()
            link_mapping[tmp[1]].add(tmp[0])
    for id, links in link_mapping.items():
        issue = issue_mapping.get(id)
        if issue is not None:
            # 遍历所有的issue.artifacts，如果二者之间存在关系 就更新权重为1
            for i in range(0, len(issue.artifacts)):
                if issue.artifacts[i].issue_id in links:
                    issue.artif_sim[i] = 1.0

    #
    # # analyze_result(test_bugs)

    BF(test_bugs, file)#todo

    print("", end=";")
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
    calculate(issues, filePath)
