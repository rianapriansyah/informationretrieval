#!/usr/bin/pythons

# Usage: python process.py <input file.html> 
# example : python process.py "input_file.pdf"

import argparse
import os
import re
#import pycountry
from bs4 import BeautifulSoup
#from nltk.tag import StanfordNERTagger
#from nltk.tokenize import word_tokenize
st = StanfordNERTagger('/Users/rianapriansyah/Downloads/stanford-ner-2018-10-16/classifiers/english.all.3class.distsim.crf.ser.gz', '/Users/rianapriansyah/Downloads/stanford-ner-2018-10-16/stanford-ner.jar')


def html_parser(file_path):
	# Recognize a file at filePath and save the extracted text to result.xml before extract intended information fromm it.
	location = ""
	customer_name = ""
	customer_address = ""
	customer_acc_number = ""
	document_date = ""

	print("Uploading..")
	
	with open(file_path, "r") as f:
		contents = f.read()

	soup = BeautifulSoup(contents, 'html.parser')

	alltext = ""

	for txt in soup.find_all('p'):
		alltext += txt.text
		alltext += os.linesep

	splitted_text = alltext.split()
	tag = st.tag(splitted_text) 
	locations = [(i, k) for (i, k) in tag if k == 'LOCATION']
	people = [(i, k) for (i, k) in tag if k == 'PERSON']

	customer_name = get_customer_name(people, splitted_text)
	location = get_location(locations)
	customer_address = get_customer_location(location, soup, customer_name)
	document_date = get_month(splitted_text)
	customer_acc_number = get_acc_number(alltext)
	#trx_list = get_transaction_list(soup)

	result = "Name of Customer : " + customer_name + os.linesep
	result += "Address of Customer : " + customer_address + os.linesep
	result += "Bank Account number : " + customer_acc_number + os.linesep
	result += "Statement Date : " + document_date 

	with open("Result.txt", "w") as text_file:
    			text_file.write(result)

	print("Result was written to {}".format("Result.txt"))
	
	
def get_transaction_list(soup):
	trx_list = []
	table_candidate = []
	alltext = ""
	ordered_table = []

	for i in soup.find_all(blocktype='Separator'):
		siblings = i.find_next_siblings("p")
		table_candidate += get_table_candidate(siblings)
		table_candidate += []

	processed = process(table_candidate)

	return trx_list

def process(table_candidate):
	#table_candidate.sort()
	#table_candidate = sorted(table_candidate, key=lambda x: x['baseline'])
	rows = []
	column = []
	table = {}
	attrs = {}
	row_counter = 1
	tolerable_value = 45

	ordered = []

	for i, val in enumerate(table_candidate):
		if i is 0:
			selector = val['baseline']
		else:
			selector = table_candidate[i - 1]['baseline']
			
		selected =	val['baseline']
		
		if selector == selected:
			column.append(val['name'])
		else:
			clmn = column.copy()
			x = str(row_counter)
			table[x] = clmn
			column.clear()
			column.append(val['name'])
			selector = selected
			row_counter += 1
			x = str(row_counter)
			table[x] = column

	for i in range(len(table)):
		i += 1
		if i == 1:
			prev = table.get(i)
		else:
			prev = table.get(i-1)

		curr = table.get(i)



		print(i)
			
		#if i is 0:
		#	selector = val['baseline']
		#else:
		#	selector = table_candidate[i - 1]['baseline']
		#
		#selected =	val['baseline']
		#
		#if selector == selected:
		#	column.append(val['name'].replace('\n', ''))
		#else:
		#	clmn = column.copy()
		#	x = str(row_counter)+"_"+str(selector)
		#	table[x] = clmn
		#	column.clear()
		#	column.append(val['name'].replace('\n', ''))
		#	selector = selected
		#	row_counter += 1

	return []

