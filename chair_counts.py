from collections import defaultdict
from typing import Set, List, Dict
import pandas as pd 
import numpy as np 
import sys 

class room_graph():
    '''
    Class for the (undirected) graph of the rooms.
    Methods to add vertices and edges, and to perform breath-first-search.
    '''

    def __init__(self) -> None:
        self.vertices = set()
        self.neighbors = defaultdict(list)

    def add_vertex(self, x):
        if x not in self.neighbors:
            self.neighbors[x] = []
        self.vertices.add(x)

    def add_edge(self, x, y):
        assert (x in self.vertices) and (y in self.vertices), "inputs must be existing vertices"
        assert x != y, "no loops allowed"

        if y not in self.neighbors[x]:
            self.neighbors[x].append(y)
        if x not in self.neighbors[y]:
            self.neighbors[y].append(x)

    def BFS(self, start_vertex) -> list:
        '''
        Breath-first search algorithm.
        Returns the list of vertices in the connected component of the start vertex.
        '''
        assert start_vertex in self.vertices, "invalid vertex"

        seen = {start_vertex}
        queue = [start_vertex]
        pointer = 0
        
        while pointer < len(queue):
            current_vertex = queue[pointer]
            neighbors = self.neighbors[current_vertex]
            for u in neighbors:
                if u not in seen:
                    seen.add(u)
                    queue.append(u)
            pointer += 1

        return queue
    
def compute_room_df(
        lines : list,
        chair_symbols = ['W', 'P', 'S', 'C'],
        room_anchor_symbol = "("
    ) -> pd.DataFrame:
    '''
    Produce a data frame with information about the rooms.
    Input is a list of lines, the chair symbols, and the anchor symbols for the rooms.
    '''

    # initialize dictionary for the coordinates of the different types of chairs
    chair_coords = {}
    for type_of_chair in chair_symbols:
        chair_coords[type_of_chair] = []

    # initialize dictionary for the anchor points of the different rooms
    room_anchor_coords = {}

    # verify if a character in the file is a valid vertex
    # room barriers are disallowed as vertices
    def valid_vertex(c):
        if c == " ":
            return True
        if c == room_anchor_symbol:
            return True
        if c in chair_symbols:
            return True
        return False

    # initialize the room graph
    g = room_graph()

    # loop through the characters in the file 
    i = 0
    while i < len(lines):
        j=0
        while j < len(lines[i]):            
            
            # check that the character defines a vertex
            if valid_vertex(lines[i][j]):
                g.add_vertex((i,j))

                # add edges to its neighbors to the right and down
                if i+1 < len(lines) and valid_vertex(lines[i+1][j]):
                    g.add_vertex((i+1,j))
                    g.add_edge((i,j), (i+1,j))
                if j+1 < len(lines[i]) and valid_vertex(lines[i][j+1]):
                    g.add_vertex((i,j+1))
                    g.add_edge((i,j), (i,j+1))
                
                # check for chairs
                if lines[i][j] in chair_symbols:
                    chair_coords[lines[i][j]].append((i,j))

                # process room names
                if lines[i][j] == "(":
                    current_room_name_list = []
                    current_room_anchor_coords = (i,j)
                    j += 1
                    while j < len(lines[i]) and lines[i][j] != ")":
                        current_room_name_list.append(lines[i][j])
                        j+= 1
                    current_room_name = "".join(current_room_name_list)
                    room_anchor_coords[current_room_name] = current_room_anchor_coords

            j += 1
        i += 1

    # create data frame for the rooms, initially only with the anchor points
    room_df = pd.DataFrame(room_anchor_coords)
    room_df = room_df.transpose()
    room_df = room_df.rename(columns={0: "anchor_x", 1: "anchor_y"})
    room_df = room_df.sort_index()

    # perform a BFS to collect all coordinates in each room
    room_areas = {}
    for r in room_df.index:
        area = g.BFS(room_anchor_coords[r])
        room_areas[r] = area

    # for each chair, find the corresponding room
    # collect the information as new columns in the data frame
    for type_of_chair in chair_symbols:
        room_df[type_of_chair] = np.zeros(len(room_df.index), dtype=int)
        for chair in chair_coords[type_of_chair]:
            for r in room_df.index:
                if chair in room_areas[r]:
                    room_df.loc[r, [type_of_chair]] +=1.0

    # return the data frame
    return room_df
    

def compute_output(
        room_df : pd.DataFrame,
        chair_symbols = ['W', 'P', 'S', 'C']
    )-> str:
    '''
    Computes the output string by parsing the data frame.
    '''

    # initialize a list that will be converted to a string
    output_list = []

    # compute the totals for the apartment
    output_list.append("total:\n")
    for type_of_chair in chair_symbols:
        assert type_of_chair in room_df.columns, "chair type does not appear in the dataframe"
        output_list.append(f"{type_of_chair}: {room_df[type_of_chair].sum()}, ")
    # remove the comma and space in the last element
    output_list[-1] = output_list[-1][:-2]
    output_list.append('\n')
    
    # append the totals for each room
    for r in room_df.index:
        output_list.append(f"{r}:\n")
        for type_of_chair in chair_symbols:
            output_list.append(f"{type_of_chair}: {room_df.loc[r, [type_of_chair]][0]}, ")
        # remove the comma and space in the last element
        output_list[-1] = output_list[-1][:-2]
        output_list.append('\n')

    # join the strings into the output string
    output_string = "".join(output_list)

    return output_string


if __name__ == "__main__":

    # read file 
    file = sys.argv[1]
    with open(file, 'r') as f:
        lines = f.readlines()

    # compute the data frame and the output
    room_df = compute_room_df(lines)
    output = compute_output(room_df)

    print(output)