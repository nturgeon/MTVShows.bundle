# NEED TO SEE IF WE CAN CUT DOWN SPECIALS SECTION AND EPISODE AND SEASON FIND
TITLE = 'MTV Shows'
PREFIX = '/video/mtvshows'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

SEARCH_URL = 'http://www.mtv.com/search/video/'
BASE_URL = 'http://www.mtv.com'
MTV_SHOWS = 'http://www.mtv.com/ontv'
MTV_SHOWS_ALL = 'http://www.mtv.com/ontv/all/'
MTV_PLAYLIST = 'http://www.mtv.com/global/music/videos/ajax/playlist.jhtml?feo_switch=true&channelId=1&id=%s'
MTV_POPULAR = 'http://www.mtv.com/most-popular/tv-show-videos/?category=%s&metric=numberOfViews&range=%s&order=desc'

RE_SEASON  = Regex('.+Season (\d{1,2}).+')
RE_SEASON_ALSO  = Regex('.+Seas. (\d{1,2}).+')
RE_EPISODE  = Regex('.+Ep. (\d{1,3})')
RE_EPISODE_ALSO  = Regex('.+Episode (\d{1,3})')
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

  #HTTP.CacheTime = CACHE_1HOUR 
 
#####################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(MTVShows, title='MTV Shows'), title='MTV Shows')) 
  oc.add(DirectoryObject(key=Callback(MTVVideos, title='MTV Videos'), title='MTV Videos')) 
  #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
  oc.add(InputDirectoryObject(key=Callback(SearchVideos, title='Search MTV Videos'), title='Search MTV Videos', summary="Click here to search videos", prompt="Search for the videos you would like to find"))
  return oc
