#!/usr/bin/env python3
#coding utf-8

from bs4 import BeautifulSoup
import argparse
import pyperclip

class bcolors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def find_hosts(tag):
	return tag.name == 'address' and not tag.parent.name == 'hosthint'

def find_services(tag):
	return tag.name == 'service' and tag.parent.name == 'port'

def find_scripts(tag):
	return tag.name == 'script' and tag.parent.name == 'port'

def main(args):
	soup = BeautifulSoup(args.xml_file, 'xml')

	if args.debug:
		print(bcolors.PURPLE + soup.prettify() + bcolors.ENDC)


	hosts = soup.find_all(find_hosts)

	for host in hosts:
		print(bcolors.RED + bcolors.BOLD + host.get('addr') + bcolors.ENDC)
		if args.ports:
			clipboard_text = ''
			ports = soup.find_all('port')
			if args.verbose:
				services = soup.find_all(find_services)
				scripts = soup.find_all(find_scripts)
			for port in ports:
				if port.get('protocol').upper() == 'TCP':
					COLOR = bcolors.YELLOW
					if args.clipboard:
						clipboard_text += "T:" + port.get('portid') + ","
				else:
					COLOR = bcolors.BLUE
					if args.clipboard:
						clipboard_text += "U:" + port.get('portid') + ","
				
				print("  " + COLOR + bcolors.BOLD + port.get('protocol').upper() + bcolors.ENDC + " " + port.get('portid'))
				if args.verbose:
					if len(services) > 0:
						for service in services:
							if service.parent.get('portid') == port.get('portid'):
								if service.has_attr('product'):
									print("    " + bcolors.CYAN + "Service: " + bcolors.ENDC + service.get('name') + " -> " + service.get('product'))
								else:
									print("    " + bcolors.CYAN + "Service: " + bcolors.ENDC + service.get('name'))
					if len(scripts) > 0:
						for script in scripts:
							if script.parent.get('portid') == port.get('portid'):
								print("    " + bcolors.GREEN + "Script: " + bcolors.ENDC + script.get('id') + " -> " + script.get('output').replace("\n", "").replace("\r", ""))
	

			if args.clipboard:
				clipboard_text = clipboard_text[:-1]	#para eliminar la última ,
				pyperclip.copy(clipboard_text)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="GET NMAP XML FILE INFORMATION")
	parser.add_argument('--debug', action='store_true', help='Debug mode')
	parser.add_argument('-c', '--clipboard', action='store_true', help='Save output in clipboard.')
	parser.add_argument('-p', '--ports', action='store_true', help='Get ports.')
	parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
	parser.add_argument('xml_file', type=argparse.FileType('r'), help="XML file with the nmap output.")

	args = parser.parse_args()
	if args.debug:
		print(args)

	main(args)
