# CS IB Unofficial Question Bank
This is an unofficial question bank for IB Computer Science. 
You supply the exam paper PDFs, I supply the ability to filter questions by topic and link them to mark schemes. This is applicable to the "First exams in 2014" [curriculum](http://ib.compscihub.net/wp-content/uploads/2015/04/IBCompSciGuide.pdf), and, at a stretch, to the previous papers as well.

IB has not provided an official exam question bank, unfortunately. For years teachers have been screen clipping individual questions and storing them in increasingly terrifying and convoluted folder structures.

This project is inspired by a Java implementation by **bluishmatt** found [here](https://github.com/bluishmatt/PastPaperPro) that I could not get to work... so I wrote my own version in Python instead. 
## The problem that is being solved here:
- Teachers need an easy way of finding exam questions that fit under a particular part of the syllabus.
- Those questions have to be separable from the PDF exam paper that includes it.
- Each question must also come with a matching mark scheme that has to be easily accessible.

## How it works:
The file `data.csv` contains a mapping of every IB CS SL/HL exam question since 2000. Every row contains:
- The relative folder address to the matching exam PDF.
- Question number.
- Topic label (linked to `topics_list.csv`).
- Relative coordinates for the question and the markscheme in the corresponding PDF files (used for extracting the question images).

Thanks to **bluishmatt** for the first few hundred question to topic labels that were kept. I have manually labelled another 1300 or so questions with the closest match of the topic. As it stands now **all** Paper 1 questions since the year 2000 have a topic association, with some questions being linked to more than one topic. Some Paper 2 questions are labelled, but not in great detail due to the nature of the paper with long intertwining questions for each section. 
Paper 3 is not labelled at all since the case study material does not sit precisely with the syllabus.

For those that are curious: the topic-to-question mapping was done by hand, but I used an image recognition library to get the coordinates of each question in the paper - so it was not all manual labour in the end.

## Important disclaimer: 
Labelling pre-2014 papers with post-2014 curriculum means that some of the older questions do not align to the current curriculum (e.g. some aspects of the course are no longer taught). The older the paper, the less precise the mapping is going to be, so use your discretion. 
Every question that comes out of my program is clearly stamped with its year and month, so it is easy to tell.


https://github.com/oschwartz10612/poppler-windows
