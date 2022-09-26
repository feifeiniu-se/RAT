from evaluation.evaluation import evaluation
# from utils import time_span_analyze


def BF_R(test_bugs):
    # bug report - file + refactoring BF_R
    for issue in test_bugs:
        classBlocks = {}
        for i in range(len(issue.artifacts)-1, -1, -1):
            files_set = set(f.new_classBlockID for f in issue.artifacts[i].files if f.new_classBlockID is not None)
            source_len = len(files_set)
            for f in files_set:
                if(f in classBlocks.keys()):
                    classBlocks[f] = classBlocks[f] + issue.artif_sim[i] * issue.artif_sim[i] / source_len
                else:
                    classBlocks[f] = issue.artif_sim[i] * issue.artif_sim[i] / source_len

        sorted_classBlocks = sorted(classBlocks.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        issue.predict_bf_r = [x[0] for x in sorted_classBlocks]

    ground_truth = [set(f.classBlockID for f in issue.files if f.classBlockID is not None) for issue in test_bugs]
    predict_result = [issue.predict_bf_r for issue in test_bugs]

    index = [i for i in range(len(ground_truth)) if len(ground_truth[i]) == 0]
    ground_truth = [ground_truth[i] for i in range(len(ground_truth)) if i not in index]
    predict_result = [predict_result[i] for i in range(len(predict_result)) if i not in index]

    evaluation(ground_truth, predict_result)