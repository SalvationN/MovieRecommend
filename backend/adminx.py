import xadmin
from .models import movie, rate, comment, blog, user, recommendion


class movieAdmin(object):
    list_display = ['id','name','rate','rate_num','comment_num','type','director','writer','area','language','date','time']
    search_fields = ['name']
    list_filter = ['rate','type','time']
    model_icon = "fa fa-toggle-right"
    list_editable = ['name','type','area','actor','writer','language']
    ordering = ['id',]
    class Meta:
        verbose_name = "电影"
        verbose_name_plural = verbose_name


class rateAdmin(object):
    list_display = ['id','uid','movie_id','rate','time']
    list_filter = ['rate','time']
    ordering = ['id',]
    model_icon = "fa fa-star-o"


class commentAdmin(object):
    list_display = ['id','uid','movie_id','comment','time']
    list_filter = ['time']
    model_icon = 'fa fa-comments-o'



class blogAdmin(object):
    list_display = ['id','title','body','author','movie','create_time']
    model_icon = 'fa fa-edit'

class recommendationAdmin(object):
    model_icon = 'fa fa-film'
    list_display = ['uid','mv1','mv2','mv3','mv4','mv5','mv6','mv7','mv8','mv9','mv10','mv11','mv12']


xadmin.site.register(movie,movieAdmin)
xadmin.site.register(rate,rateAdmin)
xadmin.site.register(comment,commentAdmin)
xadmin.site.register(blog,blogAdmin)
xadmin.site.register(recommendion,recommendationAdmin)

