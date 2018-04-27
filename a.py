import sys

class Tec2Vtk:
    def __init__(self):
        self.globalpointvar = []
        self.DATAPACKING = None
        self.VARIABLES = None
        self.ZONETYPE = None
        self.nvtx = {'FETRIANGLE': 3, 'FEBRICK': 8, 'FEQUADRILATERAL': 4, 'FETETRAHEDRON': 4}
        self.type = {'FETRIANGLE': 5, 'FEBRICK': 12, 'FEQUADRILATERAL': 9, 'FETETRAHEDRON': 10}
        self.out = None
        self.N = None
        self.E = None
        self.file = None

    def point_data(self):
        self.out.write("POINT_DATA {}\n".format(int(self.N)))
        start = 2
        if "Z" in self.VARIABLES:
            start = 3
        for i in range(start, len(self.VARIABLES)):
            self.out.write("SCALARS {} float 1\n".format(self.VARIABLES[i]))
            self.out.write("LOOKUP_TABLE default\n")
            for j in range(0, int(self.N)):
                self.out.write("{}\n".format(self.globalpointvar[j][i]))

    def cells(self):
        self.out.write("CELLS {} {}\n".format(int(self.E), int(self.E)*(1 + self.nvtx[self.ZONETYPE])))
        for j in range(0,int(self.E)):
            self.out.write("{} ".format(self.nvtx[self.ZONETYPE]))
            a = self.file.readline();
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

    def variables(self):
        a = self.file.readline();
        splitted = a.split('=', 1)
        key = splitted[0].strip()
        count = splitted[1].count(',');
        splitted = splitted[1].split(',', count)
        self.VARIABLES = [x.strip().strip('"') for x in splitted]

    def title(self):
        a = self.file.readline();
        splitted = a.split('=', 1)
        key = splitted[0].strip()
        TITLE = splitted[1].strip().strip('"')
        #out.write(TITLE+"\n")
        self.out.write("All in VTK format\n")
        self.out.write("ASCII\n")
        self.out.write("DATASET UNSTRUCTURED_GRID\n")

    def zone(self):
        a = self.file.readline();
        splitted = a.split(' ', 1)
        count = splitted[1].count(',');
        splitted = splitted[1].split(',', count)
        al = splitted[0].split('=', 1)
        self.N = al[1].strip()
        al = splitted[1].split('=', 1)
        self.E = al[1].strip()
        al = splitted[2].split('=', 1)
        self.DATAPACKING = al[1].strip()
        al = splitted[3].split('=', 1)
        self.ZONETYPE = al[1].strip()

    def points(self):
        self.out.write("POINTS " + self.N + " float\n")
        self.globalpointvar = []
        if self.DATAPACKING == "POINT":
            for j in range(0,int(self.N)):
                pointvar = []
                a = self.file.readline()
                a = a.split(' ', 1)
                pointvar.append(float(a[0]))
                for i in range(1,len(VARIABLES)):
                    a = a[1].strip().split(' ', 1)
                    pointvar.append(float(a[0]))
                if "Z" in VARIABLES:
                    self.out.write("{} {} {}\n".format(pointvar[0], pointvar[1], pointvar[2]))
                else:
                    self.out.write("{} {} {}\n".format(pointvar[0], pointvar[1], 0.0))
                self.globalpointvar.append(pointvar)
        else:
            pointvar = []
            for i in range(0,len(self.VARIABLES)):
                a = self.file.readline()
                temppointvar = []
                for token in a.split():
                    temppointvar.append(token)
                pointvar.append(temppointvar)
            for i in range(0,int(self.N)):
                if "Z" in self.VARIABLES:
                    self.out.write("{} {} {}\n".format(pointvar[0][i], pointvar[1][i], pointvar[2][i]))
                else:
                    self.out.write("{} {} {}\n".format(pointvar[0][i], pointvar[1][i], 0.0))

            for i in range(0,int(self.N)):
                templist = []
                for j in range(0,len(self.VARIABLES)):
                    templist.append(pointvar[j][i])
                self.globalpointvar.append(templist)


    def convert(self, datfile):

        self.file = open(datfile, "r")
        self.out = open("out.vtk", "w")
        self.out.write("# vtk DataFile Version 3.0\n")

        self.title()
        self.variables()
        self.zone()
        self.points()
        self.cells()
        self.point_data()






t2v = Tec2Vtk()
t2v.convert(sys.argv[1])
