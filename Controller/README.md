# CSE 4/589: PA3 AutoGrader [Controller]

Note that you need to follow the instructions below **ONLY** if you want to run the controller from source for debugging purposes or you are trying to re-package after making changes or package it into a binary for a non-Linux platform.

Typically, you do **NOT** need to specifically provide even the binary version (or a link to download it) to the students. The main assignment description/handout provided to students already contains the download link and instructions for its usage.

## Setup
You need to follow the steps below only if you want to run the controller from the source.

```bash
$ git clone --no-checkout https://github.com/cse4589/cse4589-pa3.git
$ cd cse4589-pa3
$ git config core.sparseCheckout true
$ echo 'Controller' >> .git/info/sparse-checkout
$ git checkout master
```

## Run
The function and usage of the controller application is listed in detailed in the [PA3 Template instructions](https://docs.google.com/document/d/14Uq8NinrflLrsb4y0iy2J9XsMDk4FaXkK-0NRUlOj0M/pub). For quick reference:

```bash
$ cd Controller
$ ./controller.py -h
```

The binary version (created using the steps detailed below) can be run similarly as:

```bash
$ ./controller -h
```

## Convert to Binary
We make use of the [pyinstaller](http://www.pyinstaller.org/) package to convert AutoGrader's client side python scripts into a single executable binary.

You need to first obtain the source of the controller, using instructions listed above under the [Setup](https://github.com/cse4589/cse4589-pa3/tree/master/Grader/local#setup) section. To convert to binary, execute the following with the ```Controller``` as the root directory.

```bash
$ pyinstaller --onefile controller.py
```

If everything goes well, the executable named _controller_ will be created ```Controller/dist``` directory. You can upload this binary and the example.topology to somewhere it can be publicly downloaded from.

***
##### <img src="https://cse4589.github.io/assets/site/images/UB_BLU_RGB.png" width=30></img>
In all likelihood, there is no need for this conversion as pre-compiled binaries are already available for UB students to be downloaded. The download and setup is taken care by the template scripts which are documented in the assignment handout/description.
***
