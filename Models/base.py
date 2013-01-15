#!/usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import pyodbc


Engine = create_engine ('mssql://CartoonAdmin:CartoonServerPassword@www.zhufengxm.com/CartoonServer', module = pyodbc)
base = declarative_base()
