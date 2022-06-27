import os
import shutil

user_path = "_User files"
tidy_path = os.path.join(user_path, "papers")  # this is the local folder where tidied papers go
untidy_papers_path = os.path.join(user_path, "untidy papers")  # place untidy IB papers here


class Paper:
    def __init__(self, full_path):
        self.name = None
        self.year = None
        self.month = None
        self.parse_path(full_path)

    def parse_path(self, full_path):
        year_index = full_path.find("20")  # all exam papers for IB CS I have seen are from 2000-2021.
        # this code will stop functioning in 2100, but we should all be living in the metaverse by then.
        self.year = full_path[year_index: year_index + 4]

        if "may" in full_path.lower():
            self.month = "May"
        elif "nov" in full_path.lower():
            self.month = "Nov"

        split_path = full_path.split("\\")
        raw_name = split_path[-1]  # name of the file is the last thing in a file path.
        # Now, all CS papers are named like: "Computer_science_paper_1_SL.pdf"
        # Except, since 2016 or so they used "__", like "Computer_science_paper_1__SL.pdf"
        # Why? Who knows. My "data.csv" file assumes there are only "_", so your papers need to be renamed.
        self.name = raw_name.replace("__", "_")


def get_all_paper_paths(untidy_papers=untidy_papers_path):
    papers = []
    list_dirs = os.walk(untidy_papers)
    for root, dirs, files in list_dirs:
        for f in files:
            full_path = os.path.join(root, f)
            papers.append(full_path)
    return papers


def copy_papers_to_tidy_places(paper_paths):
    for path in paper_paths:
        paper = Paper(path)

        paper_folder = os.path.join(tidy_path, paper.year, paper.month)
        os.makedirs(paper_folder, exist_ok=True)

        new_path = os.path.join(paper_folder, paper.name)
        shutil.copy(path, new_path)
        print("Copied to", new_path)


papers = get_all_paper_paths()
copy_papers_to_tidy_places(papers)
