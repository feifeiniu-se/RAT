# -*- coding:utf-8 -*-
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
import datetime
import numpy as np

# from cha.CodeBlock import CodeBlock
# from cha.CodeBlockTime import CodeBlockTime
from data_processing.File import File
from data_processing.Issue import Issue
from data_processing.Method import Method
from sentence_transformers import SentenceTransformer

def read_files(path): #读取filename,codeblockid的对应关系
    connection = sqlite3.connect(path)
    connection.text_factory = str
    cursor = connection.cursor()
    mapping_files = {}# file_name, codeBlockID
    cursor.execute("select * from Files")
    result = cursor.fetchall()
    for tmp in result:
        mapping_files[tmp[0]] = tmp[1]
    return mapping_files

def read_text_sqlite(issues, path):
    issue_map = {}
    connection = sqlite3.connect(path)
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute("select issue_id, summary, description from issue")
    result = cursor.fetchall()
    for tmp in result:
        issue_map[tmp[0]] = tmp

    for issue in issues:
        issue.original_summary = issue_map[issue.issue_id][1]
        issue.original_description = issue_map[issue.issue_id][2]
    return issues

def read_cha(path):
    connection = sqlite3.connect(path)
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute("select * from CodeBlock")
    result = cursor.fetchall()
    history = {}
    codeBlockTime = {}
    for tmp in result:
        history[tmp[0]] = CodeBlock(tmp)

    cursor.execute("select * from CodeBlockTime")
    result = cursor.fetchall()
    for tmp in result:
        cbt = CodeBlockTime(tmp, history)
        history[tmp[5]].History.append(cbt)
        codeBlockTime[cbt.id] = cbt

    cursor.execute("select * from CodeBlockTime_link where link_type=1")
    result = cursor.fetchall()
    for tmp in result:
        codeBlockTime[tmp[0]].derivee.add(codeBlockTime[tmp[1]].owner)
        codeBlockTime[tmp[1]].deriver.add(codeBlockTime[tmp[0]].owner)

    return history


