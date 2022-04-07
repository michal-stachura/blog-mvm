
import logging
import json
import argparse
import os

from app.phase1 import PhaseOne
from app.phase2 import PhaseTwo


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--cvs', type=int, default=10)
parser.add_argument('--details', type=str, default="N", choices=["Y", "N"])
parser.add_argument(
    '--p1_type',
    type=str,
    default="common",
    choices=["common", "multithreading", "multiprocessing"]
)
parser.add_argument(
    '--p2_type',
    type=str,
    default="common",
    choices=["common", "multithreading", "multiprocessing"]
)
parser.add_argument('--p1_max_workers', type=int, default=10)
parser.add_argument('--p2_max_workers', type=int, default=10)

args = parser.parse_args()

p1_max_workers = args.p1_max_workers if args.p1_type != "common" else "Not considered"
p2_max_workers = args.p2_max_workers if args.p2_type != "common" else "Not considered"
logging.info(
    f"######################\nNumber of CV's: {args.cvs}\nTest type:\n  - Phase 1: {args.p1_type}\n  - Phase 2: {args.p2_type}\nDetailed report: {args.details}\nMax workers:\n  - Phase 1: {p1_max_workers}\n  - Phase 2: {p2_max_workers}\n######################")

########################
# Phase 1              #
########################
phase_one = PhaseOne()

if args.p1_type == "common":
    phase_one.common_images_download(args.cvs)
if args.p1_type == "multithreading":
    phase_one.multhreading_images_download(
        args.cvs, max_workers=args.p1_max_workers)
if args.p1_type == "multiprocessing":
    phase_one.multprocessing_images_download(
        args.cvs, max_workers=args.p1_max_workers)
phase_one_duration = phase_one.get_duration()


########################
# Phase 2              #
########################
phase_two = PhaseTwo()

if args.p2_type == "common":
    phase_two.common_cv_generate(args.cvs)
if args.p2_type == "multithreading":
    phase_two.multhreading_cv_generate(args.cvs, args.p2_max_workers)
if args.p2_type == "multiprocessing":
    phase_two.multiprocessing_cv_generate(
        args.cvs, max_workers=args.p2_max_workers)
phase_two_duration = phase_two.get_duration()


########################
# Finall Report        #
########################
logging.info("--- Phase 1 - gathering data ---")
logging.info(f"Average request time: {phase_one.get_avg_time()}")
logging.info(f"Phase 1 took: {phase_one_duration}")
logging.info("\n\n--- Phase 2 - generate PDF ---")
logging.info(f"Average pdf generation time: {phase_two.get_avg_time()}")
logging.info(f"Phase 2 took: {phase_two_duration}")
logging.info(
    f"\n\n--- Summary ---\nWhole process took: {phase_one_duration + phase_two_duration}")

if args.details == "Y":
    logging.info(
        f"\n\n\n--- Details Phase 1 ---\n{json.dumps(phase_one.get_details(), indent=4)}")
    logging.info(
        f"\n\n--- Details Phase 2 ---\n{json.dumps(phase_two.get_details(), indent=4)}")