#####################################################################################
# For MTV main sections of Popular, Specials, and All Shows
@route(PREFIX + '/mtvshows')
def MTVShows(title):
  oc = ObjectContainer(title2=title)
  oc.add(DirectoryObject(key=Callback(ProduceShows, title='MTV Popular Shows', sort_type='shows'), title='MTV Popular Shows')) 
  oc.add(DirectoryObject(key=Callback(ProduceShows, title='MTV Specials', sort_type='specials'), title='MTV Specials')) 
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
# THIS HANDLES MOST POPULAR MORE EFFIECIENTLY SO KEEPING THIS THOUGH ONLY AVAILABLE FOR MTV. USES SAME VIDEO PULL AS ABOVE
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
# For Producing All Shows 
# This pulls MTV shows from the menu does not have proper season url for Jersey Shore, The Hills, or Laguna Beach
# CAN PRODUCES IMAGES FOR MTV POPULAR SHOWS WITH ALTERNATE XPATH - //ol/li/div[/a 
@route(PREFIX + '/produceshows')
def ProduceShows(title, sort_type):
  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(MTV_SHOWS)
  if sort_type == 'shows':
    xpath_code = '//li[@inde="24.0"]/a'
  else:
    xpath_code = '//ul[@ind="35"]/li/a'

  for video in data.xpath('%s' %xpath_code):
    url = video.xpath('.//@href')[0]
    if not url.startswith('http://'):
      url = BASE_URL + url
    title = video.xpath('.//text()')[0]
    # THE GETTHUMB FUNCTION PRODUCES IMAGES BUT SLOW DOWN PULL SO IN THIS VERSION 
    # USED THE OPTION OF ADDING THEM AS CALLBACKS TO DIRECTORYOBJECTS PER MIKE'S SUGGESTION

    if sort_type=='shows':
      if 'series.jhtml' in url:
      # Would prefer to use a content check for Other Seasons since some shows do not have /season in url but it slows down the pull
      # WHEN PULLING MTV SHOWS FROM SHOW MENU JERSEY SHORE, THE HILLS, AND LAGUNA BEACH DO NOT HAVE SEASON IN THEM AND RR/RW CHALLENGE AND REAL WORLD HAVE A DIFFERENT NAME FOR EACH SEASON AND DO NOT HAVE /SEASON_ IN URL
        if '/season_' in url or 'rwrr_challenge/' in url or '/real_world/' in url or '/jersey_shore/' in url or '/the_hills/' in url or '/laguns_beach/' in url:
          oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url, thumb=R(ICON)), title=title, thumb=Callback(GetThumb, url=url)))
        else:
          oc.add(DirectoryObject(key=Callback(ShowCreateSeasons, title=title, url=url, thumb=R(ICON)), title=title, thumb=Callback(GetThumb, url=url)))
      else:
        pass

    else:
      if 'mtv' in url:
        if 'series.jhtml' in url:
          video_url = url.replace('series.jhtml', 'video.jhtml')
          oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=video_url, thumb=R(ICON)), title=title, thumb=Callback(GetThumb, url=video_url)))
        else:
          oc.add(DirectoryObject(key=Callback(SectionYears, title=title, url=url, thumb=R(ICON)), title=title, thumb=Callback(GetThumb, url=url)))

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
  data = HTML.ElementFromURL(local_url)
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
      # Would prefer to use a content check for Other Seasons since some shows do not have /season in url but it slows down the pull
      # 16 and Pregnant does not have a listing here for each season so sending ti to ShowSeason function
      if '/16_and_pregnant/' in url:
        oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, thumb=thumb, url=url), title=title, thumb=thumb))
      # The rest of the shows are listed by individual season. But RR/RW Challenge and Real World have different names for season, they do not have a /season in url
      elif '/season_' in url or 'rwrr_challenge/' in url or '/real_world/' in url:
        if '/season_' in url:
          season = url.split('/season_')[1]
          season = season.split('/')[0]
        else:
          season = 1
        oc.add(DirectoryObject(key=Callback(ShowVideos, title=title, url=url, section_id='fulleps', season=int(season)), title = title, thumb = thumb))
      else:
        oc.add(DirectoryObject(key=Callback(ShowCreateSeasons, title=title, thumb=thumb, url=url), title = title, thumb = thumb))
    elif '/ontv/' in url:
      if 'Archive' in title:
        if 'vma' in url:
          url = url + 'archive/'
        oc.add(DirectoryObject(key=Callback(SectionYears, title=title, url=url, thumb=thumb), title=title, thumb=thumb))
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
  
  #oc.objects.sort(key = lambda obj: obj.title)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no shows to list right now.")
  else:
    return oc
#######################################################################################
# This section handles seasons that have a different url for each season
@route(PREFIX + '/showseasons')
def ShowSeasons(title, url, thumb):

  oc = ObjectContainer(title2=title)
  local_url = url.replace('series', 'seasons')
  if not local_url.startswith('http://'):
    local_url = BASE_URL + local_url
  #THIS IS A UNIQUE DATA PULL
  data = HTML.ElementFromURL(local_url)
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

  #oc.objects.sort(key = lambda obj: obj.title, reverse=True)
  if len(oc) < 1:
    Log ('still no value for season objects')
    return ObjectContainer(header="Empty", message="There are no seasons to list right now.")
  else:
    return oc