def read_sqlite(path):
    issue_map = {} # <issue_id, issue>
    connection = sqlite3.connect(path)
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute(
        "select issue_id, issue_type, fixed_date, summary_stemmed, description_stemmed, created_date from issue where issue_id in (select issue_id from v_issue_statistic) order by fixed_date")
    result = cursor.fetchall()

    issues, texts = [], []
    for tmp in result:
        new_issue = Issue(tmp)
        issues.append(new_issue)
        issue_map[new_issue.issue_id] = new_issue

    # # tfidf值
    texts = [x.summary_stem+" "+x.description_stem for x in issues if x.issue_type=="Bug"]
    vectorizer = TfidfVectorizer(encoding='utf-8')
    vectorizer.fit(texts)
    for issue in issues:
        issue.tfidf = vectorizer.transform([issue.summary_stem + " " + issue.description_stem]).toarray()[0:1]
    # bert
    # model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')
    # for issue in issues:
    #     issue.tfidf = model.encode([issue.summary_stem+" "+issue.description_stem])


    # # 读取files
    # cursor.execute("select commit_hash, file_path, sum_added_lines, sum_removed_lines, codeBlockID, issue_id from v_code_change where codeBlockID!=0")
    # cursor.execute("select commit_hash, new_path, last_modify_hash, change_type, new_codeBlockID, last_modify_date, issue_id, committed_date, commit_hash from v_code_change_file where new_path!='/dev/null' and new_codeBlockID!=0")# 新的数据集 经验证完全一致
    #采用new_filePath 用于训练，采用filePath用于评估
    cursor.execute("select commit_hash, file_path, last_modify_hash, change_type, codeBlockID, last_modify_date, issue_id, committed_date, commit_hash, new_path, new_codeBlockID from v_code_change_file")
    # 更新ground truth 为只包含delete，modify的文件，不包含add的文件
    # cursor.execute("select commit_hash, file_path, last_modify_hash, change_type, codeBlockID, last_modify_date, issue_id, committed_date, commit_hash from v_code_change_file where file_path!='/dev/null' and codeBlockID!=0")

    result = cursor.fetchall()
    for tmp in result:
        issue = issue_map[tmp[6]]
        issue.files.append(File(tmp))


        # 增加第一次commit的时间 以及首次commit的hash
        if datetime.datetime.strptime(str(issue.first_commit_date), "%Y-%m-%d %H:%M:%S") > datetime.datetime.strptime(tmp[7].replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S"):
            issue.first_commit_date = datetime.datetime.strptime(tmp[7].replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S")
            issue.first_commit_hash = set()
            issue.first_commit_hash.add(tmp[8])
        if datetime.datetime.strptime(str(issue.first_commit_date), "%Y-%m-%d %H:%M:%S") == datetime.datetime.strptime(tmp[7].replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S"):
            issue.first_commit_hash.add(tmp[8])

    #根据第一次提交的时间进行排序
    # issues.sort(key=lambda x: datetime.datetime.strptime(str(x.first_commit_date), "%Y-%m-%d %H:%M:%S")) #根据第一个提交的时间重新排序 todo
    # print()

    # # # 读取methods
    # cursor.execute(
    #     "select commit_hash, file_path, method_name, type, startLine, endLine, addLineNum, deleteLineNum, codeBlockID, issue_id from v_code_change_method where codeBlockID!=0 ")
    # result = cursor.fetchall()
    # for tmp in result:
    #     issue = issue_map[tmp[9]]
    #     file = issue.findFile(tmp[1], tmp[0])
    #     if file is not None:
    #         file.methods.add(Method(tmp))
    #
    # #  更新每个file，如果file中没有方法，就加入file name
    # for issue in issues:
    #     for file in issue.files:
    #         if len(file.methods)==0:
    #             if file.classBlockID is not None:
    #                 file.methods.add(Method(("", "", file.filePath[:-5].replace("/", ".")+".NonMethodPart:nonMethodPart", "", "", "", "", "", file.classBlockID)))
    #             if file.new_classBlockID is not None:
    #                 file.methods.add(Method(("", "", file.new_filePath[:-5].replace("/", ".")+".NonMethodPart:nonMethodPart", "", "", "", "", "", file.new_classBlockID)))


    # 读取每个commit所对应的source code list
    map_file = {} # commit_hash, source code files
    connection.text_factory = str
    cursor = connection.cursor()
    cursor.execute("select * from Commit_files_link")
    result = cursor.fetchall()
    for tmp in result:
        map_file[tmp[0]] = tmp[1]

    # # 读取每个issue中包含的commit_hash,并设置source_files 为所有commit_hash的souce code的并集
    # cursor.execute("select issue_id, commit_hash as b from v_code_change group by issue_id, commit_hash")
    # result = cursor.fetchall()
    # for tmp in result:
    #     files = map_file[tmp[1]].replace("[","").replace("]","").split(", ")
    #     issue_map[tmp[0]].source_files.update(tuple(files))

    # 此处设置source code为首次提交的commit的source code，注意首次提交的可能不止一个，可能有多个commit，有相同的commit_date
    for issue in issues:
        for hash in issue.first_commit_hash:
            files = map_file[hash].replace("[","").replace("]","").split(", ")
            issue.source_files.update(tuple(files))


    mapping_files = {}# file_name, codeBlockID
    cursor.execute("select * from Files")
    result = cursor.fetchall()
    for tmp in result:
        mapping_files[tmp[0]] = tmp[1]

    # 更新issue.source_files_ID
    for issue in issues:
        issue.source_files_ID = set([mapping_files[f] for f in issue.source_files if f in mapping_files])

    # cursor.execute("select * from Cache")
    # result = cursor.fetchall()
    # # print(len(result))
    # for tmp in result:
    #     issue = issue_map[tmp[0]]
    #     # print(issue.issue_id)
    #     issue_map[tmp[0]].cache_score[tmp[1]] = float(tmp[2])

    # # 读取cache和bluir的结果
    # connection.text_factory = str
    # cursor = connection.cursor()
    # cursor.execute("select * from Cache where issue_id in (select issue_id from v_issue_statistic)")
    # result = cursor.fetchall()
    # for tmp in result:
    #     issue = issue_map[tmp[0]]
    #     issue.cache_score[tmp[1]] = float(tmp[2])
    #     # print(tmp)
    #     if tmp[1] in mapping_files:
    #         file_id = mapping_files[tmp[1]]
    #         if file_id in issue.cache_id_score:
    #             issue.cache_id_score[file_id] = issue.cache_id_score[file_id] + float(tmp[2])
    #         else:
    #             issue.cache_id_score[file_id] = float(tmp[2])

    # cursor.execute("select * from Cache_new where issue_id in (select issue_id from v_issue_statistic)")
    # result = cursor.fetchall()
    # for tmp in result:
    #     issue = issue_map[tmp[0]]
    #     issue.cache_score_new[tmp[1]] = list(map(int, tmp[2:]))
    #     if tmp[1] in mapping_files:
    #         file_id = mapping_files[tmp[1]]
    #         if file_id in issue.cache_id_score_new:
    #             issue.cache_id_score_new[file_id] = np.array(issue.cache_id_score_new[file_id]) + np.array(list(map(int, tmp[2:])))
    #         else:
    #             issue.cache_id_score_new[file_id] = list(map(int, tmp[2:]))

    # cursor.execute("select * from Bluir where issue_id in (select issue_id from v_issue_statistic)")
    # result = cursor.fetchall()
    # for tmp in result:
    #     issue = issue_map[tmp[0]]
    #     issue.bluir_score[tmp[1]] = float(tmp[2])
    #     if mapping_files[tmp[1]] in issue.bluir_id_score:
    #         issue.bluir_id_score[mapping_files[tmp[1]]] = max(float(tmp[2]), issue.bluir_id_score[mapping_files[tmp[1]]])
    #     else:
    #         issue.bluir_id_score[mapping_files[tmp[1]]] = float(tmp[2])

    # cursor.execute("select * from SimiScore")
    # result = cursor.fetchall()
    # for tmp in result:
    #     issue = issue_map[tmp[0]]
    #     issue.simi_id_score[tmp[1]] = float(tmp[2])


    cursor.close()
    connection.close()

    # filepath2 = path.replace("tracescore", "issues")
    # commits = test.read_commits_all(filepath2)
    # for commit in commits:
    #     commit.files=set(mapping_files.get(k) for k in commit.files)

    return issues
    # return train_issue, test_issue