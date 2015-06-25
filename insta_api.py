from urllib2 import Request, urlopen, URLError
from json import load, dumps
from pprint import pprint

# explicit authentication url
client_id = '50bcab2e724f415eaa4c72f4e2523fbb' # given from instagram
url_redir = 'http://jesusdacuma.wix.com/jesus-does-data'

## use this url to authorize
## https://api.instagram.com/oauth/authorize/?client_id=50bcab2e724f415eaa4c72f4e2523fbb&redirect_uri=http://jesusdacuma.wix.com/jesus-does-data&response_type=code 
url_auth = 'https://api.instagram.com/oauth/authorize/?client_id=' + client_id + '&redirect_uri=' + url_redir + '&response_type=code'
## after user logs in to authenticate, receive code and redirect
## http://jesusdacuma.wix.com/jesus-does-data?code='code'
code = '3ddb81be6e6a49778b2b6c7fc4ade695'

## for implicit authorization
## https://instagram.com/oauth/authorize/?client_id=50bcab2e724f415eaa4c72f4e2523fbb&redirect_uri=http://jesusdacuma.wix.com/jesus-does-data&response_type=token
## after user logs in to authenticate, receive access_token
## http://your-redirect-uri#access_token=ACCESS-TOKEN
access_token_j = '807280373.50bcab2.5a302a80437e4481b7fe72eb9277a7fd' # jj
access_token_c = '11080939.50bcab2.7f6628f686574b69ae648b8f711a9e08' # sancheeeeez


# get the access token from the given code
def get_access_token(code, cid, csec, url_redir):
    from urllib2 import Request, urlopen, URLError
    from json import load, dumps
    url = 'https://api.instagram.com/oauth/access_token?'
    url += 'client_id=' + cid
    url += 'client_secret=' + csec
    url += 'grant_type=authorization_code'
    url += 'redirect_uri=' + url_redir
    url += 'code=' + code
    
    # open the url, load the JSON
    request = Request(url)
    try:
        response = urlopen(request)
        json_obj = load(response)
        print json_obj
        access = response.read()
        print access
    except URLError, e:
        print 'Attempt to get access token failed. ERROR:', e
        
def get_user_data(access_token):
    url = 'https://api.instagram.com/v1/users/self/?access_token=' + access_token
    user_data = json_obj(url)
    return user_data
        
def get_user_count(user):
    # returns the number of media posts by the user
    # argument user is a JSON object returned from get_user_data
    return user['data']['counts']['media']
    
def get_user_media(access_token, count):
    # argument access_token is from the authenticated user
    # argument count is the amount of media to return
    url = 'https://api.instagram.com/v1/users/self/media/recent/?access_token=' + access_token
    url += '&count=' + str(count)
    media = json_obj(url)
    return media
    
def get_all_user_media(access_token):
    # argument access_token is from the authenticated user
    # argument count is the amount of media to return
    url = 'https://api.instagram.com/v1/users/self/media/recent/?access_token=' + access_token
    count = 30
    url += '&count=' + str(count)
    media = json_obj(url)
    
    while 'next_url' in media['pagination']:
        next_url = media['pagination']['next_url'] + '&count=' + str(count)
        new_media = json_obj(next_url)
        media['data'].extend(new_media['data'])
        media['pagination'] = new_media['pagination']
    
    return media
    
