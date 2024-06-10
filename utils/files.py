# -*- coding: utf-8 -*-

import json, os, shutil

class JSON():
	def ASCII(Data, Ensure : bool = True): return json.dumps(Data, ensure_ascii = Ensure)
	def Indent(Data, Indent = "\t"): return json.dumps(Data, indent = Indent)
	def Read(Path : str, Encoding : str = "utf-8"):
		with open(Path, "r", encoding = Encoding) as File: return json.load(File)
	def Stringify(Data): return json.dumps(Data)
	def Write(Path: str, Data, Encoding : str = "utf-8"):
		with open(Path, "w", encoding = Encoding) as File: json.dump(Data, File, indent = "\t")

def PurgeCache(Caches : list): [shutil.rmtree(Cache) for Cache in Caches if os.path.exists(Cache)]