import sys
import os
from enum import Enum

class VTKTYPE(Enum):
    TABLE = 0
    UNSTR = 1


class Tec2Vtk:

    '''
    Only Python3!
    TITLE must be provided in tec file.
    There are only two categories: unstructured and table. If input tec file is FE-type then produce unstructured grid, 
                                                           if input tec file is ordered-ijk then produce table.
    '''

    def __init__(self):
        self.globalpointvar = [] # variables: First index corresponds to variables while second one to point
        self.DATAPACKING = None # POINT | BLOCK
        self.VARIABLES = None # Such as X, Y, Z, temperature, ...
        self.ZONETYPE = None # One of FE-types or stays as None for non-FE-types
        self.nvtx = {'FETRIANGLE': 3, 'FEBRICK': 8, 'FEQUADRILATERAL': 4, 'FETETRAHEDRON': 4} # (tec & vtk) number of vertices.
        self.type = {'FETRIANGLE': 5, 'FEBRICK': 12, 'FEQUADRILATERAL': 9, 'FETETRAHEDRON': 10} # (tec -> vtk) element type.
        self.vtk_type = None # One of VTKTYPE
        self.out = None # Output file
        self.N = None # Number of points
        self.E = None # Number of cells
        self.file = None # Input file
        self.I = None
        self.J = None
        self.K = None
        self.NP = None # Represents either N or I*J*K
        self.TITLE = None

    def title(self):
        a = self.file.readline();
        while a[0] == '\n':
            a = self.file.readline();
        splitted = a.split('=', 1)
        key = splitted[0].strip()
        self.TITLE = splitted[1].strip().strip('"')

    def variables(self):
        a = self.file.readline();
        while a[0] == '\n':
            a = self.file.readline();
        splitted = a.split('=', 1)
        key = splitted[0].strip()
        count = splitted[1].count(',');
        splitted = splitted[1].split(',', count)
        self.VARIABLES = [x.strip().strip('"') for x in splitted]

    def zone(self):
        a = self.file.readline();
        while a[0] == '\n':
            a = self.file.readline();
        splitted = a.split(' ', 1)
        count = splitted[1].count(',');
        splitted = splitted[1].split(',', count)
        for i in splitted:
            al = i.split('=', 1)
            self.det_zone_var(al)

        # Determine VTKTYPE
        if self.I != None or self.J != None or self.K != None:
            self.vtk_type = VTKTYPE.TABLE
        else:
            self.vtk_type = VTKTYPE.UNSTR

        # Determine NP
        if self.vtk_type == VTKTYPE.UNSTR:
            self.out = open("out.vtk", "w")
            self.out.write("# vtk DataFile Version 3.0\n")
            self.out.write(self.TITLE+"\n")
            self.out.write("ASCII\n")
            self.out.write("DATASET UNSTRUCTURED_GRID\n")
            self.NP = int(self.N)
        else:
            self.out = open("out.csv", "w")
            self.NP = 1
            if self.I != None:
                self.NP *= self.I
            if self.J != None:
                self.NP *= self.J
            if self.K != None:
                self.NP *= self.K


    def point_data(self):
        if self.vtk_type == VTKTYPE.UNSTR:
            self.out.write("POINT_DATA {}\n".format(self.NP))
            start = 2
            if "Z" in self.VARIABLES:
                start = 3
            for i in range(start, len(self.VARIABLES)):
                self.out.write("SCALARS {} float 1\n".format(self.VARIABLES[i]))
                self.out.write("LOOKUP_TABLE default\n")
                for j in range(0, self.NP):
                    self.out.write("{}\n".format(self.globalpointvar[i][j]))
        else:
            for i in self.VARIABLES:
                self.out.write(i)
                if i != self.VARIABLES[-1]:
                    self.out.write(',')
            self.out.write('\n')
            for j in range(0, self.NP):
                for i in range(0, len(self.VARIABLES)):
                    self.out.write("{}".format(self.globalpointvar[i][j]))
                    if i != len(self.VARIABLES)-1:
                        self.out.write(',')
                self.out.write('\n')


    def cells(self):
        self.out.write("CELLS {} {}\n".format(int(self.E), int(self.E)*(1 + self.nvtx[self.ZONETYPE])))
        for j in range(0,int(self.E)):
            self.out.write("{} ".format(self.nvtx[self.ZONETYPE]))
            a = self.file.readline();
            while a[0] == '\n':
                a = self.file.readline();
            a = a.lstrip()
            a = a.split(' ', 1)
            self.out.write("{} ".format(int(a[0])-1))
            for i in range(1,self.nvtx[self.ZONETYPE]):
                a = a[1].strip().split(' ', 1)
                self.out.write("{} ".format(int(a[0])-1))
            self.out.write("\n")
        
        # cell types
        self.out.write("CELL_TYPES {}\n".format(int(self.E)))
        for i in range(0, int(self.E)):
            self.out.write("{}\n".format(self.type[self.ZONETYPE]))

    def det_zone_var(self, al):
        s = al[1].strip()
        if al[0].strip() == 'N':
            self.N = s
        elif al[0].strip() == 'E':
            self.E = s
        elif al[0].strip() == 'DATAPACKING' or al[0].strip() == 'F':
            self.DATAPACKING = s
        elif al[0].strip() == 'ZONETYPE':
            self.ZONETYPE = s
        elif al[0].strip() == 'I':
            self.I = int(s)
        elif al[0].strip() == 'J':
            self.J = int(s)
        elif al[0].strip() == 'K':
            self.K = int(s)

    def points(self):
        if self.vtk_type == VTKTYPE.UNSTR:
            self.out.write("POINTS " + str(self.NP) + " float\n")
        self.globalpointvar = []
        if self.DATAPACKING == "POINT":
            #pointvar = len(self.VARIABLES) * [[]];
            pointvar = [[] for _ in range(len(self.VARIABLES))]
            for j in range(0, self.NP):
                a = self.file.readline()
                while a[0] == '\n':
                    a = self.file.readline();
                a = a.lstrip()
                a = a.split(' ', 1)
                pointvar[0].append(float(a[0]))
                for i in range(1,len(self.VARIABLES)):
                    a = a[1].strip().split(' ', 1)
                    pointvar[i].append(float(a[0]))
                if self.vtk_type == VTKTYPE.UNSTR:
                    if "Z" in self.VARIABLES:
                        self.out.write("{} {} {}\n".format(pointvar[0][j], pointvar[1][j], pointvar[2][j]))
                    else:
                        self.out.write("{} {} {}\n".format(pointvar[0][j], pointvar[1][j], 0.0))

            for j in range(0,len(self.VARIABLES)):
                templist = []
                for i in range(0,self.NP):
                    templist.append(pointvar[j][i])
                self.globalpointvar.append(templist)
        else:
            pointvar = []
            for i in range(0,len(self.VARIABLES)):
                total_token = 0
                temppointvar = []
                while (total_token < self.NP):
                    a = self.file.readline()
                    while a[0] == '\n':
                        a = self.file.readline();
                    asplit = a.split()
                    for token in asplit:
                        temppointvar.append(token)
                    total_token += len(asplit)
                pointvar.append(temppointvar)

            if self.vtk_type == VTKTYPE.UNSTR:
                for i in range(0,self.NP):
                    if "Z" in self.VARIABLES:
                        self.out.write("{} {} {}\n".format(pointvar[0][i], pointvar[1][i], pointvar[2][i]))
                    else:
                        self.out.write("{} {} {}\n".format(pointvar[0][i], pointvar[1][i], 0.0))

            for j in range(0,len(self.VARIABLES)):
                templist = []
                for i in range(0,self.NP):
                    templist.append(pointvar[j][i])
                self.globalpointvar.append(templist)

    def coordinates(self):
        pointvar = []
        for i in range(0,len(self.VARIABLES)):
            total_token = 0
            temppointvar = []
            while (total_token < self.NP):
                a = self.file.readline()
                asplit = a.split()
                for token in asplit:
                    temppointvar.append(token)
                total_token += len(asplit)
            pointvar.append(temppointvar)

        for j in range(0,len(self.VARIABLES)):
            templist = []
            for i in range(0,self.NP):
                templist.append(pointvar[j][i])
            self.globalpointvar.append(templist)

        if self.I != None:    
            self.out.write("X_COORDINATES {} float\n".format(self.NP))
            for i in self.globalpointvar[0]:
                self.out.write(i+" ")
            self.out.write("\n")
        if self.J != None:    
            self.out.write("Y_COORDINATES {} float\n".format(self.NP))
            for i in self.globalpointvar[1]:
                self.out.write(i+" ")
            self.out.write("\n")
        if self.K != None:    
            self.out.write("Z_COORDINATES {} float\n".format(self.NP))
            for i in self.globalpointvar[2]:
                self.out.write(i+" ")
            self.out.write("\n")


    def dimensions(self):
        self.out.write("DIMENSIONS ")
        if self.I != None:
            self.out.write("{} ".format(self.I))
        if self.J != None:
            self.out.write("{} ".format(self.J))
        if self.K != None:
            self.out.write("{} ".format(self.K))
        self.out.write("\n")


    def convert(self, datfile):

        self.file = open(datfile, "r")

        self.title()
        self.variables()
        self.zone()
        self.points()
        if self.vtk_type == VTKTYPE.UNSTR:
            self.cells()
        self.point_data()







t2v = Tec2Vtk()
t2v.convert(sys.argv[1])
