import commands
import random
import pandas as pd
import numpy as np


if __name__ == "__main__":
    methods_list = ["MV", "LFC", "CRH", "ZN", "CATD"]
    # answer_file = "datasets/faces/faces_all_ans_"
    answer_file = "datasets/faces/faces_all_improved_ans_"
    gt_file = "datasets/faces/faces_all_gold.csv"
    data_res = []

    for method in methods_list:
        print(method, answer_file)
        if method == "MV":
            method_file = "methods/c_MV/method.py"
        elif method == "DS":
            method_file = "methods/c_EM/method.py"
        elif method == "LFC":
            method_file = "methods/l_LFCmulti/method.py"
        elif method == "GLAD":
            method_file = "methods/c_GLAD/method.py"
        elif method == "CRH":
            method_file = "methods/c_PM-CRH/method.py"
        elif method == "ZN":
            method_file = "methods/l_ZenCrowd/method.py"
        elif method == "CATD":
            method_file = "methods/c_CATD/method.py"

        num_repetitions = 28
        accuracy_list = []
        for run in range(num_repetitions):
            print (run)
            answer_file_ = answer_file + "v{}.csv".format(run+1)
            tasktype = "categorical"
            output = commands.getoutput("python \"" + method_file + "\" \"" + answer_file_ + "\" " + tasktype).split('\n')[-1]
            e2lpd = eval(output)
            num_classes = len(e2lpd[e2lpd.keys()[0]])
            questions = sorted([int(i) for i in e2lpd.keys()])

            e2truth = {}
            for e in e2lpd:
                if type(e2lpd[e]) == type({}):
                    temp = 0
                    for label in e2lpd[e]:
                        if temp < e2lpd[e][label]:
                            temp = e2lpd[e][label]

                    candidate = []

                    for label in e2lpd[e]:
                        if temp == e2lpd[e][label]:
                            candidate.append(label)

                    truth = random.choice(candidate)

                else:
                    truth = e2lpd[e]

                e2truth[e] = truth

            # evaluation
            if "_improved" in answer_file_:
                answer_file_ = answer_file_.replace("_improved", "")
            df_ = pd.read_csv(answer_file_)
            df_['question_ID'] = df_['question_ID'].astype(str)

            df_gt = pd.read_csv(gt_file)
            df_gt['question_ID'] = df_gt['question_ID'].astype(str)
            num_correct = 0
            num_with_conflicts = 0.
            for _, row in df_gt.iterrows():
                obj_id = row['question_ID']
                num_unique_ans = df_[df_['question_ID'] == obj_id].answer.unique().shape[0]
                if num_unique_ans == 1:
                    continue
                gold_val = row['gold_label']
                agg_val = e2truth[obj_id]
                num_with_conflicts += 1
                if agg_val == gold_val:
                    num_correct += 1.
            # print num_with_conflicts
            accuracy = num_correct / num_with_conflicts
            accuracy_list.append(accuracy)

        accuracy_mean = np.mean(accuracy_list)
        accuracy_std = np.std(accuracy_list)
        if "_improved" in answer_file:
            method += "_improved"
        data_res.append((method, round(accuracy_mean, 3), round(accuracy_std, 3)))

        print ("------------------")
        print ("Dataset: {}".format(answer_file))
        print ("Method: {}".format(method))
        print ("*Accuracy: {:1.4} +- {:1.3}*".format(accuracy_mean, accuracy_std))
        print "Finished!, ", method_file
        print ("------------------")

    pd.DataFrame(data_res, columns=["method", "accuracy-mean", "accuracy-std"])\
        .to_csv(answer_file[:-4] + "results.csv", index=False)
