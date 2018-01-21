# CSE 4/589: PA3 AutoGrader

Note that you need to follow the instructions below **ONLY** if you want to run the grader from source for debugging purposes or you are trying to re-package after making changes or package it into a binary for a non-Linux platform.

Typically, you do **NOT** need to specifically provide even the binary version (or a link to download it) to the students. The main assignment description/handout provided to students already contains the download link and instructions for its usage.

However, note that the grader requires some configuration items (ssh username and keys etc.) that need to be provided to the students (details below). Such configuration can be distributed to the students through typical course communication channels (piazza, course website, etc.).

## Setup
You need to follow the steps below only if you want to run the grader from the source. If you are using the binary version, skip to the [Configure](https://github.com/cse4589/cse4589-pa3/blob/master/Grader/README.md#configure) section.

```bash
$ git clone --no-checkout https://github.com/cse4589/cse4589-pa3.git
$ cd cse4589-pa3
$ git config core.sparseCheckout true
$ echo 'Grader' >> .git/info/sparse-checkout
$ git checkout master
```

## Configure
Before the AutoGrader's client can talk to the server, it needs to be configured. Client's configuration is contained in ```Grader/local/grader.cfg```. Available configuration options are explained below.

### Configuration Options

* [GradingServerList]
  * **server-1 ... server-5** _FQDNs of the five grading host machines._

* [SSH]
  * **user** _Username that has ssh access to each of the five hosts listed under [GradingServerList]_.
  * **id** _Absolute path (on the local machine) to the private key of the key-pair that allows you to ssh to each of the five hosts listed under [GradingServerList]_.

* [Grader]
  * **binary** _Filename of the binary created by the submission Makefile (default=assignment3)._ This is an internal grader property and does not require any changes to it.

***
<img src="https://cse4589.github.io/assets/site/images/UB_BLU_RGB.png" width=30></img>
The binary client downloaded by students through the link provided in the assignment handout contains a pre-configured grader.cfg.

However, the students will still need to edit the grader.cfg to enter their own ssh credentials.
***

## Run
```bash
$ cd Grader
$ ./grader_controller.py -h
```

The binary version (created using the steps detailed below) can be run similarly as:

```bash
$ ../grader_controller -h
```

## Convert to Binary
We make use of the [pyinstaller](http://www.pyinstaller.org/) package to convert AutoGrader's client side python scripts into a single executable binary.

You need to first obtain the source of the grader, using instructions listed above under the [Setup](https://github.com/cse4589/cse4589-pa3/tree/master/Grader/local#setup) section. To convert to binary, execute the following with the ```Grader``` as the root directory.

```bash
$ pyinstaller --onefile grader_controller.py
```

If everything goes well, the executable named _grader_controller_ will be created ```Grader/dist``` directory. You can upload this binary and the grader.cfg to somewhere it can be publicly downloaded from.

***
##### <img src="http://cse4589.github.io/assets/site/images/UB_BLU_RGB.png" width=30></img>
In all likelihood, there is no need for this conversion as pre-compiled binaries are already available for UB students to be downloaded. The download and setup is taken care by the template scripts which are documented in the assignment handout/description.
***
