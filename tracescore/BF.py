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
            elif line.startswith("R0") or line.startswith("R100"):
                strs = line.split("	")
                if strs[0] > "R090":
                    if strs[1] not in mapping_files:
                        mapping_files[strs[1]] = len(mapping_files)
                    if strs[2] not in mapping_files:
                        mapping_files[strs[2]] = mapping_files[strs[1]]
                else:
                    if strs[1] not in mapping_files:
                        mapping_files[strs[1]] = len(mapping_files)
                    if strs[2] not in mapping_files:
                        mapping_files[strs[2]] = len(mapping_files)
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
    # mapping_files = parser_log(file)
    for issue in test_bugs:
        files = {}
        for i in range(len(issue.artifacts)-1, -1, -1):
            files_set = set(f.new_filePath for f in issue.artifacts[i].files if f.new_filePath!="/dev/null")
            source_len = len(files_set)
            for f in files_set:
                if (f in files.keys()):
                    files[f] = files[f] + issue.artif_sim[i] * issue.artif_sim[i] / source_len
                else:
                    files[f] = issue.artif_sim[i] * issue.artif_sim[i] / source_len

        sorted_files = sorted(files.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        # issue.predict_bf = sorted_files
        # gt = [f.new_filePath for f in issue.files]
        # for x in sorted_files:
        #     if x[0] in gt and x[0] not in issue.source_files:
        #         print()
        issue.predict_bf = [x[0] for x in sorted_files if x[0] in issue.source_files]

        # fileIDs = {}
        # for f,s in files.items():
        #     fid = mapping_files[f]
        #     if fid in fileIDs:
        #         fileIDs[fid] = fileIDs[fid] + s
        #     else:
        #         fileIDs[fid] = s
        #
        # sorted_files2 = sorted(fileIDs.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        # issue.predict_bf_r = [x[0] for x in sorted_files2]

        # mapping_result = {}
        # bluir_score = issue.bluir_score
        # cache_score = issue.cache_score
        # mapping_result.update({k: 0 for k in files})
        # mapping_result.update({k: 0 for k in bluir_score})
        # files = {k:files[k] if k in files else 0 for k in mapping_result}
        # bluir_score = {k:bluir_score[k] if k in bluir_score else 0 for k in mapping_result}
        # cache_score = {k:cache_score[k] if k in cache_score else 0 for k in mapping_result}
        # for f in mapping_result:
        #     score = (0.2 * files.get(f) + 0.8 * bluir_score.get(f)) * 0.7 + cache_score.get(f) * 0.3
        #     mapping_result[f] = score
        # sorted_files = sorted(mapping_result.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        # issue.amalgam = [x[0] for x in sorted_files]
        # issue.simi_score = files
        # issue.cache_score = cache_score
        # issue.bluir_score = bluir_score
        # issue.amalgam_score = mapping_result

    # evaluation
    ground_truth = [set(f.filePath for f in issue.files if f.filePath!="/dev/null") for issue in test_bugs]
    predict_result = [issue.predict_bf for issue in test_bugs]

    index = [i for i in range(len(ground_truth)) if len(ground_truth[i])==0]
    ground_truth = [ground_truth[i] for i in range(len(ground_truth)) if i not in index]
    predict_result = [predict_result[i] for i in range(len(predict_result)) if i not in index]

    evaluation(ground_truth, predict_result)

    # ground_truth = [set(mapping_files[f.new_filePath] for f in issue.files if f.new_filePath!="/dev/null") for issue in test_bugs]
    # predict_result = [issue.predict_bf_r for issue in test_bugs]
    # print(";", end="")
    # index = [i for i in range(len(ground_truth)) if len(ground_truth[i]) == 0]
    # ground_truth = [ground_truth[i] for i in range(len(ground_truth)) if i not in index]
    # evaluation(ground_truth, predict_result)


    # print("amaglam", end=";")
    # predict_result = [issue.amalgam for issue in test_bugs]
    # evaluation(ground_truth, predict_result)

