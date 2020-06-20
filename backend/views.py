import pytz
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone

from . import models
from django.db.models import Q
import datetime
from django.db.models import Sum,Count,Avg
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from . import Mypaginator
from django.core import serializers
from django.contrib import auth
import markdown

current_id = 0
# Create your views here.

# 首页视图
def index(request):
    global current_id
    user = models.user.objects.filter(username=request.user).first()
    if request.user.is_authenticated and user.is_superuser == 0:
        islogin = "true"
        userid = user.id
    else:
        islogin = "false"
        userid = 27
    recommend = models.recommendion.objects.filter(uid=userid).first()
    if(recommend==None):
        recommend = models.recommendion.objects.filter(id=27).first()
    hot = convert_recommend(recommend)
    mv_ch_hot = models.movie.objects.filter(language__contains='汉语').order_by('-comment_num')[:12]
    mv_ch_rate = models.movie.objects.filter(language__contains='汉语').order_by('-rate')[:12]
    mv_ch_new = models.movie.objects.exclude(language__contains='英语').filter(Q(language__contains='汉语')&Q(rate_num__gte=100)).order_by('-date')[:12]
    mv_fr_hot = models.movie.objects.exclude(language__contains='汉语').order_by('-comment_num')[:12]
    mv_fr_rate = models.movie.objects.exclude(language__contains='汉语').order_by('-rate')[:12]
    mv_fr_new = models.movie.objects.exclude(language__contains='汉语').filter(rate_num__gte=100).order_by('-date')[:12]

    # 查询近一个月内平均评分最高的电影，ids代表找出的电影id合集
    cur_date = datetime.datetime.now()
    last_month = cur_date - datetime.timedelta(weeks=12)
    id_week_praise = models.rate.objects.filter(Q(time__gte=last_month)&Q(time__lte=cur_date)&Q(rate__gte=8))
    sum = id_week_praise.annotate(Avg('rate')).order_by('-rate__avg').values("movie_id")
    ids = []
    cnt=0
    for item in sum:
        if cnt < 10:
            ids.append(item['movie_id'])
        cnt = cnt + 1
    week = models.movie.objects.filter(id__in = ids).order_by('-rate')

    comment_hot = models.comment.objects.filter(favor_num__gte=50).extra(where=["length(comment)>200"]).order_by('-favor_num')[:10]
    comment_args = []
    for item in comment_hot:
        tmp={}
        mvid = item.movie_id.id
        uid = item.uid.id
        movie = models.movie.objects.get(id=mvid)
        tmp['username'] = models.user.objects.get(id=uid).username
        tmp['mvid'] = movie.id
        tmp['mvname'] = movie.name
        tmp['cmt'] = item
        comment_args.append(tmp)

    args = {"hot": hot , "mv_ch_hot": mv_ch_hot, "mv_ch_rate": mv_ch_rate, "mv_ch_new": mv_ch_new,
            "mv_fr_hot": mv_fr_hot, "mv_fr_rate": mv_fr_rate, "mv_fr_new": mv_fr_new,
            "week":week,"comment_args":comment_args,"is_login":islogin,"user":user}
    return render(request,'index.html',args)


# 处理注册ajax请求
def register(request):
    global current_id
    username = request.GET.get("username")
    pwd = request.GET.get("password")
    email = request.GET.get("email")
    u = models.user.objects.filter(username=username)
    if u:
        args = {"flag":"exist"}
    else:
        user = models.user.objects.create_user(username=username,password=pwd,email=email)
        auth.login(request,user)
        current_id = user.id
        args = {"username":username,"flag":"success"}
    return JsonResponse(args)


# 处理登录ajax请求
def login(request):
    global current_id
    username = request.GET.get("username")
    pwd = request.GET.get("password")
    user = models.user.objects.get(username=username)
    next_url = request.META.get('HTTP_REFERER', '/')
    if check_password(pwd,user.password):
        auth.login(request,user)
        current_id=user.id
        args = {"flag":"success","username":username}
    else:
        args = {"flag":"fail"}
    return JsonResponse(args)


