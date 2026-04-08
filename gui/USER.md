# User manual
## RAiSD-AI
The RAiSD-AI-GUI relies on the RAiSD-AI tool to perform its computations. For more information about RAiSD-AI, please refer to the general [README.md](../README.md). It contains detailed information about the tool, its capabilities, and how it works.

## Install and Run
For information about installing and running the GUI see the appropriate chapters [Installing the GUI](/README.md#installing-the-gui) and [Running the GUI](/README.md#running-the-gui) in the project [README.md](../README.md)

## The Interface

The RAiSD-AI-GUI consists of several pages that allow you to navigate through the different features and functionalities of the tool. Below is an overview of all pages.

### Run Page

The Run Page is the main page of the GUI. It is used to execute RAiSD-AI operations. It's tabs allows you to select the operation you want to perform, configure the parameters, start the execution, monitor the progress, and view the results.

#### Operation Selection Tab

![Screenshot of the Run Page Operation Selection with Run ID](/screenshots/run-page.operation-selection.run1.png)

The operation selection tab is the first step when running RAiSD-AI operations. It has three main input sections:

1. **Run ID**: This is a unique identifier for each run. It helps you keep track of different runs and their results. The results of the run will be stored in a folder named after the run id.

2. **Operation Selection**: Here you can choose the type of operation you want to perform.

3. **Input Data**: This section allows you to input the data required for the selected operation. This can include files, folders, and parameters.

TODO: write something about how one operation will itself run the required ones before, maybe add a screenshot with an operation like sweep scan for that.

> Note: If the choice of run id or other input parameters will cause data to be overwritten, the GUI will show a warning and ask for confirmation before proceeding.

#### Parameter Input Tab

![Screenshot of the Run Page Parameter Input uncollapsed](/screenshots/run-page.parameter-input.run1.png)

The parameter input tab allows you to configure the parameters for the selected operations. The parameters are organized into sections based on category and there are specific sections each related to the selected operations. You can expand or collapse each section to focus on the parameters that are most relevant.

Most parameters have default values. To reset a parameter to its default value, click on the reset button next to it. If a parameter is invalid or missing, the GUI will show which parameters are causing the issue. You are only able to continue to the next step if all parameters are valid and the required ones are provided.

### History Page
blabla

### Settings Page
blabla

## Walktrough

show example of running raisdai sweep scan with screenshot of each page/tab