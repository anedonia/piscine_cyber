from bs4 import BeautifulSoup # type: ignore
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
import argparse
import hashlib

def main():
	
	parser = argparse.ArgumentParser(description="a simple img crapper")

	parser.add_argument('url', type=str)
	parser.add_argument('-p', type=str)
	parser.add_argument('-l', type=int)
	parser.add_argument('-r', action="store_true")
	args = parser.parse_args()

	depth = 5
	path = Path("./data/")
	recursion = False
	url = args.url

	if args.r:
		recursion = True
	if args.l:
		depth = args.l
	if args.p:
		path = Path("{args.p}")
	if not path.exists():
		path.mkdir(parents=True, exist_ok=True)

	print("depth : ", depth)
	print("path : " + str(path))
	print("recursion status : ", recursion)
	print("url : " + url)

	request_page(depth, path, recursion, url)
	
def generate_image_hash(identifier):
    hash_object = hashlib.md5(identifier.encode())
    full_hash = hash_object.hexdigest()
    short_hash = full_hash[:16]
    return short_hash

def img_filter(img_tags, path, url):
	allowed_extensions = [".png", ".gif", ".bmp", ".jpg", ".jpeg"]
	for img in img_tags:
		img_url = img.get('src')
		if img_url:
			img_url = urljoin(url, img_url)

			if allowed_extensions:
				if any(img_url.lower().endswith(ext) for ext in allowed_extensions):
					download_img(img_url, path)
	
def download_img(img_url, path):
	try:
		response = requests.get(img_url)
		response.raise_for_status()

		parsed_url = urlparse(img_url)
		img_path = Path(parsed_url.path)
		img_extension = img_path.suffix

		img_name = generate_image_hash(img_url) + img_extension        

		save_path = Path(path) / img_name
		save_path.parent.mkdir(parents=True, exist_ok=True)

		with save_path.open('wb') as img_file:
			img_file.write(response.content)

	except requests.HTTPError as http_err:
		print(f"HTTP error occurred while downloading {img_url}: {http_err}")
	except Exception as err:
		print(f"Other error occurred while downloading {img_url}: {err}")

def request_page (depth, path, recursion, url, visited=None):	

	if visited is None:
		visited = set()
	if url in visited:
		return
	visited.add(url)
	if depth == 0:
		return
	try: 
		response = requests.get(url)
		response.raise_for_status()
		if response.text: 
			soup = BeautifulSoup(response.text, 'html.parser')
			img_tags = soup.find_all('img')
			img_filter(img_tags, path, url)

			links = soup.find_all('a', href=True)
			link_list = [urljoin(url, link['href']) for link in links]
			for link in link_list:
				print(link)
				print("depth level : ", depth)


				next_depth = depth - 1 if not recursion else depth
				request_page(next_depth, path, recursion, link, visited)

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
	main()