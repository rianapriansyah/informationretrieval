#!/usr/bin/pythons

# Usage: python process.py <input file.html> 
# example : python process.py "input_file.pdf"

import argparse
import os
import re
import pycountry
from bs4 import BeautifulSoup
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
st = StanfordNERTagger('/Users/rianapriansyah/Downloads/stanford-ner-2018-10-16/classifiers/english.all.3class.distsim.crf.ser.gz', '/Users/rianapriansyah/Downloads/stanford-ner-2018-10-16/stanford-ner.jar')


def html_parser(file_path):
	# Recognize a file at filePath and save the extracted text to result.xml before extract intended information fromm it.
	customer_name = ""
	location = ""
	customer_address = ""

	print("Uploading..")
	
	with open(file_path, "r") as f:
		contents = f.read()

	soup = BeautifulSoup(contents, 'html.parser')

	alltext = ""

	for txt in soup.find_all('p'):
		alltext += txt.text
		alltext += " "

	splitted_text = alltext.split()
	tag = st.tag(splitted_text)
	locations = [(i, k) for (i, k) in tag if k == 'LOCATION']
	people = [(i, k) for (i, k) in tag if k == 'PERSON']

	customer_name = get_customer_name(people, splitted_text)
	location = get_location(locations)
	customer_address = get_customer_location(location, alltext)


	for texts in soup.find_all('p'):
		text = texts.text
		if text is  "":
			#text = clean_text(text)
			x = re.search(r"(\d{2,3}.?)\s([a-zA-Z ]{2,30})", text)
			if x is not None:
				customer_address = x.string
				break
			else:
				continue
			


	print()

def get_location(locations):
	singapore_address = re.compile(r"(\d{2,3}.?)\s([a-zA-Z ]{2,30})")

	for loc in locations:
		country = pycountry.countries.get(name=loc[0])
		if country is not None:
			return country.name
			
def get_customer_location(location, text):
	
	return ""

def clean_text(text):
	alphanum = re.compile(r"[^a-zA-Z0-9][\W]")
	ws = re.compile(r"[\s]+")
	text = re.sub(alphanum, ' ', text)
	text = re.sub(ws, ' ', text)


	return text


def create_parser():
	parser = argparse.ArgumentParser(description="Recognize a file via web service")
	parser.add_argument('source_file')

	return parser

def process_text_file():
	#function to process extracted certain information from OCR output

	extracted = ""

	extracted += "Name of customer : " + get_customer_name()
	extracted += "Statement Date : " + get_month()

	with open("Extracted.txt", "w") as text_file:
    			text_file.write(extracted)

	
	print("Result was written to {}".format("Extracted.txt"))

def get_customer_name(ppl, txts):
	#get customer name from extracted text. 
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

def get_month():
	#function to get date of statement. Assuming the date in a short name format, (eg: Jan, Feb)
	#tokenize extracted text and then iterate each word to match dict key to get correct name of month.
	#Get previous word of recognize name of month and get next word, still need a lot of improvements.
	file = open("Output.txt", "r")
	text_content = file.read()
	file.close()

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

	words = word_tokenize(text_content)

	for index, word in enumerate(words):
		if not stat_date_is_found:
			month = months.get(words[index])
			if month is not None:
				date = words[index - 1] + " " + month + " " + words[index + 1]
				stat_date_is_found = True
		

	return date

def main():
	#args = create_parser().parse_args()

	#source_file = args.source_file

	#activate this line for debugger purpose
	#source_file = "Output.html" 
	source_file = "bankstatement.html" 


	if os.path.isfile(source_file):
		html_parser(source_file)
		#process_text_file()
	else:
		print("No such file: {}".format(source_file))


if __name__ == "__main__":
	main()
