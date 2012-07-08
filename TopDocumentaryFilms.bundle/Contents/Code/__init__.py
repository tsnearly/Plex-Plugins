####################################################################################################

VIDEO_PREFIX = "/video/topdocumentaryfilms"
NAME		 = L('Title')
ART          = 'art-default.jpg'
ICON         = 'icon-default.png'

BASE         = 'http://www.topdocumentaryfilms.com'

####################################################################################################

def Start():

    ## make this plugin show up in the 'Video' section
    ## in Plex. The L() function pulls the string out of the strings
    ## file in the Contents/Strings/ folder in the bundle
    ## see also:
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    ##  http://dev.plexapp.com/docs/Bundle.html#the-strings-directory

    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)
    
    HTTP.CacheTime = CACHE_1HOUR


#### the rest of these are user created functions and
#### are not reserved by the plugin framework.
#### see: http://dev.plexapp.com/docs/Functions.html for
#### a list of reserved functions above



def VideoMainMenu():

    # Container acting sort of like a folder on
    # a file system containing other things like
    # "sub-folders", videos, music, etc
    # see:
    #  http://dev.plexapp.com/docs/Objects.html#MediaContainer
    dir = MediaContainer(viewGroup="InfoList")


	dir.Append(
		Function(
			DirectoryItem(
				AllFeatured,
				title="Featured Documentaries",
				subtitle="Featured",
				summary="Display a list of the currently featured documentaries being showcased.",
				thumb=R(ICON),
				art=R(ART)
			)
		)
	)
	
	dir.Append(
		Function(
			DirectoryItem(
				AllRecommended,
				title="Recommended Documentaries",
				subtitle="Recommended",
				summary="Display a list of recommended documentaries.",
				thumb=R(ICON),
				art=R(ART)
			)
		)
	)

	dir.Append(
		Function(
			DirectoryItem(
				ByAddDate,
				title="Recently Added Documentaries",
				subtitle="Recently Added",
				summary="Display documentaries listed by the date they were added.",
				thumb=R(ICON),
				art=R(ART)
			)
		)
	)

	dir.Append(
		Function(
			DirectoryItem(
				AllEditorsPicks,
				title="Editors' Picks",
				subtitle="Editors' Picks",
				summary="Display a list of documentaries as featured by TopDocumentaryFilms editors.",
				thumb=R(ICON),
				art=R(ART)
			)
		)
	)
					
    dir.Append(
        Function(
            DirectoryItem(
                ByCategory,
                title="Browse By Category...",
                subtitle="By Category",
                summary="Display a list of categories to select from.",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )
  
    dir.Append(
        Function(
            InputDirectoryItem(
                SearchResults,
                title="Search...",
                subtitle="Search",
                summary="Search all films.",
                prompt="Search for Movies",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )


    # ... and then return the container
    return dir


def CallbackExample(sender):
    return MessageContainer(
        "Not implemented",
        "In real life, you'll make more than one callback,\nand you'll do something useful.\nsender.itemTitle=%s" % sender.itemTitle
    )


def SearchResults(sender,query=None):
    return MessageContainer(
        "Not implemented",
        "In real life, you would probably perform some search using python\nand then build a MediaContainer with items\nfor the results"
    )

    
def AllFeatured(sender):
	page = HTML.ElementFromURL("http://topdocumentaryfilms.com/")
    playlist = page.xpath("//div[@class='docusrandom']")
    
    for video in playlist:
    	

  
  
####################################################################################################
def MainMenu():
    oc = ObjectContainer()

    oc.add(DirectoryObject(key = Callback(ByCategory), title = 'Browse By Category...'))
    oc.add(DirectoryObject(key = Callback(AllCategories), title = 'All Categories'))
    oc.add(InputDirectoryObject(key = Callback(ParseSearchResults), title = 'Search...', prompt = 'Search for Videos'))

    return oc

####################################################################################################
def ByCategory(level = 1, title = ''):
    oc = ObjectContainer(title2 = title)
    
    if level > 1:
      parse_string = '/ul/li' * (level - 1) + '[contains(.,"' + title + '")]/ul/li' 
    else:
      parse_string = '/ul/li' * level

    page = HTML.ElementFromURL('http://www.khanacademy.org/')
    elements = page.xpath("//div[@id='browse-fixed']//nav[@class='css-menu']" + parse_string)
    
    for el in elements:
      if (el.text == None):
        link = el.xpath('.//a')[0]
        if '#' in link.get('href'):
          category = String.Unquote(link.get('href').replace('#',''))
          oc.add(DirectoryObject(key = Callback(Submenu, category = category), title = link.text.strip()))
        else:
          category = String.Unquote(link.get('href'))
          oc.add(DirectoryObject(key = Callback(Submenu, category = category, test_prep = True), title = link.text.strip()))
      else:
        title = el.text.strip()
        oc.add(DirectoryObject(key = Callback(ByCategory, title = title, level = level + 1), title = title))

    return oc

####################################################################################################
def AllCategories():
    oc = ObjectContainer()

    playlists = JSON.ObjectFromURL('http://www.khanacademy.org/api/playlists')
    for playlist in playlists:
      oc.add(DirectoryObject(
        key = Callback(Submenu, category = playlist['title'].lower().replace(' ','-'), api_url = playlist['api_url']), 
        title = playlist['title']))

    return oc

####################################################################################################
def ParseSearchResults(query = 'math'):
    oc = ObjectContainer()

    page = HTML.ElementFromURL('http://www.khanacademy.org/search?page_search_query=' + query)
    results = page.xpath("//li[@class='videos']")

    for video in results:
      url = BASE + video.xpath(".//a")[0].get('href')
      title = video.xpath(".//span/text()")[0]
      summary = video.xpath(".//p/text()")[0]
      oc.add(VideoClipObject(url = url, title = title, summary = summary))

    if len(oc) == 0:
      return MessageContainer("No Results", 'No video file could be found for the following query: ' + query)

    return oc

####################################################################################################
def Submenu(category, api_url = None, test_prep = False):
    oc = ObjectContainer()

    if test_prep == False:
      if api_url == None:
        page = HTML.ElementFromURL('http://www.khanacademy.org/')
        playlist_category = page.xpath("//div[@data-role='page' and @id='" + category + "']//h2")[0].text
        api_url = "http://www.khanacademy.org/api/playlistvideos?playlist=%s" % String.Quote(playlist_category)
      
      playlist = JSON.ObjectFromURL(api_url)
      
      for video in playlist:
        oc.add(VideoClipObject(
          url = video['youtube_url'],
          title = video['title'],
          summary = video['description'],
          originally_available_at = Datetime.ParseDate(video['date_added'].split('T')[0]),
          tags = [tag.strip() for tag in video['keywords'].split(',')]))
      
    else:
      if category == '/gmat':
        oc.add(DirectoryObject(key = Callback(Submenu, category = "GMAT Data Sufficiency"), title = "Data Sufficiency"))
        oc.add(DirectoryObject(key = Callback(Submenu, category = "GMAT: Problem Solving"), title = "Problem Solving"))
      if category == '/sat':
        oc.add(DirectoryObject(key = Callback(Submenu, category = "SAT Preparation"), title = "All SAT preperation courses"))
                
    return oc

def ByRecommendation();
	oc = ObjectContainer()
	
#"//*[@class="sidebarsB"]/ul[1]/li/ul[2]/li"	
	
def GetMovieDetails(url):

	page = HTML.ElementFromURL(url)
	movie = MovieObject()
	
	movie.url = page.