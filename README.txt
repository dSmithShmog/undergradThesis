TITLE: Course Map
AUTHOR: Dillan Smith
URL: shmog.shinyapps.io/coursemap

Purpose: Mine, Visualize, and present course information at Allegheny College

Goal: To improve students knowledge of courses offered and department progressions/flow. 
This in turn hopefully improves their overall college experience and saves them time and money.

Description: This is the Course Map system -- my undergraduate thesis. It takes Allegheny College's course catalog and uses Python to 
mine it for as much relevant course information as I could get my hands on. It stores that information in a series of tsv files and a SQLite database. 
Finally, it uses R, and Shiny (an R package that allows for web development inside R), to visualize and present that 
information in a web application. It also does some very small analysis of the course information in Python. This code is not clean, nor easily testable or maintainable. That comes as a consequence of me 
continuously just figuring it out and being pressed for time. 

Future Work: Unfortunately, I was not able to smoothen out this systems pipeline. So one has to run the text miner and then upload the R scripts
along with the relevant tsv files and DB file to shinyapps.io. The R package that allows R scripts to reactively run python scripts
does not work on windows otherwise I would have used that to drastically improve things. One of the biggest changes that needs to happen
is allowing users to decide what departments are being displayed. Currently it just shows some departments I picked to both
show what the system could do and applyto as many students as possible. 