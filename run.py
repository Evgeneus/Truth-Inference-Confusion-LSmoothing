__author__ = 'JasonLee'

import commands
import sys
import random
import pandas as pd

# # Read Args
# if len(sys.argv) != 4 and len(sys.argv) != 5:
#     print "usage: %s %s %s %s %s" % \
#           (sys.argv[0], "method_file", "answer_file", "result_file", "(decision-making/single-label/continuous)")
#     exit(0)
#
# method_file, answer_file, result_file = sys.argv[1:4]

#
# if len(sys.argv) == 5:
#     tasktype = sys.argv[4]
#     assert tasktype in ['decision-making', 'single-label', 'continuous']
#
# if tasktype in ['decision-making', 'single-label']:
#     tasktype = 'categorical'

if __name__ == "__main__":
    method = "GLAD"

    if method == "MV":
        method_file = "methods/c_MV/method.py"
    elif method == "DS":
        method_file = "methods/c_EM/method.py"
    elif method == "LFC":
        method_file = "methods/l_LFCbinary/method.py"
    elif method == "GLAD":
        method_file = "methods/c_GLAD/method.py"

    answer_file = "data-soft-target/15. Wiki-attack/crowd_answers/crowd_answers_train_all.csv"
    result_file = "data-soft-target/15. Wiki-attack/agg_train/train_all_{}.csv".format(method)

    tasktype = "categorical"
    output = commands.getoutput("python \"" + method_file + "\" \"" + answer_file + "\" " + tasktype).split('\n')[-1]
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

        e2truth[int(e)] = int(truth)

    # with open(result_file, "w") as f:
    #     f.write("rev_id,label\n")
    #     for e in e2truth:
    #         f.write(str(e) + "," + str(e2truth[e]) + "\n")
    #
    df = pd.read_csv("data-soft-target/15. Wiki-attack/train.csv")
    gold_values = df['label'].values
    with open(result_file, "w") as f:
        header = "text_id,label,{}_label".format(method)
        for c in range(num_classes):
            header += ",{}conf{}".format(method, c)
        header += "\n"
        f.write(header)

        # for e in e2truth:
        for q in questions:
            line = "{},{},{}".format(q, gold_values[q], e2truth[q])
            for c in range(num_classes):
                line += ",{}".format(float(e2lpd[str(q)][str(c)]))

            f.write(line + "\n")

    print "Finished!, ", method_file
