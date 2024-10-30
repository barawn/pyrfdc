import pickle
import json
import sys
import os

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("syntax: make_paramfile <input.xci> <output.pkl>")
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        print("make_paramfile: ", sys.argv[1], "is not a file")
        sys.exit(1)
    with open(sys.argv[1], "r") as f:
        data = json.load(f)
        modelParams = data['ip_inst']['parameters']['model_parameters']
    with open(sys.argv[2], "wb") as f:
        pickle.dump(modelParams, f)
    print("make_paramfile: extracted model parameters from",
          sys.argv[1], "to", sys.argv[2])