#######################################################################################
# This section handles shows that do not have a separate page for each season
# Some shows (mostly MTV) do not have an other season link so this checks for season numbers in the main video page
@route(PREFIX + '/showcreateseasons')
def ShowCreateSeasons(title, url, thumb):

  oc = ObjectContainer(title2=title)
  season_list = []
  local_url = url.replace('series', 'video')
          
  # THIS DATA PULL IS ALSO USED FOR GETTHUMBS FUNCTION AND FOR SHOWVIDEO FUNCTION WHEN MISC VIDEOS ARE SENT
  data = HTML.ElementFromURL(local_url)
  # This function doesn't have a thumb for most shows except those coming from All Shows function, so just pulling from above video type list
  if not thumb.startswith('http://'):
    try:
      thumb = data.xpath('//ol[contains(@class, "photo-alt")]/li/div/a/img//@src')[0]
      if not thumb.startswith('http://'):
        thumb = BASE_URL + thumb
    except:
      pass
  else:
    pass
  for video in data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
    other_info = video.xpath('.//@maintitle')[0]
    episode = video.xpath('./ul/li[@class="list-ep"]//text()')[0]
    if episode == '--' or episode == 'Special':
      episode = EpisodeFind(other_info)
    else:
      episode = int(episode)
    season = SeasonFind(episode, other_info)
    if season not in season_list:
      season_list.append(season)
    else:
      pass
    
  # Need to sort the list
  season_list = sorted(season_list)
  for season_num in season_list:
  # If there is a season, the title is Season Number, if the season is 0, the title is Misc Videos
    if season_num > 0:
      oc.add(DirectoryObject(key=Callback(ShowSections, title='Season %s' %season_num, thumb=thumb, url=url, season=season_num), title = 'Season %s' %season_num, thumb = thumb))
    else:
      oc.add(DirectoryObject(key=Callback(ShowVideos, title='Other Videos', section_id='', url=url, season=season_num), title='Other Videos', thumb = thumb))

  oc.objects.sort(key = lambda obj: obj.title, reverse=True)
  if len(oc) < 1:
    # Here we can put an exception for the old video pages with a table format to send it to ShowVideo with season=1
    # DO ANY MTV SHOWS HAVE OLD TABLE FORMAT?
    oc.add(DirectoryObject(key=Callback(ShowVideos, title=title, section_id=' ', url=url, season=1), title=title, thumb = thumb))
    return oc
    #Log ('still no value for create season objects. Sending on to video function for check')
  else:
    return oc
#######################################################################################
# This section separates the MTV specials with archives into years.
# Chose to start at 2005 since that is the year that first seems to produce videos
@route(PREFIX + '/sectionyears')
def SectionYears(title, thumb, url):

  oc = ObjectContainer(title2=title)
  year = str(Datetime.Now().year)
  if 'vma' in url:
    local_url = url + 'video.jhtml'
    url = url + 'archive/'
  else:
    local_url = url + year + '/' + 'video.jhtml'
  if year not in title:
    title = year + ' ' + title
  # Need to pull thumbs here and using local url used for a pull in the other functions
  # THIS DATA PULL IS ALSO USED BY THE GETIDS AND PAGINATION FUNCTION
  data = HTML.ElementFromURL(local_url)
  thumb=data.xpath("//head//meta[@name='thumbnail']//@content")[0]
  if not thumb.startswith('http://'):
    thumb = BASE_URL + thumb
  oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=local_url, thumb=thumb), title=title, thumb=thumb))
  
  # THIS DATA PULL IS ALSO USED BY THE GETIDS AND PAGINATION FUNCTION
  #data = HTML.ElementFromURL(url)
  data = HTML.ElementFromURL(url)
  for video in data.xpath('//div[@id="sidebar"]/ol/li'):
    title = video.xpath('./p/b/a//text()')[0]
    year = int(title.split()[0])
    if year > 2004:
      url = video.xpath('./p/b/a//@href')[0]
      url = BASE_URL + url
      # A few do not put slash after the year so it causes errors
      if not url.endswith('/'):
        url = url + '/'
      oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url, thumb=thumb), title=title, thumb=thumb)) 

  #oc.objects.sort(key = lambda obj: obj.title, reverse=True)
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no years list right now.")
  else:
    return oc
