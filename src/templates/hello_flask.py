#/usr/bin/env python
import MySQLdb
import getXML
import json
from pprint import pprint
from flask import *
import libvirt
import sys
import random
import subprocess
# Create the application.
APP = Flask(__name__)

def getAttrs(object):
  return filter(lambda m: callable(getattr(object, m)), dir(object))


def rchop(thestring, ending):
  if thestring.endswith(ending):
    return thestring[:-len(ending)]
  return thestring


def getPCID(vmid):

    con = MySQLdb.connect( "localhost", "root", "mysql" ,"VM_INFO")
    cursor = con.cursor()
    sql = 'Select pcid From VM_ADDR where id = %d'%int(vmid);
    cursor.execute(sql)
    result = cursor.fetchall()
    for row in result:
        PC_ID = row[0]
    return PC_ID 

def getTypeID(vmid):
    con = MySQLdb.connect( "localhost", "root", "mysql" ,"VM_INFO")
    cursor = con.cursor()
    sql = 'Select tid From VM_ADDR where id = %d'%int(vmid);
    cursor.execute(sql)
    result = cursor.fetchall()
    for row in result:
        Type_ID = row[0]
    return Type_ID

def getName(vmid):
    con = MySQLdb.connect( "localhost", "root", "mysql" ,"VM_INFO")
    cursor = con.cursor()
    sql = 'Select name From VM_ADDR where id = %d'%int(vmid);
    cursor.execute(sql)
    result = cursor.fetchall()
    for row in result:
        name = row[0]
    return name   
def getPCIP(vmid):
    a = getPCID(vmid)
    PC_Ip = open("pm_file","r").readlines()[a]
    vmid = int(rchop(str(vmid),str(a)))
    returnval=[0,0]
    returnval[0]=PC_Ip
    returnval[1]= vmid
    return returnval

def createDatabase():
    con = MySQLdb.connect( "localhost" ,"root","mysql")
    cursor=con.cursor()
    sql = 'CREATE DATABASE IF NOT EXISTS VM_INFO';
    cursor.execute(sql)
    sql = 'use VM_INFO';
    cursor.execute(sql)
    sql = 'CREATE TABLE  IF NOT EXISTS VM_ADDR( id INT(10)  PRIMARY KEY, pcid INT, tid INT, name VARCHAR(50))'
    cursor.execute(sql)


def getVm(pmid):
    con = MySQLdb.connect( "localhost", "root", "mysql" ,"VM_INFO")
    cursor = con.cursor()
    sql = 'Select id From VM_ADDR where pcid = %d'%int(pmid);
    cursor.execute(sql)
    result = cursor.fetchall()
    liste = []
    for row in result:
        liste.append(int(row[0]))
    return liste   
#print getAttrs('Foo bar'.split(' '))


@APP.route('/vm/destroy')
def destroy():
    try:
        Actual_vmid = request.args.get('vmid')
        returnval= getPCIP(Actual_vmid)
        PC_Ip = returnval[0]
        vmid = returnval[1] 
        conn = libvirt.open("qemu+ssh://"+ PC_Ip[:len(PC_Ip)-1]+"/system")


        conn.lookupByID(int(vmid)).undefine()
        conn.lookupByID(int(vmid)).destroy()
        con = MySQLdb.connect("localhost", "root", "mysql","VM_INFO")
        cursor = con.cursor()
        sql = "DELETE FROM VM_ADDR where id LIKE %d"%int(Actual_vmid);
        if  cursor.execute(sql) is 0:
            return render_template('print.html',jsonObj={ "status":1})
        con.commit()
        return render_template('print.html',jsonObj={ "status":1})
    except:
        return render_template('print.html',jsonObj={ "status":0})

