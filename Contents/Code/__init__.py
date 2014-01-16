# VIDEO CLIP FOR BONUS CLIP OR SNEEK PEEK ONLY HAVE ONE PART DESPITE THE WEBISTE SHOWING THE METADATA FOR ALL OF THEM AS A PLAYLIST

TITLE = 'MTV Shows'
PREFIX = '/video/mtvshows'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.mtv.com'
SHOWS = 'http://www.mtv.com/ontv'
MTV_SHOWS_ALL = 'http://www.mtv.com/ontv/all/'
# This code does not currently work with shows that do not have season if you add a filter and shows with season have this code already in URL
#SERIES_VIDEOS = 'http://www.mtv.com/global/music/modules/video/shows/?seriesID=%s'
# The three variables below produce the results page for videos for shows with the new format
NEW_SHOW_AJAX = 'http://www.mtv.com/include/shows/seasonAllVideosAjax?urlKey=%s&seasonId=%s&start=%s&resultSize=30&template=%s'
ALL_VID_TEMP = '%2Fshows%2Fplatform%2Fwatch%2Fmodules%2FseasonRelatedPlaylists'
FULL_EP_TEMP = '%2Fshows%2Fplatform%2Fwatch%2Fmodules%2FepisodePlaylists'

# The url below is used for Specials or other playlist whose length varies too much to determine the number of parts.  
# It will produce a list of videos in a playlist similar to the MRSS feed,  but we use this url instead
# because the results works with the VideoPage() function that is also used to produce Most Recent and Most Popular videos
MTV_PLAYLIST = 'http://www.mtv.com/global/music/videos/ajax/playlist.jhtml?feo_switch=true&channelId=1&id=%s'
MTV_POPULAR = 'http://www.mtv.com/most-popular/%smetric=numberOfViews&range=%s&order=desc'

RE_SEASON_EP = Regex('\(Season (\d{1,2})\) \| Ep. (\d{1,2})')
RE_SEASON  = Regex('Season (\d{1,2})')
RE_EP = Regex('\| Ep. (\d{1,3})')
RE_VIDID = Regex('^http://www.mtv.com/videos/\?id=(\d{7})')
# episode regex for new show format
RE_EXX = Regex('/e(\d+)')
LATEST_VIDEOS = [
    {'title'  : 'Latest Full Episodes',  'url'  : 'http://www.mtv.com/videos/home.jhtml'},
    {'title'  : 'Latest Music Videos',   'url'  : 'http://www.mtv.com/music/videos/'},
    {'title'  : 'Latest Movie Trailers',  'url'  : 'http://www.mtv.com/movies/trailer_park/'},
    {'title'  : 'Latest Movie Interviews',   'url'  : 'http://www.mtv.com/movies/features_interviews/morevideo.jhtml'}
]
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
    #for item in html.xpath('//div[contains(@class,"mtvn-item-content")]'):
    for item in html.xpath('//div[@id="searchResults"]/ul/li'):
        link = item.xpath('.//a/@href')[0]
        # This make sure it only returns shows that start with www.mtv.com/shows/ that may contain /season_?/ and end with / or series.jhtml
        try:
            url_part = link.split('http://www.mtv.com/shows/')[1]
            if 'season_' in url_part:
                url_test = url_part.split('/')[2]
            else:
                url_test = url_part.split('/')[1]
            if not url_test or url_test=='series.jhtml':
                #title = item.xpath('.//a//text()')[0]
                title = item.xpath('./div[contains(@class,"mtvn-item-content")]//a//text()')[0]
                thumb = item.xpath('.//img/@src')[0].split('?')[0]
                # Most shows are listed by individual season in the show search
                # But these all have to go through the season check first because they may be the new format
                oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=link, thumb=thumb), title = title, thumb=thumb))
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
        oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, thumb=thumb, url=url), title=title, thumb = thumb))

    oc.objects.sort(key = lambda obj: obj.title)

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are shows to list right now.")
    else:
        return oc
