TITLE = 'MTV Shows'
PREFIX = '/video/mtvshows'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.mtv.com'
SHOWS = 'http://www.mtv.com/ontv'
MTV_SHOWS_ALL = 'http://www.mtv.com/ontv/all/'
MTV_POPULAR = 'http://www.mtv.com/most-popular/%smetric=numberOfViews&range=%s&order=desc'
# The three variables below produce the results page for videos for shows with the new format
NEW_SHOW_AJAX = 'http://www.mtv.com/include/shows/seasonAllVideosAjax?id=%s&seasonId=%s&resultSize=1000&template=%s&start=0'
ALL_VID_TEMP = '%2Fshows%2Fplatform%2Fwatch%2Fmodules%2FseasonRelatedPlaylists'
FULL_EP_TEMP = '%2Fshows%2Fplatform%2Fwatch%2Fmodules%2FepisodePlaylists'
# The code below is used for the new format when a season id is not given to show full episodes,
# but there is only one show with this situation so just using the actual page for that one
NEW_SHOW_ALT_AJAX = 'http://www.mtv.com/include/series/relatedEpisodes?id=%s&seasonId=%s&resultSize=30&template=%2Fshows%2Fplatform%2Fwatch%2Fmodules%2FepisodePlaylists&start='
BUILD_URL = 'http://www.vh1.com/video/?id='

RE_SEASON  = Regex('Season (\d{1,2})')
RE_EP = Regex('\| Ep. (\d{1,3})')
RE_VIDID = Regex('#id=(\d{7})')
# episode regex for new show format
RE_EXX = Regex('/e(\d+)')
LATEST_VIDEOS = [
    {'title'  : 'Latest Full Episodes',  'url'  : 'http://www.mtv.com/videos/home.jhtml'},
    {'title'  : 'Latest Music Videos',   'url'  : 'http://www.mtv.com/music/videos/'},
    {'title'  : 'Latest Movie Trailers',  'url'  : 'http://www.mtv.com/movies/trailer_park/'}
]
# The latest interviews do not fit into the current video page format, so we have removed them
#    {'title'  : 'Latest Movie Interviews',   'url'  : 'http://www.mtv.com/movies/features_interviews/morevideo.jhtml'}
MOST_POPULAR = [
    {'title'  : 'All Videos',  'video_type'  : 'videos/?'},
    {'title'  : 'Full Episodes',   'video_type'  : 'tv-show-videos/?category=full-episodes&'},
    {'title'  : 'After Shows',  'video_type'  : 'tv-show-videos/?category=after-shows&'},
    {'title'  : 'Show Clips',  'video_type'  : 'tv-show-videos/?category=bonus-clips&'},
    {'title'  : 'All Music Videos',   'video_type'  : 'music-videos/?'},
    {'title'  : 'Pop & Rock Music Videos',  'video_type'  : 'music-videos/?category=pop&'},
    {'title'  : 'Hip Hop Music Videos',  'video_type'  : 'music-videos/?category=hip-hop&'},
    {'title'  : 'Movie Trailers',   'video_type'  : 'movie-trailers/?'},
    {'title'  : 'Movie Interviews',  'video_type'  : 'movie-clips/?'}
]
# Specials Archive List
SPECIAL_ARCHIVES = [
    {'title'  : 'Video Music Awards',  'url'  : 'http://www.mtv.com/ontv/vma/archive/'},
    {'title'  : 'Movie Awards',   'url'  : 'http://www.mtv.com/ontv/movieawards/archive/'},
    {'title'  : 'mtvU Woodie Awards',  'url'  : 'http://www.mtv.com/ontv/woodieawards/archive/'}
]

####################################################################################################
# Set up containers for all possible objects
def Start():

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    EpisodeObject.thumb = R(ICON)
    VideoClipObject.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR 
 
#####################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(MTVShows, title='MTV Shows'), title='MTV Shows')) 
    oc.add(DirectoryObject(key=Callback(MTVVideos, title='MTV Videos'), title='MTV Videos')) 
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.mtvshows", title=L("Search MTV Videos"), prompt=L("Search for Videos")))
    return oc
