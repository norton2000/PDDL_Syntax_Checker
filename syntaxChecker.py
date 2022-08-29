from src.main import start

import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--domain", required=False, help="Path to the PDDL domain", metavar="domain_path")
ap.add_argument("-p", "--problem", required=False, help="Path to the PDDL problem", metavar="problem_path")
args = vars(ap.parse_args())


def main(domainFileName, problemFileName):
    start(domainFileName, problemFileName)

if __name__ == '__main__':
    main(args['domain'], args['problem'])