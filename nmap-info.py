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

def main(args):
	soup = BeautifulSoup(args.xml_file, 'xml')

	#print(soup.prettify())


	hosts = soup.find_all(find_hosts)

	for host in hosts:
		print(bcolors.GREEN + bcolors.BOLD + host.get('addr') + bcolors.ENDC)
		if args.ports:
			clipboard_text = ''
			ports = soup.find_all('port')
			for port in ports:
				if port.get('protocol').upper() == 'TCP':
					print("  " + bcolors.YELLOW + bcolors.BOLD + port.get('protocol').upper() + bcolors.ENDC + " " + port.get('portid'))
					if args.clipboard:
						clipboard_text += "T:" + port.get('portid') + ","
				else:
					print("  " + bcolors.BLUE + bcolors.BOLD + port.get('protocol').upper() + bcolors.ENDC + " " + port.get('portid'))
					if args.clipboard:
						clipboard_text += "U:" + port.get('portid') + ","


			if args.clipboard:
				clipboard_text = clipboard_text[:-1]	#para eliminar la última ,
				pyperclip.copy(clipboard_text)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="GET NMAP XML FILE INFORMATION")
	parser.add_argument('-c', '--clipboard', action='store_true', help='Save output in clipboard.')
	parser.add_argument('-p', '--ports', action='store_true', help='Get ports.')

	parser.add_argument('xml_file', type=argparse.FileType('r'), help="XML file with the nmap output.")

	args = parser.parse_args()

	print(args)

	main(args)
