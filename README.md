# ratings_tab for Open edX


The Open edX module adds a new course tab that will calculate and display rating grades.

To include assignment to specific rating, abbreviation of it must include either 'R1' or 'R2' or 'Exam'

Add the module name `ratings_tab` to the *Advanced Module List* (`Settings -> Advanced Settings`) to display the ratings_tab after installing the module.

``` json
[
    "ratings_tab"
]
```

**Installation**

The installation method is similar to installing XBlocks or other custom modules.

``` bash
cd $(tutor config printroot)/env/build/openedx/requirements
echo "git+https://github.com/xmaksarel/ratings_tab.git" >> private.txt

# Build the images and then restart Tutor
tutor images build openedx
tutor local stop & tutor local start -d
```