def get_table_candidate(siblings):
	table = []
	for i in siblings:
		attrs = {}
		try:
			if i.has_attr('blocktype') and i.attrs['blocktype'] == 'Separator':
				break
			else:
				attrs['baseline'] = int(i.attrs['baseline'])
				attrs['b'] = int(i.attrs['b'])
				attrs['l'] = int(i.attrs['l'])
				attrs['r'] = int(i.attrs['r'])
				attrs['t'] = int(i.attrs['t'])
				attrs['name'] = i.text.replace('\n', '')
				attrs['sourceline'] = i.sourceline
				attrs['sourcepos'] = i.sourcepos
				table.append(attrs)
		except:
			continue
		
	return table

def get_acc_number(txt):
	acc_number = ""
	acc_number_pattern = re.compile(r"^[0-9-]{7,10}")
	for i in iter(txt.splitlines()):
		result = re.match(acc_number_pattern, i)
		if result is not None:
			acc_number = result.string
			return acc_number



def get_location(locations):
	#get location of issued document to decide the regex pattern for address and postal code
	for loc in locations:
		country = pycountry.countries.get(name=loc[0])
		if country is not None:
			return country.name
			
def get_customer_location(loc, bsoup, cust_name):
	#get customer address from document using regex pattern. The pattern needs to be determined based on the issued document location

	#need to get reference of list of official postal code
	if loc == 'Singapore':
		postal_code_pattern = re.compile(r"\d{6}")

	text = ""
	after_name_block = False
	for txt in bsoup.find_all('p'):
		if txt.text == cust_name:
			after_name_block = True
		
		if after_name_block is True:
			text += txt.text
			text += os.linesep

	address = ""
	postal_code = "" 
	address_pattern = re.compile(r"\d{2,3}.?(?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?", flags=re.IGNORECASE)
	
	for line in iter(text.splitlines()):
		
		if address is "":
			result = re.match(address_pattern, line)
			if result is not None:
				address = result.string
		
		if postal_code is "":
			res = re.search(postal_code_pattern, line)
			if res is not None:
				postal_code = res.string

		if address is not "" and postal_code is not "":
			break

	address += ", " + postal_code

	return address

def create_parser():
	parser = argparse.ArgumentParser(description="Recognize a file via web service")
	parser.add_argument('source_file')

	return parser

def get_customer_name(ppl, txts):
	#get customer name from extracted text. 
	#get customer name by first accurence tag PERSON, then iterate to the next tag.
	#if the indeces of PERSON tags in a form of sequence, then we got the complete name of customer name
	customer_name = ""
	first_name = ""
	last_name = ""
	for i, v in enumerate(ppl):
		if i is not 0:
			if len(customer_name.split()) is 1:
				x = txts.index(customer_name) + 1
				if txts.index(v[0]) is x:
					last_name += v[0]
					customer_name += " " + last_name
				else:
					break
			else:
				x = txts.index(last_name) + 1
				if txts.index(v[0]) is x:
					last_name = v[0]
					customer_name += " " + last_name
				else:
					break
		else:
			first_name += v[0]
			customer_name = first_name
	return customer_name

def get_month(txt):
	#function to get date of statement. Assuming the date in a short name format, (eg: Jan, Feb)
	#tokenize extracted text and then iterate each word to match dict key to get correct name of month.
	#Get previous word of recognize name of month and get next word, still need a lot of improvements.

	stat_date_is_found = False
	date = ""

	months = {
		'Jan':'January',
		'Feb': 'February',
		'Mar': 'March',
		'Apr': 'April',
		'May': 'May',
		'Jun': 'June',
		'Jul': 'July',
		'Aug': 'August',
		'Sep': 'September',
		'Oct': 'October',
		'Nov': 'November',
		'Dec': 'December'
	}

	for index, word in enumerate(txt):
		if not stat_date_is_found:
			month = months.get(txt[index])
			if month is not None:
				date = txt[index - 1] + " " + month + " " + txt[index + 1]
				stat_date_is_found = True
		else:
			break

	return date

def main():
	#args = create_parser().parse_args()

	#source_file = args.source_file

	#activate this line for debugger purpose
	source_file = "bankstatement.html" 


	if os.path.isfile(source_file):
		html_parser(source_file)
	else:
		print("No such file: {}".format(source_file))


if __name__ == "__main__":
	main()