#####################################################################################
# For Producing Specials 
@route(PREFIX + '/producespecials')
def ProduceSpecials(title):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(BASE_URL + '/ontv', cacheTime = CACHE_1HOUR)

    for video in data.xpath('//*[text()="specials"]/parent::li/following-sibling::li/a'):
        url = video.xpath('./@href')[0]
        if not url.startswith('http://'):
            url = BASE_URL + url
        if url.startswith('http://www.mtv.com') and 'series.jhtml' in url:
            title = video.xpath('.//text()')[0]
            vid_url = url.replace('series', 'video')
            # Here we set the season to one because we do not need season numbers pulled for this
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=vid_url + '?filter=', thumb=R(ICON), season=1, show_url=vid_url), title = title))
        else:
            continue
            
    for specials in SPECIAL_ARCHIVES:
        url = specials['url']
        title = specials['title']
        oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url), title=title))
	  
    oc.objects.sort(key = lambda obj: obj.title)

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are shows to list right now.")
    else:
        return oc
#########################################################################################
# This functions pulls the full archive list of shows for MTV. This list includes specials.   /ontv/all/
@route(PREFIX + '/showsall')
def ShowsAll(title, page=1):
    oc = ObjectContainer(title2=title)
    local_url = '%s?page=%s' %(MTV_SHOWS_ALL, str(page))
    # THIS IS A UNIQUE DATA PULL
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
    for video in data.xpath('//div[@class="mdl"]/div/div/ol[@class="lst "]/li'):
        try:
            url = video.xpath('./div[@class="title2"]/a/@href')[0]
        except:
            continue
        if not url.startswith('http://'):
            url = BASE_URL + url
        title = video.xpath('./div[@class="title2"]/meta/@content')[0]
        thumb = video.xpath('./div[@class="title2"]/a/img/@src')[0]
        thumb = thumb.replace('70x53.jpg?quality=0.85', '140x105.jpg')

        if '/shows/' in url:
            if '/season_' in url:
                season = url.split('/season_')[1].split('/')[0]
            else:
                season = 1
            # These go straight to the section production because they are already broken up by season
            vid_url = url.replace('series', 'video')
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=vid_url + '?filter=', thumb=thumb, season=int(season), show_url=vid_url), title = title, thumb = thumb))
                
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
# This function produces seasons for each show based on the format
@route(PREFIX + '/showseasons')
def ShowSeasons(title, thumb, url):
    oc = ObjectContainer(title2=title)
    local_url = url.replace('series', 'video')
    # The url below uses a video player format that cuts out some of the extra code in the page, but doesn't always work
    #local_url = SERIES %local_url
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
    section_nav = data.xpath('//ul[@class=" section-nav"]/li[not(contains(@class,"subItem"))]//a//text()')
    # This is for those shows with old format
    if len(section_nav) > 0:
        # Make sure the show has videos
        if 'Watch Video' in section_nav:
            # Check for season
            season_list = data.xpath('//*[@id="videolist_id"]/option')
            if len(season_list)> 0:
                for season in season_list:
                    season_title = season.xpath('.//text()')[0]
                    season_url = BASE_URL + season.xpath('./@value')[0]
                    season = season_title.split('Season ')[1]
                    oc.add(DirectoryObject(key=Callback(ShowSections, title=season_title, url=season_url, season=season, thumb=thumb, show_url=local_url), title=season_title, thumb=thumb))
            else:
                # These could manually be broken up by season but you risk losing some videos that may not have the Season listed in the title 
                # We set the season to zero so that each season will be picked up properly
                # DO WE WANT TO LOOK AT BREAKING THIS INTO THOSE WITH MULTIPLE SEASONS AND THOSE WITH ONLY ONE?
                # THE NEXT 8 LINES BREAK IT UP
                first_title = data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]/@maintitle')[0]
                (new_season, episode) = SeasEpFind(first_title)
                if int(new_season) > 1:
                    season_title='All Seasons'
                    season = 0
                else:
                    season_title='Season One'
                    season = 1
                season_url = local_url + '?filter='
                #oc.add(DirectoryObject(key=Callback(ShowSections, title='All Season', url=season_url, season=0, thumb=thumb, show_url=local_url), title='All Seasons', thumb=thumb))
                oc.add(DirectoryObject(key=Callback(ShowSections, title=season_title, url=season_url, season=season, thumb=thumb, show_url=local_url), title=season_title, thumb=thumb))
        else:
            # This handles those without a video section
            Log ('there are no videos for this show')
            return ObjectContainer(header="Empty", message="There are no videos to list right now.")

    # This is for those shows with new format
    # For these shows we get the seasons
    elif not url.endswith('series.jhtml'):
        local_url = url + 'video/'
        html = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
        for section in html.xpath('//dd/ul/li/a'):
            title = section.xpath('./span[@class="headline-s"]//text()')[0].strip().title()
            season = int(title.split()[1])
            season_id = section.xpath('./@data-id')[0]
            url_key = url.split('shows/')[1].replace('/','')
            oc.add(DirectoryObject(key=Callback(ShowNewSections, title=title, thumb=thumb, url_key=url_key, season=season, season_id=season_id), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
    else:
        return ObjectContainer(header="Error", message="This show link is not in the proper format to return videos.")

    # This handles pages that do not have a Watch Video section
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc
#######################################################################################
# This function produces sections for shows with old table format
@route(PREFIX + '/showsectionsnew', season=int)
def ShowSections(title, thumb, url, season, show_url):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(show_url, cacheTime = CACHE_1HOUR)
    # Since we send some shows directly to this function first, we need to check for videos here as well
    video_check = data.xpath('//a[text()="Watch Video"]/parent::div')
    if video_check:
        sub_list = data.xpath('//li[contains(@class,"-subItem")]/div/a')
        # This is for those shows that have sections listed below Watch Video
        for section in sub_list:
            section_filter = section.xpath('./@href')[0].split('filter=')[1]
            sec_url = url + section_filter
            sec_title = section.xpath('.//text()')[2].strip()
            oc.add(DirectoryObject(key=Callback(ShowVideos, title=sec_title, url=sec_url, season=season), title=sec_title, thumb=thumb))

        # Add a section that shows all videos
        oc.add(DirectoryObject(key=Callback(ShowVideos, title='All Videos', url=show_url, season=season), title='All Videos', thumb = thumb))

    # This handles pages that do not have a Watch Video section
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos for this show.")
    else:
        return oc
#######################################################################################
# This function produces sections for new show format
@route(PREFIX + '/shownewsections', season=int)
def ShowNewSections(title, thumb, url_key, season, season_id):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(ShowNewVideos, title="Full Episodes", url_key=url_key, season=season, season_id=season_id), title="Full Episodes", thumb=thumb))
    oc.add(DirectoryObject(key=Callback(ShowNewVideos, title="All Videos", url_key=url_key, season=season, season_id=season_id), title="All Videos", thumb=thumb))
    return oc
