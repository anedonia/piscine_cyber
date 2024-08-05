import sys
from bs4 import BeautifulSoup # type: ignore
import requests
import os

def request_page():
	arguments = sys.argv[1:]
	
	if not len(arguments) == 1:
		print("no url given")
		return
	url = arguments[0]
	if len(arguments) == 1:
		depth = 5
	else:
		depth = arguments[1]

	try: 
		response = requests.get(url)
		response.raise_for_status()
		if response.text: 
			soup = BeautifulSoup(response.text, 'html.parser')
			img_tags = soup.find_all('img')
			if not os.path.exists("./img"):
				os.makedirs("img")
			img_tags = img_tags[:depth]
			for img in img_tags:
				img_url = img.get('src')
				if not img_url.startswith(('http://', 'https://')):
					img_url = url + img_url
					print(img_url)
				
					


		else:
			print("Received empty response.")
		

	except requests.HTTPError as http_err:
			print(f"HTTP error occurred: {http_err}")
	except Exception as err:
			print(f"Other error occurred: {err}")
	except ValueError as json_err:
		print(f"JSON decode error occurred: {json_err}")
	except Exception as err:
		print(f"An unexpected error occurred: {err}")
	
if __name__ == "__main__":
	request_page()