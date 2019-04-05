from flask import Flask, render_template, Response, request, jsonify
import json, os
import pandas as pd
import numpy as np
from wtforms import TextField, Form
app = Flask(__name__)

songs = {"a": "Shape of You", "b": "Hello", "c": "a lot", "d" : "Happy Now", "e": "Your Shirt", "f": "Just For A Moment", "g": "Moments"}
NAMES=["abc","abcd","abcde","abcdef"]
class SearchForm(Form):
    autocomp= TextField('autocomp',id='autocomplete')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
	search = request.args.get('q')
	results = [{'value': 'MIR:00000466', 'label': 'WormBase RNAi'}, \
		{'value': 'MIR:00000031', 'label': 'Wormpep'}, {'value': 'MIR:00000186', 'label': 'Xenbase'}, \
		{'value': 'MIR:00000111', 'label': 'Resource 1'}, {'value': 'MIR:00000222', 'label': 'Resource 2'}, \
		{'value': 'MIR:00000333', 'label': 'Resource 3'}, {'value': 'MIR:00000444', 'label': 'Resource 4'}, \
		{'value': 'MIR:00000555', 'label': 'Resource 5'}, {'value': 'MIR:00000666', 'label': 'Resource 6'}]

	return jsonify(matching_results=results)

# ** Example 5 **
# Autocomplete with Bloodhound with Remote data
@app.route('/bloodhoundRemote', methods=['GET', 'POST'])
def bloodhoundRemote():
	print("** bloodhoundRemote() called")
	if request.method == 'POST':
		print("POST request")
	else:
		print("GET request")
	
	citynames = ['Amsterdam', 'London', 'Paris', 'Washington', 'Sydney', 'Melbourne']
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	print(SITE_ROOT)
	json_url = os.path.join(SITE_ROOT, "static/", "song_id_and_names.json")
	data = json.load(open(json_url))
	print(data['songs'])
	print("SDF")
	# resource_list = [{'value': 'MIR:00000555', 'label': 'My WormBase RNAi'}, \
	# 	{'value': 'MIR:11100545', 'label': 'My Wormpep'}]
	return jsonify(resource_list=data['songs'], citynames=citynames)

# Route to home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def show_home():
	print("home root")
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	csv_url = os.path.join(SITE_ROOT, "static/", "recommendations_with_names.csv")
	song_id = "15O20RQyWJgKrkHID9ynT9"
	df = get_relevant_points(song_id, pd.read_csv(csv_url))
	clustering_data = df.to_dict(orient='records')
	clustering_data = json.dumps(clustering_data, indent=2)
	data = {'clustering_data': clustering_data}
	return render_template('materialTagsExamples.html', clustering_data = clustering_data)

def get_relevant_points(song_id, df):
	#print("HI")
	df1 = df[['id','cluster','song.0','song.1','song.2','song.3','song.4','song.5','song.6','song.7','song.8','song.9','X','Y']]
	row = df1.loc[df1['id'] == song_id]
	print("WHy")
	relevant_points = [row.at[0,'id'], row.at[0,'song.0'], row.at[0,'song.1'], row.at[0,'song.2'], row.at[0,'song.3'], row.at[0,'song.4'], row.at[0,'song.5'], \
		row.at[0,'song.6'], row.at[0,'song.7'], row.at[0,'song.8'], row.at[0,'song.9']]
	#print(relevant_points)
	print("SKDF1JSLKDF1JL")
	print(row)
	mask = df1['id'].isin(relevant_points)
	#print(mask)
	df1 = df1.loc[mask]
	min_x = df1['X'].min()
	max_x = df1['X'].max()
	min_y = df1['Y'].min()
	max_y = df1['Y'].max()
	#print(min_x, max_x, min_y, max_y)
	relevant_rows = df[(df['X'] >= min_x - (0.01)) & (df['X'] <= max_x + 0.01) & (df['Y'] >= min_y - 0.01) & (df['Y'] <= max_y) + 0.01]
	relevant_rows["top_10"] = False
	relevant_rows['top_10'] = np.where(relevant_rows['id'].isin(relevant_points), True, False)
	#print(relevant_rows)
	#print(df1.shape)
	return relevant_rows


@app.route('/materialTagsExamples', methods=['GET'])
def materialTagsExamples():
	print("Show materialTags Examples Examples")
	return render_template('materialTagsExamples.html')


@app.route('/songSearch', methods=['GET', 'POST'])
def songSearch():
	print("NONONO")
	song = request.json
	print("SONG OSNG ")
	print(song)

	return json.dumps({'status':'OK','id': song['song_ids'],'pass':"123"})

@app.route("/james")
def james():
    return "Hello, James"


if __name__ == "__main__":
    app.run(debug=True)
