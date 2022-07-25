

















# folder_explorer and file_explorer -> get 3 files from folder, have with tests in a test dir, use those files to test
# create new csvs
# processors
# csv traversers
# rjk filter
# url generatprs


# RP-P-1997-357, http: // hdl.handle.net/10934/RM0001.COLLECT.356891, Affiche voor 'Kleine schilderijen' door Georg Rueter, affiche, "Rueter, Georg", 1945,
# RP-P-2008-277, http: // hdl.handle.net/10934/RM0001.collect.465622, "Affiche voor expositie schilderijen en litho's van Klaas Gubbels in het Besiendershuis, Nijmegen", affiche, "Gubbels, Klaas", 1950,
# RP-P-2015-26-1036,http://hdl.handle.net/10934/RM0001.COLLECT.613311,Verzamelaar van schilderijen,prent,"Chodowiecki, Daniel Nikolaus",1781,



import unittest
import asynctest
import aiohttp
import certifi
import ssl

from utils import isNotLatinAlphabet, filter_for_rjk_fields
import settings


class TestRJKFilters(asynctest.TestCase):
    async def setUp(self):
        self.json_data1_req = f"https://www.rijksmuseum.nl/api/nl/collection/RP-P-1997-357?key={settings.rjk_api}"
        self.json_data2_req = f"https://www.rijksmuseum.nl/api/nl/collection/RP-P-2008-277?key={settings.rjk_api}"
        self.json_data3_req = f"https://www.rijksmuseum.nl/api/nl/collection/RP-P-2015-26-1036?key={settings.rjk_api}"
        self.image_link = '--test_image_link--'

        headers = {"User-Agent": settings.user_agent}
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = aiohttp.TCPConnector(ssl=ssl_context, limit=10)

        async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
            async with session.get(self.json_data1_req, allow_redirects=False) as response_1:
                self.res1 = await response_1.json(content_type='application/json')
            async with session.get(self.json_data2_req, allow_redirects=False) as response_2:
                self.res2 = await response_2.json(content_type='application/json')
            async with session.get(self.json_data3_req, allow_redirects=False) as response_3:
                self.res3 = await response_3.json(content_type='application/json')
                

    async def test_filter_for_rjk_fields1(self):
        filtered_data1 = filter_for_rjk_fields(self.res1, self.image_link)

        self.assertTrue(filtered_data1[0] == "Affiche voor 'Kleine schilderijen' door Georg Rueter")
        self.assertTrue(filtered_data1[9] == "1945 - 1960")
        self.assertTrue(len(filtered_data1) == 11)
        self.assertTrue(filtered_data1[-1] == self.image_link)
            

    async def test_filter_for_rjk_fields2(self):
        filtered_data2 = filter_for_rjk_fields(self.res2, self.image_link)

        self.assertTrue(filtered_data2[0] == "Affiche voor expositie schilderijen en litho's van Klaas Gubbels in het Besiendershuis, Nijmegen")
        self.assertTrue(filtered_data2[9] == "ca. 1950 - ca. 1970")
        self.assertTrue(len(filtered_data2) == 11)
        self.assertTrue(filtered_data2[-1] == self.image_link)
            

    async def test_filter_for_rjk_fields3(self):
        filtered_data3 = filter_for_rjk_fields(self.res3, self.image_link)

        self.assertTrue(filtered_data3[0] == "Verzamelaar van schilderijen")
        self.assertTrue(filtered_data3[9] == "1781")
        self.assertTrue(len(filtered_data3) == 11)
        self.assertTrue(filtered_data3[-1] == self.image_link)

    def test_filter_for_rjk_fields_3(self):
        self.res3['artObject']['title'] = ''
        filtered_data3 = filter_for_rjk_fields(self.res3, self.image_link)
        self.assertTrue(filtered_data3 is None)

    def tearDown(self):
        del self.json_data1_req, self.json_data2_req, self.json_data3_req, self.image_link


class TestIsNotLatinAlphabet(unittest.TestCase):

    def setUp(self):
        self.false_terms = ['hello', '123456', '*&^gzdl3ts', 'Salve']
        self.true_terms = ['你好', 'привет', 'नमस्ते']

    def test_isNotLatinAlphabet_false(self):
        for term in self.false_terms:
            self.assertFalse(isNotLatinAlphabet(term))

    def test_isNotLatinAlphabet_true(self):
        for term in self.true_terms:
            self.assertTrue(isNotLatinAlphabet(term))

    def tearDown(self):
        del self.false_terms, self.true_terms





if __name__ == '__main__':
    unittest.main()
