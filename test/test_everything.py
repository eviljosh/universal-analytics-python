#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
# Test and example kit for Universal Analytics for Python
# Copyright (c) 2013, Analytics Pros
# 
# This project is free software, distributed under the BSD license. 
# Analytics Pros offers consulting and integration services if your firm needs 
# assistance in strategy, implementation, or auditing existing work.
###############################################################################

from __future__ import absolute_import

import unittest
try:
    # try python 3
    from unittest.mock import call
    from unittest.mock import patch
except ImportError:
    # fall back to python 2
    from mock import call
    from mock import patch

from UniversalAnalytics import Tracker


class UAMPythonTestCase(unittest.TestCase):
    
    def setUp(self):
        # Create the tracker
        self.tracker = Tracker.create('UA-XXXXX-Y', client_id='123cid', use_post=True)

    def tearDown(self):
        del self.tracker

    def testTrackerOptionsBasic(self):
        self.assertEqual('UA-XXXXX-Y', self.tracker.params['tid'])  

    def testPersistentCampaignSettings(self):
        
        # Apply campaign settings
        self.tracker.set('campaignName', 'testing-campaign')
        self.tracker.set('campaignMedium', 'testing-medium')
        self.tracker['campaignSource'] = 'test-source'
    
        self.assertEqual(self.tracker.params['cn'], 'testing-campaign') 
        self.assertEqual(self.tracker.params['cm'], 'testing-medium')
        self.assertEqual(self.tracker.params['cs'], 'test-source')

    @patch('requests.post')
    def testSendPageview(self, mock_requests_post):
        # Send a pageview
        self.tracker.send('pageview', '/test')

        mock_requests_post.assert_called_once_with(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                'tid': 'UA-XXXXX-Y',
                'cid': '123cid',
                't': 'pageview',
                'dp': '/test',
                'v': 1
            }
        )

    @patch('requests.post')
    def testSendInteractiveEvent(self, mock_requests_post):
        # Send an event
        self.tracker.send('event', 'mycat', 'myact', 'mylbl', { 'noninteraction': 1, 'page': '/1' })

        mock_requests_post.assert_called_once_with(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                'dp': '/1',
                'ni': 1,
                'ec': 'mycat',
                't': 'event',
                'cid': '123cid',
                'ea': 'myact',
                'v': 1,
                'tid': 'UA-XXXXX-Y',
                'el': 'mylbl'
            }
        )

    @patch('requests.post')
    def testSendUnicodeEvent(self, mock_requests_post):

        # Send unicode data:
        # As unicode
        self.tracker.send('event', u'câtēgøry', u'åctîõn', u'låbęl', u'válüē')

        mock_requests_post.assert_called_once_with(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                'el': u'låbęl',
                't': 'event',
                'ea': u'åctîõn',
                'cid': '123cid',
                'v': 1,
                'ec': u'câtēgøry',
                'tid': 'UA-XXXXX-Y'
            }
        )

    @patch('requests.post')
    def testSendUnicodeStringEvent(self, mock_requests_post):

        # Send unicode data:
        # As str
        self.tracker.send('event', 'câtēgøry', 'åctîõn', 'låbęl', 'válüē')

        mock_requests_post.assert_called_once_with(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                'el': u'låbęl',
                't': 'event',
                'ea': u'åctîõn',
                'cid': '123cid',
                'v': 1,
                'ec': u'câtēgøry',
                'tid': 'UA-XXXXX-Y'
            }
        )

    @patch('requests.post')
    def testSocialHit(self, mock_requests_post):
        # Send a social hit
        self.tracker.send('social', 'facebook', 'share', '/test#social')

        mock_requests_post.assert_called_once_with(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                't': 'social',
                'cid': '123cid',
                'sn': 'facebook',
                'sa': 'share',
                'v': 1,
                'tid': 'UA-XXXXX-Y',
                'st': '/test#social'
            }
        )

    @patch('requests.post')
    def testTransaction(self, mock_requests_post):

        # Dispatch the item hit first (though this is somewhat unusual)
        self.tracker.send('item', {
            'transactionId': '12345abc',
            'itemName': 'pizza',
            'itemCode': 'abc',
            'itemCategory': 'hawaiian',
            'itemQuantity': 1
        }, hitage = 7200)

        mock_requests_post.assert_called_once_with(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                'iv': 'hawaiian',
                'cid': '123cid',
                'ti': '12345abc',
                't': 'item',
                'in': 'pizza',
                'qt': 7200000,
                'ic': 'abc',
                'iq': 1.0,
                'v': 1,
                'tid': 'UA-XXXXX-Y'
            }
        )

        # Then the transaction hit...
        self.tracker.send('transaction', {
            'transactionId': '12345abc',
            'transactionAffiliation': 'phone order',
            'transactionRevenue': 28.00,
            'transactionTax': 3.00,
            'transactionShipping': 0.45,
            'transactionCurrency': 'USD'
        }, hitage = 7200)

        self.assertEqual(2, mock_requests_post.call_count)
        mock_requests_post.assert_any_call(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                'tt': 3.0,
                'ti': '12345abc',
                'cu': 'USD',
                'ts': 0.45,
                'tid': 'UA-XXXXX-Y',
                'ta': 'phone order',
                'cid': '123cid',
                'qt': 7200000,
                'tr': 28.0,
                't': 'transaction',
                'v': 1
            }
        )

    @patch('requests.post')
    def testTimingAdjustedHits(self, mock_requests_post):

        # A few more hits for good measure, testing real-time support for time offset
        self.tracker.send('pageview', '/test', { 'campaignName': 'testing2' }, hitage = 60 * 5) # 5 minutes ago

        mock_requests_post.assert_called_once_with(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                'cid': '123cid',
                't': 'pageview',
                'dp': '/test',
                'qt': 300000,
                'v': 1,
                'cn': 'testing2',
                'tid': 'UA-XXXXX-Y'
            }
        )

        self.tracker.send('pageview', '/test', { 'campaignName': 'testing3' }, hitage = 60 * 20) # 20 minutes ago

        self.assertEqual(2, mock_requests_post.call_count)
        mock_requests_post.assert_any_call(
            'https://www.google-analytics.com/collect',
            headers={'User-Agent': 'Analytics Pros - Universal Analytics (Python)'},
            data={
                'cid': '123cid',
                't': 'pageview',
                'dp': '/test',
                'qt': 1200000,
                'v': 1,
                'cn': 'testing3',
                'tid': 'UA-XXXXX-Y'
            }
        )

# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