def media_to_file(media):
    # writes data from a JSON object about a user's media to a csv file
    # argument media is a JSON object returned from get_user_media
    import csv
    
    input_name = raw_input('Enter the file name: ')
    filename = '%s.csv' % input_name
    
    with open(filename, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        
        writer.writerow(('id', 'created_time', 'type', 'filter', 'caption', 'num_users', 'users_in_photo', 'num_tags', 'tags', 'location', 'num_comments', 'comments', 'likes'))

        for post in media['data']:
            id = post['id']
            created_time = post['created_time']
            type = post['type']
            filter = post['filter']
            
            try:
                caption = post['caption']['text'].encode('unicode_escape')
            except TypeError:
                caption = "NoCaption"

            num_users = len(post['users_in_photo'])
            if num_users > 0:
                users_in_photo = []
                for user in post['users_in_photo']:
                    users_in_photo.append(user['user']['username'])
                users_in_photo = list_to_element(users_in_photo,'@')
            else:
                users_in_photo = 'None'
        
            num_tags = len(post['tags'])
            if num_tags > 0:
                tags_no_emojis = []
                for tag in post['tags']:
                    tags_no_emojis.append(tag.encode('unicode_escape'))
                tags = list_to_element(tags_no_emojis,'#')
            else:
                tags = 'None'
        
            if post['location'] != None:
                if 'name' in post['location']:
                    location = post['location']['name'].encode('unicode_escape')
                else:
                    location = 'None'
            else:
                location = 'None'
        
            num_comments = post['comments']['count']
            if num_comments > 0:
                comments = []
                for comment in post['comments']['data']:
                    comments.append(comment['text'].encode('unicode_escape'))
                comments = list_to_element(comments,' ')
            else:
                comments = 'None'

            likes = post['likes']['count']
        
            writer.writerow((id, created_time, type, filter, caption, num_users, users_in_photo, num_tags, tags, location, num_comments, comments, likes))            

def print_media(media):
    i = 1
    for post in media['data']:
        print 'Post #%d \n'% i
        print 'ID: ' + str(post['id']) + '\n'  
        print 'Time Created: ' + str(post['created_time']) + '\n'
        print 'Type: ' + post['type'] + '\n'
        print 'Filter: ' + post['filter'] + '\n'
        
        print 'Caption: ' + post['caption']['text'] + '\n'
        
        num_users = len(post['users_in_photo'])
        print '# of Users in Photo: ' + str(num_users) + '\n'
        if num_users > 0:
            users_in_photo = []
            for user in post['users_in_photo']:
                users_in_photo.append(user['user']['username'])
            print 'Users in Photo: ' + list_to_element(users_in_photo,'@') + '\n'
        else:
            print 'Users in Photo: None' + '\n'
        
        num_tags = len(post['tags'])
        print '# of Tags: ' + str(num_tags) + '\n'
        if num_tags > 0:
            print 'Tags: ' + list_to_element(post['tags'],'#') + '\n'
        else:
            print 'Tags: None' + '\n'
        
        if post['location'] != None:
            if 'name' in post['location']:
                print 'Location: ' + post['location']['name'] + '\n'
            else:
                print 'Location: None' + '\n'
        else:
            print 'Location: None' + '\n'
        
        num_comments = post['comments']['count']
        print '# of Comments: ' + str(num_comments) + '\n'     
        if num_comments > 0:
            comments = []
            for comment in post['comments']['data']:
                comments.append(comment['text'])
            print 'Comments: ' + list_to_element(comments,' ') + '\n'
        else:
            print 'Comments: None' + '\n'

        likes = post['likes']['count']
        print 'Likes: ' + str(likes) + '\n'
        
        print '\n'
        i += 1
        
def list_to_element(l, d):
    d = str(d)
    element = ""
    for val in l:
        element = element + d + str(val)
    return element
    
def emoji_filter(mytext):
    # filters emojis encoded in UTF-16
    # function copied from http://stackoverflow.com/questions/13729638/how-can-i-filter-emoji-characters-from-my-input-so-i-can-save-in-mysql-5-5
    import re
    
    try:
        # UCS-4 build
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        # UCS-2 build
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    
    mytext = highpoints.sub(u'\u25FD', mytext)
    
#data
    ##attribution
    ##id
    ##created_time
    ##link
    ##filter
    ##type
    ##tags
    ##user
        ###username
        ###profile_picture
        ###id    
    ##caption
        ###created_time
        ###id
        ###text
        ###from
            ####full_name
            ####id
            ####profile_picture
            ####username
    ##likes
        ###count
        ###data
            ####username
            ####full_name
            ####id
            ####profile_picture    
    ##location
        ###latitude
        ###longitude
        ###id
        ###street_address
        ###name
    ##users_in_photo
        ###user
            ####full_name
            ####id
            ####profile_picture
            ####username            
        ###position
            ####x
            ####y 
    ##comments
        ###count
        ###data
            ####created_time
            ####id
            ####text
            ####from
                #####full_name
                #####id
                #####profile_picture
                #####username
    ##images/videos
        ###low_resolution
            ####height
            ####url
            ####width
        ###standard_resolution
            ####height
            ####url
            ####width
        ###thumbnail
            ####height
            ####url
            ####width        
    
def json_obj(url):
    # returns a JSON object from the given URL endpoint
    from urllib2 import Request, urlopen, URLError
    from json import load    
    
    request = Request(url)

    try:
        response = urlopen(request)
        json_obj = load(response)
        return json_obj
    except URLError, e:
        print 'ERROR:', e