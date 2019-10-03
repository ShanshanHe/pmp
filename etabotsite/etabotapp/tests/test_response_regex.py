import unittest
import sys
sys.path.append('..')
import response_regex as rr
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class TestResponseRegex(unittest.TestCase):
    """Test cases for response regex module."""

    def test_get_login_url(self):
        result = rr.get_login_url(response)
        logging.debug(result)
        self.assertEqual(result, ['http://localhost:8080/login.jsp'])

response = """

JiraError HTTP 403 url: http://localhost:8080/rest/api/2/serverInfo
    text: CAPTCHA_CHALLENGE; login-url=http://localhost:8080/login.jsp
    
    response headers = {'X-AREQUESTID': '740x1119x1', 'X-XSS-Protection': '1; mode=block', 'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'SAMEORIGIN', 'Content-Security-Policy': "frame-ancestors 'self'", 'X-ASEN': 'SEN-L13360980', 'Set-Cookie': 'JSESSIONID=17E2F3A39736A6FED76BF70DD099CC49; Path=/; HttpOnly', 'X-Seraph-LoginReason': 'AUTHENTICATION_DENIED', 'WWW-Authenticate': 'OAuth realm="http%3A%2F%2Flocalhost%3A8080"', 'X-ASESSIONID': '1dnd31d', 'X-Authentication-Denied-Reason': 'CAPTCHA_CHALLENGE; login-url=http://localhost:8080/login.jsp', 'Content-Type': 'text/html;charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Date': 'Fri, 05 Apr 2019 18:20:20 GMT'}
    response text = 









<html>

<head>
    <title>Forbidden (403)</title>
    



<!--[if IE]><![endif]-->
<script type="text/javascript">
    (function() {
        var contextPath = '';
        var eventBuffer = [];

        function printDeprecatedMsg() {
            if (console && console.warn) {
                console.warn('DEPRECATED JS - contextPath global variable has been deprecated since 7.4.0. Use `wrm/context-path` module instead.');
            }
        }

        function sendEvent(analytics, postfix) {
            analytics.send({
                name: 'js.globals.contextPath.' + postfix
            });
        }

        function sendDeprecatedEvent(postfix) {
            try {
                var analytics = require('jira/analytics');
                if (eventBuffer.length) {
                    eventBuffer.forEach(function(value) {
                        sendEvent(analytics, value);
                    });
                    eventBuffer = [];
                }

                if (postfix) {
                    sendEvent(analytics, postfix);
                }
            } catch(ex) {
                eventBuffer.push(postfix);
                setTimeout(sendDeprecatedEvent, 1000);
            }
        }

        Object.defineProperty(window, 'contextPath', {
            get: function() {
                printDeprecatedMsg();
                sendDeprecatedEvent('get');
                return contextPath;
            },
            set: function(value) {
                printDeprecatedMsg();
                sendDeprecatedEvent('set');
                contextPath = value;
            }
        });
    })();

</script>
<script>
window.WRM=window.WRM||{};window.WRM._unparsedData=window.WRM._unparsedData||{};window.WRM._unparsedErrors=window.WRM._unparsedErrors||{};
WRM._unparsedData["com.atlassian.plugins.atlassian-plugins-webresource-plugin:context-path.context-path"]="\"\"";
WRM._unparsedData["jira.core:feature-flags-data.feature-flag-data"]="{\"enabled-feature-keys\":[\"com.atlassian.jira.agile.darkfeature.editable.detailsview\",\"nps.survey.inline.dialog\",\"com.atlassian.jira.agile.darkfeature.edit.closed.sprint.enabled\",\"jira.plugin.devstatus.phasetwo\",\"jira.frother.reporter.field\",\"atlassian.rest.xsrf.legacy.enabled\",\"jira.issue.status.lozenge\",\"com.atlassian.jira.config.BIG_PIPE\",\"com.atlassian.jira.projects.issuenavigator\",\"com.atlassian.jira.config.PDL\",\"jira.plugin.devstatus.phasetwo.enabled\",\"atlassian.aui.raphael.disabled\",\"app-switcher.new\",\"frother.assignee.field\",\"com.atlassian.jira.projects.ProjectCentricNavigation.Switch\",\"jira.onboarding.cyoa\",\"com.atlassian.jira.agile.darkfeature.kanplan.enabled\",\"com.atlassian.jira.config.ProjectConfig.MENU\",\"com.atlassian.jira.projects.sidebar.DEFER_RESOURCES\",\"com.atlassian.jira.agile.darkfeature.kanplan.epics.and.versions.enabled\",\"com.atlassian.jira.agile.darkfeature.sprint.goal.enabled\",\"jira.zdu.admin-updates-ui\",\"jira.zdu.jmx-monitoring\",\"sd.new.settings.sidebar.location.disabled\",\"jira.zdu.cluster-upgrade-state\",\"com.atlassian.jira.agile.darkfeature.splitissue\",\"com.atlassian.jira.config.CoreFeatures.LICENSE_ROLES_ENABLED\",\"jira.export.csv.enabled\"],\"feature-flag-states\":{\"mail.batching.override.core\":true,\"jira.spectrum.m1\":true,\"jira.spectrum.m2\":false,\"com.atlassian.jira.issuetable.draggable\":true,\"mail.batching\":false,\"com.atlassian.jira.agile.darkfeature.kanban.hide.old.done.issues\":true,\"jira.jql.suggestrecentfields\":false,\"com.atlassian.jira.agile.darkfeature.backlog.showmore\":true,\"com.atlassian.jira.agile.darkfeature.optimistic.transitions\":true,\"com.atlassian.jira.issuetable.move.links.hidden\":true,\"jira.renderer.consider.variable.format\":true,\"com.atlassian.jira.agile.darkfeature.kanplan\":false,\"jira.priorities.per.project.jsd\":true,\"jira.instrumentation.laas\":false,\"com.atlassian.jira.agile.darkfeature.rapid.boards.bands\":true,\"com.atlassian.jira.sharedEntityEditRights\":true,\"jira.customfields.paginated.ui\":true,\"com.atlassian.jira.agile.darkfeature.edit.closed.sprint\":false,\"jira.create.linked.issue\":true,\"mail.batching.user.notification\":true,\"jira.spectrum.m1b\":true,\"com.atlassian.jira.agile.darkfeature.sprint.goal\":false,\"com.atlassian.jira.agile.darkfeature.dataonpageload\":true,\"com.atlassian.jira.agile.darkfeature.sidebar.boards.list\":true,\"jira.sal.host.connect.accessor.existing.transaction.will.create.transactions\":true,\"com.atlassian.jira.custom.csv.escaper\":true,\"com.atlassian.jira.plugin.issuenavigator.filtersUxImprovment\":true,\"com.atlassian.jira.agile.darkfeature.kanplan.epics.and.versions\":false,\"jira.quick.search\":true,\"jira.jql.smartautoselectfirst\":false,\"com.atlassian.jira.projects.per.project.permission.query\":true,\"com.atlassian.jira.issues.archiving\":false,\"com.atlassian.jira.projects.archiving\":true,\"index.use.snappy\":true,\"jira.priorities.per.project\":true,\"com.atlassian.jira.upgrade.startup.fix.index\":true}}";
WRM._unparsedData["jira.core:default-comment-security-level-data.DefaultCommentSecurityLevelHelpLink"]="{\"extraClasses\":\"default-comment-level-help\",\"title\":\"Commenting on an Issue\",\"url\":\"https://docs.atlassian.com/jira/jcore-docs-080/Editing+and+collaborating+on+issues#Editingandcollaboratingonissues-restrictacomment\",\"isLocal\":false}";
WRM._unparsedData["com.atlassian.analytics.analytics-client:policy-update-init.policy-update-data-provider"]="false";
WRM._unparsedData["com.atlassian.analytics.analytics-client:programmatic-analytics-init.programmatic-analytics-data-provider"]="false";
WRM._unparsedData["jira.core:dateFormatProvider.allFormats"]="{\"dateFormats\":{\"meridiem\":[\"AM\",\"PM\"],\"eras\":[\"BC\",\"AD\"],\"months\":[\"January\",\"February\",\"March\",\"April\",\"May\",\"June\",\"July\",\"August\",\"September\",\"October\",\"November\",\"December\"],\"monthsShort\":[\"Jan\",\"Feb\",\"Mar\",\"Apr\",\"May\",\"Jun\",\"Jul\",\"Aug\",\"Sep\",\"Oct\",\"Nov\",\"Dec\"],\"weekdaysShort\":[\"Sun\",\"Mon\",\"Tue\",\"Wed\",\"Thu\",\"Fri\",\"Sat\"],\"weekdays\":[\"Sunday\",\"Monday\",\"Tuesday\",\"Wednesday\",\"Thursday\",\"Friday\",\"Saturday\"]},\"lookAndFeelFormats\":{\"relativize\":\"true\",\"time\":\"h:mm a\",\"day\":\"EEEE h:mm a\",\"dmy\":\"dd/MMM/yy\",\"complete\":\"dd/MMM/yy h:mm a\"}}";
WRM._unparsedData["jira.core:avatar-picker-data.data"]="{}";
WRM._unparsedData["com.atlassian.jira.jira-header-plugin:dismissedFlags.flags"]="{\"dismissed\":[]}";
WRM._unparsedData["com.atlassian.jira.jira-header-plugin:newsletter-signup-tip-init.newsletterSignup"]="{\"signupDescription\":\"Get updates, inspiration and best practices from the team behind Jira.\",\"formUrl\":\"https://www.atlassian.com/apis/exact-target/{0}/subscribe?mailingListId=1401671\",\"signupTitle\":\"Sign up!\",\"signupId\":\"newsletter-signup-tip\",\"showNewsletterTip\":false}";
WRM._unparsedData["com.atlassian.jira.project-templates-plugin:project-templates-plugin-resources.ptAnalyticsData"]="{\"instanceCreatedDate\":\"2019-04-02\"}";
WRM._unparsedData["jira.core:user-message-flags-data.adminLockout"]="{}";
WRM._unparsedData["com.atlassian.plugins.helptips.jira-help-tips:help-tip-manager.JiraHelpTipData"]="{\"anonymous\":true}";
if(window.WRM._dataArrived)window.WRM._dataArrived();</script>
<link type="text/css" rel="stylesheet" href="/s/cbabb9286747633077899771de831d72-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/527ab6cb8db8e0b715fcef781f7fd0ca/_/download/contextbatch/css/_super/batch.css" data-wrm-key="_super" data-wrm-batch-type="context" media="all">
<link type="text/css" rel="stylesheet" href="/s/b58772d61db1abedd1dbd5a6da780d56-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/e9e6f4459890741d438b1d0e5902cfee/_/download/contextbatch/css/atl.general,jira.global,-_super/batch.css?agile_global_admin_condition=true&amp;jag=true" data-wrm-key="atl.general,jira.global,-_super" data-wrm-batch-type="context" media="all">
<link type="text/css" rel="stylesheet" href="/s/d41d8cd98f00b204e9800998ecf8427e-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/8.0.1/_/download/batch/com.atlassian.auiplugin:split_aui.pattern.label/com.atlassian.auiplugin:split_aui.pattern.label.css" data-wrm-key="com.atlassian.auiplugin:split_aui.pattern.label" data-wrm-batch-type="resource" media="all">
<link type="text/css" rel="stylesheet" href="/s/d41d8cd98f00b204e9800998ecf8427e-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/8.0.1/_/download/batch/com.atlassian.auiplugin:split_aui.splitchunk.16f099a0da/com.atlassian.auiplugin:split_aui.splitchunk.16f099a0da.css" data-wrm-key="com.atlassian.auiplugin:split_aui.splitchunk.16f099a0da" data-wrm-batch-type="resource" media="all">
<link type="text/css" rel="stylesheet" href="/s/a345de820c7e980f23a3703f6bb51899-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/1.0/_/download/batch/jira.webresources:global-static-adgs/jira.webresources:global-static-adgs.css" data-wrm-key="jira.webresources:global-static-adgs" data-wrm-batch-type="resource" media="all">
<link type="text/css" rel="stylesheet" href="/s/0dcda96854a49e304f60a09f37e45410-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/1.0/_/download/batch/jira.webresources:global-static/jira.webresources:global-static.css" data-wrm-key="jira.webresources:global-static" data-wrm-batch-type="resource" media="all">
<script type="text/javascript" src="/s/792990a3720a5fc71cb74dbd3c9b28d0-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/527ab6cb8db8e0b715fcef781f7fd0ca/_/download/contextbatch/js/_super/batch.js?locale=en-US" data-wrm-key="_super" data-wrm-batch-type="context" data-initially-rendered></script>
<script type="text/javascript" src="/s/86858128f3565138795bc75c583226b0-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/e9e6f4459890741d438b1d0e5902cfee/_/download/contextbatch/js/atl.general,jira.global,-_super/batch.js?agile_global_admin_condition=true&amp;jag=true&amp;locale=en-US" data-wrm-key="atl.general,jira.global,-_super" data-wrm-batch-type="context" data-initially-rendered></script>
<script type="text/javascript" src="/s/5a77de8f87ac426dbe2a6afd0d4be2dc-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/aae1242f5fc81cc6a5bb8bc963ccda29/_/download/contextbatch/js/atl.global,-_super/batch.js?locale=en-US" data-wrm-key="atl.global,-_super" data-wrm-batch-type="context" data-initially-rendered></script>
<script type="text/javascript" src="/s/84e48334f69873dcebc81660fa6a53eb-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/8.0.1/_/download/batch/com.atlassian.auiplugin:split_aui.pattern.label/com.atlassian.auiplugin:split_aui.pattern.label.js?locale=en-US" data-wrm-key="com.atlassian.auiplugin:split_aui.pattern.label" data-wrm-batch-type="resource" data-initially-rendered></script>
<script type="text/javascript" src="/s/84e48334f69873dcebc81660fa6a53eb-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/8.0.1/_/download/batch/com.atlassian.auiplugin:split_aui.splitchunk.16f099a0da/com.atlassian.auiplugin:split_aui.splitchunk.16f099a0da.js?locale=en-US" data-wrm-key="com.atlassian.auiplugin:split_aui.splitchunk.16f099a0da" data-wrm-batch-type="resource" data-initially-rendered></script>
<script type="text/javascript" src="/s/84e48334f69873dcebc81660fa6a53eb-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/8.0.1/_/download/batch/com.atlassian.auiplugin:split_aui.pattern.table/com.atlassian.auiplugin:split_aui.pattern.table.js?locale=en-US" data-wrm-key="com.atlassian.auiplugin:split_aui.pattern.table" data-wrm-batch-type="resource" data-initially-rendered></script>
<link type="text/css" rel="stylesheet" href="/s/69ac650ed7edc7503ab14f5239fa8488-CDN/-btxz5u/800010/6411e0087192541a09d88223fb51a6a0/504e626a69bbf59826668b7d855c4d61/_/download/contextbatch/css/jira.global.look-and-feel,-_super/batch.css" data-wrm-key="jira.global.look-and-feel,-_super" data-wrm-batch-type="context" media="all">

<script type="text/javascript" src="/rest/api/1.0/shortcuts/800010/a41d4c63750ef98b987554387fb853ff/shortcuts.js"></script>


    <meta name="application-name" content="JIRA" data-name="jira" data-version="8.0.2">
</head>
<body id="jira" class="aui-layout aui-style-default page-type-message"  data-version="8.0.2" >
    <div class="aui-page-panel"><div class="aui-page-panel-inner">
            <section class="aui-page-panel-content">
                    <header class="aui-page-header"><div class="aui-page-header-inner">
                            <div class="aui-page-header-main">
                                    <h1>Forbidden (403)</h1>
                                </div><!-- .aui-page-header-main -->
                        </div><!-- .aui-page-header-inner --></header><!-- .aui-page-header -->
                    <div class="aui-message aui-message-warning warning">
                            <p>Encountered a <code>&quot;403 - Forbidden&quot;</code> error while loading this page.</p>
                            <p>Basic Authentication Failure - Reason : AUTHENTICATION_DENIED</p>
                            <p><a href="/secure/MyJiraHome.jspa">Go to Jira home</a></p>
                        </div>
                </section><!-- .aui-page-panel-content -->
        </div><!-- .aui-page-panel-inner --></div><!-- .aui-page-panel -->
</body>
</html>
"""

captcha_sig = \
    "'X-Authentication-Denied-Reason': 'CAPTCHA_CHALLENGE"

logging.debug(captcha_sig in response)

unittest.main()