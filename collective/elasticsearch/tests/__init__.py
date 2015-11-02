# coding: utf-8
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from collective.elasticsearch.testing import \
    ElasticSearch_INTEGRATION_TESTING, \
    ElasticSearch_FUNCTIONAL_TESTING
import unittest2 as unittest
from collective.elasticsearch.es import ElasticSearchCatalog, PatchCaller
from collective.elasticsearch.interfaces import IElasticSettings
import transaction
from collective.elasticsearch import hook


class BaseTest(unittest.TestCase):

    layer = ElasticSearch_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request.environ['testing'] = True
        self.app = self.layer['app']

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IElasticSettings)
        settings.enabled = True

        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.catalog._elasticcustomindex = 'plone-test-index'
        self.es = ElasticSearchCatalog(self.catalog)
        self.es.convertToElastic()
        self.catalog.manage_catalogRebuild()
        # need to commit here so all tests start with a baseline
        # of elastic enabled
        transaction.commit()
        patched = PatchCaller(self.catalog)
        self.searchResults = patched.searchResults

    def clearTransactionEntries(self):
        _hook = hook.getHook(self.es)
        _hook.remove = []
        _hook.index = {}

    def tearDown(self):
        self.es.connection.indices.delete(index=self.es.index_name)
        self.clearTransactionEntries()


class BaseFunctionalTest(BaseTest):

    layer = ElasticSearch_FUNCTIONAL_TESTING
