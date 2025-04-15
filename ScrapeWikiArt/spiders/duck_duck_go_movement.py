from duck_duck_go import DuckDuckGoSpider
from ScrapeWikiArt.items import UpdatedMovementItem


class DuckDuckGoMovementSpider(DuckDuckGoSpider):
    name = 'duck_duck_go_movement'
    allowed_domains = ['api.duckduckgo.com']

    item_class = UpdatedMovementItem
    query_feature = 'Name'
