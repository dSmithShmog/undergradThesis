###############################################################
# Text Mining Portion of the Course Map System
# Author: Dillan Smith
# All rights reserved
# Date: 4/4/2017
# Takes a text file containing Allegheny College's course catalog
# and breaks it up by line and by paragraph. It searches that
# corpus for courses, breaks up that information, and outputs into
# 3 tsv files which are used in the R portion of this system
###############################################################
import sys
import os
import nltk
import re
import sqlite3 as lite
import string
# uncomment if need nltk corpuses
# nltk.download()
# all the course acronyms that I know of
# 'ARAB', 'ART', 'BCHEM', 'BLKST', 'BIO', 'CHEM', 'CHIN', 'CLC', 'CMPSC', 'COMJ', 'COMRT',
# 'DMS', 'ECON', 'EDUC', 'ENGL', 'ENVSC', 'EXL', 'FRNCH', 'GEO', 'GERMN', 'GHS', 'HIST',
# 'INTDS', 'INTST', 'JOURN', 'LATIN', 'MATH', 'MUSIC', 'NEURO', 'PHIL', 'PHYS', 'POLSC',
# 'PSYCH', 'RELST', 'SPAN', 'FS', 'FSART', 'FSBIO', 'FSCHE', 'FSCOM', 'FSDMS', 'FSECO',
# 'FSENG', 'FSENV', 'FSFRE', 'FSGEO', 'FSGER', 'FSGHS', 'FSHIS', 'FSMAT', 'FSMUS',
# 'FSNEU', 'FSPHI', 'FSPHY', 'FSPOL', 'FSPSY', 'FSREL', 'FSPA'
# note: FSMLG should be in here but its throwing an error
dept_acronyms = {"BIO", "PSYCH", "COMRT", "ENVSC", "CMPSC"}

def clean_text_file():

    corp = open('2016-17coursePDF.txt', 'r')
    line_txt = []

    # parse the original txt file by line
    while True:
        line = corp.readline()
        if line == "":
            break
        else:
            line_txt.append(line)
    corp.close()

    # remove spaces prior to \n
    line_txt = remove_ghost_spaces(line_txt)

    # write the cleaned lines back into a new working version of the text
    corp = open('workingVersion.txt', 'w')
    for line in line_txt:
        corp.write(line)
    corp.close()


def remove_course_lists(chunkList, checkList):
    for paragraph in chunkList:
        courseInPara = 0 # counter for course lines in the paragraph
        paragraph = paragraph.split('\n') # parse by line
        for course in checkList:
            for line in paragraph:
                if course == line+'\n':
                    courseInPara += 1
        if courseInPara > 1:   # remove all paragraphs with more than one course
            chunkList.remove('\n'.join(paragraph))

    return chunkList

#clean for course names that appear more than once
def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        if any(word in ['recommended','required'] for word in value.split(' ')):
            values.remove(value)
    values = remove_ghost_duplicates(clean_special_characters(values))
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def clean_special_characters(values):
    invalidChars = set(string.punctuation.replace(":", ""))
    invalidChars2 = set(string.punctuation.replace(",", ""))
    check1 = []
    check2 = []
    output = []
    for value in values:
        splits = value.split(' ')
        if len(splits) >= 3:
            if any((char in invalidChars for char in splits[2]) and (char in invalidChars2 for char in splits[2])):
                continue
            output.append(value)
    return output


def remove_ghost_duplicates(values):
    output = []
    for x in range(len(values)):
        sample = values[x]
        if sample[len(sample)-1] == '@':
            continue
        sampleSplit = sample.split(' ')
        real_index = x
        for y in range(x+1,len(values)):
            sample2 = values[y]
            if sample2[len(sample2)-1] == '@':
                continue
            sampleSplit2 = sample2.split(' ')
            if sampleSplit2[:2] == sampleSplit[:2]:
                real_index = y
                values[y] += '@'
        values[x] += '@'
        output.append(values[real_index][:-1])

    #for value in output:
        #print value
    print "CLEANED FOR DUPLICATES"
    return output


def remove_ghost_spaces(temp_txt):
    # remove all spaces immediately prior to newlines in the lined text
    for x in range(len(temp_txt)):
        while True:
            if temp_txt[x][len(temp_txt[x])-2]+temp_txt[x][len(temp_txt[x])-1] == ' \n':
                newline = temp_txt[x][:len(temp_txt[x])-2] + temp_txt[x][len(temp_txt[x])-1]
                temp_txt[x] = newline
            else:
                break
    return temp_txt


