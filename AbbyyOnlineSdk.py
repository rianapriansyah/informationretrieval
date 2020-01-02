#!/usr/bin/python

# Usage: process.py <input file> 
import shutil
import os
import xml.dom.minidom
try:
	import requests
except ImportError:
	print("You need the requests library to be installed in order to use this sample.")
	print("Run 'pip install requests' to fix it.")

	exit()


class ProcessingSettings:
	Language = "English"
	OutputFormat = "docx"


class Task:
	Status = "Unknown"
	Id = None
	DownloadUrl = None

	def is_active(self):
		if self.Status == "InProgress" or self.Status == "Queued":
			return True
		else:
			return False


class AbbyyOnlineSdk:
	ServerUrl = "https://cloud.ocrsdk.com"
	
	ApplicationId = "96972df2-45f8-4753-8c02-065f1e259fe5"
	Password = "lSnTlU2RQDIyToY8O1/6gVUv"
	Proxies = {}

	def process_image(self, file_path, settings):
		url_params = {
			"language": settings.Language,
			"exportFormat": settings.OutputFormat
		}
		request_url = self.get_request_url("processImage")

		with open(file_path, 'rb') as image_file:
			image_data = image_file.read()

		response = requests.post(request_url, data=image_data, params=url_params,
								 auth=(self.ApplicationId, self.Password), proxies=self.Proxies)

		# Any response other than HTTP 200 means error - in this case exception will be thrown
		response.raise_for_status()

		# parse response xml and extract task ID
		task = self.decode_response(response.text)
		return task

	def get_task_status(self, task):
		if task.Id.find('00000000-0') != -1:
			# GUID_NULL is being passed. This may be caused by a logical error in the calling code
			print("Null task id passed")
			return None

		url_params = {"taskId": task.Id}
		status_url = self.get_request_url("getTaskStatus")

		response = requests.get(status_url, params=url_params,
								auth=(self.ApplicationId, self.Password), proxies=self.Proxies)
		task = self.decode_response(response.text)
		return task

	def download_result(self, task, output_path):
		get_result_url = task.DownloadUrl
		if get_result_url is None:
			print("No download URL found")
			return

		file_response = requests.get(get_result_url, stream=True, proxies=self.Proxies)
		x = self.decode_response_xml(file_response.text)


	def decode_response_xml(self, xml_response):
		#decode_response_xml is a function to extract all text from xml to string and save it into txt file
		dom = xml.dom.minidom.parseString(xml_response)

		#get parent node of char params then iterate through it. parent node of char params indicate one section of text in pdf. (self assumption)
		par_node = dom.getElementsByTagName("formatting")

		converted_string = ""

		
		for node in par_node:
			doc_node = node.getElementsByTagName("charParams")

			for i in doc_node:
				for x in i.childNodes:
					
					converted_string += x.nodeValue
			
			converted_string += os.linesep
		
		
		with open("Output.txt", "w") as text_file:
    			text_file.write(converted_string)


	def decode_response(self, xml_response):
		""" Decode xml response of the server. Return Task object """
		dom = xml.dom.minidom.parseString(xml_response)
		task_node = dom.getElementsByTagName("task")[0]
		task = Task()
		task.Id = task_node.getAttribute("id")
		task.Status = task_node.getAttribute("status")
		if task.Status == "Completed":
			task.DownloadUrl = task_node.getAttribute("resultUrl")
		return task

	def get_request_url(self, url):
		return self.ServerUrl.strip('/') + '/' + url.strip('/')
