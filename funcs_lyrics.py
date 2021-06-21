def find_matching_artist_lyric(song_ly, artist_title):
    """
    :param song_ly: List containing song lyrics as each element of the list
    :param artist_title: string of the artist being used
    :return: number of times the artist mentions their own name in the lyrics
    """
    total_narc=0
    artist_title=artist_title.lower().split(' ')
    for lyric_iter in range(0,len(song_ly)-len(artist_title)+1):
        matches_artist=False
        if song_ly[lyric_iter].lower()==artist_title[0]:
            matches_artist=True
            for artist_word in range(len(artist_title)-1):
                if song_ly[lyric_iter+1].lower()!=artist_title[artist_word+1]:
                    matches_artist=False
        if matches_artist==True:
            total_narc+=1
    return total_narc

def split_punctuation(song_name,punctuation):
    """
    :param song_name: Name of a song as a list of strings
    :param punctuation: The punctuation type to split up by
    :return: Name of the song now split by the punctuation
    """
    song_name = [i.split(punctuation) for i in song_name]
    song_name = [item for sublist in song_name for item in sublist]
    return song_name
