from django import test
from taggit.managers import TaggableManager
from sourcebook.models import FoiaRequestBase


class SearchTest(test.TestCase):
    def test_foiarequest_search(self):
        """Makes sure partial search works on FOIA Request object"""
        new_request = FoiaRequestBase.objects.create(
            short_description="Aardvark Reports",
            requested_formats=TaggableManager(),
            requested_records="I would like all of your records on aardvarks",
            expedited_processing="Wouldn't you want to get your hands on these reports?",
        )
        filtered_result = FoiaRequestBase.objects.filter(search_vector="aardvark")
        assert len(filtered_result) == 1
        assert FoiaRequestBase.objects.get(pk=new_request.id) == filtered_result[0]
