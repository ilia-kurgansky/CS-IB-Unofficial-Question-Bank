from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from math import sqrt

import pandas as pd
import os

user_path = "_User files"
papers_path = os.path.join(user_path, "papers")  # this is the local folder where tidied papers go
image_path = os.path.join(user_path, "images")  # this is the local folder where clipped images go for each paper
export_path = os.path.join(user_path, "collated")  # this is the local folder where exported papers go

A4_h_to_w_ratio = sqrt(2)
page_header = 72  # pixels - ballpark
page_footer = 200  # pixels - ballpark
question_buffer = 30  # pixels - ballpark, looks nice
html_image_width = 900  # pixels

left_column_margin = 0.12  # proportional boundary from left edge to question body - quite precise
current_spec_year = 14  # at the time of programming, the current spec first assessment in 2014


def load_data_from_csv(data_path="data.csv"):
    question_df = pd.read_csv(data_path)
    # print(question_df.iloc[0])
    return question_df


def load_topics_from_csv(topics_path="topics_list.csv"):
    topics = pd.read_csv(topics_path)
    topics = topics.fillna("")
    return topics


def hash_paper_address(paper_address):
    # paper address is "2014\May\Computer_science_paper_1_HL.pdf"
    paper_folder_name = paper_address.replace("\\", "").replace(".pdf", "")  # "2014MayComputer_science_paper_1_HL"
    return paper_folder_name


def filter_data(q_df, topics_df, subtopics):
    # subtopics is a list of subtopic name.
    # this function looks up the matching subtopic ids as "link_id"
    # and then collates a df of the corresponding questions that have those link_ids.
    # ...not sure why I am passing subtopics by name to begin with, if I am honest...
    link_ids = topics_df[topics_df["subtopic"].isin(subtopics)]["link_id"]
    chosen_qs = q_df[q_df["link_id"].isin(link_ids)]
    chosen_qs = chosen_qs.drop_duplicates(subset=["paper", "qNum"], ignore_index=True)
    # print(chosen_qs)
    return chosen_qs


def generate_slice_info(paper_path, qnum, question_or_answer):
    # paper_path like "2014\May\Computer_science_paper_1_HL.pdf"
    # qnum is probably int
    # question_or_answer is "q" or "a", depending on whether the slice is a question or markscheme
    paper_name = hash_paper_address(paper_path)
    slice_info = {}
    slice_info["year_month"] = paper_name[2:5]
    paper_num_index = paper_name.find("paper_") + 6
    level = "HL" if "HL" in paper_name else "SL"
    slice_info["level_paper"] = level + paper_name[paper_num_index]
    slice_info["path"] = os.path.join(paper_name, str(qnum) + question_or_answer + ".png")

    # slice_info is a dict like:
    # {"path": "2014MayComputer_science_paper_1_HL\8a.png", "year_month":"14M", "level_paper":"HL1"}
    return slice_info


def find_and_return_slice_image(slice_info, stamp=True):
    # slice_info is a dict like:
    # {"path": "2014MayComputer_science_paper_1_HL\8a.png", "year_month":"14M", "level_paper":"HL1"}
    path = os.path.join(image_path, slice_info["path"])
    try:
        img = Image.open(path)
    except FileNotFoundError:
        print("No such image", slice_info["path"])
        img = Image.new('RGB', (1500, 100), color=(255, 255, 255))
        # return a blank image if there is no matching file.
        # return img

    if stamp:
        # stamps a year/month/level/paper identifier on each image for reference.
        # Also adds a rectangle if the question comes from a current specification.
        column_width = left_column_margin * img.width
        letter_width = int(column_width / 7)

        edited_img = ImageDraw.Draw(img)
        my_font = ImageFont.truetype(r"font\monofonto\monofonto rg.otf", letter_width)
        text = slice_info["year_month"] + " " + slice_info["level_paper"]
        if int(slice_info["year_month"][:2]) >= current_spec_year:
            colour = (0, 125, 0)
            shape = [(2, 25), (2 + letter_width * 4, 60)]
            edited_img.rectangle(shape, outline=colour)
        else:
            colour = (100, 100, 100)
        edited_img.text((5, 25), text, colour, font=my_font)

    # img.show()
    return img