#######################################################################################
# This is a function that only returns show urls to provide users easier access to archived shows
# This function uses the "All Results" section of the MTV search URL and only returns URLs that end with series.jhtml
# THIS DOES NOT USE OR INTERACT WITH THE SEARCH SERVICE FOR VIDEOS AND IS A COMPLETELY SEPARATE FUNCTION
@route(PREFIX + '/showsearch')
def ShowSearch(query):
    oc = ObjectContainer(title1='MTV', title2='Show Search Results')
    url = '%s/search/?q=%s' %(BASE_URL, String.Quote(query, usePlus = True))
    html = HTML.ElementFromURL(url)
    for item in html.xpath('//div[@id="searchResults"]/ul/li'):
        link = item.xpath('.//a/@href')[0]
        # This make sure it only returns show pages by making sure the url starts with www.mtv.com/shows/ that may contain /season_?/ and ends with / or series.jhtml
        try:
            season = 0
            url_part = link.split('http://www.mtv.com/shows/')[1]
            if 'season_' in url_part:
                season = int(url_part.split('season_')[1].split('/')[0])
                url_test = url_part.split('/')[2]
            else:
                url_test = url_part.split('/')[1]
            if not url_test or url_test=='series.jhtml':
                title = item.xpath('./div[contains(@class,"mtvn-item-content")]//a//text()')[0]
                thumb = item.xpath('.//img/@src')[0].split('?')[0]
                # Most shows are listed by individual season in the show search unless new format
                if link.endswith('series.jhtml'):
                    oc.add(DirectoryObject(key=Callback(ShowOldSections, title=title, thumb=thumb, url=link, season=season), title=title, thumb = thumb))
                else:
                    oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, thumb=thumb, url=link), title=title, thumb = thumb))
        except:
            continue
    return oc

#####################################################################################
# For MTV main sections of Popular, Specials, and All Shows
@route(PREFIX + '/mtvshows')
def MTVShows(title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(ProduceShows, title='Current MTV Shows'), title='Current MTV Shows')) 
    # The MTV2 currents shows link ('http://www.mtv.com/ontv/all/currentMtv2.jhtml') could also be used with AllShows() function
    oc.add(DirectoryObject(key=Callback(ProduceShows, title='Current MTV2 Shows'), title='Current MTV2 Shows')) 
    oc.add(DirectoryObject(key=Callback(ProduceSpecials, title='MTV Specials'), title='MTV Specials')) 
    oc.add(DirectoryObject(key=Callback(ShowsAll, title='All MTV & MTV2 Shows'), title='MTV All Shows')) 
    # THE MENU ITEM BELOW CONNECTS TO A FUNCTION WITHIN THIS CHANNEL CODE THAT PRODUCES A LIST OF SHOWS FOR USERS 
    # IT DOES NOT USE OR INTERACT WITH THE SEARCH SERVICES FOR VIDEOS LISTED NEXT
    #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
    oc.add(InputDirectoryObject(key=Callback(ShowSearch), title='Search for MTV Shows', summary="Click here to search for shows", prompt="Search for the shows you would like to find"))
    return oc
#####################################################################################
# For MTV main sections of Videos
@route(PREFIX + '/mtvvideos')
def MTVVideos(title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(LatestVideos, title='Latest Videos'), title='Latest Videos')) 
    oc.add(DirectoryObject(key=Callback(MostPopularVideos, title='Most Popular Videos'), title='Most Popular Videos')) 
    return oc
#####################################################################################
# For main sections of Latest Videos
@route(PREFIX + '/latestvideos')
def LatestVideos(title):
    oc = ObjectContainer(title2=title)
    for items in LATEST_VIDEOS:
        title = items['title']
        # Skip full episodes for Android Clients
        if "Full Episodes" in title and Client.Platform in ('Android'):
            continue
        url = items['url']
        oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title=title)) 
    return oc
#####################################################################################
# For main sections of Most Popular Videos
@route(PREFIX + '/mostpopularvideos')
def MostPopularVideos(title):
    oc = ObjectContainer(title2=title)
    for items in MOST_POPULAR:
        title = items['title']
        # Skip full episodes for Android Clients
        if "Full Episodes" in title and Client.Platform in ('Android'):
            continue
        video_type = items['video_type']
        oc.add(DirectoryObject(key=Callback(MostPopularSections, title=title, video_type=video_type), title=title)) 
    return oc
