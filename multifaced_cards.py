import requests
import json
import pickle


def scrape_mfdcs():
	l = ['split', 'transform', 'dfc', 'mdfc', 'adventure']
	d = {}

	for card_type in l:
		card_dict = {}
		all_pages_done = False
		content = json.loads(requests.get(f'https://api.scryfall.com/cards/search?q=is%3A{card_type}+&unique=cards&order=name').content)
		while (all_pages_done == False):
			for i in content['data']:
				if i['name'].split(' // ')[0] != i['name'].split(' // ')[1]:
					card_dict[i['name'].split(' // ')[0]] = i['name'].split(' // ')[1]
			if content['has_more'] == True:
				content = json.loads(requests.get(content['next_page']).content)
			else:
				all_pages_done = True
		d[card_type] = card_dict

	for i in d:
		print(len(d[i]))

	with open('MULTIFACED_CARDS.txt','w',encoding='utf-8') as txt:
		for i in d:
			txt.write(f'{i.upper()}\n')
			for card in d[i]:
				txt.write(f'{card} // {d[i][card]}\n')
			txt.write(f'\n')
	return