#######################################################################################
# This section handles specials that do not have a traditional show structure. We use ID numbers to produce sections for these specials
# then use those IDS with the MTV_PLAYLIST to get the playlist
# ALL SHOWS THAT ARE PRODUCED ARE WORKING NOW, BUT COULD LOOK AT ADDING MTV UNPLUGGED
@route(PREFIX + '/specialsections')
def SpecialSections(title, thumb, url):

  oc = ObjectContainer(title2=title)
  xpath_code = '//li[@itemtype="http://schema.org/VideoObject"]'
  # this line puts alternative code for archived specials and avoids latest specials that use xpath code above
  # THE ISSUE IS THAT SOME OLDER MTV AWARDS HAVE ONE COLUMN INSTEAD OF TWO SO XPATH IS NOT CONSISTENT AND REQURES PULLING ALL LINKS ON PAGE
  if '.jhtml' not in url:
    xpath_code = '//ol/li/div[@class="thumb"]/a'
  section_list = GetIds(url, xpath_code)

  # Since this is just pulling thumb for one show, it should not slow down function
  if not thumb.startswith('http://'):
    thumb = Callback(GetThumb, url=url)
  else:
    pass
  for ids in section_list:
    #it appears that is a little faster to pull the title from the Playlist than the MRSS and can use VideoPage function to produce videos
    # THIS DATA PULL IS ALSO USED BY THE SPECIAL VIDEOS FUNCTION
    id_url = MTV_PLAYLIST %ids
    #data = HTML.ElementFromURL(id_url)
    data = HTML.ElementFromURL(id_url, cacheTime=CACHE_1DAY)
    try:
      title = data.xpath('//h3/span/text()')[0]
      oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=id_url), title=title, thumb=thumb))
    except:
      pass

  #oc.objects.sort(key = lambda obj: obj.title)
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no special videos to list right now.")
  else:
    return oc
#######################################################################################
# This function produces sections for each channel. Some shows offer after shows and misc videos (if mainuri) that can be watched thru the channel
@route(PREFIX + '/showsections', season=int)
def ShowSections(title, thumb, url, season):
  oc = ObjectContainer(title2=title)
  content = HTTP.Request(url).content
  oc.add(DirectoryObject(key=Callback(ShowVideos, title='Full Episodes', section_id='fulleps', url=url, season=season), title='Full Episodes', thumb=thumb))
  if '/video.jhtml?filter=aftershows' in content:
    oc.add(DirectoryObject(key=Callback(ShowVideos, title='After Shows', section_id='aftershows', url=url, season=season), title='After Shows', thumb=thumb)) 
  oc.add(DirectoryObject(key=Callback(ShowVideos, title='All Videos', section_id='', url=url, season=season), title='All Videos', thumb=thumb)) 
  return oc
#################################################################################################################
# This function produces videos from the table layout used by show video pages for all three networks
# This function picks up all videos in all pages even without paging code
# IT PRODUCES VIDEOS EXACTLY HOW THE SITE DOES SO JERSEY SHORE SEASON 5 AND 6 SHOW ALL SEASONEPISODES
@route(PREFIX + '/showvideos', season=int)
def ShowVideos(title, section_id, url, season):
  oc = ObjectContainer(title2=title)
  local_url = url.replace('series', 'video')
  if section_id:
      local_url = local_url + '?filter=' + section_id
  else:
    pass
  # NOT SURE IF THIS PULL IS THE SAME SINCE FILTER ON END BUT SIMILAR TO CREATE SEASON FUNCTION FOR MISC VIDEO 
  data = HTML.ElementFromURL(local_url)
  for video in data.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
    # If the link does not have a mainuri, it will not play through the channel with the url service, so added a check for that here
    other_info = video.xpath('.//@maintitle')[0]
    episode = video.xpath('./ul/li[@class="list-ep"]//text()')[0]
    if episode == '--' or episode == 'Special':
      episode = EpisodeFind(other_info)
    else:
      episode = int(episode)
    all_seasons = SeasonFind(episode, other_info)
    title = video.xpath('./meta[@itemprop="name"]//@content')[0]
    if not title:
      title = other_info
    thumb = video.xpath('./meta[@itemprop="thumbnail"]//@content')[0]
    if not thumb.startswith('http://'):
      thumb = BASE_URL + thumb
    thumb = thumb.split('?')[0]
    vid_url = video.xpath('./meta[@itemprop="url"]//@content')[0]
    if not vid_url.startswith('http://'):
      vid_url = BASE_URL + vid_url
    desc = video.xpath('./meta[@itemprop="description"]//@content')[0]
    date = video.xpath('./ul/li[@class="list-date"]//text()')[0]
    if 'hrs ago' in date:
      try:
        date = Datetime.Now()
      except:
        date = ''
    else:
      date = Datetime.ParseDate(date)

    # Jersey shore is producing all previous season episodes in season 5 and 6 sections 
    # Here we can produce the shows just like the site does
    if '/season_' in url or season == all_seasons:
      oc.add(EpisodeObject(
        url = vid_url, 
        season = all_seasons,
        index = episode,
        title = title, 
        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
        originally_available_at = date,
        summary = desc
      ))

  #oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no %s videos to list right now." %section_id)
  else:
    return oc
