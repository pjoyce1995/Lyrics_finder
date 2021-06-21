#! /usr/bin/aire_proj python2.7

#IMPORT MODULES
import musicbrainzngs
import sys
import requests
from bs4 import BeautifulSoup,NavigableString
import re
import numpy as np
from matplotlib import pyplot as plt
from funcs_lyrics import find_matching_artist_lyric, split_punctuation

#INITIALISE MUSICBRAINZ
musicbrainzngs.set_useragent("pjoyce", "0.1", "peterjoyce247@gmail.com")
artist_id=''
trying=True
while artist_id == '' and trying == True:
    #ASK FOR INPUT
    input_artist = input("Please enter an artist:\n")
    result = musicbrainzngs.search_artists(artist=input_artist)
    #FIND THE RESULT THAT CORRESPONDS TO THE INPUT AND OBTAIN THE ID
    for artist in result['artist-list']:
        if input_artist.lower()==artist['name'].lower():
            artist_id=artist['id']

    #CATCH INPUTS THAT RETURN NO IDS
    if artist_id=='':
        print('Could not find exact match, press the number corresponding to your artist of choice:')
        print('[ 0 ] None of these')
        #GIVE THE OPTION OF CHOOSING THE ARTIST FROM A LIST IF NOT FOUND AN EXACT MATCH
        for artist in range(1,len(result['artist-list'])+1):
            print('[',artist,'] ',result['artist-list'][artist-1]['name'])
        answered_number=False
        while answered_number==False:
            input_num=input("Which number?:\n")
            input_num=int(input_num)
            if input_num in range(0,len(result['artist-list'])+1):
                answered_number=True
        #IF THE ARTIST IS NOT FOUND, THEN ASK IF THE USER WANTS TO TRY AGAIN
        if input_num==0:
            answered_y_n=False
            while answered_y_n==False:
                answer_trying_again=input('Could not find your artist! Would you like to try again? (y/n) \n')
                if answer_trying_again.lower() in ['n','no','nope','narp','no sirree']:
                    trying,answered_y_n=False,True
                    sys.exit()
                elif answer_trying_again.lower()  in ['y','yes','yarp']:
                    answered_y_n=True
        else:
            artist_id=result['artist-list'][input_num-1]['id']
            print('You have chosen ', result['artist-list'][input_num-1]['name'])
    else:
        print('Artist found!')

all_songs=[]
album_ids=musicbrainzngs.browse_release_groups(artist_id)['release-group-list']
print('Searching through albums...')
#ITERATE THROUGH ALL ALBUMS AND FIND ALL SONG NAMES
for alb in range(len(album_ids)):
    album_id=album_ids[alb]['id']
    release=musicbrainzngs.browse_releases( release_group=album_id, release_status=[], release_type=[], includes=[])['release-list']
    release=release[0]['id']
    songs=musicbrainzngs.browse_recordings(release=release, includes=[], limit=None, offset=None)['recording-list']
    for song in range(len(songs)):
        all_songs.append(songs[song]['title'])
print('Found ', len(all_songs), 'songs by ', input_artist)
print('Finding lyrics...')

#######################
#find lyrics from each song
########################

artist_name=input_artist
#initialise variables for output info
all_len_songs=[]
longest_song={'NA': None}
shortest_song={'NA': None}
narc_score=0
no_lyrics_found=[]
song_search=1
for song in all_songs:
    #PRINT PROGRESS
    sys.stdout.write('\rSearching for lyrics: %s / %s' % (str(song_search),len(all_songs)))
    sys.stdout.flush()

    #FORMAT ARTIST AND SONG TITLE TO MAKE URL
    song_search+=1
    song_split=song.split(' ')
    song_split = split_punctuation(song_split, '-')
    song_split = split_punctuation(song_split, '.')
    song_split = split_punctuation(song_split, '/')
    song_str=''
    for word in song_split:
        if len(word)>0:
            song_str+=re.sub('[\W_]', '', word)
            song_str+='-'
    artist_split=artist_name.split(' ')
    artist_split = split_punctuation(artist_split, '-')
    artist_split = split_punctuation(artist_split, '.')
    artist_split = split_punctuation(artist_split, '/')
    art_str=''
    for word in artist_split:
        art_str+=re.sub('[\W_]', '', word)
        art_str+='-'
    str_artist_song=art_str+song_str
    #OPEN URL
    URL='https://genius.com/'+str_artist_song+'lyrics'
    content = requests.get(URL)
    #OBTAIN LYRICS
    soup = BeautifulSoup(content.text, 'html.parser')
    #CLEAN UP LYRICS
    lyrics = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-7 jjqBBp")
    if lyrics is None:
        #alternative way of reading in lyrics for certain songs
        lyrics=(soup.p)
    if lyrics is None:
        #CATCHING SITUATIONS WHERE LYRICS NOT RELEASED (E.G. https://genius.com/Sam-fender-hypersonic-missiles-patrick-topping-shields-remix-lyrics)
        words_list = ['Sorry', 'we', 'didnt', 'mean', 'for', 'that', 'to', 'happen']
    else:
        lyrics = lyrics.get_text(' ')
        lyrics = lyrics.replace('\n', ' ')
        lyrics_no_brackets = re.sub("[\(\[].*?[\)\]]", "", lyrics)
        words_list = lyrics_no_brackets.split(' ')
        lyrics_alpha_num = re.sub('[\W_]', '', lyrics_no_brackets)
        words_list = [re.sub('[\W_]', '', i) for i in words_list if len(re.sub('[\W_]', '', i)) > 0]
    #FIND INFO ABOUT LYRICS
    if words_list!=['Sorry', 'we', 'didnt', 'mean', 'for', 'that', 'to', 'happen']:
        length_song=len(words_list)
        all_len_songs.append(length_song)
        narc_score+=find_matching_artist_lyric(words_list, artist_name)
        if 'NA' in longest_song.keys():
            longest_song  = {song: length_song}
            shortest_song = {song: length_song}
        else:
            if next(iter(longest_song.values())) < length_song:
                longest_song={song: length_song}
            if next(iter(shortest_song.values())) > length_song:
                shortest_song={song: length_song}
    else:
        no_lyrics_found.append(song)

if len(all_songs)==0:
    print('No lyrics found for the artist!')
    sys.exit()
#PRINT OUT INFO AND PLOT HISTOGRAM
print('\n Found lyrics for ', len(all_songs)-len(no_lyrics_found), '.\n Could not find lyrics for the following songs:')
print(no_lyrics_found)
print('\nMean number of lyrics over all songs: ', np.mean(all_len_songs))
print('\nStandard deviation of number of lyrics over all songs: ', np.std(all_len_songs))
print('Shortest song: ',shortest_song)
print('Longest Song: ', longest_song)
print("Narcissism Score (how many times the artist's name appears in the lyrics): ", narc_score)
plt.hist(all_len_songs)
plt.ylabel('Frequency')
plt.xlabel('Lyrics')
plt.show()