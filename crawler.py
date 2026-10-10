from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse, unquote
from collections import deque
from pathlib import Path
import json
import re
import time


MAX_PAGES=1000
DELAY=2

TOR_PROXY="socks5://127.0.0.1:9150"

def normalize_url(url):

	try:
		parsed=urlparse(url)

		if parsed.scheme not in ["http", "https"]:
			return None

		if not parsed.hostname:
			return None

		hostname=parsed.hostname.lower()

		if hostname not in seed_domains:
			return None

		parsed=parsed._replace(fragment="")

		return parsed.geturl()

	except Exception:
		return None


def extract_identifiers(text, html=""):

	content = unquote(text+"\n"+html)

	emails=re.findall(
		r"(?i)\b[A-Za-z0-9._%+-]+@[a-z0-9.-]+\.[A-Za-z]{2,}\b",
		content
	)

	telegram_links=re.findall(
		r"(?i)(?:https?://)?(?:www\.)?t\.me/[A-Za-z0-9_]{4,}",
		content
	)

	telegram_usernames=re.findall(
		r"(?i)telegram\s+(?:username|user|contact|id)\s*[:=]\s*@?([a-z0-9_]{4,})",
		content
	)

	twitter_links=re.findall(
		r"(?i)(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/[A-Za-z0-9_]{1,15}",
		content
	)

	twitter_usernames=re.findall(
		r"twitter\s+username\s*:\s*@?([A-Za-z0-9_]{1,15})",
		content,
		re.IGNORECASE
	)

	phone_pattern=re.compile(
		r"(?<![A-Za-z0-9])\+?[0-9][0-9\s().-]{6,22}[0-9](?![A-Za-z0-9])"
	)

	phones=phone_pattern.findall(content)

	normalized_phones=set()
	for phone in phones:
		digits=re.sub(r"\D", "", phone)
		if 8<= len(digits) <=15:
			normalized_phones.add(
				("+" if phone.strip().startswith("+") else "") + digits
			)

	bitcoin_pattern=re.compile(
		r"(?<![A-Za-z0-9])(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[ac-hj-np-z02-9]{11,71})(?![A-Za-z0-9])",
		re.IGNORECASE
	)
	bitcoin_addresses=bitcoin_pattern.findall(content)

	telegram_links={
		link.rstrip(".,;:!?)\"]'") for link in telegram_links
	}

	twitter_links={
		link.rstrip(",.;:!?)\"]'") for link in twitter_links
	}

	telegram_links.update(
		"https://t.me/"+username for username in telegram_usernames
	)
	twitter_links.update(
		"https://x.com/"+username for username in twitter_usernames
	)

	return{
		"emails":sorted(set(emails)),
		"telegram":sorted(telegram_links),
		"twitter_x":sorted(twitter_links),
		"phone_numbers": sorted(normalized_phones),
		"bitcoin_wallets": sorted(set(bitcoin_addresses))
	}


def main():

	SEED_FILE=Path(__file__).resolve().parent / "seed.txt"

	queue=deque()

	with SEED_FILE.open("r", encoding="utf-8-sig") as file:
		for line in file:
			url=line.strip().strip('"').strip("'")

			if url.startswith(("http://","https://")):
				queue.append(url)

	queue=deque(dict.fromkeys(queue))

	if not queue:
		print("No valid seed URLs found in:", SEED_FILE)
		return

	seed_domains={
		urlparse(url).hostname.lower()
		for url in queue
		if urlparse(url).hostname
	}

	visited=set()
	results=[]

	with sync_playwright() as p:
		print("Starting browser...")

		browser=p.firefox.launch(
			headless=True,
			proxy={
				"server":TOR_PROXY
			}
		)

		context=browser.new_context(
			ignore_https_errors=True
		)

		page=context.new_page()

		while queue and len(visited) < MAX_PAGES:

			current_url=queue.popleft()

			if current_url in visited:
				continue

			visited.add(current_url)

			print()
			print("BFS PAGE:", len(visited))
			print("Crawling:", current_url)

			try:

				response=page.goto(
					current_url,
					wait_until="domcontentloaded",
					timeout=60000
				)

				if response:
					status=response.status
					content_type=response.headers.get(
					"content-type",
					""
					)
				else:
					status=None
					content_type=""

				print("Status:", status)

				page.wait_for_timeout(60000)

				html=page.content()

				soup=BeautifulSoup(
					html,
					"html.parser"
				)

				title=""

				if soup.title:
					title=soup.title.get_text(
						" ",
						strip=True
					)

				text=soup.get_text(
					" ",
					strip=True
				)

				identifiers=extract_identifiers(text,html)

				internal_links=set()

				for tag in soup.find_all(
					"a",
					href=True
				):

					href= tag.get("href")

					absolute_url=urljoin(
						current_url,
						href
					)

					normalized_url=normalize_url(
						absolute_url
					)

					if normalized_url:
						internal_links.add(
							normalized_url
						)

				page_data={

					"url":current_url,
					"title":title,
					"status":status,
					"content-type":content_type,
					"identifiers":identifiers,
					"internal_links":sorted(internal_links)
				}

				results.append(page_data)
	
				print("Title:", title)

				print(
					"Internal links:",
					len(internal_links)
				)

				print(
					"Emails:",
					len(identifiers["emails"])
				)

				print(
					"Telegram:",
					len(identifiers["telegram"])
				)

				print(
					"Twitter/X:",
					len(identifiers["twitter_x"])
				)

				print(	
					"phone numbers:", len(identifiers["phone_numbers"])
				)

				print(
					"Bitcoin wallets:", len(identifiers.get("bitcoin_addresses",[]))
				)


				for link in internal_links:

					if link not in visited:

						if link not in queue:

							queue.append(link)

				print(
					"Queue size:",
					len(queue)
				)

			except PlaywrightTimeoutError:
				print(
					"TIMEOUT:",
					current_url
				)

			except Exception as error:
				print(
					"ERROR:",
					error
				)

			time.sleep(DELAY)

		browser.close()

	with open(
		"crawl_results.json",
		"w",
		encoding="utf-8"
	) as file:

		json.dump(
			results,
			file,
			indent=4,
			ensure_ascii=False
		)

	print()
	print("BFS CRAWLING COMPLETED")
	
	print(
		"Pages crawled:",
		len(visited)
	)

	print(
		"Pages remaining:",
		len(queue)
	)

	print(
		"Results saved: crawl_results.json"
	)

if __name__=="__main__":
	main()