def logout_view(request):
    logout(request)
    return redirect("/")

# 电影详情页视图
def moviesingle(request,mvid):
    global current_id
    current_page = int(request.GET.get("page", 1))
    offset = int(request.GET.get("offset", 5))
    max_comment_num = models.comment.objects.filter(movie_id=mvid).count()

    # 获取评论对应分类数据
    start = str((current_page - 1) * offset)
    end = str(str(current_page * offset))
    sql = "SELECT * FROM comment ORDER BY favor_num DESC LIMIT " + start + ',' + end + ';'
    comment = models.comment.objects.raw(sql)

    # 获取电影信息
    movie = models.movie.objects.get(id=mvid)
    director = movie.director.split('/')
    writer = movie.writer.split('/')
    actor = movie.actor.split('/')
    related_movie = []
    related_movie.append(models.movie.objects.get(id=20))
    related_movie.append(models.movie.objects.get(id=94))
    related_movie.append(models.movie.objects.get(id=19))
    related_movie.append(models.movie.objects.get(id=134))
    related_movie.append(models.movie.objects.get(id=132))

    # 计算页码范围
    page_range,page_num = count_page_range(max_comment_num,offset,current_page)
    user = models.user.objects.filter(username=request.user).first()
    if user==None:
        args = {"movie": movie, "comment": comment, "comment_num": max_comment_num, "page_range": page_range,
                "mvid": mvid, "director": director, "writer": writer, "actor": actor, "current_page": current_page,
                "page_num": page_num, "is_login": "false",'usr_rate':0}
    else:
        rate = models.rate.objects.filter(uid=user.id,movie_id=mvid)
        if(rate):usr_rate = rate.first().rate
        else:
            usr_rate = 0
        args = {"movie": movie, "comment": comment, "comment_num": max_comment_num, "page_range": page_range,
                "mvid": mvid, "director": director, "writer": writer, "actor": actor,"current_page":current_page,
                "page_num":page_num,"is_login":"true","user":user,'usr_rate':usr_rate,"related_movie":related_movie}
    return render(request, 'moviesingle.html', args)


# 电影详情页分页ajax
def moviesingle_page(request,mvid):
    current_page = int(request.GET.get("page", 1))
    offset = int(request.GET.get("offset", 5))
    max_comment_num = models.comment.objects.filter(movie_id=mvid).count()
    page_range, page_num = count_page_range(max_comment_num, offset, current_page)
    start = str((current_page - 1) * offset)
    sql = "SELECT * FROM comment ORDER BY favor_num DESC LIMIT " + start + ',' + str(offset) + ';'
    comment_raw = models.comment.objects.raw(sql)
    comment = []
    for item in comment_raw:
        cmt = {}
        cmt['id'] = item.id
        cmt['uid'] = item.uid
        cmt['movie_id'] = item.movie_id
        cmt['comment'] = item.comment
        cmt['time'] = item.time
        cmt['favor_num'] = item.favor_num
        cmt['oppo_num'] = item.oppo_num
        cmt['rate'] = item.rate
        comment.append(cmt)
    #print(comment)
    args = {"current_page":current_page,"page_range":page_range,"cmt":comment}
    return JsonResponse(args)


def rate(request):
    user = models.user.objects.get(username=request.user)
    mvid = request.GET.get('mvid')
    movie = models.movie.objects.get(id=mvid)
    rate = request.GET.get('rate')
    rate_item = models.rate.objects.filter(uid=user,movie_id=mvid)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    utc_timezone = pytz.timezone("UTC")
    #now = now.replace(tzinfo=pytz.timezone('Asia/Shanghai'))
    #utc_now = now.astimezone(utc_timezone)
    if rate_item:
        rate_item.update(rate=rate)
        rate_item.update(time=now)
    else:
        models.rate.objects.create(uid=user, movie_id=movie, rate=rate, time=now)
    return JsonResponse({'result':True})