#########################################################################################
# This function is for pulling searches
@route(PREFIX + '/searchvideos')
def SearchVideos(title, query='', page_url=''):
  oc = ObjectContainer(title2=title)
  if query:
    local_url = SEARCH_URL + '?q=' + String.Quote(query, usePlus = False)  + '&page=1'
  else:
    local_url = SEARCH_URL + page_url
  data = HTML.ElementFromURL(local_url)
  for item in data.xpath('//ul/li[contains(@class,"mtvn-video ")]'):
    link = item.xpath('./div/a//@href')[0]
    if 'mtviggy' in link:
      continue
    if not link.startswith('http://'):
      link = BASE_URL + link
    image = item.xpath('./div/a/span/img//@src')[0]
    if not image.startswith('http://'):
      image = BASE_URL + image
    try:
      video_title = item.xpath('./div/a/text()')[2].strip()
    except:
      video_title = item.xpath('./div/div/a/text()')[0]
    if not video_title:
      try:
        video_title = item.xpath('./div/a/span/span/text()')[0]
        video_title2 = item.xpath('./div/a/span/em/text()')[0]
        video_title = video_title + ' ' + video_title2
      except:
        video_title = ''
    try:
      date = item.xpath('./p/span/em//text()')[0]
      if date.startswith('Music'):
        date = item.xpath('./p/span/em//text()')[1]
    except:
      date = ''
    if 'hrs ago' in date:
      try:
        date = Datetime.Now()
      except:
        date = ''
    else:
      date = Datetime.ParseDate(date)

    oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=ICON)))
  # This goes through all the pages of a search
  # After first page, the Prev and Next have the same page_url, so have to check for
  try:
    page_type = data.xpath('//a[contains(@class,"pagination")]//text()')
    x = len(page_type)-1
    if 'Next' in page_type[x]:
      page_url = data.xpath('//a[contains(@class,"pagination")]//@href')[x]
      oc.add(NextPageObject(
        key = Callback(SearchVideos, title = title, page_url = page_url), 
        title = L("Next Page ...")))
    else:
      pass
  except:
    pass

  #oc.objects.sort(key = lambda obj: obj.index, reverse=True)

  if len(oc)==0:
    return ObjectContainer(header="Sorry!", message="No video available in this category.")
  else:
    return oc
####################################################################################################
# This produces videos for most popular for all networks and latest full epsodes for mtv
# This function works with the MTV video block setup as well as ajax and global module pages
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
    link = item.xpath('./div/a//@href')[0]
    if not link.startswith('http://'):
      link = BASE_URL + link
    image = item.xpath('./div/a/img//@src')[0]
    if not image.startswith('http://'):
      image = BASE_URL + image
    video_title = item.xpath('./div/meta[@itemprop="name"]//@content')[0].strip()
    video_title = video_title.replace('\n', '')
    if video_title == None or len(video_title) == 0:
      video_title = item.xpath('div/a/img')[-1].get('alt')
    try:
      date = item.xpath('./p/span/time[@itemprop="datePublished"]//text()')[0]
    except:
      date = ''
    if 'hrs ago' in date:
      try:
        date = Datetime.Now()
      except:
        date = ''
    else:
      date = Datetime.ParseDate(date)

    oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback=ICON)))
  # This goes through all the pages for MTV popular video sections
  try:
    page_type = data.xpath('//div[contains(@class,"paginationContainer")]/span/a/strong//text()')[0]
    if 'Next' in page_type:
      page = data.xpath('//div[contains(@class,"paginationContainer")]/span/a//@href')[0]
      page = page.split('page=')[1]
      oc.add(NextPageObject(
        key = Callback(ShowsAll, title = title, page = page), 
        title = L("Next Page ...")))
    else:
      pass
  except:
    pass

  #oc.objects.sort(key = lambda obj: obj.index, reverse=True)

  if len(oc)==0:
    return ObjectContainer(header="Sorry!", message="No video available in this category.")
  else:
    return oc
