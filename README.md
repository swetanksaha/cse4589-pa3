# CSE 4/589: Programming Assignment 3 (PA3) AutoGrader
If you have landed at this repository directly, you first should read up on bit of a background [here](https://cse4589.github.io/).

## Introduction
PA3 AutoGrader runs completely on the system that it is invoked from and does not require any server-side setup. It makes use of the controller application, bundled with the template, to send commands and receive responses to the submission being tested. However, it makes use of ssh/scp while testing for certain test cases.

The AutoGrader takes as input the student source code which is first uploaded to each of the grading machines, built and then tested for a given test case.

The [_Grader_](/Grader) directory holds the grader source and usage instructions.

The [_Controller_](/Controller) directory holds both source for the controller application.

The [_Template_](/Template) directory contains the source for the code template distributed to students (see [here](https://docs.google.com/document/d/1o6epHif2H0--Qhq9uo1dp0tXel5CiSYoYsuFa-s92YU/pub)).

## Requirements
* **Five(5)** Linux hosts/machines
* Networking setup such that all the five hosts are _reachable_ from each other
* User accounts and work/disk space for each student to be able to do development/testing to complete the assignment

***
<img src="http://cse4589.github.io/assets/site/images/UB_BLU_RGB.png" width=30></img>
### List of UB CSE hosts
* stones.cse.buffalo.edu
* euston.cse.buffalo.edu
* embankment.cse.buffalo.edu
* underground.cse.buffalo.edu
* highgate.cse.buffalo.edu

### Student User Accounts and Work Directories
Students should already have user accounts on the above hosts as part of the UB CSE infrastructure.

However, the home folders of students reside on a disk space that is shared among all CSE student servers. Given that PA1 involves implementation of file transfers, this makes home folders unsuitable for students to do development/testing of PA1. As a fix, CSE-IT creates a directory for each student on a non-shared disk mounted at ```/local``` on each of the five hosts.
Typically, the course instructor provides the list of students enrolled in the course each semester to CSE-IT and folders are created for each student. For example, for Fall 2017, for a student with UB-IT name [ubitname] the work/test directory could be
```/local/Fall_2017/[ubitname]```

#### Notes
* Instructor/Course staff needs to notify the students of this directory's path to use the used for all their assignment related work.
* Care should be taken in setting correct permissions for the student work folders so that they are only accessible by the student that the folder is assigned to.
***

## AutoGrader: Controller and Grader
Typically both the grader and the controller application are distributed to students as a single executable binary, instead of the raw python source files to avoid imposing any additional setup requirements on student machine environments. Setup instructions for both the grader and controller located inside their source folders (linked above) include steps to convert the python source to a Linux executable. It should be fairly straightforward to adapt the conversion process for any other OS the course staff wishes to support. In addition, we also include steps to run the grader directly from source to allow for easy debugging.