def shortcomment(request):
    content = request.GET.get('content')
    mvid = request.GET.get('mvid')
    movie = models.movie.objects.get(id=mvid)
    user = models.user.objects.get(username=request.user)
    rate_item = models.rate.objects.filter(movie_id=mvid,uid=user.id).first()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if(rate_item):rates=rate_item.rate
    else:rates=0
    models.comment.objects.create(uid=user,movie_id=movie,rate=rates,comment=content,time=now)
    return JsonResponse({'result': True})


def movielist(request):
    current_page = int(request.GET.get("page",1))
    user = models.user.objects.filter(username=request.user).first()
    if user:
        is_login = "true"
    else:
        is_login = "false"
    count = models.movie.objects.all().count()
    args={"current_page":current_page,"is_login":is_login,"user":user,"count":count}
    return render(request,'movielist.html',args)


# 电影搜索视图
def moviesearch(request):
    current_page = int(request.GET.get("page", 1))
    offset = int(request.GET.get("offset", 10))
    ordering = request.GET.get("ordering", "rate DESC")
    name = request.GET.get('mvname', '')
    types_str = request.GET.get('types','')
    rate_dowm = request.GET.get('rate_down','0')
    rate_up = request.GET.get('rate_up','10')
    year_start = request.GET.get("date_start", '')
    year_end = request.GET.get("date_end", '')
    user = models.user.objects.filter(username=request.user).first()
    if user:
        is_login = "true"
    else:
        is_login = "false"
    args = {"name":name,"types":types_str,"rate_up":rate_up,"rate_down":rate_dowm,"year_start":year_start,"year_end":year_end,"offset":offset}
    return JsonResponse(args)


# 电影搜索ajax
def moviesearchlayui(request):
    current_page = int(request.GET.get("page", 1))
    offset = int(request.GET.get('offset', 10))
    ordering = request.GET.get("ordering")
    start = str((current_page-1) * offset)
    end = str(offset)
    name = request.GET.get('name')
    type_str = request.GET.get('types')
    types = type_str.split(',')
    rate_up = request.GET.get('rate_up','10')
    if rate_up == '':
        rate_up = '10'
    rate_down = request.GET.get('rate_down','0')
    if rate_down == '':
        rate_down='0'
    year_start = request.GET.get("year_start",'1900-01-01')
    if year_start == '':
        year_start='1900-01-01'
    year_end = request.GET.get("year_end",'2020-12-31')
    if year_end == '':
        year_end='2020-12-31'
    type_sql = '('
    for item in types:
        if len(type_sql)>1:
            type_sql = type_sql + ' or '
        type_sql = type_sql + "type like '%%%%%s%%%%' " % item
    type_sql = type_sql + ') '
    #sql = "SELECT * FROM backend_movie WHERE " + type_sql + " and name like'%%%% %s%%%%' and rate BETWEEN %s and %s and date " \
    #            "BETWEEN %s and %s LIMIT %s,%s" % (name,rate_down,rate_up,year_start,year_end,start,end)
    sql = "SELECT * FROM movie WHERE " + type_sql + " and name like '%%%%%s%%%%' and rate BETWEEN %s and %s and date BETWEEN '%s' and '%s' LIMIT %s,%s" % (name,rate_down,rate_up,year_start,year_end,start,end)
    movie = []
    movie_raw = models.movie.objects.raw(sql)
    count_sql = "SELECT * FROM movie WHERE " + type_sql + " and name like '%%%%%s%%%%' and rate BETWEEN %s and %s and date BETWEEN '%s' and '%s'" % (name,rate_down,rate_up,year_start,year_end)
    total = models.movie.objects.raw(count_sql)
    count = len(list(total))
    for item in movie_raw:
        cmt = {}
        cmt['id'] = item.id
        cmt['name'] = item.name
        cmt['intro'] = item.intro
        cmt['date'] = item.date
        cmt['director'] = item.director
        cmt['time'] = item.time
        cmt['writer'] = item.writer
        cmt['rate'] = item.rate
        movie.append(cmt)
    args = {"current_page": current_page, "name": name, "types": types,
            "year_start": year_start, "year_end": year_end,"movie":movie,"count":count}
    return JsonResponse(args)