def get_courses(temp_txt, acronyms):
    temp_courses = []
    for acro in acronyms:
        for line in temp_txt:
            check = tuple(re.finditer(acro+' .{3}', line, flags=0))
            if len(check) > 1:  # skip lines that contain more than one course acronym combo
                continue
            matchObj = re.match(acro+' [0-9]{3} .*\n', line, flags=0) # look for match with CMPSC ### . . .
            if matchObj is not None:
                if matchObj.group():
                    temp_courses.append(matchObj.group())
    print "COURSES OBTAINED"
    return temp_courses


def get_summaries(temp_paragraphs, temp_courses):
    summaries, new_courses = [], []
    for para in temp_paragraphs:
        line_para = para.split('\n')  # break each paragraph up by line

        if len(para) < 3:  # dont try to process garbage paragraphs
            continue
        for course in temp_courses:  # search for course that matches start of para
            if line_para[0] == course[:len(course)-1]:  # courses have \n whereas .split strips them off line_para
                summaries.append('\n'.join(line_para[1:]))  # append rejoined paragraph to working summaries
                new_courses.append(course)  # append working course, index matches the above summary
    print "RETURNING SUMMARIES WITH MATCHING COURSES"
    return summaries, new_courses


def parse_summaries(summaries, prereq, coreq, cred, dist):
     for y in range(len(summaries)):
        prereq.append('')
        cred.append('')
        dist.append('')
        coreq.append('')
        tokens = nltk.word_tokenize(summaries[y])
        for x in range(len(tokens)):
            # check for prereq trigger
            if tokens[x] == 'Prerequisites' or tokens[x] == 'Prerequisite':
                x += 1  # compensate for colon, avoid trying to reference out of range index
                temp = x
                temp += 1
                while True:

                    # if it's the last word in the sentence (theres a period) cut out the garbage space in
                    # the prereq and quit
                    if tokens[temp][len(tokens[temp])-1] == '.':
                        prereq[y] = prereq[y][:-1]
                        break

                    prereq[y] += tokens[temp] + ' '
                    temp += 1
                x = temp
            # look for coreq info
            elif tokens[x] == 'Corequisite':
                x += 1  # compensate for colon, avoid trying to reference out of range index
                temp = x
                temp += 1
                while True:

                    # if it's the last word in the sentence cut out garbage space and quit
                    if tokens[temp][len(tokens[temp])-1] == '.':
                        coreq[y] = coreq[y][:-1]
                        break

                    coreq[y] += tokens[temp] + ' '
                    temp += 1
                x = temp
            # grab credit information
            elif tokens[x] == 'Credit':
                x += 1  # compensate for colon, avoid trying to reference out of range index
                temp = x
                temp += 1
                while tokens[temp] != '.':
                    cred[y] += tokens[temp] + ' '
                    temp += 1
                x = temp\
            # look for new dist. tags
            elif tokens[x] == 'Distribution Requirements':
                x += 1  # compensate for colon, avoid trying to reference out of range index
                temp = x
                temp += 1
                while True:

                    # if it's the last word in the sentence cut out of the period and break
                    if tokens[temp][len(tokens[temp])-1] == '.':
                        dist[y] = dist[y][:-1]
                        break

                    dist[y] += tokens[temp] + ' '
                    temp += 1
                x = temp

     print "SUMMARIES PARSED"
     return prereq, coreq, cred, dist


