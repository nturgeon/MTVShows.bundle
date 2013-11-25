# VIDEO CLIP FOR BONUS CLIP OR SNEEK PEEK ONLY HAVE ONE PART DESPITE THE WEBISTE SHOWING THE METADATA FOR ALL OF THEM AS A PLAYLIST

TITLE = 'MTV Shows'
PREFIX = '/video/mtvshows'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.mtv.com'
SHOWS = 'http://www.mtv.com/ontv'
MTV_SHOWS_ALL = 'http://www.mtv.com/ontv/all/'
MTV_PLAYLIST = 'http://www.mtv.com/global/music/videos/ajax/playlist.jhtml?feo_switch=true&channelId=1&id=%s'
MTV_POPULAR = 'http://www.mtv.com/most-popular/tv-show-videos/?category=%s&metric=numberOfViews&range=%s&order=desc'
SEARCH_URL = 'http://www.mtv.com/search/'

# Specials Archive List
SPECIAL_ARCHIVES = [
  {'title'  : 'Video Music Awards',  'url'  : 'http://www.mtv.com/ontv/vma/archive/'},
  {'title'  : 'Movie Awards',   'url'  : 'http://www.mtv.com/ontv/movieawards/'},
  {'title'  : 'mtvU Woodie Awards',  'url'  : 'http://www.mtv.com/ontv/woodieawards/'}
]

RE_SEASON  = Regex('.+(Season|Seas.) (\d{1,2}).+')
RE_EPISODE  = Regex('.+(Episode|Ep.) (\d{1,3})')
####################################################################################################
# Set up containers for all possible objects
def Start():

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  EpisodeObject.thumb = R(ICON)
  EpisodeObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

  HTTP.CacheTime = CACHE_1HOUR 
 
#####################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(MTVShows, title='MTV Shows'), title='MTV Shows')) 
  oc.add(DirectoryObject(key=Callback(MTVVideos, title='MTV Videos'), title='MTV Videos')) 
  # THE MENU ITEM BELOW CONNECTS TO A FUNCTION WITHIN THIS CHANNEL CODE THAT PRODUCES A LIST OF SHOWS FOR USERS 
  # IT DOES NOT USE OR INTERACT WITH THE SEARCH SERVICES FOR VIDEOS LISTED NEXT
  #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
  oc.add(InputDirectoryObject(key=Callback(ShowSearch), title='Search for MTV Shows', thumb=R(ICON), summary="Click here to search for shows", prompt="Search for the shows you would like to find"))
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.mtvshows", title=L("Search MTV Videos"), prompt=L("Search for Videos")))
  return oc
#######################################################################################
# This function produces a list of shows from the main search page at mtv.com so users can more easily find archived shows
# It uses the "All Results" section of the search and only returns those that end with series.jhtml
# THIS IS JUST A FUNCTION TO PROVIDE MORE ACCESS TO USERS AND DOES NOT USE OR INTERACT WITH THE SEARCH SERVICE FOR VIDEOS
@route(PREFIX + '/showsearch')
def ShowSearch(query):
    oc = ObjectContainer(title1='MTV', title2='Show Search Results')
    url = SEARCH_URL + '?q=' + String.Quote(query, usePlus = True)
    html = HTML.ElementFromURL(url)
    for item in html.xpath('//div[contains(@class,"mtvn-item-content")]'):
        link = item.xpath('./div/a//@href')[0]
        # This make sure it only returns shows that are located at mtv.com
        if 'www.mtv.com/shows/' in link and link.endswith('series.jhtml'):
            title = item.xpath('./div/a//text()')[0]
            # The shows are listed by individual season in the show search so find season and send to sections
            if '/season_' in link:
              season = link.split('/season_')[1].split('/')[0]
            else:
              season = 1
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=link, thumb=R(ICON), season=int(season)), title = title))
    return oc

#####################################################################################
# For MTV main sections of Popular, Specials, and All Shows
@route(PREFIX + '/mtvshows')
def MTVShows(title):
  oc = ObjectContainer(title2=title)
  oc.add(DirectoryObject(key=Callback(ProduceShows, title='MTV Popular Shows'), title='MTV Popular Shows')) 
  oc.add(DirectoryObject(key=Callback(ProduceSpecials, title='MTV Specials'), title='MTV Specials')) 
  oc.add(DirectoryObject(key=Callback(ShowsAll, title='MTV All Shows'), title='MTV All Shows')) 
  return oc
#####################################################################################
# For MTV main sections of Videos
@route(PREFIX + '/mtvvideos')
def MTVVideos(title):
  oc = ObjectContainer(title2=title)
  oc.add(DirectoryObject(key=Callback(VideoPage, title='MTV Latest Full Episodes', url='http://www.mtv.com/videos/home.jhtml'), title='MTV Latest Full Episodes')) 
  oc.add(DirectoryObject(key=Callback(MostPopularMain, title='MTV Most Popular Videos'), title='MTV Most Popular Videos')) 
  return oc
