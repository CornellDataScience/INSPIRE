from flask import Flask, render_template, Response, request, jsonify
import json, os
import pandas as pd
import numpy as np
from wtforms import TextField, Form
app = Flask(__name__)

# Route to home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def show_home():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	csv_url = os.path.join(SITE_ROOT, "static/", "songs_with_recommendations_and_2d_proj_60k.csv")
	song_id = "5pvJ59i7JxylN8VB24xdMs"
	df = get_relevant_points(song_id, pd.read_csv(csv_url))
	clustering_data = df.to_dict(orient='records')
	clustering_data = json.dumps(clustering_data, indent=2)
	data = {'clustering_data': clustering_data}
	return render_template('search_page.html', clustering_data = clustering_data)

def get_relevant_points(song_id, df):
	df1 = df[['song_id','cluster','song_1','song_2','song_3','song_4','song_5','song_6','song_7','song_8','song_9','song_10','x','y']]
	row = df1.loc[df1['song_id'] == song_id]
	print(row)
	print(row['song_id'].values[0])

	relevant_points = [row['song_id'].values[0], row['song_1'].values[0], row['song_2'].values[0], row['song_3'].values[0], row['song_4'].values[0], row['song_5'].values[0], row['song_6'].values[0], \
		row['song_7'].values[0], row['song_8'].values[0], row['song_9'].values[0], row['song_10'].values[0]]

	print(row)
	mask = df1['song_id'].isin(relevant_points)

	df1 = df1.loc[mask]
	min_x = df1['x'].min()
	max_x = df1['x'].max()
	min_y = df1['y'].min()
	max_y = df1['y'].max()
	center_x = (min_x + max_x) / 2
	center_y = (min_y + max_y) / 2
	#relevant_rows = df[(df['x'] >= min_x - (0.4)) & (df['x'] <= max_x + 0.4) & (df['y'] >= min_y - 0.4) & (df['y'] <= max_y) + 0.4]
	relevant_rows = df[(df['x'] - center_x)**2 + (df['y'] - center_y)**2 <= max(max_x - center_x, max_y - center_y)**2 + 0.10]
	#relevant_rows = df
	relevant_rows["top_10"] = False
	relevant_rows["top_10"] = np.where(relevant_rows['song_id'].isin(relevant_points), True, False)
	#return df
	return relevant_rows


@app.route('/songSearchHandler', methods=['GET', 'POST'])
def songSearchHandler():
	song_id = request.json
	song_id = list(song_id.values())[0]
	print(song_id)
	print(type(song_id))
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	csv_url = os.path.join(SITE_ROOT, "static/", "songs_with_recommendations_and_2d_proj_60k.csv")
	df = get_relevant_points(song_id, pd.read_csv(csv_url))
	clustering_data = df.to_dict(orient='records')
	clustering_data = json.dumps(clustering_data, indent=2)
	data = {'clustering_data': clustering_data}
	print("SONG SONG SONG")

	return json.dumps({'status':'OK','id': song_id,'relevant_points': clustering_data})

def getPairwiseComparisonData(song_id_1, song_id_2, df):
	rows = df.loc[df['song_id'].isin([song_id_1, song_id_2])]
	return rows

@app.route("/radioPlot")
def radioPlot():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	csv_url = os.path.join(SITE_ROOT, "static/", "normalized_songs_for_radio_plot.csv")
	song_id_1 = "5pvJ59i7JxylN8VB24xdMs"
	song_id_2 = "3uHaLhm6yStMMAGetn1Z47"
	#df = getPairwiseComparisonData(song_id_1, song_id_2, pd.read_csv(csv_url))
	df = pd.read_csv(csv_url);
	two_points = df.to_dict(orient='records')
	two_points = json.dumps(two_points, indent=2)
	return render_template('radioplot.html', two_points = two_points) 


if __name__ == "__main__":
    app.run(debug=True)