def export_papers(q_df, topics_df, subtopics):
    # happens after all of the selection is done.
    # processes the selected questions and outputs them into an HTML file
    # the question images are clickable and display the matching markscheme (if it exists)
    def save_images_for_html(qs, ms, imgpath, scale=True):
        # qs and ms contain loaded img files, which are kept in memory until saved in the loop below.
        # Images need to be renamed for HTML use and rescaled/compressed to conserve space.
        for i, q in enumerate(qs):  # doing questions and answers separately as not all qs have markschemes.
            savepath = os.path.join(imgpath, str(i + 1) + "q.jpg")
            if scale:
                new_width = min(html_image_width, q.width)
                new_height = int(q.height * new_width / q.width)
                q = q.resize((new_width, new_height))
            q.save(savepath, "JPEG")

        for i, a in enumerate(ms):
            savepath = os.path.join(imgpath, str(i + 1) + "a.jpg")
            if scale:
                new_width = min(html_image_width, a.width)
                new_height = int(a.height * new_width / a.width)
                a = a.resize((new_width, new_height))  # if no markscheme, this will show a blank image.
            a.save(savepath, "JPEG")

    def write_html(qs, ms, save_name, save_path, subtopics):
        html_path = os.path.join(save_path, save_name + ".html")
        with open(html_path, "w") as site:
            header = f"<!DOCTYPE html><html><body><h2>{subtopics}</h2>"
            footer = "</body></html>"
            middle = ""
            for i in range(len(qs)):
                impath = os.path.join("img", str(i + 1) + "q.jpg")  # this needs to be relative to HTML
                apath = os.path.join("img", str(i + 1) + "a.jpg")  # ... so not using full img_path
                middle += f"""<div style='font-size: 18px'>{i + 1}.
                           <a href="{apath}"> 
                           <img style='height: 100%; 
                                       width: 80%; 

                                       display: block;
                                       margin-left: auto;  
                                       margin-right: auto;
                                       margin-bottom: 0.6cm' 
                                       src="{impath}"> </a></div>"""
            full = header + middle + footer
            site.write(full)

    folder_name = input("Give your exported file a name: ")

    save_path = os.path.join(export_path, folder_name)
    img_path = os.path.join(save_path, "img")
    try:
        os.makedirs(img_path)
    except FileExistsError:
        print("An export called that already exists. I would rather not overwrite it.")
        print("Delete it if you want to save under the same name again.")
        return None

    chosen_qs = filter_data(q_df, topics_df, subtopics)
    chosen_qs = chosen_qs.sort_values(["question_type"], ascending=[False])
    chosen_qs = chosen_qs.reset_index()

    # the two lists below will store references to actual loaded image files.
    qs = []
    ms = []
    for index, row in chosen_qs.iterrows():
        qslice_info = generate_slice_info(row["paper"], row["qNum"], "q")
        qs.append(find_and_return_slice_image(qslice_info))

        # the bit below will need reviewing.
        # If there is no matching mark scheme, it will generate a path to a nonexistent image.
        # However, if it can't find an image, it will return a small rectangular black image as a placeholder.
        aslice_info = generate_slice_info(row["paper"], row["qNum"], "a")
        ms.append(find_and_return_slice_image(aslice_info))

    save_images_for_html(qs, ms, img_path)
    write_html(qs, ms, folder_name, save_path, subtopics)


def topics_selection(q_df, topics_df, selection=list()):
    # the main point of interaction.
    # Menu that allows the user to select which topics they would like questions for.

    def get_topic_selection(topic_dict):
        # output the dictionary of topics and allow user to select by using number entry.
        # returns a valid topic number.
        print()
        print("Select topic category by topic code:")
        for i, key in enumerate(sorted(topic_dict)):
            print(f"{key} {topic_dict[key]}")

        choice = input("Enter topic code, e.g. '1.1': ")
        if choice not in topic_dict.keys():
            print("No such topic number, try again.")
            return get_topic_selection(topic_dict)
        return choice

    def get_subtopic_selection(subtopic_list):
        print()
        print("Select subtopic by number:")
        for i, subtopic in enumerate(subtopic_list):
            print(f"{i + 1}. {subtopic}")

        choice = input("Enter subtopic number, e.g. '2': ")
        try:
            # does not return the link_id for subtopic, but returns the actual name of the subtopic.
            # this was done so that it looks useful when output on the screen, skipping a look up.
            return subtopic_list[int(choice) - 1]
        except:
            print("Bad selection, try again.")
            return get_subtopic_selection(subtopic_list)

    def main_menu(selection):
        # returns one of the "choices" in the list as a string.
        print()
        if len(selection) > 0:
            numqs = len(filter_data(q_df, topics_df, selection)["link_id"])
            print(f"You currently selected {selection}, which is {numqs} questions")

        print("Choose to add topics to your selection, or to start the export:")
        choices = ["Add topics", "Export questions"]
        for i, c in enumerate(choices):
            print(f"{i + 1}. {c}")
        choice = input("Selection: ")
        try:
            return choices[int(choice) - 1]
        except:
            print("Incorrect choice, try again.")
            # recursive input validation.
            return main_menu(selection)

    def select_topics(selection):
        # the subtopic aggregation function.
        # takes the current list of selected subtopics.
        # guides the user through menu structures for big topic selection...
        # ... that then takes the user to select a subtopic from the chosen bigger topic.
        # Appends final subtopic choice to the "selection" list as a string.
        # Returns to outer function.
        topic_dict = {}
        numbers = topics_df["number"].unique()  # get list of topic codes.

        for n in numbers:
            topic_dict[n] = topics_df[topics_df["number"] == n]["topic"].iloc[0]
            # makes a dictionary like {"3.1":"Networks", "5.1":"Abstract Data Structures",..}

        topic_num_choice = get_topic_selection(topic_dict)  # this is now e.g. "3.1"

        subtopics = topics_df[topics_df["number"] == topic_num_choice]["subtopic"].unique()
        # the above line finds all of the matching subtopics for the "3.1" from above.

        subtopic_choice = get_subtopic_selection(subtopics)  # this is now e.g. "Trees and linked lists"

        selection.append(subtopic_choice)
        return selection

    top_choice = main_menu(selection)  # get and validate top level main menu.
    # the "selection" parameter is a list of subtopic names selected so far.
    # "selection" starts as empty list, grows as the selection function is re-run.
    if top_choice == "Add topics":  # if adding more topics, run the selection pathway.
        selection = select_topics(selection)
        topics_selection(q_df, topics_df, selection)  # recursively run self to give option to add more topics.
    else:
        export_papers(q_df, topics_df, selection)  # if done with adding topics, export HTML


# find_and_return_slice_image(generate_slice_info("2014\May\Computer_science_paper_1_HL.pdf", 14, "q"))
topics_df = load_topics_from_csv()
questions_df = load_data_from_csv()

topics_selection(questions_df, topics_df)
