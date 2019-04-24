from flask import Flask, render_template, Response, request, jsonify
import json, os
import pandas as pd
import numpy as np
import spotipy
import spotipy.util as util
app = Flask(__name__)

# Global Variables
# Percentile df
percentile_df = None
token = None
sp = None
# Route to home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def show_home():
	scope = 'playlist-read-private playlist-read-collaborative user-library-read user-read-recently-played user-top-read'
	username = 'jchen13542'
	global token
	global sp
	token = util.prompt_for_user_token(username,scope,client_id=os.environ['SPOTIPY_CLIENT_ID'],client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])
	sp = spotipy.Spotify(auth=token)
	return render_template('search_page.html')

def get_relevant_points(song_id, df):
	df1 = df[['song_id','cluster','song_1','song_2','song_3','song_4','song_5','song_6','song_7','song_8','song_9','song_10','x','y']]
	row = df1.loc[df1['song_id'] == song_id]

	relevant_points = [row['song_id'].values[0], row['song_1'].values[0], row['song_2'].values[0], row['song_3'].values[0], row['song_4'].values[0], row['song_5'].values[0], row['song_6'].values[0], \
		row['song_7'].values[0], row['song_8'].values[0], row['song_9'].values[0], row['song_10'].values[0]]

	mask = df1['song_id'].isin(relevant_points)

	df1 = df1.loc[mask]
	min_x = df1['x'].min()
	max_x = df1['x'].max()
	min_y = df1['y'].min()
	max_y = df1['y'].max()
	center_x = (min_x + max_x) / 2
	center_y = (min_y + max_y) / 2
	relevant_rows = df[(df['x'] - center_x)**2 + (df['y'] - center_y)**2 <= max(max_x - center_x, max_y - center_y)**2 + 0.10]
	relevant_rows["top_10"] = False
	relevant_rows["top_10"] = np.where(relevant_rows['song_id'].isin(relevant_points), True, False)
	return relevant_rows

def precompute_percentages(df):
	global percentile_df
	df_features = df[['song_id', 'song_name', 'artist', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']]
	for feature in list(df_features.columns.values)[3:]:
		col_name = feature + '_percentile'
		df_features[col_name] = df_features[feature].rank(pct=True)
	percentile_df = df_features

def get_percentiles(song_id):
	row = percentile_df.loc[percentile_df['song_id'] == song_id]
	song_name = row['song_name'].values[0]
	artist = row['artist'].values[0]
	return row, song_name, artist

@app.route('/songSearchHandler', methods=['GET', 'POST'])
def songSearchHandler():
	song_id = request.json
	song_id = list(song_id.values())[0]
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	csv_url = os.path.join(SITE_ROOT, "static/", "songs_with_recommendations_and_2d_proj_60k.csv")
	csv_data = pd.read_csv(csv_url)
	if percentile_df is None:
		precompute_percentages(csv_data)
	
	df = get_relevant_points(song_id, csv_data)
	clustering_data = df.to_dict(orient='records')
	clustering_data = json.dumps(clustering_data, indent=2)

	statistics_df, song_name, artist = get_percentiles(song_id)
	statistics_df_t = statistics_df.T
	statistics_df_t['feature'] = statistics_df_t.index
	statistics_df_t.columns = ['value', 'feature']
	statistics_data = statistics_df_t.to_dict(orient = 'records')
	statistics_data = json.dumps(statistics_data, indent = 2)
	return json.dumps(
		{'id': song_id,
		'relevant_points': clustering_data,
		'percentile_data': statistics_data,
		'song_name': song_name,
		'artist': artist})

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


@app.route('/playlistRetriever', methods=['GET', 'POST'])
def playlistRetriever():
	playlists = sp.current_user_playlists()
	playlist_data = []
	for playlist in playlists['items']:
		playlist_id = playlist['id']
		playlist_name = playlist['name']
		playlist_data.append({'playlist_id': playlist_id, 'playlist_name': playlist_name})

	print(playlist_data)
	return json.dumps(
		playlist_data
	)

@app.route('/playlistTrackRetriever', methods = ['GET', 'POST'])
def playlistTrackRetriever():
	playlist_track_ids = []
	print("ASDFKL;DFJFK;LDJFKDJKDFDFDFJAJLFJSJSFLSJLSJFLJLSFSFDFDFDF")
	playlist_id = list(request.json.values())[0]
	print(sp.me())
	results = sp.user_playlist('1226629431', playlist_id, fields = 'tracks,next,name')
	for track in results['tracks']['items']:
		if track != None and track['track'] != None:
			track_id = track['track']['id']
			playlist_track_ids.append(track_id)
	print(playlist_track_ids)
	return json.dumps( {'playlist_track_ids': playlist_track_ids})
	

if __name__ == "__main__":
    app.run(debug=True)
