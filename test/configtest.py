#!/usr/bin/env python -B

import unittest
import subprocess
import sys
import os

from mock import patch, Mock

"""
Add pkg and parent directory for mock testing of authentication errors
"""
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pkg"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config import AccountKey, BingRewardsReportItem, Config, ConfigError
mockdate = "2017-09-06 00:44:47.7"

"""
  Test xml is correctly stored
"""
class TestConfig(unittest.TestCase):
    def setUp(self):
        self.configFBXML = """
<configuration>
    <general
        betweenQueriesInterval="12.271"
        betweenQueriesSalt="5.7"
        betweenAccountsInterval="404.1"
        betweenAccountsSalt="40.52" />

    <accounts>
        <account type="Facebook" disabled="false">
            <login>john.smith@gmail.com</login>
            <password>xxx</password>
        </account>
    </accounts>

    <events>
        <onError>
            <retry interval="5" salt="3.5" count="1" />
            <notify cmd="echo error %a %p %r %l %i" />
        </onError>
        <onComplete>
            <retry if="%p lt 16" interval="5" salt="3.5" count="1" />
            <notify if="%l gt 3000" cmd="echo complete %a %p %r %P %l %i" />
            <notify if="%p ne 16" cmd="echo complete %a %p %r %P %l %i" />
            <notify if="%P gt 475" cmd="echo complete %a %p %r %P %l %i" />

            <account ref="Facebook_john.smith@gmail.com">
                <retry if="%p lt 31" interval="5" salt="3.5" count="1" />
                <notify if="%l gt 10000" cmd="echo complete %a %p %r %P %l %i" />
                <notify if="%p ne 31" cmd="echo complete %a %p %r %P %l %i" />
                <notify if="%P gt 475" cmd="echo complete %a %p %r %P %l %i" />
            </account>

        </onComplete>
        <onScriptComplete>
            <notify cmd="./mail.sh" />
        </onScriptComplete>
        <onScriptFailure>
            <notify cmd="./onScriptFailure.sh" />
        </onScriptFailure>
    </events>
    <queries generator="wikipedia" />
</configuration>
        """
        self.config = Config()
        self.configXMLString = """
<configuration>
    <general
        betweenQueriesInterval="12.271"
        betweenQueriesSalt="5.7"
        betweenAccountsInterval="404.1"
        betweenAccountsSalt="40.52" />

    <accounts>
        <account type="Live" disabled="false">
            <login>ms@ps.com</login>
            <password>zzz</password>
        </account>
    </accounts>

    <events>
        <onError>
            <retry interval="5" salt="3.5" count="1" />
            <notify cmd="echo error %a %p %r %l %i" />
        </onError>
        <onComplete>
            <retry if="%p lt 16" interval="5" salt="3.5" count="1" />
            <notify if="%l gt 3000" cmd="echo complete %a %p %r %P %l %i" />
            <notify if="%p ne 16" cmd="echo complete %a %p %r %P %l %i" />
            <notify if="%P gt 475" cmd="echo complete %a %p %r %P %l %i" />

            <account ref="Live_ms@ps.com">
                <retry if="%p lt 31" interval="5" salt="3.5" count="1" />
                <notify if="%l gt 10000" cmd="echo complete %a %p %r %P %l %i" />
                <notify if="%p ne 31" cmd="echo complete %a %p %r %P %l %i" />
                <notify if="%P gt 475" cmd="echo complete %a %p %r %P %l %i" />
            </account>

        </onComplete>
        <onScriptComplete>
            <notify cmd="echo" />
        </onScriptComplete>
        <onScriptFailure>
            <notify cmd="echo" />
        </onScriptFailure>
    </events>
    <queries generator="googleTrends" />
</configuration>
        """
        self.config.parseFromString(self.configXMLString)

    import helpers
    @patch('helpers.getResponseBody')
    @patch('time.sleep')
    def test_auth(self, timemock, helpmock):
        """
        test authentication decoding error
        :return:
        """
        import bingAuth
        import main

        helpmock.return_value = '"WindowsLiveId":""     "WindowsLiveId":""'
        timemock.return_value = ''

        main.run(self.config)

    def test_accounts(self):
        self.assertIsNotNone(self.config.accounts)
        self.assertEqual(len(self.config.accounts), 1)
        accounts = dict()

        acc = Config.Account()
        acc.accountLogin = "ms@ps.com"
        acc.password = "zzz"
        acc.accountType = "Live"
        acc.disabled = False
        accounts[acc.getRef()] = acc

        self.assertEqual(accounts, self.config.accounts)

    def test_facebook(self):
        """
        Should throw Not supported value for facebook parameters
        """
        self.config.parseFromString(self.configFBXML)
        import main
        self.assertRaisesRegexp(ValueError, "Not supported", main.run, self.config)

"""
  Testing bing reward with configuration files below
"""
class TestBing(unittest.TestCase):
  def test_assert(self):
      cmd = "ls config.xml"
      cmds = cmd.split()
      status = subprocess.check_call(cmds)
      self.assertEqual(status, 0, "no config.xml file")

  def test_configfile(self):
      cmd = "./main.py -f config.xml.dist"
      cmds = cmd.split()
      output = subprocess.check_output(cmds, stderr=subprocess.STDOUT)
      self.assertRegexpMatches(output, "AuthenticationError", "should have seen invalid account auth\n" + output)

if __name__ == '__main__':
  unittest.main(verbosity=3)
