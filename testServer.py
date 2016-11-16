"""Tagger Testing Server"""

import argparse
import os
import flask
from flask import Flask
from flask import request, current_app
from flask.json import JSONEncoder
import optparse
import time
import sys, getopt, io
import unittest
from server import app
from server import annotate

class SimpleTest(unittest.TestCase):

    def setUp(self):
        #Create a test client
        self.app = app.test_client()
        #Propagate the exceptions to the test client
        self.app.testing = True 

    #Test the input which is successfully tagged
    def testAnnotateFormattingAddedData(self):
        
        response = self.app.get('/annotate?entity_types=-111,3&text=.SHp-endm', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[{"end":9,"entities":[{"id":"123","type":-111}],"start":1}]}\n')

	response = self.app.get('/annotate?entity_types=-111,3&text=sHp-endm', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[{"end":8,"entities":[{"id":"123","type":-111}],"start":0}]}\n')

	response = self.app.get('/annotate?entity_types=-111,3&text=sHp-endmaaaaaa', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[]}\n')

	response = self.app.get('/annotate?entity_types=-111,3&text=asdasd-sHp-endm', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[{"end":15,"entities":[{"id":"123","type":-111}],"start":7}]}\n')

	response = self.app.get('/annotate?entity_types=-111,3&text=shpendmasdashpendmsd-sHp-endm', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[{"end":29,"entities":[{"id":"123","type":-111}],"start":21}]}\n')

	response = self.app.get('/annotate?entity_types=-111,3&text=.shpendmasdashpendmsd-sHp-en.dm', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[]}\n') #it doesn't work correctly for this case. This shouldn't be the case since there is one shpendm there.

	response = self.app.get('/annotate?entity_types=-111,3&text=-.s-h-penddm', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[]}\n') #it doesn't work correctly for this case

	response = self.app.get('/annotate?entity_types=-111,3&text=-.s-h-pen.dm', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[]}\n') #it doesn't work correctly for this case


    #Test the functionality of server
    def testFailingOfServer(self): 

        response = self.app.get('/annotate?text=adds', content_type='application/json')
        self.assertEquals(response.status_code, 500)

	response = self.app.get('/annotate?entity_types=-111,3', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[]}\n')

	response = self.app.get('/annotate?entity_types=-111,3a', content_type='application/json')
        self.assertEquals(response.status_code, 500)

	response = self.app.get('/annotate?entity_types=-111,3.2', content_type='application/json')
        self.assertEquals(response.status_code, 500)

	response = self.app.get('/annotate?entity_types=-111,,322', content_type='application/json')
        self.assertEquals(response.status_code, 500)

	response = self.app.get('/annotate?entity_types', content_type='application/json')
        self.assertEquals(response.status_code, 500)

	response = self.app.get('/annotate', content_type='application/json')
        self.assertEquals(response.status_code, 500)

	response = self.app.get('/annotate/text', content_type='application/json')
        self.assertEquals(response.status_code, 404)

    #Tests with human and sometime mouse organisms
    def testAnnotateFormattingCurrentData(self): 

        response = self.app.get('/annotate?entity_types=10090,9606,1856129&text=Tumor%20protein%20p53%20and%20human%20CDK1%20and%20mouse%20CDK1%20and%20influenza', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[{"end":17,"entities":[{"id":"ENSP00000269305","type":9606}],"start":0},{"end":32,"entities":[{"id":"ENSP00000378699","type":9606},{"id":"ENSMUSP00000020099","type":10090}],"start":28},{"end":47,"entities":[{"id":"ENSP00000378699","type":9606},{"id":"ENSMUSP00000020099","type":10090}],"start":43}]}\n')

	response = self.app.get('/annotate?entity_types=10090,9606,1856129&text=p53%20dhe%20.p53%20dhe%20P53.1%20dhe%20P5-3%20dhe%20-p53%20and%20nucleus%20and%20human', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[{"end":3,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":0},{"end":7,"entities":[{"id":"ENSMUSP00000029699","type":10090}],"start":4},{"end":12,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":9},{"end":16,"entities":[{"id":"ENSMUSP00000029699","type":10090}],"start":13},{"end":20,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":17},{"end":26,"entities":[{"id":"ENSMUSP00000029699","type":10090}],"start":23},{"end":31,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":27},{"end":35,"entities":[{"id":"ENSMUSP00000029699","type":10090}],"start":32},{"end":40,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":37}]}\n')

	response = self.app.get('/annotate?entity_types=10090,9606,1856129&text=Emdal%20KB,%20Pedersen%20AK,%20Bekker-Jensen%20DB,%20Tsafou%20KP,%20Horn%20H,%20Lindner%20S,%20Schulte%20JH,%20Eggert%20A,%20Jensen%20LJ,%20Francavilla%20C,%20Olsen%20JV%20Sci%20Signal.%208(374):ra40%202015%20Temporal%20proteomics%20of%20NGF-TrkA%20signaling%20identifies%20an%20inhibitory%20role%20for%20the%20E3%20ligase%20Cbl-b%20in%20neuroblastoma%20cell%20differentiation.%20SH-SY5Y%20neuroblastoma%20cells%20respond%20to%20nerve%20growth%20factor%20(NGF)-mediated%20activation%20of%20the%20tropomyosin-related%20kinase%20A%20(TrkA)%20with%20neurite%20outgrowth,%20thereby%20providing%20a%20model%20to%20study%20neuronal%20differentiation.%20We%20performed%20a%20time-resolved%20analysis%20of%20NGF-TrkA%20signaling%20in%20neuroblastoma%20cells%20using%20mass%20spectrometry-based%20quantitative%20proteomics.%20The%20combination%20of%20interactome,%20phosphoproteome,%20and%20proteome%20data%20provided%20temporal%20insights%20into%20the%20molecular%20events%20downstream%20of%20NGF%20binding%20to%20TrkA.%20We%20showed%20that%20upon%20NGF%20stimulation,%20TrkA%20recruits%20the%20E3%20ubiquitin%20ligase%20Cbl-b,%20which%20then%20becomes%20phosphorylated%20and%20ubiquitylated%20and%20decreases%20in%20abundance.%20We%20also%20found%20that%20recruitment%20of%20Cbl-b%20promotes%20TrkA%20ubiquitylation%20and%20degradation.%20Furthermore,%20the%20amount%20of%20phosphorylation%20of%20the%20kinase%20ERK%20and%20neurite%20outgrowth%20increased%20upon%20Cbl-b%20depletion%20in%20several%20neuroblastoma%20cell%20lines.%20Our%20findings%20suggest%20that%20Cbl-b%20limits%20NGF-TrkA%20signaling%20to%20control%20the%20length%20of%20neurites.', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[{"end":183,"entities":[{"id":"ENSP00000358525","type":9606}],"start":180},{"end":188,"entities":[{"id":"ENSP00000431418","type":9606}],"start":184},{"end":252,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":247},{"end":350,"entities":[{"id":"ENSP00000358525","type":9606}],"start":331},{"end":355,"entities":[{"id":"ENSP00000358525","type":9606}],"start":352},{"end":412,"entities":[{"id":"ENSP00000431418","type":9606}],"start":384},{"end":418,"entities":[{"id":"ENSP00000431418","type":9606}],"start":414},{"end":549,"entities":[{"id":"ENSP00000358525","type":9606}],"start":546},{"end":554,"entities":[{"id":"ENSP00000431418","type":9606}],"start":550},{"end":780,"entities":[{"id":"ENSP00000358525","type":9606}],"start":777},{"end":796,"entities":[{"id":"ENSP00000431418","type":9606}],"start":792},{"end":821,"entities":[{"id":"ENSP00000358525","type":9606}],"start":818},{"end":839,"entities":[{"id":"ENSP00000431418","type":9606}],"start":835},{"end":878,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":873},{"end":999,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":994},{"end":1013,"entities":[{"id":"ENSP00000431418","type":9606}],"start":1009},{"end":1106,"entities":[{"id":"ENSMUSP00000101471","type":10090},{"id":"ENSP00000363763","type":9606},{"id":"ENSMUSP00000023462","type":10090},{"id":"ENSP00000215832","type":9606}],"start":1103},{"end":1149,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":1144},{"end":1228,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":1223},{"end":1239,"entities":[{"id":"ENSP00000358525","type":9606}],"start":1236},{"end":1244,"entities":[{"id":"ENSP00000431418","type":9606}],"start":1240}]}\n')

    #Tests with organisms from here: http://string-db.org/mapping_files/uniprot_mappings/
    def testAnnotateFormattingDifferentOrganisms(self): 

        response = self.app.get('/annotate?entity_types=10090,9606,1856129&text=Tumor%20prot.ein%20p53%20and%20hu.m-an%20CDK1%20and%20m.o-use%20CDK1%20and%20influenza', content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, '{"entities":[{"end":18,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":15},{"end":35,"entities":[{"id":"ENSP00000378699","type":9606},{"id":"ENSMUSP00000020099","type":10090}],"start":31},{"end":52,"entities":[{"id":"ENSP00000378699","type":9606},{"id":"ENSMUSP00000020099","type":10090}],"start":48}]}\n')

	response = self.app.get('/annotate?entity_types=-3,-22&text=proline%20rich%20domain%20important%20for%20the%20apoptotic%20activity%20of%20p53%20human%20protein%20by%20nuclear%20exportation%20via%20MAPK%20human%20and%20mouse%20and%20MLLT2%20188del11', content_type='application/json')
	self.assertEquals(response.status_code, 200)
	self.assertEquals(response.data, '{"entities":[{"end":69,"entities":[{"id":"ENSP00000269305","type":9606}],"start":60},{"end":88,"entities":[{"id":"GO:0005634","type":-22}],"start":81},{"end":115,"entities":[{"id":"9606","type":-3}],"start":110},{"end":125,"entities":[{"id":"10090","type":-3}],"start":120},{"end":135,"entities":[{"id":"ENSP00000378578","type":9606},{"id":"ENSMUSP00000031256","type":10090}],"start":130}]}\n')

	response = self.app.get('/annotate?entity_types=-3,-22&text=Arabidopsis%20and%20yeast%20are%20some%20organisms', content_type='application/json')
	self.assertEquals(response.status_code, 200)
	self.assertEquals(response.data, '{"entities":[{"end":11,"entities":[{"id":"3702","type":-3}],"start":0},{"end":21,"entities":[{"id":"4932","type":-3}],"start":16}]}\n')

	response = self.app.get('/annotate?entity_types=-3,-22&text=AT2s2,%204cll3%20and%20others%20are%20used%20to%20test%20arabidopsis%20and%20pfk27,%20gnd1%20and%20-a-ar2%20are%20used%20to%20test%20yeast', content_type='application/json')
	self.assertEquals(response.status_code, 200)
	self.assertEquals(response.data, '{"entities":[{"end":5,"entities":[{"id":"AT4G27150.1","type":3702}],"start":0},{"end":12,"entities":[{"id":"AT1G20490.1","type":3702}],"start":7},{"end":52,"entities":[{"id":"3702","type":-3}],"start":41},{"end":62,"entities":[{"id":"YOL136C","type":4932}],"start":57},{"end":68,"entities":[{"id":"YHR183W","type":4932}],"start":64},{"end":79,"entities":[{"id":"YBL074C","type":4932}],"start":74},{"end":102,"entities":[{"id":"4932","type":-3}],"start":97}]}\n')

	response = self.app.get('/annotate?entity_types=-3,-22&text=Fission%20yeast%20and%20yeast%20and%20Schizosaccharomyces%20pombe%20have%20paa1%20but%20only%20yeast%20has%20cbs2%20and%20abc4', content_type='application/json')
	self.assertEquals(response.status_code, 200)
	self.assertEquals(response.data, '{"entities":[{"end":13,"entities":[{"id":"4896","type":-3}],"start":0},{"end":23,"entities":[{"id":"4932","type":-3}],"start":18},{"end":53,"entities":[{"id":"4896","type":-3}],"start":28},{"end":63,"entities":[{"id":"YDR071C","type":4932},{"id":"SPAP8A3.09c.1","type":4896},{"id":"SPAC9.02c.1","type":4896}],"start":59},{"end":78,"entities":[{"id":"4932","type":-3}],"start":73},{"end":87,"entities":[{"id":"YDR197W","type":4932},{"id":"SPAC1556.08c.1","type":4896}],"start":83},{"end":96,"entities":[{"id":"SPAC30.04c.1","type":4896}],"start":92}]}\n')

	response = self.app.get('/annotate?entity_types=-3,-22&text=drosophila%20and%20fruit%20fly%20are%20a%20bit%20ague%20as%20terms%20and%20have%20pgd%20and%20abd-b', content_type='application/json')
	self.assertEquals(response.status_code, 200)
	self.assertEquals(response.data, '{"entities":[{"end":10,"entities":[{"id":"7227","type":-3},{"id":"7244","type":-3}],"start":0},{"end":24,"entities":[{"id":"7227","type":-3}],"start":15},{"end":61,"entities":[{"id":"FBpp0070368","type":7227},{"id":"FBpp0070365","type":7227}],"start":58},{"end":71,"entities":[{"id":"FBpp0082826","type":7227}],"start":66}]}\n')

	response = self.app.get('/annotate?entity_types=-3,-22&text=Brachydanio%20rerio%20%20or%20danio%20rerio%20have%20aldh9a1a%20and%20ab-cb8', content_type='application/json')
	self.assertEquals(response.status_code, 200)
	self.assertEquals(response.data, '{"entities":[{"end":17,"entities":[{"id":"7955","type":-3}],"start":0},{"end":33,"entities":[{"id":"7955","type":-3}],"start":22},{"end":47,"entities":[{"id":"ENSDARP00000118280","type":7955}],"start":39},{"end":58,"entities":[{"id":"ENSDARP00000073658","type":7955}],"start":52}]}\n')


if __name__ == '__main__':
    unittest.main()
