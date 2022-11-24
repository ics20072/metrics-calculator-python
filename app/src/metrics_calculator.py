from os import listdir
from os.path import isfile, join
from visitor import LCOM_Visitor
from visitor import Hierarchy_Visitor
from visitor import MethodsCalled_Visitor
from visitor import MPC_Visitor
from visitor import CBO_Visitor
from classDecl import Class


# In this class exists methods that calculates metrics for the whole project
class MetricsCalculator:

    def __init__(self, classObj: Class):
        self.classObj = classObj
        self.calcWMPC2()
        self.calcNOM()
        self.calcSIZE2()
        self.calcWAC()
        self.calcMPC()
        self.calcCBO()
        self.calcLCOM()
        self.calcLOC()
        self.calcRFC()
        self.calcNOCC()

    # Count the Classes that exists in the whole project.
    # The method will called only once time when we want to print the results
    @staticmethod
    def calcNOC(files):
        noc = 0
        for python_file in files:
            noc += len(python_file.getFileClasses())

        return noc

    # Count the number of methods for each class in the project
    def calcNOM(self):
        self.classObj.getSizeCategoryMetrics().setNOM(len(self.classObj.get_methods()))

    # Count the number of methods for each class in the project
    def calcWMPC2(self):
        self.classObj.getComplexityCategoryMetrics().setWMPC2(len(self.classObj.get_methods()))

    # Count the number of methods and fields for each class in the project
    def calcSIZE2(self):
        self.classObj.getSizeCategoryMetrics().setSIZE2(len(self.classObj.get_methods()) + len(self.classObj.get_fields()))

    # Count the number of fields for each class
    def calcWAC(self):
        self.classObj.getSizeCategoryMetrics().setWAC(len(self.classObj.get_fields()))

    # Calculate LCOM Metric
    def calcLCOM(self):
        cohesive = 0
        non_cohesive = 0

        uses_in_methods = LCOM_Visitor(self.classObj).visit(self.classObj.getClassAstNode())

        for i in range(0, len(uses_in_methods), 1):
            for j in range(i + 1, len(uses_in_methods), 1):
                if (len(list(set(list(uses_in_methods.values())[i]).intersection(list(uses_in_methods.values())[j])))) == 0:
                    non_cohesive += 1
                else:
                    cohesive += 1

        if (non_cohesive - cohesive < 0):
            self.classObj.getCohesionCategoryMetrics().set_LCOM(0)
        else:
            self.classObj.getCohesionCategoryMetrics().set_LCOM(non_cohesive - cohesive)

    # Calculate RFC Metric
    def calcRFC(self):
        remoteMethodsSum = len(MethodsCalled_Visitor(self.classObj).visit_ClassDef(self.classObj.getClassAstNode()))
        self.classObj.getComplexityCategoryMetrics().setRFC(self.classObj.getSizeCategoryMetrics().getNOM() + remoteMethodsSum)

    # Calculate NOCC Metric
    def calcNOCC(self):
        allParentClasses = []
        myClassChildrenClasses = 0
        for pythonFile in self.classObj.getPyFileObj().getProject().get_files():
            for classObj in pythonFile.getFileClasses():
                allParentClasses = allParentClasses + Hierarchy_Visitor(classObj).visit_ClassDef(classObj.getClassAstNode())
        for myClass in allParentClasses:
            if (myClass == self.classObj.name):
                myClassChildrenClasses = myClassChildrenClasses + 1

        self.classObj.getSizeCategoryMetrics().setNOCC(myClassChildrenClasses)

    # Calculate LOC Metric
    def calcLOC(self):
        self.classObj.getSizeCategoryMetrics().setLOC(self.countIn(self.classObj.getPyFileObj().getProject().get_root_folder_path()))

    def calcMPC(self):
        messages = MPC_Visitor(self.classObj).visit(self.classObj.getClassAstNode())

        self.classObj.getCouplingCategoryMetrics().set_MPC(messages)

    def calcCBO(self):
        elements = CBO_Visitor(self.classObj).visit(self.classObj.getClassAstNode())
        elementsNoLibrary = set()
        keys = [k for k, v in elements.items()]
        for phythonFile in self.classObj.getPyFileObj().getProject().get_files():
            for classofFile in phythonFile.getFileClasses():
                if(classofFile.get_name() in keys):
                    for c, method in elements.items():
                        if(method in classofFile.get_methods()):
                            elementsNoLibrary.add(c)

        self.classObj.getCouplingCategoryMetrics().set_CBO(len(elementsNoLibrary))


##################### Methods necessary for LOC calculation #####################


    def countLinesInPath(self, path, directory):
        count = 0
        for line in open(join(directory, path), encoding="utf8"):
            count += 1
        return count

    def countLines(self, paths, directory):
        count = 0
        for path in paths:
            count = count + self.countLinesInPath(path, directory)
        return count

    def getPaths(self, directory):
        return [f for f in listdir(directory) if isfile(join(directory, f))]

    def countIn(self, directory):
        return self.countLines(self.getPaths(directory), directory)