####################################################################################################
# MTV Popular Split by day week and month
@route(PREFIX + '/mostpopularsections')
def MostPopularSections(title, video_type):
    oc = ObjectContainer(title2=title)
    time = ["today", "week", "month"]
    oc.add(DirectoryObject(key=Callback(VideoPage, url = MTV_POPULAR %(video_type, time[0]), title="Most Popular Today"), title="Most Popular Today"))
    oc.add(DirectoryObject(key=Callback(VideoPage, url = MTV_POPULAR %(video_type, time[1]), title="Most Popular This Week"), title="Most Popular This Week"))
    oc.add(DirectoryObject(key=Callback(VideoPage, url = MTV_POPULAR %(video_type, time[2]), title="Most Popular This Month"), title="Most Popular This Month"))
    return oc
#####################################################################################
# For Producing Popular Shows 
@route(PREFIX + '/produceshows')
def ProduceShows(title):
    oc = ObjectContainer(title2=title)
    if 'MTV2' in title:
        xpath = 'mtv2shows'
        local_url = BASE_URL + '/mtv2/'
    else:
        xpath = 'currentShows'
        local_url = BASE_URL + '/ontv'
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)

    for video in data.xpath('//div[contains(@class, "%s")]//div[@class="content-box"]/a' %xpath):
        url = video.xpath('./@href')[0]
        if not url.startswith('http://'):
            url = BASE_URL + url
        title = video.xpath('.//img/@alt')[0].title()
        title = title.replace('&#36;', '$')
        thumb = video.xpath('.//img/@src')[0].split('?')[0]
        if '/shows/' in url:
            # These shows have a bad url, so fix it first
            if 'teen_mom_2/series.jhtml' in url or 'awkward/series.jhtml' in url:
                url = url.split('series.jhtml')[0]
            # This is for those shows with old format
            if url.endswith('series.jhtml'):
                oc.add(DirectoryObject(key=Callback(ShowOldSections, title=title, thumb=thumb, url=url), title=title, thumb = thumb))
            else:
                oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, thumb=thumb, url=url), title=title, thumb = thumb))

    oc.objects.sort(key = lambda obj: obj.title)

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are shows to list right now.")
    else:
        return oc
#####################################################################################
# For Producing the Specials Archive list of shows
@route(PREFIX + '/producespecials')
def ProduceSpecials(title):
    oc = ObjectContainer(title2=title)
    for specials in SPECIAL_ARCHIVES:
        url = specials['url']
        title = specials['title']
        oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url), title=title))
    return oc
#########################################################################################
# This functions pulls the full archive list of shows for MTV from  '/ontv/all/'. This list includes specials.
@route(PREFIX + '/showsall')
def ShowsAll(title, page=1):
    oc = ObjectContainer(title2=title)
    local_url = '%s?page=%s' %(MTV_SHOWS_ALL, str(page))
    # THIS IS A UNIQUE DATA PULL
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
    for video in data.xpath('//div[@class="mdl"]/div/div/ol[@class="lst "]/li'):
        try: url = BASE_URL + video.xpath('./div[@class="title2"]/a/@href')[0]
        except: continue
        title = video.xpath('./div[@class="title2"]/meta/@content')[0]
        thumb = video.xpath('./div[@class="title2"]/a/img/@src')[0]
        thumb = thumb.replace('70x53.jpg?quality=0.85', '140x105.jpg')

        if '/shows/' in url:
            if '/season_' in url:
                season = int(url.split('/season_')[1].split('/')[0])
            else:
                season = 1
            # Old formated shows go straight to the section production and are already broken up by seasons
            if url.endswith('series.jhtml'):
                oc.add(DirectoryObject(key=Callback(ShowOldSections, title=title, url=url, thumb=thumb, season=season), title = title, thumb = thumb))
            # New shows do not have unique addresses for season so they go to the NewSeason function broken up by season
            # 16 AND PREGNANT AND Rob Dyrdek's Fantasy Factory ARE SHOWING WITH NEW URLS AND FORMAT IN SHOW ARCHIVE
            else:
                oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url, thumb=thumb), title = title, thumb = thumb))
                
        elif '/ontv/' in url:
            if 'Archive' in title:
                if 'archive' not in url:
                    url = url + 'archive/'
                oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url), title=title, thumb=thumb))
            else:
                url + '/video.jhtml'
                oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title = title, thumb=thumb))
        else:
            pass

