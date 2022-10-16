import ast
from sys import orig_argv
from cohesion_category import CohesionCategory
from coupling_category import CouplingCategory
from qmood_category import QMOODCategory
from size_category import SizeCategory
from complexity_category import ComplexityCategory
from python_file import Python_File
from classDecl import *


class Init_Visitor(ast.NodeVisitor):

    def __init__(self, python_file):
        self.python_file = python_file
        self.currClass = None

    # Visit the node of the whole .py file
    def visit_Module(self, node):
        # We need for loop because in one .py file can be more than one classes
        for child in node.body:
            # We want to start analyzing only for classes and no for non oop code
            if (isinstance(child, ast.ClassDef)):
                self.visit_ClassDef(child)

    # Visit the node of a class
    def visit_ClassDef(self, node):
        print(node.name)
        # Create class instance
        classObj = Class(node.name, self.python_file, node, CohesionCategory(), ComplexityCategory(), CouplingCategory(), QMOODCategory(), SizeCategory())
        self.currClass = classObj
        self.python_file.addClass(classObj)
        for child in node.body:
            # We will visit the whole node of a method
            if (isinstance(child, ast.FunctionDef)):
                self.visit_FunctionDef(child)
            else:
                # In else, we are outside of the methods, so we will visit this part
                AttrVisitor(classObj).visit(child)

    # Visit the node of a method in a class
    def visit_FunctionDef(self, node):
        print(node.name)
        self.currClass.add_method(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.generic_visit(node)

    # Visitor to get instance attributes and class attributes that declared in method's body!
    def visit_Attribute(self, node):
        if (isinstance(node.ctx, ast.Store)):
            # Instance attributes
            if (node.value.id == "self"):
                print(node.attr)
                self.currClass.add_instanceAttribute(node.attr)
            # Class attributes that declared inside a method
            else:
                print(node.attr)
                self.currClass.add_classAttribute(node.attr)


class AttrVisitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj

    # Visitor to get ONLY class attributes that declared outside of methods!
    def visit_Name(self, node):
        if (isinstance(node.ctx, ast.Store)):
            print(node.id)
            self.classObj.add_classAttribute(node.id)


class visit_methodsForLCOM(ast.NodeVisitor):

    def __init__(self, classObj: Class):
        # A dictionary with key the function name and with value a list with the fields/attrs that the function uses
        self.uses_in_method = {}
        self.classObj = classObj

    def visit_ClassDef(self, node):
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit_FunctionDef(child)
        # return the dictionary after walk to all class node
        return self.uses_in_method

    def visit_FunctionDef(self, node):
        values = []
        for child in node.body:
            exp = ""
            if isinstance(child, ast.Assign):
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Attribute):
                    exp = str(child.targets[0].attr)
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Name):
                    exp = str(child.targets[0].id)
            elif (isinstance(child, ast.AugAssign)):
                if isinstance(child.target, ast.Attribute):
                    exp = str(child.target.attr)
                if isinstance(child.target, ast.Name):
                    exp = str(child.target.id)
            elif (isinstance(child, ast.Expr)):
                for i in range(0, len(child.value.args), 1):
                    if (isinstance(child.value.args[i], ast.BinOp)):
                        exp = child.value.args[i].right.attr
                    elif (isinstance(child.value.args[i], ast.Attribute)):
                        exp = child.value.args[i].attr

            if (exp != "" and exp in self.classObj.get_fields()):
                values.append(exp)

        self.uses_in_method[node.name] = values