####################################################################################################
# This handles most popular that have a carousel (MTV)
@route(PREFIX + '/mostpopularmain')
def MostPopularMain(title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(MostPopularSections, video_type='full-episodes', title="Most Popular Full Episodes"), title="Most Popular Full Episodes"))
    oc.add(DirectoryObject(key=Callback(MostPopularSections, video_type='after-shows', title="Most Popular After Shows"), title="Most Popular After Shows"))
    oc.add(DirectoryObject(key=Callback(MostPopularSections, video_type='bonus-clips', title="Most Popular Show Clips"), title="Most Popular Show Clips"))
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
  data = HTML.ElementFromURL(SHOWS, cacheTime = CACHE_1HOUR)

  for video in data.xpath('//div[contains(@class, "currentShows")]//li/div/a'):
    url = video.xpath('.//@href')[0]
    if not url.startswith('http://'):
      url = BASE_URL + url
    title = video.xpath('./div/img//@alt')[0]
    title = title.title()
    title = title.replace('&#36;', '$')
    thumb = video.xpath('./div/img//@src')[0].split('?')[0]
    if '/season_' in url or 'rwrr_challenge/' in url or '/real_world/' in url:
      oc.add(DirectoryObject(key=Callback(ShowCreateSeasons, title=title, url=url, thumb=thumb), title=title, thumb=thumb))
    else:
      oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=url, season=0), title=title, thumb = thumb))

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
  data = HTML.ElementFromURL(SHOWS, cacheTime = CACHE_1HOUR)

  for video in data.xpath('//*[text()="specials"]/parent::li/following-sibling::li/a'):
    url = video.xpath('.//@href')[0]
    if not url.startswith('http://'):
      url = BASE_URL + url
    if 'www.mtv.com' in url and 'series.jhtml' in url:
      title = video.xpath('.//text()')[0]
      oc.add(DirectoryObject(key=Callback(ShowVideos, title=title, url=url, season=0), title = title))
    else:
      continue
      
  for specials in SPECIAL_ARCHIVES:
    url = specials['url']
    title = specials['title']
    oc.add(DirectoryObject(key=Callback(SpecialArchives, title=title, url=url), title=title))

  oc.objects.sort(key = lambda obj: obj.title)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are shows to list right now.")
  else:
    return oc
#########################################################################################
# This functions pulls the full archive list of shows for MTV. This list includes specials. 
@route(PREFIX + '/showsall')
def ShowsAll(title, page=1):
  oc = ObjectContainer(title2=title)
  local_url = MTV_SHOWS_ALL + '?page=' + str(page)
  # THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
  for video in data.xpath('//div[@class="mdl"]/div/div/ol[@class="lst "]/li'):
    try:
      url = video.xpath('./div[@class="title2"]/a//@href')[0]
    except:
      continue
    if not url.startswith('http://'):
      url = BASE_URL + url
    title = video.xpath('./div[@class="title2"]/meta//@content')[0]
    thumb = video.xpath('./div[@class="title2"]/a/img//@src')[0]
    thumb = thumb.replace('70x53.jpg?quality=0.85', '140x105.jpg')

    if '/shows/' in url:
      # Sixteen and pregnant does not separate into separate seasons. The rest of the shows are listed by individual season in All Shows
      if '16_and_pregnant' in url:
        oc.add(DirectoryObject(key=Callback(ShowCreateSeasons, title=title, url=url, thumb = thumb), title = title, thumb = thumb))
      else:
        if '/season_' in url:
          season = url.split('/season_')[1].split('/')[0]
        else:
          season = 1
        oc.add(DirectoryObject(key=Callback(ShowSections, title=title, url=url, thumb=thumb, season=int(season)), title = title, thumb = thumb))
    elif '/ontv/' in url:
      if 'Archive' in title:
        if 'vma' in url:
          url = url + 'archive/'
        oc.add(DirectoryObject(key=Callback(SpecialArchives, title=title, url=url), title=title, thumb=thumb))
      else:
        oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, thumb=thumb, url=url), title = title, thumb = thumb))
    else:
      pass

