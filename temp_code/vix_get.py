# -*- coding: utf-8 -*-


def loadobj(xmlnode):
	o = object.__new__(globals()[xmlnode.xpath('@class')[0].split('.')[-1]])
	o.__init__(**dict(zip(xmlnode.xpath('param/@name'), xmlnode.xpath('param/@value'))))
	o.__dict__.update(zip(xmlnode.xpath('property/@name'), xmlnode.xpath('property/@value')))
	globals()[xmlnode.xpath('@name')[0].strip()] = o

import lxml.etree

import codecs
with codecs.open('config.xml', encoding='utf-8') as f:
	obj = lxml.etree.XML(f.read())

from logging.handlers import TimedRotatingFileHandler

handler = obj.xpath('//handler')[0]



loadobj(handler)
print (filelog)
