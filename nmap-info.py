#!/usr/bin/env python3
#coding utf-8

import xml.etree.ElementTree as ET
import argparse
import pyperclip


class Script:
	def __init__(self, script_name = ""):
		self.script_name = script_name
		self.info = None

class Port:
	def __init__(self, port_number = 0):
		self.port_number = port_number
		self.state = None
		self.protocol = None
		self.service = None
		self.information = None
		self.scripts = None
		self.version = None

class Host:
	def __init__(self, timestamp = 0):
		self.timestamp = timestamp
		self.address = None
		self.address_type = None
		self.ports = None
		self.name = None
		self.state = None

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
		file = file[1:-1]	#quitar ' al principio y final

		if args.very_verbose:
			print("File: " + bcolors.GREEN + file + bcolors.ENDC)

		filter_ports = []
		if args.ports:
			for port in args.ports.split(","):
				filter_ports.append(int(port))

		try:
			tree = ET.parse(file)
			hosts = tree.findall('host')

			open_ports = []
			for host in hosts:
				if host.find('status') != None and host.find('status').attrib['state'].upper() == "UP":
					if host.find('address') != None:
						print(bcolors.RED + bcolors.BOLD + host.find('address').attrib['addr'] + bcolors.ENDC)
					if host.find('hostname') != None:
						print(bcolors.RED + bcolors.BOLD + host.find('hostname').attrib['name'] + bcolors.ENDC)
					
					if host.find('ports') != None:
						ports = host.find('ports').findall('port')
						for port in ports:
							if port.find('state').attrib['state'].upper() == 'OPEN':
								if len(filter_ports) == 0 or (len(filter_ports) > 0 and int(port.attrib['portid']) in filter_ports):
									PORT_PROTOCOL = ""
									SERVICE_NAME = ""
									PORT = port.attrib['portid']
									service = port.find('service')
									scripts = port.findall('script')

									if port.attrib['protocol'].upper() == 'TCP':
										PORT_PROTOCOL = bcolors.BOLD + bcolors.YELLOW + port.attrib['protocol'].upper() + bcolors.ENDC + " "
									else:
										PORT_PROTOCOL = bcolors.BOLD + bcolors.BLUE + port.attrib['protocol'].upper() + bcolors.ENDC + " "
									if service:
										SERVICE_NAME = " - " + bcolors.CYAN + service.attrib['name'] + bcolors.ENDC
									
									print("  " + PORT_PROTOCOL + PORT + SERVICE_NAME)

									if args.verbose:
										if service != None and 'product' in service.attrib:
											SERVICE_PRODUCT = service.attrib['product']
											SERVICE_VERSION = ""
											SERVICE_EXTRAINFO = ""
											if 'version' in service.attrib:
												SERVICE_VERSION = " <" + service.attrib['version'] + ">"
											if 'extrainfo' in service.attrib:
												SERVICE_EXTRAINFO = service.attrib['extrainfo']
												if not SERVICE_EXTRAINFO.startswith("(") and not SERVICE_EXTRAINFO.endswith(")"):
													SERVICE_EXTRAINFO = "(" + SERVICE_EXTRAINFO + ")"
												SERVICE_EXTRAINFO = " " + SERVICE_EXTRAINFO
											print( "    " + bcolors.GREEN + "Service: " + bcolors.ENDC + SERVICE_PRODUCT + SERVICE_VERSION + SERVICE_EXTRAINFO)

										for script in scripts:
											SCRIPT_ID = script.attrib['id']
											SCRIPT_OUTPUT = ""
											if 'output' in script.attrib:
												SCRIPT_OUTPUT = " -> " + script.attrib['output']
												SCRIPT_OUTPUT = SCRIPT_OUTPUT.replace("\n","").replace("\r",".").replace("  "," ")
											print( "    " + bcolors.PURPLE + "Script: " + bcolors.ENDC + SCRIPT_ID + SCRIPT_OUTPUT)
								
							if args.clipboard:
								open_ports.append(PORT)

				if host.find('hostscript') != None and args.verbose:
					scripts = host.find('hostscript').findall('script')
					for script in scripts:
						SCRIPT_ID = script.attrib['id']
						SCRIPT_OUTPUT = ""
						if 'output' in script.attrib:
							SCRIPT_OUTPUT = " -> " + script.attrib['output']
							SCRIPT_OUTPUT = SCRIPT_OUTPUT.replace("\n","").replace("\r",".").replace("  "," ")
						print( "  " + bcolors.PURPLE + "HostScript: " + bcolors.ENDC + SCRIPT_ID + SCRIPT_OUTPUT)
			
			if args.clipboard:
				clipboard_text = ','.join(list(set(open_ports)))	#para eliminar la última ,
				pyperclip.copy(clipboard_text)
		except Exception as e:
			if args.very_verbose:
				print("  " + bcolors.MAGENTA + "EXCEPTION: " + str(e) + bcolors.ENDC)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="GET NMAP XML FILE INFORMATION")
	parser.add_argument('--debug', action='store_true', help='Debug mode')
	parser.add_argument('-c', '--clipboard', action='store_true', help='Save output in clipboard.')
	parser.add_argument('-p', '--ports', help='Show ports, default all.')
	parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
	parser.add_argument('-vv', '--very_verbose', action='store_true', help='Very verbose mode')
	parser.add_argument('xml_file', nargs='+', type=ascii, help="XML file with the nmap output.")


	args = parser.parse_args()

	if args.debug:
		print(bcolors.PURPLE + str(args) + bcolors.ENDC)
	
	if args.very_verbose:
		args.verbose = True

	main(args)
