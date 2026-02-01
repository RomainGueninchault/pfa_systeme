#!/usr/bin/env python

import sys
import yaml
import os
import tempfile
import shutil
import time

def loadConfig(startPath):
    currentDir=startPath
    if os.path.isfile(os.path.join(startPath,"config.yml"))==False:
        return None
    parent=loadConfig(os.path.join(startPath,".."))
    mergeConfig={}
    rootPath=currentDir
    if parent!=None:
        mergeConfig=parent
    # now load local config.yml
    localConfig={}
    try:
        with open(os.path.join(startPath,"config.yml")) as f:
            localConfig=yaml.full_load(f)
    except:
        print("error while loading config.yml from ",currentDir)
    for k in localConfig.keys():
        overrideMode=False
        lk=k
        mk=k
        if k[0]=='=':
            mk=k[1:]
            overrideMode=True
        if not mk in mergeConfig: # just add the new values
            mergeConfig[mk]=localConfig[lk]
        else:
            if type(localConfig[lk]) not in [dict,list]: # override value
                mergeConfig[mk]=localConfig[lk]
            else:
                # merge ?
                if overrideMode==True:
                    mergeConfig[mk]=localConfig[lk]
                else:
                    if type(localConfig[k])==dict:
                        for a in localConfig[k]:
                            mergeConfig[k][a]=localConfig[k][a]
                    else: # list
                        for a in localConfig[k]:
                            mergeConfig[k].append(a)
    if 'rootPath' not in mergeConfig:
        mergeConfig['rootPath']=os.path.abspath(startPath)
    mergeConfig['exoPath']=startPath
    return mergeConfig

def getExercices(path):
    exos=[]
    for root,dirs,files in os.walk(path):
        if 'config.yml' in files:
            c=loadConfig(root)
            if 'name' in c:
                exos.append(c)
    return exos

CWD=os.path.abspath(".")

HOME=os.getenv("TM_HOME")
if HOME==None:
    HOME=os.path.join(os.getenv("HOME"),".trainme")
os.makedirs(HOME, exist_ok=True)

from tm_args import argParser
args=argParser.parse_args()



if args.cmd=="config":
    print("actual home storage dir is: ",HOME)    
elif args.cmd=="update":
    # move to HOME and perform a git pull
    os.chdir(HOME)
    for e in os.listdir(HOME):
        if os.path.isdir(e):
            print("updating ",e,"...")
            os.chdir(e)
            os.system("git pull")
            os.chdir(HOME)
elif args.cmd=='import':
    # move to HOME and perform a git clone
    os.chdir(HOME)
    os.system("git clone "+args.url)
elif args.cmd=='list':
    os.chdir(HOME)
    for e in os.listdir(HOME):
        if os.path.isdir(e):
            print(e,':')
            os.chdir(e)
            for exo in getExercices("."):
                print(exo['name'],':',exo.get('desc','no description'))

elif args.cmd=="run":
    exos=getExercices(HOME)
    exo=[]
    for e in exos:
        if e.get('name')==args.exercice:
            exo.append(e)
    if len(exo)==0:
        print(args.exercice," not found!")
        sys.exit(1)
    if len(exo)>1:
        print("multiple exercices with name ", args.exercice,"found! use repository@exoName")
    config=exo[0]
    exercice=os.path.abspath(config['exoPath'])
    exerciceBaseName=os.path.basename(exercice)
    #loading config:
    rootPath=config['rootPath']
    
    # prepare working dir
    if args.dir!=None:
        workingDir=args.dir
    elif args.tmp==True:
        workingDir=tempfile.mkdtemp(prefix='tm_')
    else:
        workingDir=CWD
    # checking working dir is empty:
    if len(os.listdir(workingDir))>0:
        print("working dir (",workingDir,") is not empty, aborting")
        exit(1)
    
    ## deploying selected exercice:
    # make a copy into a temp folder
    dstDir=tempfile.mkdtemp(prefix='tm_')
    tempExerciceDir=os.path.join(dstDir,exerciceBaseName)
    print("tempExerciceDir is ",tempExerciceDir)
    # check if there is a "common" dir un rootPath
    if os.path.isdir(os.path.join(rootPath,"common")):
        print("copy common dir")
        shutil.copytree(os.path.join(rootPath,"common"),tempExerciceDir)
    shutil.copytree(exercice,tempExerciceDir,dirs_exist_ok=True)
    print("prepare directory is: ",dstDir)
    # run prepare cmd
    os.chdir(tempExerciceDir)
    try:
        prepareCmd=config['commands']['prepare']
        if os.system(prepareCmd)!=0:
            print("cmd failed: ",prepareCmd)
            exit(1)
    except:
        pass

    for source in config['distributes']:
        if (type(source)==str):
            path=os.path.join(tempExerciceDir,source)
            if os.path.isdir(path):
                shutil.copytree(path,workingDir)
            else:
                shutil.copy(path,workingDir)
        else:
            for src,dst in source.items():
                path=os.path.join(tempExerciceDir,src)
                if os.path.isdir(path):
                    shutil.copytree(path,workingDir)
                else:
                    shutil.copy(path,workingDir)
                os.rename(os.path.join(workingDir,src),os.path.join(workingDir,dst))
    print(workingDir," ready")
    os.chdir(workingDir)
    shutil.rmtree(tempExerciceDir)
    # start timer (i.e. but time.now() into .time file)
    with open(".time","w") as f:
        f.write(str(time.time()))
    with open(".origin","w") as f:
        f.write(exercice)
    # open a terminal into the temp dir
    # os.system('x-terminal-emulator')
elif args.cmd=="check":
    if not os.path.isfile(".time") or not os.path.isfile(".origin"):
        print("current directory is not an exercice")
        sys.exit(1)
    with open(".origin") as f:
        exoDir=f.read()
    c=loadConfig(exoDir)
    if os.system(c['commands']['execute'])!=0:
        print("exercice failed")
        sys.exit(1)
    with open(".time") as f:
        startTime=float(f.read())
    elapsedTime=time.time()-startTime
    elapsedTime=elapsedTime/60.0
    if elapsedTime>c['timeout']:
        print("exercice failed: time limit exceeded (",elapsedTime,"min, ",c['timeout'],"min allowed)")
        sys.exit(1)
    print("exercice succeeded, you make it in ",elapsedTime,"min (",c['timeout'],"min allowed)")
    # record the exercice as done in HOME