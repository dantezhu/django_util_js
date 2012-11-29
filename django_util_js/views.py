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
#      Version: 0.0.2
#      History:
#               0.0.1 | dantezhu | 2012-11-28 15:11:48 | init
#               0.0.2 | dantezhu | 2012-11-28 21:13:39 | no cache
#
#=============================================================================
"""

import re
import sys
import types
from django.utils.datastructures import SortedDict
from django.conf import settings
from django.http import HttpResponse
import django.utils.simplejson as json
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver

UTIL_JS_TPL = """
var django_util = function(){

    function _get_path(name, kwargs, urls)
    {

        var path = urls[name] || false;

        if (!path)
        {
            throw('URL not found for view: ' + name);
        }

        var _path = path;

        var key;
        for (key in kwargs)
        {
            if (kwargs.hasOwnProperty(key)) {
                if (!path.match('<' + key +'>'))
                {
                    throw(key + ' does not exist in ' + _path);
                }
                path = path.replace('<' + key +'>', kwargs[key]);
            }
        }

        var re = new RegExp('<[a-zA-Z0-9-_]{1,}>', 'g');
        var missing_args = path.match(re);
        if (missing_args)
        {
            throw('Missing arguments (' + missing_args.join(", ") + ') for url ' + _path);
        }

        return path;

    }

    return {
        url_for: function(name, kwargs, urls) {
            if (!urls)
            {
                urls = django_urlconf || {};
            }

            return _get_path(name, kwargs, urls);
        }
    };

}();

var django_urlconf = %s;
"""

def django_util_js(request):

    RE_KWARG = re.compile(r"(\(\?P\<(.*?)\>.*?\))") #Pattern for recongnizing named parameters in urls
    RE_ARG = re.compile(r"(\(.*?\))") #Pattern for recognizing unnamed url parameters

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
                if pattern.name or hasattr(pattern, '_callback_str'):
                    full_url = prefix + pattern.regex.pattern
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
                    js_patterns[pattern.name] = "/" + full_url
                    # add by dantezhu
                    if hasattr(pattern, '_callback_str'):
                        js_patterns[pattern._callback_str] = "/" + full_url

            elif issubclass(pattern.__class__, RegexURLResolver):
                if pattern.urlconf_name:
                    # modified by dantezhu
                    handle_url_module(js_patterns, pattern.urlconf_name, prefix=prefix+pattern.regex.pattern)

    js_patterns = SortedDict()
    handle_url_module(js_patterns, settings.ROOT_URLCONF)

    content = UTIL_JS_TPL % js_patterns

    response = HttpResponse(content, mimetype='text/javascript')
    response['Cache-Control'] = 'no-cache'
    return response
