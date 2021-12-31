# APIMatchmak

## Running steps

1. Use getSDKVersion.py to get the SDK Version (including the min SDK version and target SDK version) of each app.

2. Use PresolvedCSVFilter.py to solve the descriptions.

3. Use lib/APIExtractor.jar to extract the method declarations and method invocations of each app.

4. Use the DatasetGenerator.py to generate the datasets for evaluation.

5. Run main.py to start. The arguments are detailed in the *getOptions()* function of main.py.
    

## The code structure

1. The *lib* folder contains a tool developed to extract the methods and APIs from the APK files.

2. The *Dataset* folder contains a file that points to the url of the openly available dataset.

3. The *Helper* folder contains some basic functions, such as the crawler we used to collect the descriptions.

4. The *Main* folder contains the contains the most core code, including the implementation of our approach.