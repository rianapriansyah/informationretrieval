#!/usr/bin/pythons

# Usage: python process.py <input file.html> 
# example : python process.py "input_file.pdf"

import argparse
import os
import re
from bs4 import BeautifulSoup
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
st = StanfordNERTagger('/Users/rianapriansyah/Downloads/stanford-ner-2018-10-16/classifiers/english.all.3class.distsim.crf.ser.gz', '/Users/rianapriansyah/Downloads/stanford-ner-2018-10-16/stanford-ner.jar')


def html_parser(file_path):
	# Recognize a file at filePath and save the extracted text to result.xml before extract intended information fromm it.
	print("Uploading..")
	
	with open(file_path, "r") as f:
		contents = f.read()

	soup = BeautifulSoup(contents, 'html.parser')

	customer_name = ""

	for texts in soup.find_all('p'):
		text = texts.text
		if text is not "":
			text = clean_text(text)
			sp = text.split(sep=" ")
			if len(sp) > 4:
				continue
			else:
				tagged = st.tag(sp)
				if tagged[0][1] == 'PERSON':
					customer_name = text
					break

	for texts in soup.find_all('p'):
		text = texts.text
		if text is not "":
			#text = clean_text(text)
			x = re.search(r"\d{1,3}.?\d{0,3}\s[a-zA-Z]{2,30}\s[a-zA-Z]{2,15}", text)
			if x is not None:
				customer_address = x.string
				break
			else:
				continue
			


	print()

def clean_text(text):
	alphanum = re.compile(r"[^a-zA-Z ]")
	ws = re.compile(r"[\s]+")
	text = re.sub(alphanum, '#', text)
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

def get_customer_name():
	#get customer name from extracted text. 
	file = open("Output.txt", "r")
	name = ""
	for line in file:
		tagged = st.tag(word_tokenize(line))
		if tagged[0][1] == 'PERSON':
			name = line
			break

	file.close()
	return name

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
