#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os
import gtk
import time
from datetime import timedelta


class Graph:
    def __init__(self, ui):
        try:
            os.mkdir("/tmp/pynetmap/")
        except:
            pass
        self.store = ui.store
        self.ui = ui
        self.header = "Digraph{ \nnode [style=\"filled, rounded\",fillcolor=\"#eeeeee\",fontname=\"Sans\", fixedsize=false,shape=plaintext];\ngraph [splines=\"line\", dpi = 196, pad=\"1\", ranksep=\"1\",nodesep=\"0.5\"]\n"
        self.footer = "}"
        self.format = "jpeg"

    def edge(self, a, b, lvl=0):
        i = 0
        s = "\t"
        while i < lvl:
            s += "\t"
            i += 1
        s += "\""+str(a)+"\" -> \""+str(b)+"\" \n"
        return s

    def calldot(self, filecontent):
        file = open("/tmp/pynetmap/graph.dot", "w")
        file.write(filecontent)
        file.close()
        os.system("dot -T"+self.format +
                  " /tmp/pynetmap/graph.dot -o  /tmp/pynetmap/graph."+self.format + "; exit")
        r = gtk.gdk.pixbuf_new_from_file("/tmp/pynetmap/graph."+self.format)
        os.system("rm /tmp/pynetmap/*")
        return r

    def node(self, key, detailed, lvl=0):

        vmstate = self.store.get_attr(
            "module", key, "module.state.status")

        vmicon = self.store.get_attr(
            "schema", self.store.get_attr("base", key, "base.core.schema"), "Icon")

        vmname = self.store.get_attr("base", key, "base.name")

        icon = vmicon+".png"
        try:
            if vmstate == "running":
                icon = vmicon+"_running.png"
            elif vmstate == "stopped":
                icon = vmicon+"_stopped.png"
            elif vmstate == "unknown":
                icon = vmicon+"_unknown.png"
        except:
            pass
        s = "\t"
        i = 0
        while i < lvl:
            s += "\t"
            i += 1
        s += "\""+str(key)+"\" "
        s += " [label=<<TABLE border='0' cellborder='0' cellspacing='5'>"
        s += "<TR><TD port='IMG' colspan='2'><IMG SRC='"+icon+"' /></TD></TR>"
        s += "<TR><TD colspan='2' ><b>" + vmname+"</b></TD></TR>"
        if detailed:
            vmfields = self.store.get_attr(
                "schema", self.store.get_attr("base", key, "base.core.schema"), "Fields")
            info = self.store.get("module", key)
            table = dict()
            table["history"] = []
            table["list"] = []
            table["base"] = []
            table["baseinfo"] = []
            table["basemultiline"] = []
            for k in self.store.get("base", key).keys():
                if (not k.startswith("base.core")) and (self.store.get_attr("base", key, k) != ""):
                    if k in vmfields.keys() and vmfields[k] == "LONG":
                        table["basemultiline"].append(k)
                    else:
                        table["base"].append(k)

            try:
                for k in info.keys():
                    if (info[k] != ""):
                        if k.startswith("module.state.history"):
                            table["history"].append(k)
                        elif k.startswith("module.state.list"):
                            table["list"].append(k)
                        elif k.startswith("module."):
                            table["baseinfo"].append(k)
                        else:
                            pass
            except:
                pass
            tblhistoryb = False
            tblbaseb = False
            tbllistb = False

            for k in table:
                table[k].sort()

            # History
            tblhistory = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            for k in table["history"]:
                name = (vmname+k+".png").replace(" ", "").lower()
                if k == "module.state.history.status":
                    self.subgraph(info[k], name, self.ui.lang.get(k), True)
                else:
                    self.subgraph(info[k], name, self.ui.lang.get(k))

                tblhistory += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><IMG SRC='/tmp/pynetmap/" + \
                    name+"' /></TD></TR>"
                tblhistoryb = True
            tblhistory += "</TABLE>"
            # Base
            tblbase = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            for k in table["base"]:
                if ".password" in k:
                    rst = "*" * len(str(self.store.get_attr("base", key, k)))
                else:
                    rst = str(self.store.get_attr("base", key, k))
                    rst = rst.replace('"', '\"')
                tblbase += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><B>"+self.ui.lang.get(k) + \
                    "</B></TD><TD VALIGN='TOP' ALIGN='LEFT'>"+rst + "</TD></TR>"
                tblbaseb = True
            for k in table["baseinfo"]:
                if k == "module.state.lastupdate":
                    rst = "-" + \
                        str(timedelta(seconds=int(time.time() - info[k])))
                else:
                    rst = str(info[k])
                    rst = rst.replace('"', '\"')
                tblbase += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><B>"+self.ui.lang.get(k) + \
                    "</B></TD><TD VALIGN='TOP' ALIGN='LEFT'>"+rst + "</TD></TR>"
                tblbaseb = True
            for k in table["basemultiline"]:
                rst = str(self.store.get_attr("base", key, k))
                rst = rst.replace('\n', "<BR ALIGN='LEFT'/>")
                tblbase += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><B>"+self.ui.lang.get(k) + \
                    "</B></TD><TD VALIGN='TOP' ALIGN='LEFT'>"+rst + "</TD></TR>"
                tblbaseb = True

            tblbase += "</TABLE>"

            # List
            tbllist = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            for k in table["list"]:
                rst = info[k]
                if len(rst) > 0:
                    tbllist += "<TR><TD VALIGN='TOP' ALIGN='LEFT'>"

                    tbllist += "<TABLE border='0' cellborder='0' cellspacing='5'><TR><TD ALIGN='LEFT'><B><U>" + \
                        self.ui.lang.get(k)+"</U></B></TD></TR>"

                    for l in rst:
                        tbllist += "<TR>"
                        for d in l.keys():
                            tbllist += "<TD VALIGN='TOP' ALIGN='LEFT'>" + \
                                l[d].strip()+"</TD>"
                        tbllist += "</TR>"
                    tbllist += "</TABLE>"
                    tbllist += "</TD></TR>"
                    tbllistb = True
            tbllist += "</TABLE>"

            if tblhistoryb and tblbaseb:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT'>"+tblhistory + \
                    "</TD><TD VALIGN='TOP' ALIGN='LEFT'>"+tblbase + "</TD></TR>"
            else:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT' colspan='2'>" + \
                    tblbase + "</TD></TR>"

            if tbllistb:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT' colspan='2'>"+tbllist + "</TD></TR>"

        s += "</TABLE>>]\n"
        return s

    def subgraph(self, list, name, title, bln=False):
        i = 0
        file = open("/tmp/pynetmap/"+name+".list", "w")
        for e in list:
            ee = str(e).replace("[^0-9.]+", "").replace("%", "")
            if ee != "":
                ee = float(ee)
                if bln:
                    if ee == 100:
                        color = 1
                    else:
                        color = 2
                else:
                    if ee < 25:
                        color = 0
                    elif ee < 75:
                        color = 1
                    else:
                        color = 2

                file.write(str(i) + "    "+str(ee) +
                           "    " + str(color) + "\n")
                i = i+1
        file.close()

        cmd = """gnuplot -e "set terminal png transparent size 800,400 font arial 18;
        set title '"""+title+"""';
        set yrange [0:100];
        set palette model RGB maxcolors 3;
        set palette model RGB defined (0 '#999900', 1 '#009900', 2 '#cc0000');
        set cbrange [0:2];
        set nocbtics;
        unset colorbox;
        plot '/tmp/pynetmap/""" + name+""".list' notitle  with filledcurves above x1 fc palette;" > /tmp/pynetmap/""" + name+""" && rm '/tmp/pynetmap/"""+name+""".list'"""
        os.system(cmd)

    def generate_node_recur(self, key,  detailed, lvl):
        st = self.node(key, detailed, lvl)
        for k in self.store.get_children(key):
            st += self.generate_node_recur(k, detailed, lvl+1)
            st += self.edge(key, k, lvl+1)
        return st

    def generate(self):

        st = self.header
        st += self.node(self.ui.selection[0], True)
        i = 1
        while i < len(self.ui.selection):
            st += self.node(self.ui.selection[i], False)
            st += self.edge(self.ui.selection[i], self.ui.selection[i-1], 0)
            i += 1

        for o in self.store.get_children(self.ui.selection[0]):
            st += self.generate_node_recur(o, False, 1)
            st += self.edge(self.ui.selection[0], o, 1)
        st += self.footer
        return self.calldot(st)

    def generate_all_map(self):
        st = self.header
        elm = self.store.get_table("structure")
        for k in elm:
            st += self.generate_node_recur(k, False, 0)

        st += self.footer
        return self.calldot(st)