def populate_db(idTemp,deptTemp, numberTemp, titleTemp,prerequisitesTemp,corequisiteTemp,creditsTemp,distributionTemp):
    conn = lite.connect('testDB.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE Nodes;")
    cur.execute("CREATE TABLE Nodes"
                "(id TEXT PRIMARY KEY NOT NULL,"
                " dept TEXT,"
                " number INT,"
                " title TEXT,"
                " prerequisites TEXT,"
                " corequisites TEXT,"
                " credits TEXT,"
                " distribution TEXT);")
    for x in range(len(idTemp)):
        record = "\"" + idTemp[x] + "\"," + "\"" + deptTemp[x] + "\"," + "\"" + numberTemp[x] + "\"," + "\"" + \
                 titleTemp[x] + "\"," + "\"" + prerequisitesTemp[x] + "\"," + "\"" + \
                 corequisiteTemp[x] + "\"," + "\"" + creditsTemp[x] + "\"," + "\"" + distributionTemp[x] + "\""
        #print record
        cur.execute("INSERT INTO Nodes VALUES(" + record + ');')
    conn.commit()
    conn.close()

#breaks courses up into specific details
def getCourseDetails(tempCourses):
    course_department, course_number, course_id, course_title = [], [], [], []
    for x in range(len(tempCourses)):
        temp_course = tempCourses[x]
        split_course = temp_course.split(' ')
        course_department.append(split_course[0])
        course_number.append(split_course[1])
        course_id.append(split_course[0] + str(split_course[1]))
        course_title.append(' '.join(split_course[2:len(split_course)]))
    return course_id, course_department, course_number, course_title


def textMine():
    # uncomment if you need to clean up converted text document still, creates 'workingVersion.txt'
    clean_text_file()

    corp = open('workingVersion.txt')
    line_txt = []
    while True:
        line = corp.readline()
        if line == "":
            break
        else:
            line_txt.append(line)
    corp.close()
    # course names
    courses = []



    # grab all the course titles, NOTE: this also grabs course titles that are not followed by summaries
    courses = get_courses(line_txt, dept_acronyms)
    courses = remove_duplicates(courses)  # remove duplicate courses and calls other things
    courses = sorted(courses)  # sort the courses, this results in department clusters sorted by course number

    # rejoin and cluster text by paragraph
    corpus = ''.join(line_txt)
    paragraphs = corpus.split('\n\n')
    paragraphs = remove_course_lists(paragraphs, courses)  # remove paragraphs with more than one course in them
    summaries, courses = get_summaries(paragraphs, courses)



    # get the seperate department code names and class numbers and create course id

    course_id, course_department, course_number, course_title = getCourseDetails(courses)


    for x in range(len(course_title)):
        course_title[x] = course_title[x][:-1]

    prerequisites, corequisite, credits, distribution = [], [], [], []
    prerequisites, corequisite, credits, distribution = parse_summaries(summaries, prerequisites, corequisite, credits,
                                                                        distribution)
    # shorten and clean summaries for information I already pulled out and for \t values
    for x in range(len(summaries)):
        # only keep what comes before all the information I already mined
        summaries[x] = summaries[x].split("Prerequisite:", 1)[0]
        summaries[x] = summaries[x].split("Prerequisites:", 1)[0]
        summaries[x] = summaries[x].split("Corequisite:", 1)[0]
        summaries[x] = summaries[x].split("Credit:", 1)[0]
        summaries[x] = summaries[x].split("Distribution Requirements:", 1)[0]
        # make sure they dont screw up my tsv format
        summaries[x] = summaries[x].replace('\t', ' ')

    # I dont remember why this is here
    for x in range(len(prerequisites)):
        prerequisites[x] = prerequisites[x].translate(None, string.punctuation)

    # attaching department IDs for color coding within R
    dept_id = []
    count = 1
    dept_id.append(count)
    for x in range(1, len(course_id)):
        if course_department[x] != course_department[x - 1]:  # if its a new department
            count += 1
        dept_id.append(count)
    for x in range(len(summaries)):
        summaries[x] = ' '.join(summaries[x].split('\n'))

    return courses, course_id, course_department, dept_id, course_number, course_title, prerequisites, corequisite, \
           credits, distribution, summaries

# populates the database.tsv file with course information
def popDBTSV(t_course_id, t_course_department, t_course_number, t_course_title, t_prerequisites,
                 t_corequisite, t_credits, t_distribution, t_summaries):
    db_tsv = open('courseMap/database.tsv', 'w')
    db_tsv.write('id\tdept\tnumber\ttitle\tprerequisites\tcorequisites\tcredits\tdistribution\tsummary\n')
    for x in range(len(t_course_id)):
        if t_course_id[x] == '':
            t_course_id[x] = 'NA'
        if t_course_department[x] == '':
            t_course_department[x] = 'NA'
        if t_course_number[x] == '':
            t_course_number[x] = 0
        if t_course_title[x] == '':
            t_course_title[x] = 'NA'
        if t_prerequisites[x] == '':
            t_prerequisites[x] = 'NA'
        if t_corequisite[x] == '':
            t_corequisite[x] = 'NA'
        if t_credits[x] == '':
            t_credits[x] = 'Assumed 4'
        if t_distribution[x] == '':
            t_distribution[x] = 'NA'
        if t_summaries[x] == '':
            t_summaries[x] = 'NA'
        if x != len(t_course_id) - 1:
            db_tsv.write(
                t_course_id[x] + '\t' + t_course_department[x] + '\t' + t_course_number[x] + '\t' + t_course_title[x]
                + '\t' + t_prerequisites[x] + '\t' + t_corequisite[x] + '\t' + t_credits[x] + '\t' + t_distribution[x]
                + '\t' + t_summaries[x] + '\n')
        else:
            db_tsv.write(
                t_course_id[x] + '\t' + t_course_department[x] + '\t' + t_course_number[x] + '\t' + t_course_title[x]
                + '\t' + t_prerequisites[x] + '\t' + t_corequisite[x] + '\t' + t_credits[x] + '\t' + t_distribution[x]
                + '\t' + t_summaries[x] + '\n')

    db_tsv.close()

# populate nodes.tsv file with some course information
def popNodesTSV(t_course_id, t_course_department, t_dept_id, t_course_number, t_course_title):
    node_csv = open('courseMap/nodes.tsv', 'w')
    node_csv.write("id\tdept\tdeptNum\tnumber\ttitle\n")
    for x in range(len(t_course_id)):
        if x != len(t_course_id) - 1:
            node_csv.write(
                t_course_id[x] + '\t' + t_course_department[x] + '\t' + str(t_dept_id[x]) + '\t' + t_course_number[x]
                + '\t' + t_course_title[x] + '\n')
        else:
            node_csv.write(
                t_course_id[x] + '\t' + t_course_department[x] + '\t' + str(t_dept_id[x]) + '\t' + t_course_number[x]
                + '\t' + t_course_title[x])

    node_csv.close()

# find edge relationships by mining prerequisite information
def getEdges(t_prerequisites, t_course_id):
    t_edges = [[]]
    # need to figure out a less ugly way to do this but it works
    for x in range(len(t_prerequisites)):
        split_prereq = t_prerequisites[x].split(' ')
        for y in range(len(split_prereq) - 1):
            sample = (split_prereq[y] + split_prereq[y + 1]).upper()  # stick two together, looking for id matches
            for z in range(len(t_course_id)):
                if sample == t_course_id[z]:
                    t_edges.append([sample, t_course_id[x]])

    t_edges = t_edges[1:]  # remove empty zeroth pair, don't know why it's there
    return t_edges

#populate the edges.tsv file with relationships found in previous method
def popEdgesTSV(t_edges):
    csv = open('courseMap/edges.tsv', 'w')
    csv.write('from\tto\tweight\n')
    for x in range(len(t_edges)):
        if x == len(t_edges)-1:
            csv.write(t_edges[x][0] + "\t" + t_edges[x][1] + "\t" + '5')
        else:
            csv.write(t_edges[x][0] + "\t" + t_edges[x][1] + "\t" + '5\n')
    csv.close()

#very similar to text mine, information is more available except for prereq stuff
def sheetMine():
    import csv
    courses, course_id, course_department, dept_id, course_number, course_title, prerequisites, corequisite, credits, \
    distribution, summaries = [], [], [], [], [], [], [], [], [], [], []
    with open('corpus.tsv', 'r') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        firstLine = True
        for row in reader:
            if firstLine:
                firstLine = False
                continue
            courseNum = row[0].split('*')[1]
            courseDept = row[0].split('*')[0]
            if courseDept+courseNum in course_id:
                continue
            courses.append(courseDept+courseNum+' '+row[1])
            course_id.append(courseDept+courseNum)
            course_department.append(courseDept)
            course_number.append(courseNum)
            course_title.append(row[1])
            summaries.append(row[4])
            credits.append(row[2])
            distribution.append(row[5]+','+row[6])

    for y in range(len(summaries)):
        prerequisites.append('')
        corequisite.append('')
        if summaries[y] == '':
            summaries[y] = 'NA'
        if summaries[y][len(summaries[y])-1] != '.':
            summaries[y] = summaries[y] + '.'
        tokens = nltk.word_tokenize(summaries[y])
        for x in range(len(tokens)):
            # check for prereq trigger
            if tokens[x] == 'Prerequisites' or tokens[x] == 'Prerequisite':
                x += 1  # compensate for colon, avoid trying to reference out of range index
                temp = x
                temp += 1
                while True:

                    # if it's the last word in the sentence (theres a period) cut out the garbage space in the
                    # prereq and quit
                    if tokens[temp][len(tokens[temp]) - 1] == '.':
                        prerequisites[y] = prerequisites[y][:-1]
                        break

                    prerequisites[y] += tokens[temp] + ' '
                    temp += 1
                x = temp
            # look for coreq info
            elif tokens[x] == 'Corequisite':
                x += 1  # compensate for colon, avoid trying to reference out of range index
                temp = x
                temp += 1
                while True:

                    # if it's the last word in the sentence cut out garbage space and quit
                    if tokens[temp][len(tokens[temp]) - 1] == '.':
                        corequisite[y] = corequisite[y][:-1]
                        break

                    corequisite[y] += tokens[temp] + ' '
                    temp += 1
                x = temp
    count = 1
    dept_id.append(count)
    for x in range(1, len(course_id)):
        if course_department[x] != course_department[x - 1]:  # if its a new department
            count += 1
        dept_id.append(count)
    for x in range(len(summaries)):
        summaries[x] = ' '.join(summaries[x].split('\n'))

    return courses, course_id, course_department, dept_id, course_number, course_title, prerequisites, corequisite, \
           credits, distribution, summaries



def main():

    temp = raw_input("Would you like to mine course info from the text or from the spread sheet? (text,sheet):  ")
    if temp == "text":
        courses, course_id, course_department, dept_id, course_number, course_title, prerequisites, corequisite, \
        credits, distribution, summaries = textMine()
    elif temp == "sheet":
        courses, course_id, course_department, dept_id, course_number, course_title, prerequisites, corequisite, \
        credits, distribution, summaries = sheetMine()
    # debugging output to make sure everything matches up
    print len(course_id)
    print len(course_department)
    print len(dept_id)
    print len(course_number)
    print len(course_title)
    print len(prerequisites)
    print len(corequisite)
    print len(credits)
    print len(distribution)
    print len(summaries)

    popDBTSV(course_id, course_department, course_number, course_title, prerequisites, corequisite, credits,
             distribution, summaries)  # create database.tsv
    popNodesTSV(course_id, course_department, dept_id, course_number, course_title)  # create nodes.tsv
    edges = getEdges(prerequisites, course_id)  # mine prerequisites for relationships and create edges

    count = 0
    unattachedCoursesPerDepartment = [0]
    courseCount = []

    popEdgesTSV(edges)  # create edges.tsv

    # uncomment if you need to repopulate db with mined information
    populate_db(course_id, course_department, course_number, course_title, prerequisites, corequisite,
                credits, distribution)




    # FINDING NUMBER OF UNLINKED COURSES PER DEPARTMENT
    vertices = open('courseMap/nodes.tsv', 'r')
    links = open('courseMap/edges.tsv', 'r')
    count = 0
    vertices.readline()
    vList = vertices.read()
    vList = vList.split('\t')
    links.readline()
    lList = links.read()
    lList = lList.split('\t')
    for x in range(len(lList)):
        lList[x] = lList[x].replace('5\n', '')
    print lList
    for acro in sorted(dept_acronyms):
        courseCount.append(course_department.count(acro))
    for x in range(0, len(course_id)):
        if x > 0 and course_department[x] != course_department[x - 1]:  # if its a new department
            count += 1
            unattachedCoursesPerDepartment.append(0)
        if course_id[x] not in lList:
            print course_id[x] + " is not in the lList"
            unattachedCoursesPerDepartment[count] += 1


    print "Number of Unlinked Courses: "+str(count)
    print sorted(dept_acronyms)
    print "# of Courses: " + str(courseCount)
    print "# of unnattached courses: " + str(unattachedCoursesPerDepartment)
    proportionUnattached = []
    for x in range(len(courseCount)):
        proportionUnattached.append(unattachedCoursesPerDepartment[x]/float(courseCount[x]))
    print proportionUnattached
###############################################################

if __name__ == "__main__":
    main()
