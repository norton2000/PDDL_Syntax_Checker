from src.main import start

import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--domain", required=True, help="Path to the PDDL domain", metavar="domain_path")
ap.add_argument("-p", "--problem", required=False, help="Path to the PDDL problem", metavar="problem_path")
ap.add_argument('-o', "--optimize", dest='optimization', action='store_true', help='Search for an optimization and do it.')

args = vars(ap.parse_args())


def main(domainFileName, problemFileName, opt):
    start(domainFileName, problemFileName, opt)

if __name__ == '__main__':
    #print(args["optimization"]) Dentro args["optimization"] so se devo ottimizare o no
    main(args['domain'], args['problem'], args["optimization"])