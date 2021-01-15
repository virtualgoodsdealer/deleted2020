import json

with open('post_list.json') as json_file:
	data = json.load(json_file)
	for post in data:
		post_id = post['post_id']
		f = open("markdown_files/2020-12-31-" + post_id + ".md", "w")
		f.write("---\nlayout: post \n---")
		f.close