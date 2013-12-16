django_util_js
==============
django's util in javascript. such as url_for etc.

### usage

###### install django_util_js to your server app

    1. add to INSTALLED_APPS
        INSTALLED_APPS = (
            ...
            'django_util_js',
        )
    2. add to urls.py
        url(r'^django_util.js$', 'django_util_js.views.django_util_js'),

###### load django_util.js in your html file

    <script src="{% url 'django_util_js.views.django_util_js' %}" type="text/javascript" charset="utf-8"></script>


###### use url_for in your js code

    var url = django_util.url_for('sub.bpt_index', {y:2, x:'/sdf'});
