import re


imdb_rating = 'strong>6.8</strong'
imdb_rating = re.findall(r'>[\d\.]*<', str(imdb_rating))
imdb_rating=imdb_rating[0][1:-1]
print(imdb_rating)