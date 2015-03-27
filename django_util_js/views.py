# -*- coding: utf-8 -*-

"""
#=============================================================================
#
#     FileName: views.py
#         Desc: django's util in javascript. such as url_for etc.
#
#       Author: dantezhu
#        Email: zny2008@gmail.com
#     HomePage: http://www.vimer.cn
#
#      Created: 2012-11-28 15:11:48
#      History:
#               0.0.1 | dantezhu | 2012-11-28 15:11:48 | init
#               0.0.2 | dantezhu | 2012-11-28 21:13:39 | no cache
#               0.0.3 | dantezhu | 2012-11-29 23:36:24 | url encode
#               0.0.4 | dantezhu | 2012-11-30 11:00:46 | content-type
#               0.0.5 | dantezhu | 2013-07-16 12:06:59 | 使用encodeURIComponent，否则中文有问题
#
#=============================================================================
"""

import re
import sys
import types
from django.utils.datastructures import SortedDict
from django.conf import settings
from django.http import HttpResponse
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.shortcuts import RequestContext
from django.template import Context, loader

UTIL_JS_TPL = '''
{% autoescape off %}
var django_util = function() {

    var rule_map = {{ rule_map }};

    function _get_path(name, kwargs, urls) {

        var path = urls[name] || false;

        if (!path) {
            throw('URL not found for view: ' + name);
        }

        var _path = path;

        var key;
        for (key in kwargs) {
            if (kwargs.hasOwnProperty(key)) {
                if (!path.match('<' + key +'>')) {
                    throw(key + ' does not exist in ' + _path);
                }
                path = path.replace('<' + key +'>', encodeURIComponent(kwargs[key]));
            }
        }

        var re = new RegExp('<[a-zA-Z0-9-_]{1,}>', 'g');
        var missing_args = path.match(re);
        if (missing_args) {
            throw('Missing arguments (' + missing_args.join(", ") + ') for url ' + _path);
        }

        return path;

    }

    return {
        url_for: function(name, kwargs, urls) {
            if (!urls) {
                urls = rule_map || {};
            }

            return _get_path(name, kwargs, urls);
        },
        rule_map: rule_map
    };

}();
{% endautoescape %}
'''

def django_util_js(request):

    RE_KWARG = re.compile(r"(\(\?P\<(.*?)\>.*?\))") #Pattern for recongnizing named parameters in urls
    RE_ARG = re.compile(r"(\(.*?\))") #Pattern for recognizing unnamed url parameters

    def force_str(src):
        if src is None:
            src = ''
        return src.encode('utf8') if isinstance(src, unicode) else src

    def handle_url_module(js_patterns, module_name, prefix=""):
        """
        Load the module and output all of the patterns
        Recurse on the included modules
        """
        if isinstance(module_name, basestring):
            __import__(module_name)
            root_urls = sys.modules[module_name]
            patterns = root_urls.urlpatterns
        elif isinstance(module_name, types.ModuleType):
            root_urls = module_name
            patterns = root_urls.urlpatterns
        else:
            root_urls = module_name
            patterns = root_urls

        for pattern in patterns:
            if issubclass(pattern.__class__, RegexURLPattern):
                # add by dantezhu
                if pattern.name or getattr(pattern, '_callback_str', None):
                    full_url = prefix + pattern.regex.pattern
                    # 为了解决类似 /site\_media\/
                    full_url = re.sub(r'\\(\S)', '\\1', full_url)

                    for chr in ["^","$"]:
                        full_url = full_url.replace(chr, "")
                    #handle kwargs, args
                    kwarg_matches = RE_KWARG.findall(full_url)
                    if kwarg_matches:
                        for el in kwarg_matches:
                            #prepare the output for JS resolver
                            full_url = full_url.replace(el[0], "<%s>" % el[1])
                    #after processing all kwargs try args
                    args_matches = RE_ARG.findall(full_url)
                    if args_matches:
                        for el in args_matches:
                            full_url = full_url.replace(el, "<>")#replace by a empty parameter name
                    if pattern.name:
                        js_patterns[force_str(pattern.name)] = force_str("/" + full_url)
                    # add by dantezhu
                    if getattr(pattern, '_callback_str', None):
                        js_patterns[force_str(pattern._callback_str)] = force_str("/" + full_url)

            elif issubclass(pattern.__class__, RegexURLResolver):
                if pattern.urlconf_name:
                    # modified by dantezhu
                    handle_url_module(js_patterns, pattern.urlconf_name, prefix=prefix+pattern.regex.pattern)

    js_patterns = SortedDict()
    handle_url_module(js_patterns, settings.ROOT_URLCONF)

    t = loader.get_template_from_string(UTIL_JS_TPL)
    c = Context(dict(
        rule_map=js_patterns,
    ))
    c.update(RequestContext(request))
    
    content = t.render(c)

    response = HttpResponse(
        content, 
        content_type='text/javascript; charset=UTF-8',
        )
    response['Cache-Control'] = 'no-cache'
    return response
