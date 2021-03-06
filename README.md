## Foreword

When you running tempest, you probably want to review result in a human manner.

You running it once again... and again... and a couple times more the next day... you end up with 20+ files in '.testrepository' folder. Start digging how specific tempest test was executed yesterday, how changed result is today. 'grep', 'less'... Brain goes hot.
...
Honestly, Subunit's CLI output is good enough for reading the word PASSED at the end...and the summary.

So, there is a need to:
- import tempest tests results
- match tests by Class, test_name and options
- produce some sort of a report to work with test statuses and track them over time
- Have error messages be added to the report

## Usage

This util is originally intended for 'import-match-export' flow to produce CSV with tests matched by Class and name against the list of tests that was originally executed.

```python tempest_parser.py -c matched.csv tempest.log```

Folder also can be used:

```python tempest_parser.py -c matched.csv folder1```

And finally, here is HTML report

```python tempest_parser.py -r trending.html tempest.xml```

or

```python tempest_parser.py -r trending.html folder1```

## Imported Formats

### .log files
Bare tempest output captured with either rediurection or by copying XX numbered files from `.testrepository` folder.
LOG parser anchors against lines started with specific strings. Make sure to remove leading evironment variables and worker report stuff.

### .xml files
Files exported from PyCharm UnitTests engine.

### .json files
[Rally](https://github.com/openstack/rally) tool export: 

```rally verify results --json --output-file result1.json```