# Paging code that looks for next page url code and pulls the number asssociated with it
  try:
    page = data.xpath('//div[@class="pagintation"]/a[@class="page-next"]//@href')[0]
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
# This section handles shows that have a separate page for each season
# Shows that do not have an other season link will just produce all videos for all seasons
@route(PREFIX + '/showcreateseasons')
def ShowCreateSeasons(title, url, thumb):

  oc = ObjectContainer(title2=title)
  local_url = url.replace('series', 'seasons')
  #THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
  for video in data.xpath('//div[1]/ol/li/div[contains(@class,"title")]/a'):
    url = video.xpath('.//@href')[0]
    url = BASE_URL + url
    # RR/RW Challenge and Real World do not have season numbers, so this checks for those shows
    if '/season_' in url:
      season = url.split('season_')[1]
      season = int(season.replace('/series.jhtml', ''))
    else:
      season = 1
    title = video.xpath('./img//@alt')[0]
    if '&rsaquo;' in title:
      title = title.replace('&rsaquo;', '')
    thumb = video.xpath('./img//@src')[0]
    if not thumb.startswith('http://'):
      thumb = BASE_URL + thumb

    oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=url, season=int(season)), title = title, thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

  oc.objects.sort(key = lambda obj: obj.title, reverse=True)
  
  if len(oc) < 1:
    # DO ANY MTV SHOWS HAVE OLD TABLE FORMAT?
    oc.add(DirectoryObject(key=Callback(ShowSections, title='All Videos', thumb=thumb, url=url, season=0), title='All Videos', thumb = thumb))
    return oc
    Log ('still no value for create season objects. Sending on to section function')
  else:
    return oc
#######################################################################################
# This function produces sections for each channel bases on the sections listed below Watch Video
@route(PREFIX + '/showsections', season=int)
def ShowSections(title, thumb, url, season):
  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
  # This is for those shows that have sections listed below Watch Video
  for sections in data.xpath('//li[contains(@class,"-subItem")]/div/a'):
    sec_url = BASE_URL + sections.xpath('.//@href')[0]
    sec_title = sections.xpath('.//text()')[2].strip()
    oc.add(DirectoryObject(key=Callback(ShowVideos, title=sec_title, url=sec_url, season=season), title=sec_title, thumb=thumb))

  # For shows that do not have video section, we make sure they have videos and then produce one All Videos section
  if len(oc) < 1:
    section_nav = data.xpath('//ul[contains(@class,"section-nav")]//a//text()')
    if 'Watch Video' in section_nav:
      oc.add(DirectoryObject(key=Callback(ShowVideos, title='All Videos', url=url, season=0), title='All Videos', thumb = thumb))
      return oc
    else:
      return ObjectContainer(header="Empty", message="This show has no videos.")
      Log ('still no value for video sections')
  else:
    return oc
#######################################################################################
# This section separates the MTV specials with archives into years.
# Chose to start at 2005 since that is the year that first seems to produce videos  
@route(PREFIX + '/specialarchives')
def SpecialArchives(title, url):

  oc = ObjectContainer(title2=title)
  # Pull the current season
  data = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
  current_url = BASE_URL + data.xpath('//ul[@class="section-nav"]/li/a//@href')[-1] + 'video.jhtml'
  thumb=data.xpath('//img[@id="featImg"]//@src')[0]
  if not thumb.startswith('http://'):
    thumb = BASE_URL + thumb
  current_title = data.xpath('//ul[@class="section-nav"]/li/a//text()')[-1]
  oc.add(DirectoryObject(key=Callback(SpecialSections, title=current_title, url=current_url, thumb=thumb), title=current_title, thumb=thumb))
  
  # Pull the rest of the years
  for video in data.xpath('//li/p/b/a'):
    title = video.xpath('.//text()')[0]
    year = int(title.split()[0])
    if year > 2004:
      url = video.xpath('.//@href')[0]
      url = BASE_URL + url
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
#######################################################################################
# This section handles the latest year of specials 
@route(PREFIX + '/specialsections')
def SpecialSections(title, thumb, url):

  oc = ObjectContainer(title2=title)
  local_url = url +'video.jhtml'
  data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
  for videos in data.xpath('//li/div[@class="title1"]'):
    vid_id = videos.xpath('./a//@href')[0].split('?id=')[1]
    title = videos.xpath('./meta[@itemprop="name"]//@content')[0]
    title2 = videos.xpath('./a/img//@alt')[0]
    thumb = videos.xpath('./a/img[@alt="%s"]//@src' %title2)[0]
    if not thumb.startswith('http:'):
      thumb = BASE_URL + thumb
    thumb = thumb.replace('70x53.jpg', '140x105.jpg')
    if 'vid' not in vid_id:
      vid_url = MTV_PLAYLIST %vid_id
      oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title, thumb=thumb))    
    
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no special videos to list right now.")
  else:
    return oc