#################################################################################################################
# This function produces videos from the table layout used by show video pages
# This function picks up all videos in all pages even without paging code. BUT NOT SURE ABOUT THE TABLE STYLE WITH SEASONS
# VIDEOS ARE PRODUCED EXACTLY HOW THE SITE DOES SO IF THE SITE DOES NOT BREAK THE SHOW INTO SEASON THEY ARE NOT BROKEN UP HERE
@route(PREFIX + '/showvideos', season=int)
def ShowVideos(title, url, season):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url)
    for video in data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
        title = video.xpath('./@maintitle')[0]
        thumb = video.xpath('./meta[@itemprop="thumbnail"]/@content')[0].split('?')[0]
        if not thumb:
            thumb = video.xpath('.//li[contains(@id,"img")]/img/@src')[0]
        if not thumb.startswith('http:'):
            thumb = BASE_URL + thumb
        vid_url = BASE_URL + video.xpath('./@mainurl')[0]
        desc = video.xpath('./@maincontent')[0]

        # HERE WE CHECK TO SEE IF THE VIDEO CLIP IS A PLAYLIST (SEE CHANNEL README FILE FOR FULL EXPLANATION) 
        # ANNOYINGLY ALMOST ALL OF THE URLS AND URI DATA FOR VIDEO CLIPS ON THE MTV WEBSITE ARE LISTED AS PLAYLIST EVEN THOUGH
        # MOST OF THE BONUS CLIPS, SNEAK PEAKS, ETC FOR EACH SHOW ONLY HAVE ONE VIDEO IN THAT PLAYLIST.
        # THIS IS SET TO PRODUCE PLAYLISTS FOR SPECIALS THAT END WITH SERIES.JHTML SINCE THEY ALL HAVE MULTIPLE PARTS
        # BUT IT DOES PRODUCES PLAYLISTS FOR BONUS CLIPS, SNEAK PEAKS, ETC FOR EACH SHOW'S ALL VIDEOS SECTION.
        if '&id=' in vid_url and 'filter=' not in url:
            vid_id = vid_url.split('&id=')[1]
            vid_url = MTV_PLAYLIST %vid_id
            # send to videopage function
            oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title, thumb=thumb, summary=desc))
        else:
            date = video.xpath('./@mainposted')[0]
            if 'hrs ago' in date or 'today' in date or 'hr ago' in date:
                date = Datetime.Now() 
            else:
                date = Datetime.ParseDate(date)
            episode = video.xpath('.//li[@class="list-ep"]//text()')[0]
            # We call the pull new_season so the blank value for shows without separate seasons stays intact for check
            if episode.isdigit()==False or season==0:
                (new_season, episode) = SeasEpFind(title)
            else:
                new_season = season
            oc.add(EpisodeObject(
                url = vid_url, 
                season = int(new_season),
                index = int(episode),
                title = title, 
                thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
                originally_available_at = date,
                summary = desc
            ))

    # The site currently orders the videos by most recent but may need to use it later
    #oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc
#######################################################################################
# This function produces videos for the new show format
@route(PREFIX + '/shownewvideos', season=int, start=int)
def ShowNewVideos(title, url_key, season, season_id, start=0):
    oc = ObjectContainer(title2=title)
  
    if title == 'All Videos':
        template = ALL_VID_TEMP
    else:
        template = FULL_EP_TEMP
    local_url = NEW_SHOW_AJAX %(url_key, season_id, str(start), template)
    data = HTML.ElementFromURL(local_url)
    video_list = data.xpath('//div[@class="span4"]')
    for video in video_list:
        vid_type = video.xpath('./@data-filter')[0]
        vid_url = video.xpath('./a/@href')[0]
        thumb = video.xpath('.//img/@data-src')[0]
        seas_ep = video.xpath('.//div[@class="header"]/span[@class="headline"]//text()')[0].strip()
        # Full episodes have a sub-header field for the title but video clips have a hidden title
        try:
            vid_title = video.xpath('.//div[@class="sub-header"]/span//text()')[0].strip()
        except:
            vid_title = video.xpath('.//div[@class="header"]/span[@class="hide"]//text()')[0].strip()
        # One descriptions is blank and gives an error
        try:
            desc = video.xpath('.//div[contains(@class,"deck")]/span//text()')[0].strip()
        except:
            desc = None
        other_info = video.xpath('.//div[@class="meta muted"]/small//text()')[0].strip()
        duration = Datetime.MillisecondsFromString(other_info.split(' - ')[0])
        date = Datetime.ParseDate(video.xpath('./@data-sort')[0])
        try:
            episode = int(RE_EXX.search(seas_ep).group(1))
        except:
            episode = None

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
      
    # Paging code. Each page pulls 30 results
    # There is not a total number of videos to check against to make sure the next page has results
    x = len(video_list)
    if x >= 30:
        start = start + 30
        oc.add(NextPageObject(key = Callback(ShowNewVideos, title="All Videos", url_key=url_key, season=season, season_id=season_id, start=start), title = L("Next Page ...")))
    else:
        pass

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    else:
        return oc