#################################################################################################################
# This function creates a list of the unique ids for specials pages
@route(PREFIX + '/getids')
def GetIds(url, xpath_code):

  section_list = []
  data = HTML.ElementFromURL(url)
  # The best place to get the ids are from the uri for the links so we check for that first
  for ids in data.xpath('%s' %xpath_code):
    try:
      id_num = ids.xpath('.//@mainuri')[0]
      id_num = id_num.split('videolist:mtv.com:')[1]
    except:
      try:
        id_num = ids.xpath('./div/a//@href')[0]
        # This below handles series that do not have a mainuri and archived award shows
      except:
        id_num = ids.xpath('.//@href')[0]
      if '#id=' in id_num or '?id=' in id_num:
        try:
          id_num = id_num.split('#id=')[1]
        except:
          id_num = id_num.split('?id=')[1]
        if 'vid=' in id_num:
          id_num = id_num.split('&vid')[0]
    # make sure it is a 7 digit number could even add int check
    if len(id_num) == 7:
      if id_num not in section_list:
        section_list.append(id_num)
    else:
      pass
  return section_list
###########################################################################################
# This function is used in CreateShowSeasons and ShowVideo to pull episode numbers for shows that have '--' in epside field
@route(PREFIX + '/episodefind')
def EpisodeFind(other_info):
  try:
    # A couple of shows do not have an episode number but do have the episode number in other info in the format of Ep. or Episode 
    episode = int(RE_EPISODE.search(other_info).group(1))
  except:
    try:
      episode = int(RE_EPISODE_ALSO.search(other_info).group(1))
    except:
      episode = 0
  #Log('the value of episode at the end of the EpisodeFind function is %s' %episode)
  return episode
###########################################################################################
# This function is used in CreateShowSeasons and ShowVideo to pull season numbers for shows that do not have an _season url
@route(PREFIX + '/seasonfind')
def SeasonFind(episode, other_info):
  episode = str(episode)
  if len(episode) > 2:
    season = int(episode[0])
  else:
    if '(Season' in other_info:
      season = int(RE_SEASON.search(other_info).group(1))
    elif '(Seas.' in other_info:
      season = int(RE_SEASON_ALSO.search(other_info).group(1))
    else:
      if episode == '0':
        season = 0
      else:
        season = 1
  #Log('the value of season at the end of the SeasonFind function is %s' %season)
  return season
#############################################################################################################################
# This is a function to pull the thumb image from a page. 
# We first try the top of the page if it isn't there, we can pull an image from the video page side block
@route(PREFIX + '/gethumb')
def GetThumb(url):
  # NEED TO BE AWARE OF OTHER PULLS TO THIS URL AND MAKE SURE THEY ARE ALL THE SAME CACHE
  if 'series.jhtml' in url:
    local_url = url.replace('series', 'video')
  else:
    local_url = url
  try:
    #page = HTML.ElementFromURL(local_url)
    page = HTML.ElementFromURL(local_url, cacheTime = CACHE_1DAY)
  except:
    thumb = None
    pass
  try:
    thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
  except:
    try:
      thumb = page.xpath('//ol[contains(@class, "photo-alt")]/li/div/a/img//@src')[0]
    except:
      try:
        thumb = page.xpath("//head//meta[@name='thumbnail']//@content")[0]
      except:
        thumb = None
  if thumb:
    if '?' in thumb:
      thumb = thumb.split('?')[0]
    if not thumb.startswith('http://'):
      thumb = main_url + thumb
    return Redirect(thumb)
  else:
    return Redirect(R(ICON))
