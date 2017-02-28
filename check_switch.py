#!/usr/bin/python
import sys,argparse,re,netsnmp

def getmodel(session):
    model=0;
    oid = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.2.1.1.1.0'))
    res = session.get(oid)[0]
    if session.ErrorInd != 0:
        print "SNMP error: "+session.ErrorStr
        sys.exit(3)
    if res == None:
        return 0
    elif re.search("procurve", res, re.IGNORECASE):
        return 4                                    #HP Procurve
    elif re.search("A55[0-9]{1}[0-9]{1}", res, re.IGNORECASE):
        return 1                                    #HP A5500
    elif re.search("57[0-9]{1}[0-9]{1}", res, re.IGNORECASE):
        return 5                                    #HP 5700
    elif re.search("A31[0-9]{1}[0-9]{1}", res, re.IGNORECASE):
        return 2                                    #HP A3100
    elif re.search("HP 75[0-9]{1}[0-9]{1}", res, re.IGNORECASE):
        return 3                                    #HP 7510
    return 0


def getcpu(session, model, modules=[]):
    oid = []
    if len(modules) == 0:
        if model == 1:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.6.65'))
        elif model == 2:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.6.11'))
        elif model == 4:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.11.2.14.11.5.1.9.6.1.0'))
        elif model == 5:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.6.192'))
        else:
            return 0
    else:
        for i in range(len(modules)):
           if model == 3:
               oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.6.'+str(modules[i])))
        if len(oid) == 0:
            return 0
    res = session.get(oid)
    return res

def getramusage(session, model, modules=[]):
    oid = []
    if len(modules) == 0:
        if model == 5:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.8.192'))
        elif model == 1:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.8.65'))
        elif model == 2:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.8.11'))
        else:
            return 0
    else:
        for i in range(len(modules)):
            if model == 3:
                oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.8.'+str(modules[i])))
        if len(oid) == 0:
            return 0
    res = session.get(oid)
    return res

def getramsize(session, model, modules=[]):
    oid = []
    if len(modules) == 0:
        if model == 5:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.10.192'))
        elif model == 1:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.10.65'))
        elif model == 2:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.10.11'))
        else:
            return 0
    else:
        for i in range(len(modules)):
            if model == 3:
                oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.10.'+str(modules[i])))
        if len(oid) == 0:
            return 0
    res = session.get(oid)
    return res

def gettemp(session, model, modules=[]):
    oid = []
    if len(modules) == 0:
        if model == 1:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.12.65'))
        elif model == 5:
            oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.12.192'))
        else:
            return 0
    else:
        for i in range(len(modules)):
            if model == 3:
                oid.append(netsnmp.Varbind('.1.3.6.1.4.1.25506.2.6.1.1.1.1.12.'+str(modules[i])))
        if len(oid) == 0:
            return 0
    res = session.get(oid)
    return res

def getmodules(session, model):
    OIDs=[];
    oid=[]
    for i in range(10):
        if model==3:
            oid.append(netsnmp.Varbind('.1.3.6.1.2.1.47.1.1.1.1.7.'+str(44+i)))
    res = session.get(oid)
    for i in range(10):
        if len(res) >= 1 and res[i] != None:
            if model==3:
                if re.search("board", res[i], re.IGNORECASE):
                    OIDs.append(44+i)
    return OIDs

def getmodelname(model):
    if model == 1:
        return "HP A5500"
    elif model == 2:
        return "HP A3100"
    elif model == 3:
        return "HP 7500"
    elif model == 4:
        return "HP Procurve"
    elif model == 5:
        return "HP 5700"
    else:
        return "Unknown model"

parser=argparse.ArgumentParser(description="Nagios SNMP switch check.")
parser.add_argument("-C", action="store", dest="community", default="public", help="set the community string")
parser.add_argument("-v", action="store", dest="version", type=int, default=1, choices=[1, 2, 3], help="specifies SNMP version to use")
parser.add_argument("-a", action="store", dest="action", required=True, nargs=1, choices=["cpu","ram-usage","ram-size","temp"], default="cpu", help="specifies parameter to check")
parser.add_argument("-w", action="store", dest="warning", required=True, type=float, help="set the warning level")
parser.add_argument("-c", action="store", dest="critical", required=True, type=float, help="set the critical level")
parser.add_argument("host", action="store", nargs=1, metavar="HOST", help="the host to check")
args=parser.parse_args()

session = netsnmp.Session( DestHost=args.host[0], Version=args.version, Community=args.community)
model=getmodel(session)
if model == 0:
    print "Unknown model"
    sys.exit(3)
OIDs=getmodules(session, model)

val=[]
if args.action[0]=="cpu":
    val=getcpu(session, model, OIDs)
elif args.action[0]=="ram-usage":
    val=getramusage(session, model, OIDs)
elif args.action[0]=="ram-size":
    val=getramsize(session, model, OIDs)
elif args.action[0]=="temp":
    val=gettemp(session, model, OIDs)

if val == 0 or len(val) == 0:
    print "Invalid result: "+str(val)+", model: "+getmodelname(model)
    sys.exit(3)

max=0;
for i in range(len(val)):
    if float(val[i])>max:
        max=float(val[i])

if max >= args.critical:
    if args.action[0]=="cpu":
        print "cpu: "+str(max)+"%|'cpu'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
    elif args.action[0]=="ram-usage":
        print "used ram: "+str(max)+"%|'ram'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
    elif args.action[0]=="ram-size":
        print ""
    elif args.action[0]=="temp":
        print "temperature: "+str(max)+"c|'temp'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
    sys.exit(2)
elif max >= args.warning:
    if args.action[0]=="cpu":
        print "cpu: "+str(max)+"%|'cpu'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
    elif args.action[0]=="ram-usage":
        print "used ram: "+str(max)+"%|'ram'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
    elif args.action[0]=="ram-size":
        print ""
    elif args.action[0]=="temp":
        print "temperature: "+str(max)+"c|'temp'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
    sys.exit(1)
else:
    if args.action[0]=="cpu":
        print "cpu: "+str(max)+"%|'cpu'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
    elif args.action[0]=="ram-usage":
        print "used ram: "+str(max)+"%|'ram'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
    elif args.action[0]=="ram-size":
        print ""
    elif args.action[0]=="temp":
        print "temperature: "+str(max)+"c|'temp'="+str(max)+"%;"+str(args.warning)+";"+str(args.critical)+";;"
sys.exit(0)

