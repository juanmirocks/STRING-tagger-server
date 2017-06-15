"""Tagger Testing Server"""

import flask
from flask import Flask
from flask import request, current_app, json
from collections import OrderedDict
import unittest
from server import app
from server import annotate_post
from server import string_id_to_uniprot_id


class SimpleTest(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_basic_calls_on_server(self):
        response = self.app.get('/', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, "Welcome")

        response = self.app.get('/annotate', content_type='application/json', data=json.dumps({"text": "p53"}))
        self.assertEquals(response.status_code, 200)  # basic post

        response = self.app.get('/annotate', content_type='application/json')
        self.assertEquals(response.status_code, 405)  # must send some data

        response = self.app.get('/annotate/text', content_type='application/json')
        self.assertEquals(response.status_code, 404)  # does not exist

    #
    # All following predictions tests must be re-written
    #

    # # test when we provide only text
    # def test_annotate_only_text(self):
    #     response = self.app.post('/annotate/post', data=json.dumps({"text": "p53"}), content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":3,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps({"text": "p53 mouse"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":1}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps({"text": "tp53"}), content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":4,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1},'
    #         '{"end":4,"normalizations":[{"id":"ENSP00000371475","type":9606},{"id":"Q12888|TP53B_HUMAN","type":"uniprot:9606"}],"start":1}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps(
    #         {"text": "Tumor protein p53 and human CDK1 and mouse CDK1 and influenza"}), content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":17,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1},'
    #         '{"end":32,"normalizations":[{"id":"ENSP00000378699","type":9606},{"id":"P06493|CDK1_HUMAN","type":"uniprot:9606"}],"start":29},'
    #         '{"end":32,"normalizations":[{"id":"ENSMUSP00000020099","type":10090},{"id":"P11440|CDK1_MOUSE","type":"uniprot:10090"}],"start":29},'
    #         '{"end":47,"normalizations":[{"id":"ENSP00000378699","type":9606},{"id":"P06493|CDK1_HUMAN","type":"uniprot:9606"}],"start":44},'
    #         '{"end":47,"normalizations":[{"id":"ENSMUSP00000020099","type":10090},{"id":"P11440|CDK1_MOUSE","type":"uniprot:10090"}],"start":44}]}'))
    #
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"text": "p53 dhe .p53 dhe P53.1 dhe P5-3 dhe -p53 and and human"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":3,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1},'
    #         '{"end":12,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":10},'
    #         '{"end":20,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":18},'
    #         '{"end":31,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":28},'
    #         '{"end":40,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":38}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps(
    #         {"text": "Tumor prot.ein p53 and hu.m-an CDK1 and m.o-use CDK1 and influenza"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":18,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],'
    #         '"start":16},{"end":35,"normalizations":[{"id":"ENSP00000378699","type":9606},{"id":"P06493|CDK1_HUMAN","type":"uniprot:9606"}],"start":32},'
    #         '{"end":52,"normalizations":[{"id":"ENSP00000378699","type":9606},{"id":"P06493|CDK1_HUMAN","type":"uniprot:9606"}],"start":49}]}'))
    #
    # # test when we provide ids and text
    # def test_annotate_only_ids_and_text(self):
    #     response = self.app.post('/annotate/post', data=json.dumps({"ids": "-22,10090", "text": "p53"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":3,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":1}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps({"ids": "-22", "text": "p53"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads('{"entities":[]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps(
    #         {"ids": "-22,10090", "text": "Tumor prot.ein p53 and hu.m-an CDK1 and m.o-use CDK1 and influenza"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":18,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":16},'
    #         '{"end":18,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":16},'
    #         '{"end":35,"normalizations":[{"id":"ENSP00000378699","type":9606},{"id":"P06493|CDK1_HUMAN","type":"uniprot:9606"}],"start":32},'
    #         '{"end":35,"normalizations":[{"id":"ENSMUSP00000020099","type":10090},{"id":"P11440|CDK1_MOUSE","type":"uniprot:10090"}],"start":32},'
    #         '{"end":52,"normalizations":[{"id":"ENSP00000378699","type":9606},{"id":"P06493|CDK1_HUMAN","type":"uniprot:9606"}],"start":49},'
    #         '{"end":52,"normalizations":[{"id":"ENSMUSP00000020099","type":10090},{"id":"P11440|CDK1_MOUSE","type":"uniprot:10090"}],"start":49}]}'))
    #
    # # test when we provied text and autodetect
    # def test_annotate_only_text_and_autodetect(self):
    #     response = self.app.post('/annotate/post', data=json.dumps({"text": "p53 mouse tp53", "autodetect": "True"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":1},'
    #         '{"end":14,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":11},'
    #         '{"end":14,"normalizations":[{"id":"ENSP00000371475","type":9606},{"id":"Q12888|TP53B_HUMAN","type":"uniprot:9606"}],"start":11},'
    #         '{"end":14,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":11}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps({"text": "p53 mouse tp53", "autodetect": "False"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":3,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1},'
    #         '{"end":14,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":11},'
    #         '{"end":14,"normalizations":[{"id":"ENSP00000371475","type":9606},{"id":"Q12888|TP53B_HUMAN","type":"uniprot:9606"}],"start":11}]}'))
    #
    # # test when we provide ids, text and autodetect
    # def test_annotate_ids_and_text_and_autodetect(self):
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22,9606", "text": "p53 mouse tp53", "autodetect": "True"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":1},'
    #         '{"end":14,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":11},'
    #         '{"end":14,"normalizations":[{"id":"ENSP00000371475","type":9606},{"id":"Q12888|TP53B_HUMAN","type":"uniprot:9606"}],"start":11},'
    #         '{"end":14,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":11}]}'))
    #
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22,9606", "text": "p53 mouse tp53", "autodetect": "False"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":3,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1},'
    #         '{"end":14,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":11},'
    #         '{"end":14,"normalizations":[{"id":"ENSP00000371475","type":9606},{"id":"Q12888|TP53B_HUMAN","type":"uniprot:9606"}],"start":11}]}'))
    #
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22,10090", "text": "p53 mouse tp53", "autodetect": "True"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":1},'
    #         '{"end":14,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":11}]}'))
    #
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22,10090", "text": "p53 mouse tp53", "autodetect": "False"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":1},'
    #         '{"end":14,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":11}]}'))
    #
    # # ttest when we provide -22 as id
    # def test_annotate_ids_minus22(self):
    #     response = self.app.post('/annotate/post', data=json.dumps({"ids": "-22", "text": "p53 human nucleus"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1},{"end":17,"normalizations":[{"id":"GO:0005634","type":-22}],"start":11}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps({"ids": "-22", "text": "p53 human"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1}]}'))
    #
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22", "text": "nucleus", "autodetect": "False"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":7,"normalizations":[{"id":"GO:0005634","type":-22}],"start":1}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps(
    #         {"ids": "-22", "text": "tp53 mouse tp53 nucleus", "autodetect": "False"}), content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":23,"normalizations":[{"id":"GO:0005634","type":-22}],"start":17}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps(
    #         {"ids": "-22", "text": "tp53 mouse tp53 nucleus", "autodetect": "True"}), content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":4,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":1},{"end":15,"normalizations":[{"id":"ENSMUSP00000104298","type":10090},{"id":"P02340|P53_MOUSE","type":"uniprot:10090"}],"start":12},{"end":23,"normalizations":[{"id":"GO:0005634","type":-22}],"start":17}]}'))
    #
    # # test when we provide -22 and 7227 as ids
    # def test_annotate_ids_minus22_and_7227(self):
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22,7227", "text": "p53 human", "autodetect": "False"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":3,"normalizations":[{"id":"FBpp0083753","type":7227},{"id":"","type":"uniprot:7227"}],"start":1},'
    #         '{"end":3,"normalizations":[{"id":"FBpp0081732","type":7227},{"id":"O46339|HTH_DROME","type":"uniprot:7227"}],"start":1},'
    #         '{"end":3,"normalizations":[{"id":"FBpp0072177","type":7227},{"id":"P08841|TBB3_DROME","type":"uniprot:7227"}],"start":1}]}'))
    #
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22,7227", "text": "p53 human", "autodetect": "True"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1}]}'))
    #
    # # test when we provide -22, 7227 and 9606 as ids
    # def test_annotate_ids_minus22_and_7227_and_9606(self):
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22,7227,9606", "text": "p53 human", "autodetect": "False"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1}]}'))
    #
    #     response = self.app.post('/annotate/post',
    #                              data=json.dumps({"ids": "-22,7227,9606", "text": "p53 human", "autodetect": "True"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":9,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1}]}'))
    #
    # # test when we provide text for different organisms
    # def test_annotate_other_data(self):
    #     response = self.app.post('/annotate/post', data=json.dumps({
    #         "text": "AT2s2, 4cll3 and others are used to test arabidopsis and pfk27, gnd1 and -a-ar2 are used to test yeast"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":5,"normalizations":[{"id":"AT4G27150.1","type":3702},{"id":"P15458|2SS2_ARATH","type":"uniprot:3702"}],"start":1},'
    #         '{"end":12,"normalizations":[{"id":"AT1G20490.1","type":3702},{"id":"Q3E6Y4|4CLL3_ARATH","type":"uniprot:3702"}],"start":8},'
    #         '{"end":62,"normalizations":[{"id":"YOL136C","type":4932},{"id":"Q12471|6P22_YEAST","type":"uniprot:4932"}],"start":58},'
    #         '{"end":68,"normalizations":[{"id":"YHR183W","type":4932},{"id":"P38720|6PGD1_YEAST","type":"uniprot:4932"}],"start":65},'
    #         '{"end":79,"normalizations":[{"id":"ENSP00000313674","type":9606},{"id":"Q9Y312|AAR2_HUMAN","type":"uniprot:9606"}],"start":75},'
    #         '{"end":79,"normalizations":[{"id":"YBL074C","type":4932},{"id":"P32357|AAR2_YEAST","type":"uniprot:4932"}],"start":75}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps({
    #         "text": "Fission yeast and yeast and Schizosaccharomyces pombe have paa1 but only yeast has cbs2 and abc4"}),
    #                              content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":63,"normalizations":[{"id":"YDR071C","type":4932},{"id":"Q12447|PAA1_YEAST","type":"uniprot:4932"}],"start":60},'
    #         '{"end":63,"normalizations":[{"id":"SPAP8A3.09c.1","type":4896},{"id":"Q9UT08|2AAA_SCHPO","type":"uniprot:4896"}],"start":60},'
    #         '{"end":63,"normalizations":[{"id":"SPAC9.02c.1","type":4896},{"id":"Q9UT25|YFY2_SCHPO","type":"uniprot:4896"}],"start":60},'
    #         '{"end":87,"normalizations":[{"id":"YDR197W","type":4932},{"id":"P14905|CBS2_YEAST","type":"uniprot:4932"}],"start":84},'
    #         '{"end":87,"normalizations":[{"id":"SPAC1556.08c.1","type":4896},{"id":"Q10343|AAKG_SCHPO","type":"uniprot:4896"}],"start":84},'
    #         '{"end":96,"normalizations":[{"id":"SPAC30.04c.1","type":4896},{"id":"Q9P7V2|ABC4_SCHPO","type":"uniprot:4896"}],"start":93}]}'))
    #
    #     response = self.app.post('/annotate/post', data=json.dumps(
    #         {"text": "Brachydanio rerio  or danio rerio have aldh9a1a and ab-cb8"}), content_type='application/json')
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(json.loads(response.data), json.loads(
    #         '{"entities":[{"end":47,"normalizations":[{"id":"ENSDARP00000118280","type":7955},{"id":"Q7ZVB2|A9A1A_DANRE","type":"uniprot:7955"}],"start":40},'
    #         '{"end":58,"normalizations":[{"id":"ENSP00000351717","type":9606},{"id":"Q9NUT2|ABCB8_HUMAN","type":"uniprot:9606"}],"start":53},'
    #         '{"end":58,"normalizations":[{"id":"ENSDARP00000073658","type":7955},{"id":"Q56A55|ABCB8_DANRE","type":"uniprot:7955"}],"start":53}]}'))


if __name__ == '__main__':
    unittest.main()
