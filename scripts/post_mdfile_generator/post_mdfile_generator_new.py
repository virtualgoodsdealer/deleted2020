import json

with open('post_dictionary.json', 'rb') as json_file:
	data = json.load(json_file)
	for post_id, post in data.items():
		f = open("markdown_files/" + post_id + ".md", "w")
		f.write("---\n\n---")
		f.close