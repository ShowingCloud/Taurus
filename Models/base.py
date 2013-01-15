#!/usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import pyodbc


Engine = create_engine ('mssql://CartoonAdmin:CartoonServerPassword@61.147.79.115/CartoonServer', module = pyodbc)
base = declarative_base()
