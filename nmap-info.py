#!/usr/bin/env python3
#coding utf-8

import xml.etree.ElementTree as ET
import argparse, traceback, json, pyperclip

class Script:
	name = ""
	information = ""
	def __init__(self, script_name = ""):
		self.name = script_name

class Port:
	port_number = 0
	state = ""
	protocol = ""
	service = ""
	product = ""
	information = ""
	scripts = []
	version = ""
	def __init__(self, port_number = 0):
		self.port_number = port_number

class Host:
	timestamp = None
	address = ""
	address_type = ""
	ports = []
	scripts = []
	name = ""
	state = ""
	def __init__(self, timestamp = 0):
		self.timestamp = timestamp

	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

class bcolors:
    PURPLE = '\033[35m'
    MAGENTA = '\033[105m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main(args):

	for file in args.xml_file:
		if file.startswith("'") and file.endswith("'"):
			file = file[1:-1]	#quitar ' al principio y final

		if args.very_verbose and args.no_verbose == False:
			print("File: " + bcolors.GREEN + file + bcolors.ENDC)

		filter_ports = []
		if args.ports:
			for port in args.ports.split(","):
				filter_ports.append(int(port))
		try:
			tree = ET.parse(file)
			hosts = tree.findall('host')

			host_objs = []
			for host in hosts:
				host_obj = Host()

				if host.find('status') != None and host.find('status').attrib['state'].upper() == "UP":
					host_obj.state = "UP"
					if host.find('address') != None:
						if args.no_verbose == False:
							host_obj.address = host.find('address').attrib['addr']
							if not args.csv:
								print(bcolors.RED + bcolors.BOLD + host.find('address').attrib['addr'] + bcolors.ENDC)
					if host.find('hostname') != None:
						if args.no_verbose == False:
							host_obj.name = hostname.attrib['name']
							if not args.csv:
								print(bcolors.RED + bcolors.BOLD + host.find('hostname').attrib['name'] + bcolors.ENDC)

					port_objs = []
					if host.find('ports') != None and args.show_hosts_only == False:
						ports = host.find('ports').findall('port')
						for port in ports:
							port_obj = Port()
							if port.find('state').attrib['state'].upper() == 'OPEN':
								port_obj.state = "OPEN"
								if len(filter_ports) == 0 or (len(filter_ports) > 0 and int(port.attrib['portid']) in filter_ports):
									PORT_PROTOCOL = ""
									SERVICE_NAME = ""
									PORT = port.attrib['portid']
									service = port.find('service')
									scripts = port.findall('script')

									port_obj.protocol = port.attrib['protocol'].upper()
									port_obj.port_number = int(PORT)

									if port.attrib['protocol'].upper() == 'TCP':
										PORT_PROTOCOL = bcolors.BOLD + bcolors.YELLOW + port.attrib['protocol'].upper() + bcolors.ENDC + " "
									else:
										PORT_PROTOCOL = bcolors.BOLD + bcolors.BLUE + port.attrib['protocol'].upper() + bcolors.ENDC + " "
									
									service_str = ""
									if service != None and 'name' in service.attrib:
										service_str = service.attrib['name']
										#Si tiene el tunell ssl añado la s al final del servicio http "+" s
										if 'tunnel' in service.attrib.keys() and service.attrib['tunnel'] == "ssl":
											service_str += "s"
										SERVICE_NAME = " - " + bcolors.CYAN + service_str + bcolors.ENDC
										port_obj.service = service_str

									if args.no_verbose == False:
										if args.csv:
											print("\"{}\";{};{};\"{}\"".format(host.find('address').attrib['addr'] ,port.attrib['protocol'].upper(), PORT, service_str))
										else:
											print("  " + PORT_PROTOCOL + PORT + SERVICE_NAME)

									if args.verbose:
										if service != None and 'product' in service.attrib:
											SERVICE_PRODUCT = service.attrib['product']
											SERVICE_VERSION = ""
											SERVICE_EXTRAINFO = ""

											port_obj.product = SERVICE_PRODUCT

											if 'version' in service.attrib:
												SERVICE_VERSION = " <" + service.attrib['version'] + ">"
												port_obj.version = SERVICE_VERSION
											if 'extrainfo' in service.attrib:
												SERVICE_EXTRAINFO = service.attrib['extrainfo']
												if not SERVICE_EXTRAINFO.startswith("(") and not SERVICE_EXTRAINFO.endswith(")"):
													SERVICE_EXTRAINFO = "(" + SERVICE_EXTRAINFO + ")"
												SERVICE_EXTRAINFO = " " + SERVICE_EXTRAINFO
												port_obj.information = SERVICE_EXTRAINFO
											if args.no_verbose == False:
												print( "    " + bcolors.GREEN + "Service: " + bcolors.ENDC + SERVICE_PRODUCT + SERVICE_VERSION + SERVICE_EXTRAINFO)

										script_objs = []
										for script in scripts:
											script_obj = Script()

											SCRIPT_ID = script.attrib['id']
											SCRIPT_OUTPUT = ""
											if 'output' in script.attrib:
												SCRIPT_OUTPUT = " -> " + script.attrib['output']
												SCRIPT_OUTPUT = SCRIPT_OUTPUT.replace("\n","").replace("\r",".").replace("  "," ")
											
											script_obj.name = SCRIPT_ID
											script_obj.information = SCRIPT_OUTPUT.replace(" -> ", "")
											script_objs.append(script_obj)

											if args.no_verbose == False:
												print( "    " + bcolors.PURPLE + "Script: " + bcolors.ENDC + SCRIPT_ID + SCRIPT_OUTPUT)
										port_obj.scripts = script_objs

									port_objs.append(port_obj)
								
							if args.clipboard:
								open_ports.append(PORT)

						#for ports end
					host_obj.ports = port_objs

				if host.find('hostscript') != None and args.verbose:
					scripts = host.find('hostscript').findall('script')
					host_script_objs = []
					for script in scripts:
						host_script_obj = Script()
						SCRIPT_ID = script.attrib['id']
						SCRIPT_OUTPUT = ""
						if 'output' in script.attrib:
							SCRIPT_OUTPUT = " -> " + script.attrib['output']
							SCRIPT_OUTPUT = SCRIPT_OUTPUT.replace("\n","").replace("\r",".").replace("  "," ")
						if args.no_verbose == False:
							print( "  " + bcolors.PURPLE + "HostScript: " + bcolors.ENDC + SCRIPT_ID + SCRIPT_OUTPUT)

						host_script_obj.name = SCRIPT_ID
						host_script_obj.information = SCRIPT_OUTPUT.replace(" -> ", "")
						host_script_objs.append(host_script_obj)


					host_obj.scripts = host_script_objs

				host_objs.append(host_obj)
			
			if args.clipboard:
				clipboard_text = ','.join(list(set(open_ports)))	#para eliminar la última ,
				pyperclip.copy(clipboard_text)

			json_list = []
			for host_obj in host_objs:
				json_list.append(host_obj.toJSON())
			return json_list

		except Exception as e:
			if args.very_verbose and args.no_verbose == False:
				print("  " + bcolors.MAGENTA + "EXCEPTION: " + str(e) + bcolors.ENDC)
			if args.debug:
				print(traceback.format_exc())

			return []