# Paging code that looks for next page url code and pulls the number asssociated with it
    try:
        page = data.xpath('//div[@class="pagintation"]/a[@class="page-next"]/@href')[0]
        page = page.split('=')[1]
        oc.add(NextPageObject(
            key = Callback(ShowsAll, title = title, page = page), 
            title = L("Next Page ...")))
    except:
        pass
  
    if len(oc) < 1:
        Log ('still no value for All Show objects')
        return ObjectContainer(header="Empty", message="There are no shows to list right now.")
    else:
        return oc
#######################################################################################
# This function produces sections for shows with old table format
@route(PREFIX + '/showoldsections', season=int)
def ShowOldSections(title, thumb, url, season=0):
    oc = ObjectContainer(title2=title)
    local_url = url.replace('series', 'video')
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
    # First check to make sure there are videos for this show
    # FOUND THAT SOME DO NOT HAVE A WATCH VIDEO LINK ON THE SIDE BUT ALL HAVE WATCH VIDEO IN THE TITLE OF THE VIDEO PAGE
    video_check = data.xpath('//div/h1//text()')[0]
    if video_check:
        # This is for those shows that have sections listed below Watch Video
        for section in data.xpath('//li[contains(@class,"-subItem")]/div/a'):
            section_title = section.xpath('.//text()')[2].strip()
            section_url = BASE_URL + section.xpath('./@href')[0]
            oc.add(DirectoryObject(key=Callback(VideoPage, title=section_title, url=section_url, season=season), title=section_title, thumb=thumb))
        # Add a section to show all videos
        oc.add(DirectoryObject(key=Callback(VideoPage, title='All Videos', url=local_url, season=season), title='All Videos', thumb=thumb))
    # This handles pages that do not have a Watch Video section
    else:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos listed for this show.")
    return oc