####################################################################################################
# This produces videos for most popular and latest videos, specials that do not have a table layout, as well for playlist broken down with the MTV_Playlist
@route(PREFIX + '/videopage', page=int)
def VideoPage(url, title, page=1):
    oc = ObjectContainer(title2=title)
    if '?' in url:
        local_url = url + '&page=' + str(page)
    else:
        local_url = url + '?page=' + str(page)
    # THIS IS A UNIQUE DATA PULL
    data = HTML.ElementFromURL(local_url)
    for item in data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
        link = item.xpath('.//a/@href')[0]
        # THIS PREVENTS ERRORS FROM SOME HIDDEN LIST OF SHOWS ON THE LATEST FULL EPISODES PAGE
        if '/video.jhtml' in link or '/video/full-episodes/' in link:
            continue
        if not link.startswith('http://'):
            link = BASE_URL + link
        #image = item.xpath('.//img/@src')[0]
        try:
            image = item.xpath('.//img[@itemprop="thumbnail"]/@src')[0]
        except:
            image = item.xpath('.//img/@src')[0]
        if not image.startswith('http://'):
            image = BASE_URL + image
        try:
            video_title = item.xpath('.//meta[@itemprop="name"]/@content')[0].strip()
            video_title = video_title.replace('\n', '')
        except:
            video_title = item.xpath('.//img[@itemprop="thumbnail"]/@alt')[0]
        # here we want to see if there is an episode and season info for the video
        (season, episode) = SeasEpFind(title=video_title)
        (season, episode) = (int(season), int(episode))
        try:
            date = item.xpath('.//time[@itemprop="datePublished"]/text()')[0]
        except:
            date = ''
        if 'hrs ago' in date or 'today' in date or 'hr ago' in date:
            date = Datetime.Now()
        else:
            date = Datetime.ParseDate(date)

        try:
        # This handles those that are video playlists but Woodie Awards are not in VideoObject so they do not get picked up
            # We first check for a "deck" which lists the number of videos in the group and tells us this is a playlist
            num_vids = item.xpath('.//p[@class="deck"]/span/text()')[0].strip()
            vid_id = RE_VIDID.search(link).group(1)
            vid_url = MTV_PLAYLIST %vid_id
            oc.add(DirectoryObject(key=Callback(VideoPage, title=video_title, url=vid_url), title=video_title, thumb=image))
        except:
            if episode==0:
                oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=ICON)))
            else:
                oc.add(EpisodeObject(url=link, title=video_title, season=season, index=episode, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=ICON)))

    # This goes through all the pages for MTV popular video sections
    try:
        # The specials has the word pagination spelled wrong so have to look for that separate
        for pages in data.xpath('//div[contains(@class,"pagintation")or contains(@class,"paginationContainer")]//a'):
            page_link = pages.xpath('./@href')[0]
            # Some put the next in a bold and so some will not find the next if you don't check for both
            try: page_text = pages.xpath('./strong//text()')[0]
            except: page_text = pages.xpath('.//text()')[0]
            if 'Next' in page_text:
                page = page_link.split('page=')[1] 
                oc.add(NextPageObject(key = Callback(VideoPage, title=title, url=url, page=page), title = L("Next Page ...")))
            else:
                pass
    except:
        pass

    if len(oc)==0:
        return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
        return oc
###########################################################################################
# This function is used to pull the season and episodes from a show title
@route(PREFIX + '/seasepfind')
def SeasEpFind(title):

    #Log('the value of title is %s' %title)
    try:
        (season, episode) = RE_SEASON_EP.search(title).groups()
    except:
        try:
            episode = RE_EP.search(title).group(1)
            if len(episode)>2:
                season = episode[0]
            else:
                season = 1
        except:
            try:
                season = RE_SEASON.search(title).group(1)
                episode = 0
            except:
                (season, episode) = (1, 0)
                        
    #Log('the value of season is %s and episode is %s' %(season, episode))
    return (season, episode)
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
        vid_url = MTV_PLAYLIST %vid_id
        oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title, thumb=thumb))
	
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no special videos to list right now.")
    else:
        return oc