def api(xml_file):
	class Args:
		xml_file = ""
		very_verbose = True
		verbose = True
		clipboard = False
		debug = False
		ports = None
		no_verbose = True
		csv = False
		show_hosts_only = False
		def __init__(self, xml_file):
			self.xml_file = [xml_file]
	args = Args(xml_file)

	print(args)

	return main(args)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="GET NMAP XML FILE INFORMATION")
	parser.add_argument('--debug', action='store_true', help='Debug mode')
	parser.add_argument('-c', '--clipboard', action='store_true', help='Save output in clipboard.')
	parser.add_argument('-p', '--ports', help='Show ports, default all.')
	parser.add_argument('--show_hosts_only',action='store_true', help='Only show hosts')
	parser.add_argument('--no_colors',action='store_true', default=False, help='Only show hosts')
	parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
	parser.add_argument('-vv', '--very_verbose', action='store_true', help='Very verbose mode')
	parser.add_argument('--csv', action='store_true', help='Output in CSV')
	parser.add_argument('xml_file', nargs='+', type=ascii, help="XML file with the nmap output.")


	args = parser.parse_args()

	if args.debug:
		print(bcolors.PURPLE + str(args) + bcolors.ENDC)
	
	args.no_verbose = False

	if args.very_verbose:
		args.verbose = True

	if args.no_colors:
	    bcolors.PURPLE = ''
	    bcolors.MAGENTA = ''
	    bcolors.BLUE = ''
	    bcolors.CYAN = ''
	    bcolors.GREEN = ''
	    bcolors.YELLOW = ''
	    bcolors.RED = ''
	    bcolors.ENDC = ''
	    bcolors.BOLD = ''
	    bcolors.UNDERLINE = ''

	main(args)