#######################################################################################
# This function produces sections for shows with new format
@route(PREFIX + '/showseasons')
def ShowSeasons(title, thumb, url):
    oc = ObjectContainer(title2=title)
    local_url = url + 'video/'
    html = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
    new_season_list = html.xpath('//span[@id="season-dropdown"]//li/a')
    if len(new_season_list)> 0:
        for section in new_season_list:
            title = section.xpath('./span[@class="headline-s"]//text()')[0].strip().title()
            season = int(title.split()[1])
            season_id = section.xpath('./@data-id')[0]
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=local_url, season=season, season_id=season_id), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
    else:
        # COULD GET THE SEASON FROM THE FIRST VIDEO HERE WITH REGEX IF THE SEASON WAS WANTED
        oc.add(DirectoryObject(key=Callback(ShowSections, title='Current Season', thumb=thumb, url=local_url, season=0), title='Current Season', thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

    # This handles pages that do not have a Watch Video section
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos listed for this show.")
    else:
        return oc
#######################################################################################
# This function produces sections for new show format
@route(PREFIX + '/showsections', season=int)
def ShowSections(title, thumb, url, season, season_id=''):
    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    section_list = html.xpath('//span[@id="video-filters-dropdown"]//li/a')
    for section in section_list:
        id = section.xpath('./@data-seriesid')[0]
        url = BASE_URL + section.xpath('./@href')[0]
        section_title = section.xpath('./span/text()')[0].title()
        if 'Full Episodes' in section_title:
            template = FULL_EP_TEMP
        else:
            template = ALL_VID_TEMP
        if season_id:
            new_url = NEW_SHOW_AJAX %(id, season_id, template)
        else:
            new_url = url
        oc.add(DirectoryObject(key=Callback(ShowVideos, title=section_title, url=new_url, season=season), title=section_title, thumb=thumb))
    return oc
#######################################################################################
# This function produces videos for the new show format
# LIMITING RESULTS PER PAGE DOES NOT SEEM TO WORK SO REMOVED PAGING
# FOR NOW I HAVE CHOSEN TO NOT SHOW RESULTS THAT HAVE "NOT AVAILABLE" BUT INCLUDE THOSE THAT GIVE A DATE FOR WHEN IT WILL BE AVAILABLE
@route(PREFIX + '/showvideos', season=int, start=int)
def ShowVideos(title, url, season):

    oc = ObjectContainer(title2=title)
    try: data = HTML.ElementFromURL(url)
    except: return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    video_list = data.xpath('//div[@class="span4"]')
    for video in video_list:
        try: vid_avail = video.xpath('.//div[@class="message"]//text()')[0]
        except: vid_avail = 'Now'
        # Full episodes have a sub-header field for the title but all videos have a second header hidden text
        try: vid_title = video.xpath('.//div[@class="sub-header"]/span//text()')[0].strip()
        except: vid_title = video.xpath('.//div[@class="header"]/span[@class="hide"]//text()')[0].strip()
        thumb = video.xpath('.//div[@class=" imgDefered"]/@data-src')[0]
        seas_ep = video.xpath('.//div[@class="header"]/span[@class="headline"]//text()')[0].strip()
        if vid_avail == 'not available':
            continue
        if vid_avail == 'Now':
            vid_type = video.xpath('./@data-filter')[0]
            # Skip full episodes for Android Clients
            if vid_type=="FullEpisodes" and Client.Platform in ('Android'):
                continue
            vid_url = video.xpath('./a/@href')[0]
            # One descriptions is blank and gives an error
            try: desc = video.xpath('.//div[contains(@class,"deck")]/span//text()')[0].strip()
            except: desc = None
            other_info = video.xpath('.//div[@class="meta muted"]/small//text()')[0].strip()
            duration = Datetime.MillisecondsFromString(other_info.split(' - ')[0])
            date = Datetime.ParseDate(video.xpath('./@data-sort')[0])
            try: episode = int(RE_EXX.search(seas_ep).group(1))
            except: episode = None
            # This creates a url for playlists of video clips
            if '#id=' in url:
                id_num = RE_VIDID.search(vid_url).group(1)
                new_url = BUILD_URL + id_num
                vid_url = new_url

            oc.add(EpisodeObject(
                url = vid_url, 
                season = season,
                index = episode,
                title = vid_title, 
                thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
                originally_available_at = date,
                duration = duration,
                summary = desc
            ))
        else:
            avail_date = vid_avail.split()[1]
            avail_title = 'NOT AVAILABLE UNTIL %s' %avail_date
            desc = '%s - %s' %(seas_ep, vid_title)
            oc.add(PopupDirectoryObject(key=Callback(NotAvailable, avail=vid_avail), title=avail_title, summary=desc, thumb=thumb))
      
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos available to watch." )
    else:
        return oc
####################################################################################################
# This produces videos for most popular as well for specials
@route(PREFIX + '/videopage', season=int)
def VideoPage(url, title, season=0):
    oc = ObjectContainer(title2=title)
    id_num_list = []
    data = HTML.ElementFromURL(url)
    for item in data.xpath('//li[@itemtype="http://schema.org/VideoObject"]'):
        # This pulls data for show videos in table format
        try:
            link = item.xpath('./@mainurl')[0]
            video_title = item.xpath('./@maintitle')[0]
            image = item.xpath('./meta[@itemprop="thumbnail"]/@content')[0].split('?')[0]
            date = item.xpath('./@mainposted')[0]
            desc = item.xpath('./@maincontent')[0]
            # Some videos are locked or unavailable but still listed on the site
            # most have 'class="quarantineDate"' in, the description, but not all so using the text also
            if 'quarantineDate' in desc or 'Not Currently Available' in desc:
                continue
        # This pulls data for all other types of videos
        except:
            link = item.xpath('.//a/@href')[0]
            video_title = item.xpath('.//meta[@itemprop="name"]/@content')[0].strip()
            image = item.xpath('.//*[@itemprop="thumbnail" or @class="thumb"]/@src')[0].split('?')[0]
            try: date = item.xpath('.//time[@itemprop="datePublished"]//text()')[0]
            except: date = ''
            desc = None

        if 'hrs ago' in date or 'today' in date or 'hr ago' in date:
            date = Datetime.Now()
        else:
            date = Datetime.ParseDate(date)
        if not image.startswith('http:'):
            image = BASE_URL + image
        # THIS PREVENTS ERRORS FROM SOME SHOW PAGES LISTED ON THE LATEST FULL EPISODES VIDEO PAGE
        if '/video.jhtml' in link or '/video/full-episodes/' in link:
            continue
        # Here we start building the url
        if not link.startswith('http:'):
            link = BASE_URL + link
        # This handles playlists of video clips. They end with #id and a 7 digit number
        if '#id=' in link:
            # We first check to see if the id_num has been processed so we do not have multiple listings of the same playlist
            id_num = RE_VIDID.search(link).group(1)
            if id_num not in id_num_list:
                id_num_list.append(id_num)
                new_url = BUILD_URL + id_num
            else:
                continue
        else:
            new_url = link
            
        # Skip full episodes for Android Clients
        # Video clip playlists will only play the first clip for Android Clients
        if Client.Platform in ('Android') and 'playlist.jhtml' in new_url:
            continue

        # check for episode and season in code or the title
        try: episode = item.xpath('.//li[@class="list-ep"]//text()')[0]
        except: episode = 'xx'
        if episode.isdigit()==False:
            try:  episode = int(RE_EP.search(video_title).group(1))
            except: episode = 0
        else:
            episode = int(episode)
        if season==0:
            try: this_season = int(RE_SEASON.search(video_title).group(1))
            except:
                this_season = 0
        else:
            this_season = season
            
        if episode>0 or this_season>0:
            oc.add(EpisodeObject(url=new_url, title=video_title, season=this_season, index=episode, summary=desc, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))
        else:
            oc.add(VideoClipObject(url=new_url, title=video_title, summary=desc, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos that are currently available in this category right now.")
    else:
        return oc
#######################################################################################
# This function produces sections for specials
@route(PREFIX + '/specialsections')
def SpecialSections(title, url):
    oc = ObjectContainer(title2=title)
    current_url = url.replace('archive/', 'video.jhtml')
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Current Year", url=current_url), title = "Current Year"))
    oc.add(DirectoryObject(key=Callback(SpecialArchives, title="Archives", url=url), title="Archives"))
    return oc
#######################################################################################
# This section separates the MTV specials with archives into years.
@route(PREFIX + '/specialarchives')
def SpecialArchives(title, url):

    oc = ObjectContainer(title2=title)
    # Pull the metadata for the current season
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
    thumb=data.xpath('//img[@id="featImg"]//@src')[0]
    if not thumb.startswith('http://'):
        thumb = BASE_URL + thumb
    for video in data.xpath('//li/p/b/a'):
        title = video.xpath('.//text()')[0]
        year = int(title.split()[0])
        # Chose to start at 2005 since that is the year that first seems to produce videos  
        if year > 2004:
            url = BASE_URL + video.xpath('.//@href')[0]
            # A few do not put slash after the year so it causes errors
            if not url.endswith('/'):
                url = url + '/'
            oc.add(DirectoryObject(key=Callback(ArchiveSections, title=title, url=url, thumb=thumb), title=title, thumb=thumb)) 

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no years list right now.")
    else:
        return oc
#######################################################################################
# This section handles the archived years of specials 
@route(PREFIX + '/archivesections')
def ArchiveSections(title, thumb, url):

    oc = ObjectContainer(title2=title)
    # Check to see if there is a second pages here
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    section_list =[]
    for videos in data.xpath('//div[@id="generic2"]//ol/li'):
        vid_id = videos.xpath('.//a//@href')[0].split('?id=')[1]
        title = videos.xpath('./p/strong/a//text()')[0]
        thumb = BASE_URL + videos.xpath('.//img//@src')[1]
        thumb = thumb.replace('70x53.jpg', '140x105.jpg')
        vid_url = BUILD_URL + vid_id
        oc.add(VideoClipObject(url=vid_url, title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
	
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no special videos to list right now.")
    else:
        return oc
############################################################################################################################
# This function creates an error message for entries that are not currrently available
@route(PREFIX + '/notavailable')
def NotAvailable(avail):
  return ObjectContainer(header="Not Available", message='This video is currently unavailable - %s.' %avail)

