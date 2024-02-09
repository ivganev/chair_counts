# Chair Counts

This project provides a command line tool to read a file containing the floor plan of an apartment with the rooms and chairs marked, and to produce a summary of the number and types of chairs in different rooms.

The main algorithm is a breath-first search on a graph produced from the input file. The connected components of this graph are the various rooms. The chairs appear as certain nodes of this graph. 



## Requirements

[Pandas](https://pandas.pydata.org/)

[Numpy](https://numpy.org/)

## Running the code

Run the following with `<file_name>` replaced by the name of the file with the plan of the apartment:

```
python chair_counts.py <file_name>
```

## Possible improvements
* create unit tests.
* check for chairs during the breath-first search so that 
the coordinates of all points in a room do not need to be stored.

