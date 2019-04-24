from flask import Flask, render_template, Response, request, jsonify
import json, os
import pandas as pd
import numpy as np
import spotipy
import spotipy.util as util
app = Flask(__name__)


normalized_csv_df = None
percentile_df = None
token = None
sp = None
# Route to home page

@app.route('/search_page', methods=['GET', 'POST'])
def search_page():
	global normalized_csv_df
	global token
	global sp
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	csv_url = os.path.join(SITE_ROOT, "static/", "songs_with_recommendations_and_2d_proj_60k.csv")
	csv_url = os.path.join(SITE_ROOT, "static/", "normalized_songs_2.csv")
	normalized_csv_df = pd.read_csv(csv_url)
	scope = 'playlist-read-private playlist-read-collaborative user-library-read user-read-recently-played user-top-read'
	username = 'jchen13542'
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


def get_relevant_song_attr(song_id):
	df = normalized_csv_df
	df1 = df[['song_id','cluster','song_1','song_2','song_3','song_4','song_5','song_6','song_7','song_8','song_9','song_10', \
		"energy", "loudness", "danceability", "valence", "tempo","acousticness", "liveness", "duration_ms", "speechiness"]]

	row = df1.loc[df1['song_id'] == song_id]
	print(row)
	print(row['song_id'].values[0])

	relevant_points = [row['song_id'].values[0], row['song_1'].values[0], row['song_2'].values[0], row['song_3'].values[0], row['song_4'].values[0], row['song_5'].values[0], row['song_6'].values[0], \
		row['song_7'].values[0], row['song_8'].values[0], row['song_9'].values[0], row['song_10'].values[0]]

	print(row)
	mask = df1['song_id'].isin(relevant_points)

	df1 = df1.loc[mask]

	return df1

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
	df = get_relevant_points(song_id, pd.read_csv(csv_url))

	df_radar = get_relevant_song_attr(song_id)

	radar_data = df_radar.to_dict(orient='records')
	radar_data = json.dumps(radar_data, indent=2)

	clustering_data = df.to_dict(orient='records')
	clustering_data = json.dumps(clustering_data, indent=2)

	csv_data = pd.read_csv(csv_url)
	if percentile_df is None:
		precompute_percentages(csv_data)

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
		'artist': artist,
    'radar_points' : radar_data})

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
	scope = 'playlist-read-private playlist-read-collaborative user-library-read user-read-recently-played user-top-read'
	username = 'jchen13542'
	global token
	global sp
	token = util.prompt_for_user_token(username,scope,client_id=os.environ['SPOTIPY_CLIENT_ID'],client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])
	sp = spotipy.Spotify(auth=token)
	playlists = sp.current_user_playlists()
	playlist_data = []
	for playlist in playlists['items']:
		playlist_image = playlist['images'][0]['url']
		playlist_id = playlist['id']
		playlist_name = playlist['name']
		playlist_data.append({'playlist_id': playlist_id, 'playlist_name': playlist_name, 'playlist_url': playlist_image})

	return json.dumps(
		playlist_data
	)

@app.route('/playlistTrackRetriever', methods = ['GET', 'POST'])
def playlistTrackRetriever():
	playlist_track_ids = []
	playlist_id = list(request.json.values())[0]
	results = sp.user_playlist('1226629431', playlist_id, fields = 'tracks,next,name')
	for track in results['tracks']['items']:
		if track != None and track['track'] != None:
			track_id = track['track']['id']
			playlist_track_ids.append(track_id)
	return json.dumps( {'playlist_track_ids': playlist_track_ids})
	
@app.route('/summarizationPage', methods = ['GET', 'POST'])
def summarizationPage():
	scope = 'playlist-read-private playlist-read-collaborative user-library-read user-read-recently-played user-top-read'
	username = 'jchen13542'
	global token
	global sp
	token = util.prompt_for_user_token(username,scope,client_id=os.environ['SPOTIPY_CLIENT_ID'],client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])
	sp = spotipy.Spotify(auth=token)
	return render_template('summarization_page.html')

@app.route('/', methods = ['GET', 'POST'])
def homePage():
	scope = 'playlist-read-private playlist-read-collaborative user-library-read user-read-recently-played user-top-read'
	username = 'jchen13542'
	global token
	global sp
	token = util.prompt_for_user_token(username,scope,client_id=os.environ['SPOTIPY_CLIENT_ID'],client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])
	sp = spotipy.Spotify(auth=token)
	return render_template('index.html')


def trackAnalysis(track_ids):
	print("TRACK ANALYSIS")
	artist_ids = set()
	for track_id in track_ids:
		track_information = sp.track(track_id)
		artist_id = None
		try:
			artist_id = track_information['album']['artists'][0]['id']
		except Exception as e:
			pass
		if artist_id != None:
			artist_ids.add(artist_id)
		all_genres = []
		for artist_id in artist_ids:
			try:
				
				artist_genres = sp.artists(artist_ids)['artists'][0]['genres']
				all_genres += artist_genres
			except Exception as e:
				print(e)
				pass
	print("WTF")
	print(all_genres)
	all_genres = [x.lower() for x in all_genres]
	genre_counts = [[x,all_genres.count(x)] for x in set(all_genres)]
	print(genre_counts)

	sorted_by_occurrence = sorted(genre_counts, key=lambda tup: tup[1])
	top_genres = [x[0] for x in sorted_by_occurrence[0:3]]
	print(top_genres)
	genres_text = ", ".join(top_genres)
	text = "This playlist consists primarily of songs from the " + genres_text + " genre(s)."

	return text

@app.route('/playlistTrackAnalysis', methods = ['GET', 'POST'])
def playlistTrackAnalysis():
	scope = 'playlist-read-private playlist-read-collaborative user-library-read user-read-recently-played user-top-read'
	username = 'jchen13542'
	global token
	global sp
	token = util.prompt_for_user_token(username,scope,client_id=os.environ['SPOTIPY_CLIENT_ID'],client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])
	sp = spotipy.Spotify(auth=token)
	track_ids = request.json
	track_ids = list(track_ids.values())[0]
	print(type(track_ids))
	print("lalalaalalalaala")
	print(track_ids)
	summary_information = trackAnalysis(track_ids)
	return json.dumps( {'track_analysis': summary_information})

if __name__ == "__main__":
    app.run(debug=True)