@APP.route('/vm/create')
def create():

    try:
        flag=0
        name = request.args.get('name')
        instance_type = request.args.get('instance_type')
        image_id = request.args.get('image_id')

        with open('flavor_file.json') as data_file:
            data = json.load(data_file)
        pprint(data)
        nocpu = data['types'][int(instance_type)-1]['cpu']
        ram = data['types'][int(instance_type)-1]['ram']
        disk = data['types'][int(instance_type)-1]['disk']
        num_lines = sum(1 for line in open('pm_file'))
        for i in range(num_lines):
            PC_Ip = open("pm_file","r").readlines()[a]
            mem_free = subprocess.Popen(["ssh",PC_Ip,"grep","MemFree","/proc/meminfo"],stdout=subprocess.PIPE).communicate()[0].strip('\n')

            if int(mem_free[:-2]) > ram :
                conn = libvirt.open("qemu+ssh://"+ PC_Ip[:len(PC_Ip)-1] + "/system")
                connect= conn.defineXML(getXML.get(name,1,nocpu,ram,disk))
                if connect.create() is not 0:
                    return render_template('print.html',jsonObj=0)
                vmid = conn.lookupByName(name).ID()
                con = MySQLdb.connect("localhost", "root", "mysql","VM_INFO")
                cursor = con.cursor()
                sql ="INSERT INTO VM_ADDR (id,pcid, tid, name) VALUES ({}, {},{},'{}')".format(int(str(vmid) + str(a)), a, int(instance_type),name)
                print sql
                if cursor.execute(sql)!= 1:
                    return render_template('print.html',jsonObj=0) 
                con.commit()
                return render_template('print.html',jsonObj={"vmid":int(str(vmid)+str(a))})
            except:
                return render_template('print.html',jsonObj=0)
        else:
            return render_template('print.html',jsonObj=0)
@APP.route('/vm/query')
def VM_QUERY():
    
    try:
        vmid = request.args.get('vmid')
        PC_ID = getPCID(vmid)
        Type_ID = getTypeID(vmid)
        Name = getName(vmid)
        jsonObj= {
            "vmid": int(vmid),
            "name" : Name,
            "instance_type": int(Type_ID),
            "pmid": int(PC_ID)
            }
        return render_template('print.html',jsonObj=jsonObj)
    except:
        return render_template('print.html',jsonObj=0)

@APP.route('/pm/listvms')
def List_VM(getsize=False):
    pmid = request.args.get('pmid')
    liste = getVm(pmid)

    if len(liste) :
        return render_template('print.html',jsonObj={ "vmids":liste })
    else:
        return render_template('print.html',jsonObj=0)

@APP.route('/pm/list')
def PM_List():
    num_lines = sum(1 for line in open('pm_file'))
    liste=[]
    for i in range(num_lines):
        liste.append(i)
    return render_template('print.html',jsonObj={"pmids":liste})

@APP.route('/vm/types')
def VM_Type():
    with open('flavor_file.json') as data_file:
        data = json.load(data_file)
        pprint(data)
    return json.dumps(data,indent=4)

@APP.route('/pm/query')
def PM_QUERY():
    pmid = request.args.get('pmid')
    PC_Ip = open("pm_file","r").readlines()[int(pmid)]

    mem_free = subprocess.Popen(["ssh",PC_Ip,"grep","MemFree","/proc/meminfo"],stdout=subprocess.PIPE).communicate()[0].strip('\n')
    mem_total = subprocess.Popen(["ssh",PC_Ip,"grep","MemTotal","/proc/meminfo"],stdout=subprocess.PIPE).communicate()[0].strip('\n')
    cpu_total = subprocess.Popen(["ssh",PC_Ip,"grep","processor","/proc/cpuinfo"],stdout=subprocess.PIPE).communicate()[0].strip('\n')
    Count_vm = len(getVm(pmid))
    return render_template("print.html",jsonObj = { "capacity": {"ram": mem_total,"cpu":int(cpu_total[-1])+1},"free":{"ram":mem_free},"vms":Count_vm})
if __name__ == '__main__':
    createDatabase()
    APP.debug=True
    APP.run()