#################################################################################################################
# This function produces videos from the table layout used by show video pages
# This function picks up all videos in all pages even without paging code
# IT PRODUCES VIDEOS EXACTLY HOW THE SITE DOES SO IF THE SITE DOES NOT BREAK THE SHOW INTO SEASON THEY ARE NOT BROKEN UP HERE
@route(PREFIX + '/showvideos', season=int)
def ShowVideos(title, url, season):
  oc = ObjectContainer(title2=title)
  local_url = url.replace('series', 'video')
  data = HTML.ElementFromURL(local_url)
  for video in data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
    # If the link does not have a mainuri, it will not play through the channel with the url service, so added a check for that here
    title = video.xpath('.//@maintitle')[0]
    episode = video.xpath('./ul/li[@class="list-ep"]//text()')[0]
    seas_ep = SeasEpFind(episode,title, season)
    episode = int(seas_ep[0])
    new_season = int(seas_ep[1])
    thumb = video.xpath('./meta[@itemprop="thumbnail"]//@content')[0].split('?')[0]
    if not thumb.startswith('http:'):
      humb = BASE_URL + thumb
    if not thumb:
      thumb = video.xpath('.//li[contains(@class="img")]/img///@src')[0]
    vid_url = BASE_URL + video.xpath('.//@mainurl')[0]
    desc = video.xpath('.//@maincontent')[0]
    date = video.xpath('.//@mainposted')[0]
    if 'hrs ago' in date:
      date = Datetime.Now()
    else:
      date = Datetime.ParseDate(date)

    # HERE WE CHECK TO SEE IF THE VIDEO CLIP IS A PLAYLIST (SEE CHANNEL README FILE FOR FULL EXPLANATION) 
    # ANNOYINGLY ALMOST ALL OF THE URLS AND URI DATA FOR ALL VIDEO CLIPS LISTED ON THE MTV WEBSITE ARE LISTED AS PLAYLIST EVEN THOUGH
    # THE BONUS CLIPS, SNEAK PEAKS, ETC FOR EACH SHOW ONLY HAVE ONE VIDEO IN THAT PLAYLIST, SO WE IGNORE THOSE.
    if '&id=' in vid_url and '?filter=' not in url:
      vid_id = vid_url.split('&id=')[1]
      vid_url = MTV_PLAYLIST %vid_id
      # send to videopage function
      oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=vid_url), title=title, thumb=thumb))
    else:
      oc.add(EpisodeObject(
        url = vid_url, 
        season = new_season,
        index = episode,
        title = title, 
        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
        originally_available_at = date,
        summary = desc
      ))

  # The site currently orders the videos by most recent but may need to use it later
  #oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no %s videos to list right now." %section_id)
  else:
    return oc
####################################################################################################
# This produces videos for most popular and latest full epsodes as well for playlist broken down with the MTV_Playlist
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
    link = BASE_URL + item.xpath('.//a//@href')[0]
    image = item.xpath('.//img//@src')[0]
    if not image.startswith('http://'):
      image = BASE_URL + image
    try:
      video_title = item.xpath('.//img[@itemprop="thumbnail"]//@alt')[0]
    except:
      video_title = item.xpath('./div/meta[@itemprop="name"]//@content')[0].strip()
      video_title = video_title.replace('\n', '')
    # here we want to see if there is an episode and season info for the video
    seas_ep = SeasEpFind(episode='--', other_info=video_title, season=0)
    episode = int(seas_ep[0])
    season = int(seas_ep[1])
    try:
      date = item.xpath('.//time[@itemprop="datePublished"]//text()')[0]
    except:
      date = ''
    if 'hrs ago' in date:
      date = Datetime.Now()
    else:
      date = Datetime.ParseDate(date)

    if episode > 0:
      oc.add(EpisodeObject(url=link, title=video_title, season=season, index=episode, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=ICON)))
    else:
      oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=ICON)))

  # This goes through all the pages for MTV popular video sections
  try:
    page_type = data.xpath('//div[contains(@class,"paginationContainer")]/span/a/strong//text()')[0]
    if 'Next' in page_type:
      page = data.xpath('//div[contains(@class,"paginationContainer")]/span/a//@href')[0]
      page = page.split('page=')[1]
      oc.add(NextPageObject(
        key = Callback(VideoPage, title = title, url=url, page = page), 
        title = L("Next Page ...")))
    else:
      pass
  except:
    pass

  if len(oc)==0:
    return ObjectContainer(header="Sorry!", message="No video available in this category.")
  else:
    return oc
###########################################################################################
# This function is used to pull the season and episodes for shows 
@route(PREFIX + '/seasepfind')
def SeasEpFind(episode, title, season):

  #Log('the value of title is %s' %title)
  try:
    test_ep = int(episode)
  except:
    try:
      episode = RE_EPISODE.search(title).group(2)
    except:
      episode = '0'
  if season==0:
    if len(episode)==3:
      new_season = episode[0]
    else:
      try:
        new_season = RE_SEASON.search(title).group(2)
      except:
        new_season = '1'
  else:
    new_season = season
    
  seas_ep=[episode, new_season]
  #Log('the value of seas_ep is %s' %seas_ep)
  return seas_ep
