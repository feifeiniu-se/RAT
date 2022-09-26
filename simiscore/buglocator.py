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
                    # mapping_files[strs[2]] = len(mapping_files) # todo
            elif line.startswith("C0"):
                strs = line.split("	")
                if strs[1] not in mapping_files:
                    mapping_files[strs[1]] = len(mapping_files)
                if strs[2] not in mapping_files:
                    mapping_files[strs[2]] = len(mapping_files)
        line = f.readline()
    return mapping_files

def BF(test_bugs, file):
    # replication of Patrick Mader, only file level
    mapping_files = parser_log(file)
    for issue in test_bugs:
        files = {}
        for i in range(len(issue.artifacts)-1, -1, -1):
            files_set = set(f.new_filePath for f in issue.artifacts[i].files if f.new_filePath!="/dev/null")
            source_len = len(files_set)
            if source_len==0:
                print(issue.artifacts[i].issue_id)
            for f in files_set:
                if (f in files.keys()):
                    files[f] = files[f] + issue.artif_sim[i] / source_len
                else:
                    files[f] = issue.artif_sim[i] / source_len

        sorted_files = sorted(files.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        # issue.predict_bf = [x[0] for x in sorted_files if x[0] in issue.source_files]
        issue.predict_bf = [x[0] for x in sorted_files]

        fileIDs = {}
        for f,s in files.items():
            fid = mapping_files[f]
            if fid in fileIDs:
                fileIDs[fid] = fileIDs[fid] + s
            else:
                fileIDs[fid] = s

        sorted_files2 = sorted(fileIDs.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        issue.predict_bf_r = [x[0] for x in sorted_files2]

    # evaluation
    ground_truth = [set(f.new_filePath for f in issue.files if f.new_filePath!="/dev/null") for issue in test_bugs]
    predict_result = [issue.predict_bf for issue in test_bugs]
    index = [i for i in range(len(ground_truth)) if len(ground_truth[i]) == 0]
    ground_truth = [ground_truth[i] for i in range(len(ground_truth)) if i not in index]
    predict_result = [predict_result[i] for i in range(len(predict_result)) if i not in index]
    evaluation(ground_truth, predict_result)

    # ground_truth = [set(mapping_files[f.filePath] for f in issue.files if f.filePath!="/dev/null") for issue in test_bugs]
    # predict_result = [issue.predict_bf_r for issue in test_bugs]
    # print(";", end="")
    # evaluation(ground_truth, predict_result)


