"""Tagger Testing Server"""

import flask
from flask import Flask
from flask import request, current_app, json
import unittest
from server import app
from server import annotatePost

class SimpleTest(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True 


    def testFailingOfServer(self): 

	response = self.app.get('/annotate/post', content_type='application/json')
        self.assertEquals(response.status_code, 405)

	response = self.app.get('/annotate/text', content_type='application/json')
        self.assertEquals(response.status_code, 404)


    def testAnnotateFormattingCurrentData(self): 

	response = self.app.post('/annotate/post', data=json.dumps(dict(text="p53")),content_type='application/json')
	self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), json.loads('{"entities":[{"end":4,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1}]}'))


	response = self.app.post('/annotate/post', data=json.dumps(dict(text="Tumor protein p53 and human CDK1 and mouse CDK1 and influenza")),content_type='application/json')
	self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), json.loads('{"entities":[{"end":18,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1},{"end":33,"normalizations":[{"id":"ENSMUSP00000020099","type":10090},{"id":"P11440|CDK1_MOUSE","type":"uniprot:10090"}],"start":29},{"end":48,"normalizations":[{"id":"ENSMUSP00000020099","type":10090},{"id":"P11440|CDK1_MOUSE","type":"uniprot:10090"}],"start":44}]}'))


	response = self.app.post('/annotate/post', data=json.dumps(dict(text="p53 dhe .p53 dhe P53.1 dhe P5-3 dhe -p53 and and human")),content_type='application/json')
	self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), json.loads('{"entities":[{"end":4,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":1},{"end":13,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":10},{"end":21,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":18},{"end":32,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":28},{"end":41,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":38}]}'))


	response = self.app.post('/annotate/post', data=json.dumps(dict(text="d decreases in abundance. We also found that recruitment of Cbl-b promotes TrkA ubiquitylation and degradation. Furthermore, the amount of phosphorylation of the kinase ERK and neurite outgrowth increased upon Cbl-b depletion in several neuroblastoma cell lines. Our findings suggest that Cbl-b l")),content_type='application/json')
	self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), json.loads('{"entities":[{"end":66,"normalizations":[{"id":"ENSP00000445920","type":9606},{"id":"Q96EY8|MMAB_HUMAN","type":"uniprot:9606"}],"start":61},{"end":80,"normalizations":[{"id":"ENSP00000431418","type":9606},{"id":"P04629|NTRK1_HUMAN","type":"uniprot:9606"}],"start":76},{"end":173,"normalizations":[{"id":"ENSP00000215832","type":9606},{"id":"P28482|MK01_HUMAN","type":"uniprot:9606"}],"start":170},{"end":216,"normalizations":[{"id":"ENSP00000445920","type":9606},{"id":"Q96EY8|MMAB_HUMAN","type":"uniprot:9606"}],"start":211},{"end":295,"normalizations":[{"id":"ENSP00000445920","type":9606},{"id":"Q96EY8|MMAB_HUMAN","type":"uniprot:9606"}],"start":290}]}'))


	response = self.app.post('/annotate/post', data=json.dumps(dict(text="Tumor prot.ein p53 and hu.m-an CDK1 and m.o-use CDK1 and influenza")),content_type='application/json')
	self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), json.loads('{"entities":[{"end":19,"normalizations":[{"id":"ENSP00000269305","type":9606},{"id":"P04637|P53_HUMAN","type":"uniprot:9606"}],"start":16},{"end":36,"normalizations":[{"id":"ENSP00000378699","type":9606},{"id":"P06493|CDK1_HUMAN","type":"uniprot:9606"}],"start":32},{"end":53,"normalizations":[{"id":"ENSP00000378699","type":9606},{"id":"P06493|CDK1_HUMAN","type":"uniprot:9606"}],"start":49}]}'))


    def testAnnotateFormattingCurrentData(self): 


        response = self.app.post('/annotate/post', data=json.dumps(dict(text="AT2s2, 4cll3 and others are used to test arabidopsis and pfk27, gnd1 and -a-ar2 are used to test yeast")),content_type='application/json')
	self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), json.loads('{"entities":[{"end":6,"normalizations":[{"id":"AT4G27150.1","type":3702},{"id":"P15458|2SS2_ARATH","type":"uniprot:3702"}],"start":1},{"end":13,"normalizations":[{"id":"AT1G20490.1","type":3702},{"id":"Q3E6Y4|4CLL3_ARATH","type":"uniprot:3702"}],"start":8},{"end":63,"normalizations":[{"id":"YOL136C","type":4932},{"id":"Q12471|6P22_YEAST","type":"uniprot:4932"}],"start":58},{"end":69,"normalizations":[{"id":"YHR183W","type":4932},{"id":"P38720|6PGD1_YEAST","type":"uniprot:4932"}],"start":65},{"end":80,"normalizations":[{"id":"YBL074C","type":4932},{"id":"P32357|AAR2_YEAST","type":"uniprot:4932"}],"start":75}]}'))


        response = self.app.post('/annotate/post', data=json.dumps(dict(text="Fission yeast and yeast and Schizosaccharomyces pombe have paa1 but only yeast has cbs2 and abc4")),content_type='application/json')
	self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), json.loads('{"entities":[{"end":64,"normalizations":[{"id":"SPAC9.02c.1","type":4896},{"id":"Q9UT25|YFY2_SCHPO","type":"uniprot:4896"}],"start":60},{"end":88,"normalizations":[{"id":"SPAC1556.08c.1","type":4896},{"id":"Q10343|AAKG_SCHPO","type":"uniprot:4896"}],"start":84},{"end":97,"normalizations":[{"id":"SPAC30.04c.1","type":4896},{"id":"Q9P7V2|ABC4_SCHPO","type":"uniprot:4896"}],"start":93}]}'))


        response = self.app.post('/annotate/post', data=json.dumps(dict(text="Brachydanio rerio  or danio rerio have aldh9a1a and ab-cb8")),content_type='application/json')
	self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), json.loads('{"entities":[{"end":48,"normalizations":[{"id":"ENSDARP00000118280","type":7955},{"id":"Q7ZVB2|A9A1A_DANRE","type":"uniprot:7955"}],"start":40},{"end":59,"normalizations":[{"id":"ENSDARP00000073658","type":7955},{"id":"Q56A55|ABCB8_DANRE","type":"uniprot:7955"}],"start":53}]}'))



if __name__ == '__main__':
    unittest.main()