# 处理电影列表layui
def movielistlayui(request):
    current_page = int(request.GET.get("page", 1))
    offset = int(request.GET.get("offset", 10))
    ordering = request.GET.get("ordering", "rate DESC")
    is_search = request.GET.get("search","false")
    start = str((current_page-1) * offset)
    end = str(offset)
    sql = "SELECT * FROM movie WHERE rate>0 and time>0 ORDER BY %s LIMIT %s,%s" % (ordering,start,end)
    movie_raw = models.movie.objects.raw(sql)
    count = models.movie.objects.all().count()
    max_page, t = divmod(count, offset)
    if (t):
        max_page = max_page + 1
    movie = []
    for item in movie_raw:
        cmt = {}
        cmt['id'] = item.id
        cmt['name'] = item.name
        cmt['intro'] = item.intro
        cmt['date'] = item.date
        cmt['director'] = item.director
        cmt['time'] = item.time
        cmt['writer'] = item.writer
        cmt['rate'] = item.rate
        movie.append(cmt)
    args = {"page": current_page, "movie": movie,"pages":max_page}
    return JsonResponse(args)


# 电音图标视图
def moviegrid(request):
    current_page = int(request.GET.get("page", 1))
    offset = int(request.GET.get("offset", 20))
    count = models.movie.objects.all().count()
    user = models.user.objects.get(username=request.user)
    max_page, t = divmod(count, offset)
    if (t):
        max_page = max_page + 1
    user = models.user.objects.filter(username=request.user).first()
    if user:
        is_login = "true"
    else:
        is_login = "false"
    args = {"max_page": max_page, "current_page": current_page,"count":count,"user":user,"is_login":is_login,"user":user}
    return render(request,'moviegrid.html',args)


#电影图标layui
def moviegridlayui(request):
    current_page = int(request.GET.get("page", 1))
    offset = int(request.GET.get("offset", 20))
    ordering = request.GET.get("ordering", "rate DESC")
    start = str((current_page-1) * offset)
    end = str(offset)
    sql = "SELECT * FROM movie WHERE rate>0 and time>0 ORDER BY %s  LIMIT %s,%s" % (ordering, start, end)
    movie_raw = models.movie.objects.raw(sql)
    count = models.movie.objects.all().count()
    max_page, t = divmod(count, offset)
    if (t):
        max_page = max_page + 1
    movie = []
    for item in movie_raw:
        cmt = {}
        cmt['id'] = item.id
        cmt['name'] = item.name
        cmt['intro'] = item.intro
        cmt['date'] = item.date
        cmt['director'] = item.director
        cmt['time'] = item.time
        cmt['writer'] = item.writer
        cmt['rate'] = item.rate
        movie.append(cmt)
    args = {"page": current_page + 1, "movie": movie, "pages": max_page}
    return JsonResponse(args)


def userprofile(request):
    user = models.user.objects.get(username=request.user)
    if request.user.is_authenticated:
        args = {"user":user,"is_login":"true"}
        return render(request,'userprofile.html',args)
    else:
        print("no login")
        return render(request,'404.html')

def userchangeinfo(request):
    user = models.user.objects.get(username=request.user)
    email = request.GET.get("email")
    first_name = request.GET.get("first_name")
    last_name = request.GET.get("last_name")
    nickname = request.GET.get("nickname")
    flag = False
    #print(email,first_name,last_name,nickname)
    if email and email != user.email:
        user.email = email
        flag=True
    if last_name and last_name != user.last_name:
        user.last_name = last_name
        flag=True
    if first_name and first_name != user.first_name:
        user.first_name = first_name
        flag=True
    if nickname and nickname != user.nickname:
        user.nickname = nickname
        flag=True

    user.save()
    args = {"email":email,"first_name":first_name,"last_name":last_name,"nickname":nickname,"flag":flag}
    return JsonResponse(args)


def userchangepwd(request):
    pwd1 = request.GET.get("pwd1")
    pwd2 = request.GET.get("pwd2")
    user = models.user.objects.get(username=request.user)
    if(pwd1==pwd2):
        return JsonResponse({"flag":False})
    else:
        user.set_password(pwd2)
        return JsonResponse({"flag":True})


