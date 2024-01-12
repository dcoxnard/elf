import csv
import argparse

from round import Round


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    help = """
    Path to file to initialize round from.  File must be CSV format with the exact schema specified in round.import_from_previous_round.
    """.strip()
    parser.add_argument("-f", "--file", required=True, type=str, help=help)

    args = parser.parse_args()

    file = args.file
    with open(file, "r") as f_obj:
        reader = csv.reader(f_obj)
        data = [row for row in reader]

    round = Round()
    round.import_from_previous_round(data)
