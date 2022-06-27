from PIL import Image
import pandas as pd
from math import sqrt
import os

from pdf2image import convert_from_path  # library needed to convert pdf to images
from pdf2image.exceptions import PDFPageCountError

# the pdf2image library depends on poppler binary being installed.
poppler_path = r"poppler/Library/bin"  # I have it near the Python file. Change path as appropriate.

user_path = "_User files"
papers_path = os.path.join(user_path, "papers")  # this is the local folder where tidied papers go
image_path = os.path.join(user_path, "images")  # this is the local folder where clipped images go for each paper

A4_h_to_w_ratio = sqrt(2)
page_header = 72  # pixels - ballpark
page_footer = 200  # pixels - ballpark
question_buffer = 30  # pixels - ballpark, looks nice

left_column_margin = 0.12  # proportional boundary from left edge to question body - quite precise


def load_data_from_csv(data_path="data.csv"):
    # default location of the file is next to this program as "data.csv". You can specify a different path.
    question_df = pd.read_csv(data_path)
    return question_df


def hash_paper_address(paper_address):
    # paper address is "2014\May\Computer_science_paper_1_HL.pdf" #
    paper_folder_name = paper_address.replace("\\", "").replace(".pdf", "")  # "2014MayComputer_science_paper_1_HL"
    return paper_folder_name


def make_monster_png(path_to_file):
    try:
        # try to load the pdf as a list of page image files.
        images = convert_from_path(path_to_file, poppler_path=poppler_path)

        page_width = images[0].size[0]
        page_height = images[0].size[1]
        total_height = page_height * len(images)
    except PDFPageCountError:
        print()
        print(path_to_file, "doesn't exist")
        return None

    monster = Image.new("RGB", (page_width, total_height))
    for i, image in enumerate(images):
        monster.paste(image, (0, i * page_height))
    return monster


def slice_from_pdf(q_df):  # takes in dataframe of questions.
    def slice_images(qimages, paper_address):
        # qimages looks like {"images\2014MayComputer_science_paper_1_HL\8q.png" : (scroll start as float,scroll end)}
        # paper address looks like "2014\May\Computer_science_paper_1_HL.pdf"

        # if the paper has been processed previously, we should skip opening the pdf and converting to png.
        # so we check if corresponding sliced pngs already exist for this entire paper and only skip if they all exist.
        # so if one slice is missing, it would re-do this paper.
        found_all = True
        for q in qimages:
            if not os.path.isfile(q):
                found_all = False
        if found_all:
            print(f"All images for {paper_address} already exist")
            print()
            return None


        relative_paper_address = os.path.join(papers_path, paper_address)
        image = make_monster_png(relative_paper_address)  # this loads the pdf and returns it as a long png.
        # The above always happens, even if the sliced questions already exist.
        # This means adding a single paper involves processing all of the previous ones again...
        # Should really rearrange this so that it checks for existing images first...but probably later.
        if image is None:
            print("Nothing to slice here.", paper_address)
            print()
            return None

        page_width = image.width
        total_height = image.height

        # NOW DO THE ACTUAL SLICING
        for question in qimages:
            # print(qimages)
            try:
                scroll_start = qimages[question][0]
                scroll_end = qimages[question][1]

                pixel_start = scroll_start * total_height
                pixel_end = scroll_end * total_height
            except IndexError:
                # in some cases a question may not have associated start and end coordinates
                # in this case give some fake data for a blank part of the document.
                # SHOULD NO LONGER BE THE CASE WITH OCR, but hey...
                pixel_start = image.height - 10
                pixel_end = image.height
            # print(question, pixel_start)

            # page_width = image.width
            if not os.path.isfile(question):  # if this question slice already exists, skip.
                try:
                    # crop the full pdf image according to the boundaries provided in the data.
                    img = image.crop((0, pixel_start, page_width, pixel_end + 1))
                    img.save(question, "PNG")
                    print("Saved:", question)
                except ValueError:
                    # if at least one of the boundaries is not provided, then crop can't happen.
                    # Skip this question then.
                    print("Missing a boundary:", [pixel_start, pixel_end])

            else:
                print("Already exists:", question)

    q_df.reset_index()  # just in case
    paper_names = q_df["paper"].unique()

    # loop through papers
    for paper in paper_names:
        # paper looks like "2014\May\Computer_science_paper_1_HL.pdf"
        if pd.isna(paper):
            continue
        markscheme = paper.replace(".pdf", "_markscheme.pdf")
        qimages = {}  # question images
        aimages = {}  # answer images

        paper_folder_name = hash_paper_address(paper)  # "2014MayComputer_science_paper_1_HL" e.g.
        paper_image_path = os.path.join(image_path, paper_folder_name)  # images\2014MayComputer_science_paper_1_HL
        if os.path.exists(paper_image_path) is False:
            os.mkdir(paper_image_path)

        paper_df = q_df.loc[q_df["paper"] == paper]
        # print(paper_df)
        for index, row in paper_df.iterrows():
            scroll_start = row["scrollLocation"]
            scroll_end = row["scrollLocation_end"]
            question_image_path = os.path.join(paper_image_path,
                                               str(int(row["qNum"]))) + "q.png"  # for questions...
            # question_image_path looks like "images\2014MayComputer_science_paper_1_HL\8q.png"
            qimages[question_image_path] = (scroll_start, scroll_end)

            ms_scroll_start = row["scrollLocationMS"]
            ms_scroll_end = row["scrollLocationMS_end"]
            markscheme_image_path = os.path.join(paper_image_path,
                                                 str(int(row["qNum"]))) + "a.png"  # for markschemes.
            # question_image_path looks like "images\2014MayComputer_science_paper_1_HL\8a.png"
            aimages[markscheme_image_path] = (ms_scroll_start, ms_scroll_end)

        slice_images(qimages, paper)
        slice_images(aimages, markscheme)


data = load_data_from_csv()
slice_from_pdf(data)