def usercomments(request):
    user = models.user.objects.get(username=request.user)
    comment = models.comment.objects.filter(uid=user.id).order_by("time")
    count = comment.count()
    comment = comment[:5]
    data = []
    for item in comment:
        tmp = {}
        movie = item.movie_id
        tmp['movie'] = movie.name
        tmp['comment'] = item.comment
        tmp['time'] = item.time
        tmp['rate'] = item.rate
        tmp['mvid'] = movie.id
        data.append(tmp)
    page_range,page_num = count_page_range(count,5,1)
    args = {"current_page":1,"count":count,"data":data,"page_range":page_range}
    return render(request,'userrate.html',args)


def usercommentslayui(request):
    pass


def count_page_range(max_item_num,offset,current_page):
    page_num, mods = divmod(max_item_num, offset)
    if mods:
        page_num = page_num + 1
    if page_num < 9:
        page_start = 1
        page_end = page_num + 1
    else:
        if current_page <= 4:
            page_start = 1
            page_end = 9
        else:
            if current_page + 4 > page_num:
                page_start = current_page - 4
                page_end = page_num + 1
            else:
                page_start = current_page - 4
                page_end = current_page + 4
    page_range = []
    for i in range(page_start, page_end):
        page_range.append(i)
    return page_range,page_num



def writeblog(request):
    return render(request,'writeblog.html',{"is_login":"true"})


def blogpost(request):
    title = request.GET.get('title')
    name = request.GET.get('name')
    movie = models.movie.objects.get(name=name)
    msg = request.GET.get('message')
    user = models.user.objects.get(username=request.user)
    blogs = models.blog.objects.create(author_id=user.id,movie_id=movie.id,title=title,body=msg)
    return redirect('/blogdetail/%d' % blogs.id)



def blogdetail(request,id):
    blog = models.blog.objects.get(id=id)
    blog.body =  markdown.markdown(blog.body,
        extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',

        # 目录扩展
        'markdown.extensions.toc',
        ]
    )
    user = models.user.objects.filter(username=request.user).first()
    if user:
        is_login = "true"
    else:
        is_login = "false"
    return render(request,'blogdetail.html',{'blog':blog,"is_login":is_login})

def bloglist(request):
    user = models.user.objects.filter(username=request.user).first()
    if user:
        is_login = "true"
    else:
        is_login = "false"
    blogs = models.blog.objects.all().order_by('-create_time')
    args = {"user":user,"blogs":blogs,"is_login":is_login}
    return render(request,'bloglist.html',args)


def adjustRecommend(request):
    print("comming")
    user = models.user.objects.get(username="user13542")
    auth.login(request, user)
    mv1 = models.movie.objects.get(id=17)
    mv2 = models.movie.objects.get(id=8)
    mv3 = models.movie.objects.get(id=178)
    mv4 = models.movie.objects.get(id=26)
    mv5 = models.movie.objects.get(id=21)
    mv6 = models.movie.objects.get(id=453)
    mv7 = models.movie.objects.get(id=242)
    mv8 = models.movie.objects.get(id=373)
    mv9 = models.movie.objects.get(id=45)
    mv10 = models.movie.objects.get(id=772)
    mv11 = models.movie.objects.get(id=23)
    mv12 = models.movie.objects.get(id=28)
    models.recommendion.objects.create(uid=user,mv1=mv1,mv2=mv2,mv3=mv3,mv4=mv4,mv5=mv5,mv6=mv6,mv7=mv7,mv8=mv8,mv9=mv9,mv10=mv10,mv11=mv11,mv12=mv12)
    return redirect('/')


def convert_recommend(q):
    res = []
    res.append(q.mv1)
    res.append(q.mv2)
    res.append(q.mv3)
    res.append(q.mv4)
    res.append(q.mv5)
    res.append(q.mv6)
    res.append(q.mv7)
    res.append(q.mv8)
    res.append(q.mv9)
    res.append(q.mv10)
    res.append(q.mv11)
    res.append(q.mv12)
    return res